"""RAG (Retrieval Augmented Generation) service."""

from typing import List, Dict, Any, Optional
from rag.embeddings import EmbeddingService
from rag.vectorstore import VectorStore
from rag.document_processor import DocumentProcessor
from config.settings import settings
from logger.setup import get_logger

logger = get_logger(__name__)

class RAGService:
    """Orchestrate RAG pipeline."""
    
    def __init__(self):
        """Initialize RAG service."""
        self.vectorstore = VectorStore(
            str(settings.VECTORSTORE_PATH),
            embedding_dim=settings.EMBEDDING_DIMENSION
        )
    
    def process_and_store_document(self, text: str, language: str = "en", document_metadata: Dict[str, Any] = None) -> int:
        """
        Process document, create chunks, embed, and store vectors.
        Returns number of chunks created.
        """
        try:
            # Clean text
            text = DocumentProcessor.clean_text(text)
            
            # Chunk text
            chunks = DocumentProcessor.chunk_text(text, language)
            
            if not chunks:
                logger.warning("No chunks generated from document")
                return 0
            
            # Embed chunks
            embeddings = EmbeddingService.embed_texts(chunks)
            
            # Store vectors with metadata
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                metadata = {
                    "text": chunk,
                    "language": language,
                    "chunk_index": idx,
                    "document_metadata": document_metadata or {}
                }
                self.vectorstore.add_vector(embedding, metadata)
            
            # Save updated vectorstore
            self.vectorstore.save()
            
            logger.info(f"Document processed: {len(chunks)} chunks stored")
            return len(chunks)
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    def retrieve_context(self, query: str, language: str = "en", top_k: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for query.
        """
        try:
            if top_k is None:
                top_k = settings.TOP_K_RESULTS
            
            # Embed query
            query_embedding = EmbeddingService.embed_text(query)
            
            # Search vectorstore
            results = self.vectorstore.search(query_embedding, top_k=top_k)
            
            logger.debug(f"Retrieved {len(results)} results for query")
            return results
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []
    
    def get_context_string(self, query: str, language: str = "en", top_k: int = None, separator: str = "\n\n") -> str:
        """
        Retrieve and format context as string for LLM prompt.
        """
        try:
            results = self.retrieve_context(query, language, top_k)
            context_pieces = [result.get("text", "") for result in results if result.get("text")]
            return separator.join(context_pieces)
        except Exception as e:
            logger.error(f"Error getting context string: {str(e)}")
            return ""
    
    def get_vectorstore_stats(self) -> Dict[str, Any]:
        """Get vectorstore statistics."""
        return self.vectorstore.get_stats()

# Global RAG service instance
_rag_service = None

def get_rag_service() -> RAGService:
    """Get or create RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
