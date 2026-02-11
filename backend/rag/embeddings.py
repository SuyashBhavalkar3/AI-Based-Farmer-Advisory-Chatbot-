"""Enhanced embedding service."""

from sentence_transformers import SentenceTransformer
from typing import List, Union
from config.settings import settings
from logger.setup import get_logger

logger = get_logger(__name__)

class EmbeddingService:
    """Generate embeddings for text."""
    
    _model = None
    
    @classmethod
    def _get_model(cls):
        """Get or load embedding model (lazy loading)."""
        if cls._model is None:
            try:
                cls._model = SentenceTransformer(settings.EMBEDDING_MODEL)
                logger.info(f"Embedding model loaded: {settings.EMBEDDING_MODEL}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {str(e)}")
                raise
        return cls._model
    
    @staticmethod
    def embed_text(text: str) -> List[float]:
        """Embed a single text string."""
        try:
            if not text or not text.strip():
                raise ValueError("Cannot embed empty text")
            
            model = EmbeddingService._get_model()
            embedding = model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error embedding text: {str(e)}")
            raise
    
    @staticmethod
    def embed_texts(texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings."""
        try:
            if not texts:
                raise ValueError("Cannot embed empty list")
            
            # Filter empty texts
            texts = [t for t in texts if t and t.strip()]
            
            if not texts:
                raise ValueError("No valid texts to embed")
            
            model = EmbeddingService._get_model()
            embeddings = model.encode(texts, convert_to_tensor=False)
            return [e.tolist() for e in embeddings]
        except Exception as e:
            logger.error(f"Error embedding texts: {str(e)}")
            raise
    
    @staticmethod
    def get_embedding_dimension() -> int:
        """Get embedding dimension size."""
        return settings.EMBEDDING_DIMENSION
