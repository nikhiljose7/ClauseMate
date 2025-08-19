# ClauseMate

ClauseMate is your legal clause companion. It's a Streamlit web application that allows you to analyze legal documents. You can upload a PDF, provide a link to a webpage with terms and conditions, or paste the text of a document, and then ask questions about it. The application uses a large language model to understand the document and provide answers.

## Features

* **Multiple Input Methods:**
    * **PDF Document Upload:** Upload any legal document in PDF format.
    * **URL Input:** Provide a URL to a webpage containing terms and conditions or other legal text.
    * **Text Input:** Paste the text of your legal document directly into the application.
* **Question Answering:** Ask questions about the provided document in natural language.
* **Language Model Powered:** Uses a powerful language model to understand the context of the document and provide accurate answers.
* **User-Friendly Interface:** Simple and intuitive web interface built with Streamlit.

## How it Works

1.  **Document Loading:** The application uses different loaders based on your input: `PyPDFLoader` for PDFs, and it can also handle text from URLs and direct text input.
2.  **Text Splitting:** The document is split into smaller chunks of text for processing.
3.  **Embeddings:** The text chunks are converted into numerical representations (embeddings) using the `HuggingFaceInstructEmbeddings` model.
4.  **Vector Store:** The embeddings are stored in a `FAISS` vector store, which allows for efficient similarity search.
5.  **Language Model:** A `Llama-2-7b-chat` model is used to generate answers to the user's questions.
6.  **Question Answering Chain:** A question answering chain is created that takes the user's question, finds the most relevant text chunks from the vector store, and then uses the language model to generate an answer based on the retrieved context.

## How to Run

### Prerequisites

* Python 3.x
* The following packages:
    * streamlit
    * langchain
    * faiss-cpu
    * pypdf
    * python-dotenv
    * sentence-transformers
    * ctransformers

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/nikhiljose7/ClauseMate.git](https://github.com/nikhiljose7/ClauseMate.git)
    cd ClauseMate
    ```
2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Usage

1.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
2.  **Open your web browser** and go to the local URL provided by Streamlit (usually `http://localhost:8501`).
3.  **Choose your input method** in the sidebar: "Upload a PDF", "Enter a URL", or "Paste Text".
4.  **Provide the document** using your chosen method.
5.  **Ask a question** in the text input box and press Enter. The answer will be displayed below.
