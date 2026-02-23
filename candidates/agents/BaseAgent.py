import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


class BaseAgent:
    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "openai")

        if provider == "openai":
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        elif provider == "google":
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                temperature=0,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")