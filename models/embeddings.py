'''from langchain.embeddings import HuggingFaceEmbeddings

def get_embeddings_model():
    """
    Load the embeddings model for semantic search.
    """
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"'''
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embeddings_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}  # or "cuda" if you have GPU
    )
