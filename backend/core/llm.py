import logging
from typing import Optional
from core.config import settings

logger = logging.getLogger(__name__)

def get_gemini_llm(temperature: float = 0.2):
    """Factory to initialize ChatGoogleGenerativeAI or provide informative mock if key missing."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set. Agents will use analytical rule-based synthesis.")
        return None
        
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=api_key,
            temperature=temperature
        )
        return llm
    except Exception as e:
        logger.error(f"Error initializing ChatGoogleGenerativeAI: {e}")
        return None
