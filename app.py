import sys
import os
import logging
from datetime import datetime

# --- FIX FOR IMPORT ERRORS ---
# Add the project root directory to the Python path.
# This ensures that all modules (like utils, models, and config) can be found.
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

# --- SETUP LOGGING ---
# This will make sure the logs appear in the Streamlit Cloud console.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # Explicitly direct logs to standard output
)

from utils import document_loader, vectorstore, prompts, search
from models.llm import gemini_generate, groq_generate


def process_document(uploaded_file, url, pasted_text):
    """Extracts text from the provided source and builds a vector store."""
    try:
        logging.info("Starting document processing.")
        if uploaded_file:
            text = (
                document_loader.extract_text_from_pdf(uploaded_file)
                if uploaded_file.type == "application/pdf"
                else document_loader.extract_text_from_docx(uploaded_file)
            )
        elif url:
            text = document_loader.extract_text_from_url(url)
        elif pasted_text.strip():
            text = pasted_text
        else:
            raise ValueError("Please provide a document by uploading a file, entering a URL, or pasting text.")

        chunks = document_loader.split_text(text)
        vectorstore.create_vectorstore(chunks)
        st.session_state["doc_text"] = text
        logging.info("Document processing successful.")
        return text
    except Exception as e:
        logging.error("Error in process_document", exc_info=True)
        raise e


def perform_initial_analysis(text, model_choice, mode):
    """Generates a summary and extracts the company name from the text."""
    try:
        logging.info(f"Performing initial analysis with {model_choice}.")
        llm_generate = groq_generate if model_choice == "Groq" else gemini_generate
        
        summary_prompt = prompts.SUMMARY_PROMPT.format(
            context=text[:2000],
            question="Can you summarize this document in a clear and simple way for users?",
            detail_level=mode.lower()
        )
        summary = llm_generate(summary_prompt).strip()
        logging.info("Summary generated.")

        company_name = "an unknown company"
        lines = text.split("\n")
        for line in lines[:15]:
            if "terms" in line.lower() and ("for" in line.lower() or "of" in line.lower()):
                company_name = line.strip()
                break
        logging.info("Company name extracted.")

        return {
            "summary": summary,
            "company_name": company_name
        }
    except Exception as e:
        logging.error("Error in perform_initial_analysis", exc_info=True)
        return {
            "summary": "Could not generate summary.",
            "company_name": "an unknown company"
        }


def get_rag_response(query, mode, special_mode, model_choice):
    """Gets a response from the RAG pipeline."""
    logging.info(f"--- Starting RAG response for query: '{query}' with model: {model_choice} ---")
    try:
        vs = vectorstore.load_vectorstore()
        context_docs = vs.similarity_search(query, k=3) if vs else []
        
        if context_docs:
            logging.info("Found context from existing document.")
            context = "\n".join([d.page_content for d in context_docs])
        else:
            logging.info("No document context found. Performing live web search.")
            context = search.live_web_search(query)
            logging.info("Live web search successful.")

        history = "".join(f"{('User' if msg['role'] == 'user' else 'Assistant')}: {msg['content']}\n" for msg in st.session_state.tc_messages)
        
        prompt_question = f"{history}User: {query}\n"
        prompt = prompts.QA_PROMPT.format(context=context, question=prompt_question, detail_level=mode.lower())
        
        llm_generate = groq_generate if model_choice == "Groq" else gemini_generate
        logging.info(f"Generating answer with {model_choice}...")
        answer = llm_generate(prompt)
        logging.info("Answer generated successfully.")

        if special_mode:
            logging.info("Applying special mode: Rewriting to legal language.")
            rewrite_prompt = prompts.REWRITE_PROMPT.format(clause=answer)
            answer = llm_generate(rewrite_prompt)
            logging.info("Rewrite successful.")

        logging.info("--- RAG response finished successfully. ---")
        return answer.strip()
    except Exception as e:
        logging.error(f"CRITICAL ERROR in get_rag_response: {e}", exc_info=True)
        st.error(f"An error occurred: {e}")
        logging.shutdown() # Force logs to be written
        return "Sorry, a critical error occurred. Please check the application logs for details."


def clear_document_memory():
    """Clears all document-related data from the session state."""
    doc_keys = ["document_processed", "doc_text", "doc_summary", "company_name"]
    for key in doc_keys:
        st.session_state.pop(key, None)
    st.session_state.tc_messages = []
    st.rerun()


def analyzer_page():
    """Renders the main analyzer page."""
    st.title("Terms & Conditions Analyzer")

    with st.sidebar:
        st.header("Settings")
        mode = st.radio("Response Mode", ["Concise", "Detailed"])
        special_mode = st.checkbox("Rewrite to Legal Language")
        model_choice = st.selectbox("Select Model", ["Groq", "Gemini"], key="model_choice")
        
        st.divider()

        if st.session_state.get("document_processed"):
            st.success("Document Loaded")
        else:
            st.info("No document loaded. You can generate content directly.")

        if st.button("Clear Document Memory", use_container_width=True):
            clear_document_memory()

    if st.session_state.get("document_processed") and "doc_summary" in st.session_state:
        with st.expander("Document Preview", expanded=False):
            st.info(f"Currently analyzing: **{st.session_state.get('company_name', 'an unknown company')}**.")
            st.markdown(f"**Summary:** {st.session_state.get('doc_summary', 'Not available.')}")

    # --- MODIFICATION: Display speaker names instead of time ---
    for message in st.session_state.tc_messages:
        name = "You" if message["role"] == "user" else "ClauseMate"
        with st.chat_message(message["role"]):
            st.markdown(f"**{name}**")
            st.markdown(message["content"])

    if st.session_state.get("show_attachment", False):
        with st.expander("Attach Document", expanded=True):
            input_method = st.radio("Choose input method:", ["Upload File (PDF/DOCX)", "Enter URL", "Paste Text"], horizontal=True)
            
            uploaded_file = url = pasted_text = None
            if input_method == "Upload File (PDF/DOCX)":
                uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
            elif input_method == "Enter URL":
                url = st.text_input("Enter the URL")
            else:
                pasted_text = st.text_area("Paste your text here", height=150)

            if st.button("Process Document", type="primary", use_container_width=True):
                with st.spinner("Processing document..."):
                    try:
                        text = process_document(uploaded_file, url, pasted_text)
                        analysis_results = perform_initial_analysis(text, model_choice, mode)

                        st.session_state.update(analysis_results)
                        st.session_state.document_processed = True
                        st.session_state.show_attachment = False
                        
                        preview_message_content = (
                            f"**Document Processed: {analysis_results.get('company_name')}**\n\n"
                            f"**Summary:**\n{analysis_results.get('summary')}"
                        )
                        # --- MODIFICATION: Remove time from message ---
                        st.session_state.tc_messages.append({
                            "role": "assistant",
                            "content": preview_message_content
                        })

                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to process document: {e}")
                        st.session_state.document_processed = False

    with st.container():
        col1, col2 = st.columns([1, 10])
        with col1:
            st.button("Attach", on_click=lambda: st.session_state.update(show_attachment=not st.session_state.get("show_attachment", False)))
        with col2:
            query = st.chat_input("Ask a question or request to generate Terms & Conditions...")

    if query:
        if not st.session_state.tc_messages or st.session_state.tc_messages[-1].get("content") != query:
            # --- MODIFICATION: Remove time from messages ---
            st.session_state.tc_messages.append({"role": "user", "content": query})
            
            with st.spinner("Generating response..."):
                answer = get_rag_response(query, mode, special_mode, model_choice)
            
            st.session_state.tc_messages.append({"role": "assistant", "content": answer})
            st.rerun()

def instructions_page():
    """Renders the instructions page."""
    st.title("How to Use This App")
    st.markdown("""
    This app helps you understand or write Terms & Conditions or legal documents.

    ### How It Works
    - **Analyze a Document:** Upload, paste, or link to a document to ask specific questions about it. The app uses Retrieval-Augmented Generation (RAG) to find the exact clauses in your document to answer your questions.
    - **Generate a Document:** If no document is uploaded, simply ask the AI to write one for you (e.g., "Write T&C for a mobile app"). It will use a live web search for context.

    ### Steps
    1.  Go to the **Analyzer** tab.
    2.  Click the **Attach** button to add a document (optional).
    3.  Ask a question or request a new document in the chat box below.
    """)


def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="T&C Analyzer",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.session_state.setdefault("tc_messages", [])
    st.session_state.setdefault("show_attachment", False)
    st.session_state.setdefault("model_choice", "Groq")

    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to:", ["Analyzer", "Instructions"])
        
        st.divider()

        if page == "Analyzer":
            if st.button("Clear Chat History", use_container_width=True):
                st.session_state.tc_messages = []
                st.rerun()

    if page == "Instructions":
        instructions_page()
    else:
        analyzer_page()


if __name__ == "__main__":
    main()
