import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """Returns an instance of Gemini Pro."""
    api_key = os.getenv("GOOGLE_API_KEY", "dummy-key")
    return ChatGoogleGenerativeAI(model="gemini-3.1-pro", google_api_key=api_key)
