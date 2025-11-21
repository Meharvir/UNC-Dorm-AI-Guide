# app.py - Fixed UNC Dorm Guide

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import uuid
from typing import Optional
from datetime import datetime
import re
from rag_query import build_context, retrieve
from rag_index import build_index

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    message: str
    session_id: Optional[str] = None
    expand: Optional[bool] = False

# Session and chat history
user_sessions = {}
chat_history = {}

def extract_user_info(message: str, session_id: str):
    """Extract basic user info from messages"""
    message_lower = message.lower()
    if session_id not in user_sessions:
        user_sessions[session_id] = {}
    user = user_sessions[session_id]

    # Extract name
    name_patterns = [r"my name is (\w+)", r"i'm (\w+)", r"i am (\w+)", r"call me (\w+)"]
    for pattern in name_patterns:
        match = re.search(pattern, message_lower)
        if match:
            user["name"] = match.group(1).capitalize()
            break

    # Extract major
    if "computer science" in message_lower or " cs " in message_lower:
        user["major"] = "Computer Science"
    elif "business" in message_lower:
        user["major"] = "Business"

def _friendly_source_name(filename: str) -> str:
    """Convert a filename like 'hinton_james.txt' to a friendly source string."""
    name = os.path.basename(filename)
    name = re.sub(r'\.txt$', '', name, flags=re.IGNORECASE)
    name = name.replace('_', ' ').title()
    return f"Source: RAG Knowledge — {name}"


def format_response(text: str, expand: bool = False):
    """Format Gemini response for optimal chat readability.

    If `expand` is False, return a short, emoji-rich summary suitable for chat.
    If `expand` is True, return the full cleaned content.
    """
    if not text:
        return "I'm sorry — no content returned."

    # Remove control / weird characters and stray markdown
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    text = text.replace('`', '')
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)  # Remove bold/italic
    text = re.sub(r'#{1,6}\s*', '', text)  # Remove headers
    # Normalize bullets
    text = re.sub(r'[•\u2022\u2023\u25E6]', '-', text)

    # Replace filename citations like [hinton_james.txt] with friendly source names
    def _replace_fn(m):
        fname = m.group(1)
        return f"[{_friendly_source_name(fname)}]"
    text = re.sub(r'\[([^\]]+\.txt)\]', _replace_fn, text, flags=re.IGNORECASE)

    # If user requested expanded content, return cleaned full text
    if expand:
        return text.strip()

    # Otherwise produce a concise summary + short numbered list when possible
    lines = [ln.strip() for ln in text.split('\n') if ln.strip()]

    # Try to detect key dorm lines (simple heuristic)
    dorms = []
    for line in lines:
        m = re.match(r'^(Horton|Hinton James|Avery|Spencer|Craige North|Morrison)[\s\-:–—]*(.*)', line, re.IGNORECASE)
        if m:
            name = m.group(1).title()
            summary = m.group(2).strip()
            dorms.append((name, summary))

    if dorms:
        # Build short numbered list
        short_lines = ["🏆 Best Dorms for Studying at UNC:"]
        for i, (name, summary) in enumerate(dorms[:5]):
            snippet = summary if summary else ''
            snippet = snippet.split('.')[0][:80].strip()
            short_lines.append(f"{i+1}. {name} — {snippet}".strip())
        short_lines.append('\nWant a breakdown of each? 👇')
        short = '\n'.join(short_lines)
        # enforce short length
        if len(short) > 320:
            short = short[:300].rstrip() + '...\n\nWant a breakdown of each? 👇'
        # Remove duplicate lines and repeated greetings
        seen = set()
        cleaned_lines = []
        for ln in short.split('\n'):
            ln_stripped = ln.strip()
            if not ln_stripped:
                continue
            if ln_stripped.lower().startswith('welcome to'):
                continue
            if ln_stripped in seen:
                continue
            seen.add(ln_stripped)
            cleaned_lines.append(ln_stripped)
        return '\n'.join(cleaned_lines)

    # Fallback: produce first 2 meaningful sentences
    joined = ' '.join(lines)
    sentences = re.split(r'(?<=[.!?])\s+', joined)
    summary = ' '.join(sentences[:2]).strip()
    if len(summary) > 320:
        summary = summary[:300].rstrip() + '...'
    summary += '\n\nWant a breakdown of each? 👇'
    return summary

def build_prompt(message: str, session_id: str, context: str = None):
    """Build a prompt for a ChatGPT-like structured response, with optional retrieved context."""
    user_info = user_sessions.get(session_id, {})
    user_name = user_info.get("name", "Student")
    base = (
        f"You are a helpful UNC dorm advisor. Answer the following question with a well-structured, clear, and informative response.\n\n"
        f"Question from {user_name}: {message}\n\n"
        "Below is context retrieved from our trusted RAG database. If it is relevant, use it to answer. If not, use your own knowledge, but always generate a structured, clear response and cite sources when possible.\n"
        "RESPONSE STRUCTURE:\n1. Start with a brief, one-sentence summary.\n2. Provide 2-3 recommendations, each with a short paragraph (location, why it's good, pros/cons, and cite sources).\n3. Always cite sources and include follow-up suggestions.\n4. If multiple sources are available, aggregate and compare them.\n5. If the answer is uncertain, say so.\n"
    )
    if context:
        base += f"\nRAG Context:\n{context}\n\nUse the information above to ground your answer and cite sources when appropriate."
    # Force concise single-block answers suitable for chatbot UX
    base += (
        "\nOUTPUT RULES:\n- Answer in a single concise block; do not include multiple Q&A or repeated greetings.\n"
        "- Start with a short emoji summary if listing recommendations (one line).\n"
        "- Do not repeat the user's question or include internal filenames.\n"
        "- If you want to offer more detail, append a single line: 'Want a breakdown of each? 👇' and stop.\n"
        "- Keep the response short (max ~300 characters) unless asked to expand.\n"
    )
    return base
from fastapi.responses import JSONResponse
import glob
import traceback
@app.get("/dorms")
async def list_dorms():
    # List all dorms based on files in data/docs
    dorm_files = glob.glob(os.path.join(os.path.dirname(__file__), '..', 'data', 'docs', '*_hall_reviews.txt'))
    dorms = [os.path.basename(f).replace('_hall_reviews.txt', '').replace('_', ' ').title() for f in dorm_files]
    return {"dorms": dorms}

@app.get("/dorm/{name}")
async def dorm_details(name: str):
    # Return dorm details and reviews
    dorm_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'docs', f"{name.lower().replace(' ', '_')}_hall_reviews.txt")
    if not os.path.exists(dorm_file):
        return JSONResponse(status_code=404, content={"error": "Dorm not found"})
    with open(dorm_file, encoding="utf-8") as f:
        reviews = f.read()
    return {"dorm": name.title(), "reviews": reviews}

@app.get("/reviews/{name}")
async def dorm_reviews(name: str):
    # Alias for dorm_details
    return await dorm_details(name)

@app.get("/policies")
async def housing_policies():
    # Return housing policies file
    policies_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'docs', 'carolina_housing_policies.txt')
    if not os.path.exists(policies_file):
        return JSONResponse(status_code=404, content={"error": "Policies file not found"})
    with open(policies_file, encoding="utf-8") as f:
        policies = f.read()
    return {"policies": policies}

@app.get("/search")
async def search_dorms(q: str, k: int = 5):
    # Search all docs for relevant passages
    try:
        results = retrieve(q, k=k)
        return {"query": q, "results": results}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()})

@app.get("/status")
async def index_status():
    # Show index status
    index_path = os.path.join(os.path.dirname(__file__), 'rag_index.pkl')
    exists = os.path.exists(index_path)
    size = os.path.getsize(index_path) if exists else 0
    return {"index_exists": exists, "index_size": size}

@app.post("/rebuild-index")
async def rebuild_index():
    try:
        build_index()
        return {"status": "Index rebuilt"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()})

@app.post("/query")
async def chat(query: Query):
    session_id = query.session_id or str(uuid.uuid4())
    if session_id not in chat_history:
        chat_history[session_id] = []

    # Track user info
    extract_user_info(query.message, session_id)

    # Retrieve relevant context using local RAG (optional)
    context = None
    try:
        context = build_context(query.message, k=3)
    except FileNotFoundError:
        # Index not yet built — try to build and retry once
        try:
            print('RAG index missing; building index...')
            build_index()
            context = build_context(query.message, k=3)
        except Exception as e:
            print('RAG build/retrieve error:', e)
            context = None
    except Exception as e:
        print('RAG retrieve error:', e)
        context = None

    prompt = build_prompt(query.message, session_id, context)

    # Use Gemini 2.5-flash with simple response handling
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    try:
        response = model.generate_content(prompt)
        
        # Simple response extraction
        raw_answer = response.text.strip() if response.text else ""
        
        if not raw_answer:
            raise Exception("Empty response from Gemini")

        # Format into concise bullet points (respect expand flag)
        answer = format_response(raw_answer, expand=query.expand)

        print(f"✅ Gemini raw: {raw_answer[:50]}...")
        print(f"✅ Formatted: {answer[:50]}...")

    except Exception as e:
        print(f"❌ Gemini error: {type(e).__name__}: {e}")
        # Better debug info
        if hasattr(e, 'response'):
            print(f"❌ Response details: {e.response}")
        
        answer = "I'm having trouble right now. Could you rephrase your question about UNC dorms?"

    # Save chat history (limit last 10 messages)
    chat_history[session_id].append({
        "user": query.message,
        "bot": answer,
        "timestamp": datetime.now().isoformat()
    })
    if len(chat_history[session_id]) > 10:
        chat_history[session_id] = chat_history[session_id][-10:]

    return {"response": answer, "session_id": session_id}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "UNC Dorm Guide is running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)
