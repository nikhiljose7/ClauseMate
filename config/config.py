from dotenv import load_dotenv
import os
import streamlit as st

# Load environment variables from .env (used locally)
load_dotenv()

# API keys (fetched from environment or Streamlit secrets)
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") or st.secrets.get("TAVILY_API_KEY")

# Default model names
DEFAULT_GROQ_MODEL = "llama3-70b-8192"
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"

# Document chunking parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# FAISS index storage path
VECTOR_DB_PATH = "vectorstore/faiss_index"
