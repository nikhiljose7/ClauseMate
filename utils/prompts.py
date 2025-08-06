from langchain.prompts import PromptTemplate

RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question", "detail_level"],
    template=(
        "You are a legal assistant analyzing Terms & Conditions.\n"
        "Context:\n{context}\n\n"
        "User Question: {question}\n"
        "Respond in a {detail_level} manner. If unsure, say so."
    )
)

REWRITE_PROMPT = PromptTemplate(
    input_variables=["clause"],
    template="Rewrite the following clause in formal, professional legal language:\n{clause}"
)
