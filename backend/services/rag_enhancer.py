"""RAG enhancement service for source citations and confidence scoring."""

from typing import List, Dict, Any, Tuple
from rag.rag_service import get_rag_service
from logger.setup import get_logger
import json

logger = get_logger(__name__)


class EnhancedRAGService:
    """Enhanced RAG with source tracking and confidence scoring."""

    def __init__(self):
        """Initialize enhanced RAG service."""
        self.rag_service = get_rag_service()

    def retrieve_with_citations(
        self, query: str, language: str = "en", top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve context with source citations and confidence scores.

        Returns:
            {
                "context": formatted context string,
                "sources": [
                    {
                        "text": source text,
                        "confidence": 0-100,
                        "similarity": 0-100,
                        "rank": 1-5,
                        "document": document name if available
                    }
                ],
                "average_confidence": 0-100
            }
        """
        try:
            results = self.rag_service.retrieve_context(
                query, language=language, top_k=top_k
            )

            if not results:
                return {
                    "context": "",
                    "sources": [],
                    "average_confidence": 0,
                }

            # Process results and add confidence scoring
            sources = []
            total_confidence = 0

            for rank, result in enumerate(results, 1):
                # Calculate confidence based on various factors
                confidence = self._calculate_confidence(result, rank, len(results))

                source = {
                    "text": result.get("text", ""),
                    "confidence": confidence,
                    "similarity": result.get("similarity", 0),
                    "rank": rank,
                    "document": result.get(
                        "document_name",
                        f"Document {result.get('chunk_index', 1)}",
                    ),
                }
                sources.append(source)
                total_confidence += confidence

            average_confidence = int(total_confidence / len(sources))

            return {
                "context": self._format_context_with_citations(sources),
                "sources": sources,
                "average_confidence": average_confidence,
            }

        except Exception as e:
            logger.error(f"Error in enhanced retrieval: {str(e)}")
            return {
                "context": "",
                "sources": [],
                "average_confidence": 0,
                "error": str(e),
            }

    def _calculate_confidence(self, result: Dict[str, Any], rank: int, total: int) -> int:
        """Calculate confidence score (0-100) for a result."""
        try:
            # Similarity-based confidence (60% weight)
            similarity = min(100, result.get("similarity", 0) * 100)
            similarity_score = similarity * 0.6

            # Rank-based confidence (30% weight) - earlier ranks get higher scores
            rank_score = ((total - rank) / total) * 100 * 0.3

            # Metadata quality (10% weight) - if has proper metadata
            metadata_score = 10 if result.get("document_name") else 5

            confidence = int(similarity_score + rank_score + metadata_score)
            return min(100, max(0, confidence))

        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 50

    def _format_context_with_citations(self, sources: List[Dict[str, Any]]) -> str:
        """Format context string with source references."""
        parts = []

        for source in sources:
            citation_marker = f"[Source {source['rank']}: {source['document']} (Confidence: {source['confidence']}%)]"
            parts.append(f"{source['text']}\n{citation_marker}")

        return "\n\n".join(parts)

    def get_top_documents_preview(
        self, query: str, language: str = "en", top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Get preview of top relevant documents."""
        try:
            results = self.rag_service.retrieve_context(
                query, language=language, top_k=top_k
            )

            previews = []
            for idx, result in enumerate(results):
                preview = {
                    "rank": idx + 1,
                    "document": result.get("document_name", "Unknown"),
                    "preview": result.get("text", "")[:200] + "...",
                    "full_text": result.get("text", ""),
                    "similarity_score": min(100, int(result.get("similarity", 0) * 100)),
                }
                previews.append(preview)

            return previews

        except Exception as e:
            logger.error(f"Error getting document previews: {str(e)}")
            return []

    def generate_confidence_badge(self, score: int) -> str:
        """Generate human-readable confidence badge."""
        if score >= 90:
            return "🟢 High Confidence"
        elif score >= 70:
            return "🟡 Medium Confidence"
        elif score >= 50:
            return "🟠 Moderate Confidence"
        else:
            return "🔴 Low Confidence"

    def should_generate_answer(self, confidence: int, threshold: int = 50) -> Tuple[bool, str]:
        """Determine if RAG confidence is sufficient to generate answer."""
        if confidence >= threshold:
            return True, "Sufficient confidence in available knowledge"
        else:
            return (
                False,
                f"Confidence ({confidence}%) below threshold ({threshold}%). May provide inaccurate information.",
            )
