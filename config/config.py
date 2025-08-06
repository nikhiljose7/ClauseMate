from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # For live search
GROQ_API_KEY = os.getenv("GROQ_API_KEY")   # For live search


# Document chunking settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Path to store FAISS index
VECTOR_DB_PATH = "vectorstore/faiss_index"
