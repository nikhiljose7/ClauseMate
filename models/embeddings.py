import torch
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embeddings_model():
    """
    Load the HuggingFace embeddings model with automatic device selection.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Using device: {device}")

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": device}
    )
