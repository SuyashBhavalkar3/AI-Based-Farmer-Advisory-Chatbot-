"""Enhanced FAISS vector store."""

import faiss
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from logger.setup import get_logger

logger = get_logger(__name__)

class VectorStore:
    """FAISS-based vector store for embeddings."""
    
    def __init__(self, store_path: str, embedding_dim: int = 384):
        """Initialize vector store."""
        self.store_path = Path(store_path)
        self.embedding_dim = embedding_dim
        self.metadata: List[Dict[str, Any]] = []
        
        self.index_path = self.store_path / "index.faiss"
        self.meta_path = self.store_path / "metadata.pkl"
        
        # Create FAISS index
        self.index = faiss.IndexFlatL2(embedding_dim)
        
        # Load if exists
        if self.index_path.exists() and self.meta_path.exists():
            self.load()
            logger.info(f"FAISS index loaded from {store_path} ({self.index.ntotal} vectors)")
        else:
            logger.info(f"New FAISS index created at {store_path}")
    
    def add_vector(self, vector: List[float], metadata: Dict[str, Any]):
        """Add single vector with metadata."""
        try:
            if not vector or len(vector) != self.embedding_dim:
                raise ValueError(f"Vector dimension mismatch: expected {self.embedding_dim}, got {len(vector)}")
            
            vector_array = np.array([vector], dtype='float32')
            self.index.add(vector_array)
            self.metadata.append(metadata)
            logger.debug(f"Vector added to store. Total: {self.index.ntotal}")
        except Exception as e:
            logger.error(f"Error adding vector: {str(e)}")
            raise
    
    def add_vectors(self, vectors: List[List[float]], metadatas: List[Dict[str, Any]]):
        """Add multiple vectors with metadata."""
        try:
            if len(vectors) != len(metadatas):
                raise ValueError("Mismatch between vectors and metadatas count")
            
            for vector, metadata in zip(vectors, metadatas):
                self.add_vector(vector, metadata)
            
            logger.debug(f"Batch added. Total vectors: {self.index.ntotal}")
        except Exception as e:
            logger.error(f"Error adding vectors batch: {str(e)}")
            raise
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        try:
            if self.index.ntotal == 0:
                logger.warning("Search on empty index")
                return []
            
            if len(query_vector) != self.embedding_dim:
                raise ValueError(f"Query vector dimension mismatch")
            
            query = np.array([query_vector], dtype='float32')
            distances, indices = self.index.search(query, min(top_k, self.index.ntotal))
            
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx >= 0:  # Valid index
                    result = self.metadata[idx].copy()
                    result['distance'] = float(distance)
                    result['similarity_score'] = 1 / (1 + float(distance))  # Convert distance to similarity
                    results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            return []
    
    def save(self):
        """Save index and metadata to disk."""
        try:
            self.store_path.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(self.index_path))
            with open(self.meta_path, "wb") as f:
                pickle.dump(self.metadata, f)
            logger.info(f"Vector store saved to {self.store_path}")
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            raise
    
    def load(self):
        """Load index and metadata from disk."""
        try:
            self.index = faiss.read_index(str(self.index_path))
            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)
            logger.info(f"Vector store loaded from {self.store_path}")
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        return {
            "total_vectors": self.index.ntotal,
            "embedding_dimension": self.embedding_dim,
            "store_path": str(self.store_path)
        }
