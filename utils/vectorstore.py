from langchain_community.vectorstores import FAISS
from models.embeddings import get_embeddings_model
import os
from config.config import VECTOR_DB_PATH

def create_vectorstore(chunks):
    """
    Create and save a FAISS vector store from text chunks.
    """
    embeddings = get_embeddings_model()
    vectordb = FAISS.from_texts(chunks, embeddings)
    vectordb.save_local(VECTOR_DB_PATH)
    print(f"✅ Vector store created and saved at: {VECTOR_DB_PATH}")

def load_vectorstore():
    """
    Load an existing FAISS vector store from disk.
    """
    if os.path.exists(VECTOR_DB_PATH):
        embeddings = get_embeddings_model()
        # ✅ This flag is REQUIRED for new LangChain versions
        return FAISS.load_local(
            folder_path=VECTOR_DB_PATH,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
    print("⚠ No existing vector store found.")
    return None
