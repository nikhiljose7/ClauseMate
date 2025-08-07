from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# === API KEYS ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# === DEFAULT MODELS ===
DEFAULT_GROQ_MODEL = "llama3-70b-8192"  # or any other supported by Groq

DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"  

# === DOCUMENT CHUNKING ===
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# === FAISS Index Path ===
VECTOR_DB_PATH = "vectorstore/faiss_index"
