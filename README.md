# UNC Dorm AI Guide

An intelligent chatbot that helps UNC Chapel Hill first-year students find their ideal dorm through conversational AI.

## Project Motivation

Choosing a first-year dorm shapes the college experience. Generic AI models lack UNC-specific knowledge. This project provides trustworthy, personalized dorm recommendations based on real student experiences, making it easier for newcomers to navigate Carolina’s housing landscape.

## Why RAG?

We enhanced Google's Gemini AI with RAG (Retrieval-Augmented Generation) to ground responses in authentic UNC housing data. Gemini handles natural language queries, while RAG retrieves context from student reviews and housing guides, ensuring recommendations are accurate, actionable, and tailored to Carolina culture.

## Features

- **AI-Powered Recommendations**: Uses Gemini AI with RAG for data-driven dorm suggestions  
- **Interactive Chat Interface**: Clean UI with real-time responses and typing animations  
- **Chat History**: Save, load, and manage multiple sessions  
- **Smart Search**: Filter past messages for specific info  
- **Expandable Responses**: "Show more" to view detailed recommendations  

## Tech Stack

**Backend:** FastAPI, Gemini 2.5 Flash, TF-IDF RAG system, Python with scikit-learn  
**Frontend:** React + Vite, modern CSS, LocalStorage for session persistence  

## Project Structure

```
├── Backend/          # FastAPI server and RAG implementation
├── Frontend/         # React chat interface
└── data/docs/        # UNC housing data corpus
```


## Setup

1. Install backend dependencies: `pip install -r Backend/requirements.txt`  
2. Add Gemini API key to `Backend/.env`  
3. Install frontend dependencies: `npm install` in `Frontend/`  
4. Run backend: `python Backend/app.py`  
5. Run frontend: `npm run dev` in `Frontend/`
