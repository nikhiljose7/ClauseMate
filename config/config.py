from dotenv import load_dotenv
import os
import streamlit as st

# Load environment variables from .env (for local use)
load_dotenv()

# === API KEYS ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") or st.secrets.get("TAVILY_API_KEY")

# === DEFAULT MODELS ===
DEFAULT_GROQ_MODEL = "llama3-70b-8192"  # or any other supported by Groq
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"  

# === DOCUMENT CHUNKING ===
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# === FAISS Index Path ===
VECTOR_DB_PATH = "vectorstore/faiss_index"
