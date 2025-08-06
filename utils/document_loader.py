from langchain.text_splitter import RecursiveCharacterTextSplitter
import docx
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
from config.config import CHUNK_SIZE, CHUNK_OVERLAP

def extract_text_from_pdf(file):
    """
    Extract text from uploaded PDF.
    """
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def extract_text_from_docx(file):
    """
    Extract text from uploaded DOCX.
    """
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_from_url(url):
    """
    Extract raw text from a web page.
    """
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")

def split_text(text):
    """
    Split text into overlapping chunks for embedding.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_text(text)
