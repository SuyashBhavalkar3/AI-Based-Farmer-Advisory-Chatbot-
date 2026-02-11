"""Retrieval logic for RAG."""

from typing import List, Dict, Any
from rag.rag_service import get_rag_service
from logger.setup import get_logger

logger = get_logger(__name__)

class Retriever:
    """RAG retriever for fetching relevant documents."""
    
    @staticmethod
    def retrieve(query: str, top_k: int = 5, language: str = "en") -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for query.
        """
        try:
            rag_service = get_rag_service()
            return rag_service.retrieve_context(query, language, top_k)
        except Exception as e:
            logger.error(f"Retrieval error: {str(e)}")
            return []
    
    @staticmethod
    def retrieve_formatted(query: str, top_k: int = 5, language: str = "en") -> str:
        """Retrieve and format context for LLM."""
        try:
            rag_service = get_rag_service()
            return rag_service.get_context_string(query, language, top_k)
        except Exception as e:
            logger.error(f"Formatted retrieval error: {str(e)}")
            return ""
