import sys
import os
import logging
import streamlit as st

# Add the project root directory to the Python path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

from utils import document_loader, vectorstore, prompts, search
from models.llm import gemini_generate, groq_generate


def process_document(uploaded_file, url, pasted_text):
    """
    Extracts text from a source and builds a vector store.
    """
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
        elif pasted_text and pasted_text.strip():
            text = pasted_text
        else:
            # Added a check for empty pasted_text
            st.error("Please provide a document, URL, or paste text to process.")
            return None

        chunks = document_loader.split_text(text)
        vectorstore.create_vectorstore(chunks)
        st.session_state["doc_text"] = text
        logging.info("Document processing successful.")
        return text
    except Exception as e:
        logging.error(f"Error in process_document: {e}", exc_info=True)
        st.error(f"Failed to process the document. Error: {e}")
        return None


def perform_initial_analysis(text, model_choice, detail_level):
    """
    Generates a summary and extracts the company name from the text.
    """
    try:
        logging.info(f"Performing initial analysis with {model_choice}.")
        llm_generate = groq_generate if model_choice == "Groq" else gemini_generate

        # Use the SUMMARY_PROMPT for initial analysis
        summary_prompt = prompts.SUMMARY_PROMPT.format(
            context=text[:2500], # Provide a slightly larger context for better summary
            question="Summarize this document for a user.",
            detail_level=detail_level.lower()
        )
        summary = llm_generate(summary_prompt).strip()
        logging.info("Summary generated.")
        
        # A simple way to guess the company name
        company_name = "the document"
        lines = text.split('\n')
        if lines:
            # Often the first non-trivial line has the title or company
            for line in lines[:10]:
                if len(line.strip()) > 5: # Avoid short/empty lines
                    company_name = line.strip()
                    break
        logging.info(f"Extracted company/document name: {company_name}")

        return {"summary": summary, "company_name": company_name}
    except Exception as e:
        logging.error(f"Error in perform_initial_analysis: {e}", exc_info=True)
        return {
            "summary": "Could not generate a summary for the document.",
            "company_name": "the document"
        }


def get_response(query, detail_level, app_mode, model_choice):
    """
    Gets a response based on the selected application mode.
    """
    logging.info(f"--- Starting response generation for mode: {app_mode} ---")
    llm_generate = groq_generate if model_choice == "Groq" else gemini_generate
    
    try:
        if app_mode == "Analyzer":
            # RAG-based response using the uploaded document
            vs = vectorstore.load_vectorstore()
            if not vs:
                st.warning("No document is loaded. Please process a document first for analysis.")
                return "I need a document to analyze. Please use the 'Attach' button to upload one."

            context_docs = vs.similarity_search(query, k=3)
            context = "\n".join([d.page_content for d in context_docs])
            prompt = prompts.QA_PROMPT.format(context=context, question=query, detail_level=detail_level.lower())

        elif app_mode == "T&C Writer":
            # Generate legal clauses from user's informal input
            prompt = prompts.REWRITE_PROMPT.format(clause=query)

        else:  # General Chat
            # General conversation, with optional web search for context
            logging.info("No document context found. Performing live web search.")
            context = search.live_web_search(query)
            prompt = prompts.GENERAL_CHAT.format(context=context, question=query, detail_level=detail_level.lower())

        logging.info(f"Generating answer with {model_choice}...")
        answer = llm_generate(prompt)
        logging.info("--- Response generation finished successfully. ---")
        return answer.strip()

    except Exception as e:
        logging.error(f"CRITICAL ERROR in get_response: {e}", exc_info=True)
        st.error(f"An error occurred: {e}")
        return "Sorry, a critical error occurred. Please check the application logs."


def clear_document_memory():
    """Clears document-related data from the session state."""
    keys_to_clear = ["document_processed", "doc_text", "doc_summary", "company_name"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    # Keep chat history for now, or clear it as well if desired
    # st.session_state.messages = []
    st.rerun()


def main_app_page(app_mode):
    """
    Renders the main application page based on the selected mode.
    """
    st.title(f"ClauseMate: {app_mode}")

    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        detail_level = st.radio("Response Mode", ["Concise", "Detailed"])
        model_choice = st.selectbox("Select Model", ["Groq", "Gemini"], key="model_choice")
        st.divider()

        # Analyzer-specific sidebar items
        if app_mode == "Analyzer":
            if st.session_state.get("document_processed"):
                st.success(f"Document Loaded: {st.session_state.get('company_name', 'Unknown')}")
                if st.button("Clear Document Memory", use_container_width=True):
                    clear_document_memory()
            else:
                st.info("No document loaded for analysis.")

    # Document processing UI (only for Analyzer mode)
    if app_mode == "Analyzer":
        if st.session_state.get("document_processed") and "doc_summary" in st.session_state:
            with st.expander("Document Preview", expanded=False):
                st.info(f"Currently analyzing: **{st.session_state.get('company_name', 'an unknown company')}**.")
                st.markdown(f"**Summary:** {st.session_state.get('doc_summary', 'Not available.')}")

        # Attachment expander
        with st.expander("Attach Document", expanded=not st.session_state.get("document_processed", False)):
            input_method = st.radio("Input method:", ["Upload", "URL", "Text"], horizontal=True)
            
            uploaded_file = url = pasted_text = None
            if input_method == "Upload":
                uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
            elif input_method == "URL":
                url = st.text_input("Enter the URL")
            else:
                pasted_text = st.text_area("Paste your text here", height=150)

            if st.button("Process Document", type="primary"):
                with st.spinner("Processing document..."):
                    text = process_document(uploaded_file, url, pasted_text)
                    if text:
                        analysis = perform_initial_analysis(text, model_choice, detail_level)
                        st.session_state.update(analysis)
                        st.session_state.document_processed = True
                        st.rerun()

    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if query := st.chat_input(f"Ask a question in {app_mode} mode..."):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.spinner("Generating response..."):
            response = get_response(query, detail_level, app_mode, model_choice)
            with st.chat_message("assistant"):
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})


def about_page():
    """Renders the 'About' page with updated instructions."""
    st.title("About ClauseMate")
    st.markdown("""
    ### What is ClauseMate?
    **ClauseMate** is your AI-powered legal assistant, designed to help you understand and create complex legal documents. It operates in three distinct modes:

    1.  **Analyzer:** Upload a legal document (like Terms & Conditions or a Privacy Policy), and ClauseMate will answer your specific questions about its content.
    2.  **T&C Writer:** Provide informal notes or bullet points, and ClauseMate will draft them into formal, professional legal clauses suitable for an official document.
    3.  **General Chat:** Ask general questions about legal concepts or how standard policies work. ClauseMate will use its knowledge and web search to provide informative answers.

    ### How to Use the App
    1.  **Select a Mode:** Use the radio buttons in the sidebar to choose between **Analyzer**, **T&C Writer**, or **General Chat**.
    2.  **Adjust Settings:** In the sidebar, you can select the AI model (Groq for speed, Gemini for power) and choose between "Concise" or "Detailed" responses.

    #### Using the Analyzer
    - Click the **Attach Document** expander.
    - Choose to upload a file (PDF/DOCX), paste a URL, or paste raw text.
    - Click **Process Document**. Once processed, you can ask questions about the document in the chat box (e.g., "What does this say about data retention?").

    #### Using the T&C Writer
    - Simply type your requirements into the chat box (e.g., "Users can't share their login info. We can close accounts if they misuse the service.").
    - ClauseMate will rewrite your input into a formal legal clause.

    #### Using General Chat
    - Ask any general question in the chat box (e.g., "What is a limitation of liability clause?").
    """)


def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="ClauseMate",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state variables
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("model_choice", "Groq")

    with st.sidebar:
        st.title("ClauseMate")
        st.subheader("Your AI Legal Assistant")
        st.divider()

        # App navigation
        page = st.radio("Navigation", ["App", "About"])
        st.divider()
        
        # Mode selection is now part of the sidebar settings
        app_mode = st.radio("Choose Mode:", ["Analyzer", "T&C Writer", "General Chat"], key="app_mode")

        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    if page == "About":
        about_page()
    else:
        main_app_page(app_mode)


if __name__ == "__main__":
    main()
