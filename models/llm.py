import google.generativeai as genai
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from config.config import GEMINI_API_KEY, GROQ_API_KEY, DEFAULT_GEMINI_MODEL, DEFAULT_GROQ_MODEL

# Configure Gemini once using API key
genai.configure(api_key=GEMINI_API_KEY)

def gemini_generate(prompt, model=DEFAULT_GEMINI_MODEL, temperature=0.2):
    model_instance = genai.GenerativeModel(model)
    response = model_instance.generate_content(
        prompt,
        generation_config={"temperature": temperature}
    )
    return response.text


def groq_generate(prompt, model=DEFAULT_GROQ_MODEL, temperature=0.2):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found in .env file")

    model_instance = ChatGroq(
        api_key=GROQ_API_KEY,
        model=model,
        temperature=temperature
    )

    response = model_instance.invoke([HumanMessage(content=prompt)])
    return response.content
