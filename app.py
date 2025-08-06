import streamlit as st
import os
import sys

# Adjust path to import local modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils import document_loader, vectorstore, prompts, search
from models.llm import gemini_generate,groq_generate

def process_document(uploaded_file, url, pasted_text):
    """
    Processes the uploaded document, URL, or pasted text to extract text,
    split it into chunks, and create a vector store.
    """
    try:
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                text = document_loader.extract_text_from_pdf(uploaded_file)
            else:
                text = document_loader.extract_text_from_docx(uploaded_file)
        elif url:
            text = document_loader.extract_text_from_url(url)
        elif pasted_text.strip():
            text = pasted_text
        else:
            return None, "Please provide a document by uploading a file, entering a URL, or pasting text."

        chunks = document_loader.split_text(text)
        vectorstore.create_vectorstore(chunks)
        return text, None
    except Exception as e:
        return None, f"Error processing document: {str(e)}"

def get_rag_response(query, mode, special_mode):
    """
    Gets a response from the RAG model based on the user's query and the processed document.
    """
    try:
        vs = vectorstore.load_vectorstore()
        if not vs:
            return "⚠ No document processed yet. Please upload or paste text first."

        docs = vs.similarity_search(query, k=3)
        context = "\n".join([d.page_content for d in docs]) if docs else search.live_web_search(query)

        prompt = prompts.RAG_PROMPT.format(context=context, question=query, detail_level=mode.lower())
        #answer = gemini_generate(prompt)
        answer = groq_generate(prompt)

        if special_mode:
            rewrite_prompt = prompts.REWRITE_PROMPT.format(clause=answer)
            #answer = gemini_generate(rewrite_prompt)
            answer =  groq_generate(rewrite_prompt)

        return answer
    except Exception as e:
        return f"Error getting response: {str(e)}"

def instructions_page():
    """
    Displays the user guide and explains how the app works.
    """
    st.title("📜 How to Use This App")
    st.markdown("""
    This app helps you quickly understand complex documents like Terms & Conditions or legal agreements.

    ### 🤔 How It Works
    You provide a document, and the AI reads and understands it. When you ask a question, the bot finds the most relevant information within that document and uses it to give you a clear and simple answer. It's like having a helpful assistant who has already read the fine print for you!

    ### 🚀 How to Use
    1.  Go to the **Analyzer** page from the sidebar navigation.
    2.  Click the **➕ button** to open the document attachment section.
    3.  Choose your preferred method: **upload a file**, **paste a web link**, or **paste text** directly.
    4.  Click the **"Process Document"** button and wait for the success message.
    5.  Once the document is loaded, you can start asking questions in the chat box at the bottom of the screen!

    ### ⚙️ Settings
    - **Response Mode**: Choose "Concise" for short answers or "Detailed" for more thorough explanations.
    - **Rewrite to Legal Language**: Check this box if you want the AI to phrase its answers in a more formal, legal style.
    - **Clear Document Memory**: Use this to remove the current document and start over with a new one.
    """)

def analyzer_page():
    """
    Displays the main T&C Analyzer page with chat and document processing functionality.
    """
    st.title("⚖️ Terms & Conditions Analyzer")

    with st.sidebar:
        st.header("Settings")
        mode = st.radio("Response Mode", ["Concise", "Detailed"])
        special_mode = st.checkbox("Rewrite to Legal Language")

        if st.session_state.get("document_processed"):
            st.success("Document Loaded ✅")
        else:
            st.warning("No Document Loaded ⚠️")

        if st.button("Clear Document Memory", use_container_width=True):
            st.session_state.pop("document_processed", None)
            st.session_state.tc_messages = []
            st.rerun()

    st.session_state.setdefault("tc_messages", [])
    st.session_state.setdefault("show_attachment", False)

    def toggle_attachment():
        st.session_state.show_attachment = not st.session_state.show_attachment

    for message in st.session_state.tc_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.show_attachment:
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
                    text, error = process_document(uploaded_file, url, pasted_text)
                    if error:
                        st.error(error)
                        st.session_state.document_processed = False
                    else:
                        st.session_state.document_processed = True
                        st.success("Document processed successfully!")
                        st.session_state.show_attachment = False
                        st.rerun()

    with st.container():
        col1, col2 = st.columns([1, 10])
        with col1:
            st.button("➕", on_click=toggle_attachment)
        with col2:
            query = st.chat_input("Ask a question about the document...")

    if query:
        st.session_state.tc_messages.append({"role": "user", "content": query})
        
        # Check if a document has been processed before getting a response
        if not st.session_state.get("document_processed"):
            st.session_state.tc_messages.append({
                "role": "assistant", 
                "content": "⚠️ Please upload a document to use the chatbot. Click the '➕' button to attach a document."
            })
        else:
            with st.spinner("Analyzing and generating response..."):
                answer = get_rag_response(query, mode, special_mode)
            st.session_state.tc_messages.append({"role": "assistant", "content": answer})
        
        st.rerun()

def main():
    """
    Main function to run the Streamlit application and handle page navigation.
    """
    st.set_page_config(
        page_title="T&C Analyzer",
        page_icon="📜",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to:", ["Analyzer", "Instructions"])

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
