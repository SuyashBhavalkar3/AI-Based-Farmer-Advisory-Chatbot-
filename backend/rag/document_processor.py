"""Document processing for RAG."""

import re
from pathlib import Path
from typing import List, Tuple
from config.constants import LANGUAGE_CHUNK_CONFIG
from logger.setup import get_logger

logger = get_logger(__name__)

class DocumentProcessor:
    """Process documents for RAG."""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            from PyPDF2 import PdfReader
            import io
            
            pdf_reader = PdfReader(io.BytesIO(file_content))
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text += page.extract_text() + "\n"
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {str(e)}")
            
            if not text.strip():
                logger.warning("No text extracted from PDF")
            return text
        except Exception as e:
            logger.error(f"Error reading PDF: {str(e)}")
            raise
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file."""
        try:
            from docx import Document
            import io
            
            doc = Document(io.BytesIO(file_content))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error reading DOCX: {str(e)}")
            raise
    
    @staticmethod
    def extract_text(file_content: bytes, file_type: str) -> str:
        """Extract text from file based on type."""
        if file_type.lower() == "pdf":
            return DocumentProcessor.extract_text_from_pdf(file_content)
        elif file_type.lower() == "docx":
            return DocumentProcessor.extract_text_from_docx(file_content)
        elif file_type.lower() == "txt":
            return file_content.decode("utf-8")
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    @staticmethod
    def chunk_text(text: str, language: str = "en") -> List[str]:
        """
        Chunk text into overlapping chunks.
        Language-specific chunk sizes for better context.
        """
        try:
            if not text or not text.strip():
                logger.warning("Cannot chunk empty text")
                return []
            
            # Get language-specific config
            config = LANGUAGE_CHUNK_CONFIG.get(language, LANGUAGE_CHUNK_CONFIG["en"])
            chunk_size = config["chunk_size"]
            overlap = config["overlap"]
            
            # Split into sentences first for better coherence
            sentences = DocumentProcessor._split_sentences(text)
            
            chunks = []
            current_chunk = []
            current_length = 0
            
            for sentence in sentences:
                words = sentence.split()
                if current_length + len(words) <= chunk_size:
                    current_chunk.extend(words)
                    current_length += len(words)
                else:
                    # Save current chunk
                    if current_chunk:
                        chunk_text = " ".join(current_chunk)
                        chunks.append(chunk_text)
                    
                    # Start new chunk with overlap
                    overlap_words = min(overlap, current_length)
                    current_chunk = current_chunk[-overlap_words:] if overlap_words > 0 else []
                    current_chunk.extend(words)
                    current_length = len(current_chunk)
            
            # Add last chunk
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            
            logger.info(f"Text chunked into {len(chunks)} pieces for language: {language}")
            return [c.strip() for c in chunks if c.strip()]
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            raise
    
    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = " ".join(text.split())
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s\n।.!?,-]', '', text)
        return text
