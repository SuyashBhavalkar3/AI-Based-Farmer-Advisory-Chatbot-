"""Result reranking for better relevance."""

from typing import List, Dict, Any
from logger.setup import get_logger

logger = get_logger(__name__)

class Reranker:
    """Rerank retrieval results for better relevance."""
    
    @staticmethod
    def rerank(results: List[Dict[str, Any]], query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank results based on relevance to query.
        Currently uses distance-based scoring, can be enhanced with cross-encoder.
        """
        try:
            if not results:
                return []
            
            # Sort by similarity score (already calculated in vectorstore)
            ranked = sorted(results, key=lambda x: x.get("similarity_score", 0), reverse=True)
            return ranked[:top_k]
        except Exception as e:
            logger.error(f"Reranking error: {str(e)}")
            return results
