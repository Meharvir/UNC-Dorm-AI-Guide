# UNC Dorm AI Guide

An intelligent chatbot that helps UNC Chapel Hill first-year students find their ideal dorm through conversational AI.

## Project Motivation

As UNC students, we recognized that choosing a first-year dorm is a critical decision that significantly impacts the college experience. Generic AI models lack specific knowledge about UNC's unique housing landscape and student experiences. We built this project to solve a real problem we faced: finding trustworthy, personalized dorm recommendations based on actual student feedback rather than official descriptions alone.

## Why RAG?

We enhanced Google's Gemini AI with RAG (Retrieval-Augmented Generation) to ground responses in real UNC housing data. While Gemini provides conversational intelligence, RAG ensures every recommendation is backed by authentic student reviews and experiences from sources like RoomSurf. This combination delivers both accuracy and personalization—Gemini understands natural language queries while RAG retrieves relevant context from our curated database of UNC student sentiments, making recommendations specific to Carolina's housing culture.

## Features

- **AI-Powered Recommendations**: Uses Google's Gemini AI with RAG (Retrieval-Augmented Generation) to provide accurate, data-driven dorm suggestions
- **Interactive Chat Interface**: Clean, modern UI with real-time responses and typing animations
- **Chat History**: Save, load, and manage multiple conversation sessions
- **Smart Search**: Filter through past messages to find specific information
- **Expandable Responses**: "Show more" button to view full detailed recommendations

## Tech Stack

**Backend:**
- FastAPI for the REST API
- Google Gemini 2.5 Flash for AI responses
- TF-IDF based RAG system for context retrieval
- Python with scikit-learn

**Frontend:**
- React + Vite
- Modern CSS 
- LocalStorage for session persistence

## Project Structure

```
├── Backend/          # FastAPI server and RAG implementation
├── Frontend/         # React chat interface
└── data/docs/        # UNC housing data corpus
```

## Setup

1. Install backend dependencies: `pip install -r Backend/requirements.txt`
2. Add your Gemini API key to `Backend/.env`
3. Install frontend dependencies: `npm install` in `Frontend/`
4. Run backend: `python Backend/app.py`
5. Run frontend: `npm run dev` in `Frontend/`
