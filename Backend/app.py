# app.py

import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from prompt_builder import build_prompt

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

class Query(BaseModel):
    message: str

@app.post("/query")
async def get_dorm_recommendation(query: Query):
    prompt = build_prompt(query.message)

    model = genai.GenerativeModel("gemini-pro")

    response = model.generate_content(prompt)

    return {"response": response.text}
