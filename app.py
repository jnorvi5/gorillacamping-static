import os
import re
import random
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session, Response
from flask_compress import Compress
from pymongo import MongoClient
from urllib.parse import urlparse, parse_qs
import traceback
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import google.generativeai as genai

# --- FLASK SETUP ---
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'guerilla-camping-secret-2024')

Compress(app)

# --- CHROMADB + HUGGINGFACE EMBEDDINGS ---
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "gorillacamping_kb"
hf_ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
knowledge_base = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=hf_ef)

# --- GEMINI AI SETUP ---
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    raise RuntimeError("GEMINI_API_KEY must be set in environment")
genai.configure(api_key=gemini_api_key)

def ask_gemini(user_query, context=""):
    model = genai.GenerativeModel("gemini-pro")
    # This works for the current Gemini python API (June 2024)
    response = model.generate_content([{"role":"user", "parts":[context + "\n\n" + user_query]}])
    return response.text

# --- DB SETUP ---
try:
    mongodb_uri = os.environ.get('MONGODB_URI') or os.environ.get('MONGO_URI')
    if mongodb_uri:
        client = MongoClient(mongodb_uri)
        db = client.get_default_database()
        db.command('ping')
        print("✅ MongoDB connected successfully!")
    else:
        print("⚠️ No MongoDB URI found - running in demo mode")
        db = None
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    db = None

# --- BASIC ROUTES AND UTILITIES OMITTED FOR BREVITY ---

@app.route("/api/optimize", methods=['POST'])
def generative_ai_assistant():
    data = request.json
    user_query = data.get("query", "I need some camping advice.")
    # 1. RAG: Retrieve context from your knowledge base using HuggingFace embeddings
    results = knowledge_base.query(query_texts=[user_query], n_results=5)
    context = "\n\n---\n\n".join(results['documents'][0]) if results['documents'] else ""
    # 2. Gemini Prompt
    system_prompt = (
    "You are Guerilla the Gorilla, the smartest, most rugged, and resourceful ape in these digital jungles. "
    "You sound like a seasoned off-grid veteran—funny, a bit rough, always authentic. "
    "You help fellow tribe members with camping, gear, and survival. Share only what you know from the context. "
    "When you don’t know, say so, but always add a bit of Guerilla’s wisdom or a witty comment."
)
   
    
    try:
        ai_response = ask_gemini(user_query, context)
        # Optionally recommend gear based on AI answer (if you want to keep this function)
        gear_links = "" # You can implement your own logic here as needed
        if db:
            db.ai_logs.insert_one({
                "question": user_query,
                "ai_response": ai_response,
                "timestamp": datetime.utcnow(),
                "user_agent": request.headers.get('User-Agent'),
                "ip_hash": hash(request.remote_addr) if request.remote_addr else None,
            })
        return jsonify({"success": True, "response": ai_response + gear_links})
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return jsonify({"success": False, "message": "The AI brain is currently offline. Please try again later."})

from flask import session

@app.route("/api/optimize", methods=['POST'])
def generative_ai_assistant():
    # Limit: 3 free queries per session unless Pro
    if not session.get("pro_user"):
        session['queries'] = session.get('queries', 0) + 1
        if session['queries'] > 3:
            return jsonify({"success": False, "message": "Upgrade to Pro for unlimited AI!"})
    # ... rest of your existing code ...
# -- The rest of your Flask app (routes, Stripe, blog, etc) remains unchanged --
if __name__ == '__main__':
    app.run(debug=True)
