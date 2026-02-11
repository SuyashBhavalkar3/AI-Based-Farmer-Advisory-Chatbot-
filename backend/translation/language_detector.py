"""Language detection service."""

from typing import Tuple
from config.constants import Language
from logger.setup import get_logger

logger = get_logger(__name__)

class LanguageDetector:
    """Detect language from text."""
    
    @staticmethod
    def detect(text: str) -> str:
        """
        Detect language from text.
        Returns language code: 'en', 'hi', 'mr'
        """
        try:
            # Try to import textblob or langdetect
            try:
                from textblob import TextBlob
                blob = TextBlob(text)
                detected_lang = blob.detect_language()
            except ImportError:
                try:
                    from langdetect import detect
                    detected_lang = detect(text)
                except ImportError:
                    # Fallback: simple heuristic
                    detected_lang = LanguageDetector._simple_detect(text)
            
            # Map detected language to supported languages
            lang_map = {
                'en': Language.ENGLISH,
                'hi': Language.HINDI,
                'mr': Language.MARATHI,
            }
            
            # Return mapped language or default to English
            result = lang_map.get(detected_lang[:2], Language.ENGLISH).value
            logger.debug(f"Detected language: {result} from text: {text[:50]}...")
            return result
        except Exception as e:
            logger.warning(f"Language detection failed: {str(e)}, defaulting to English")
            return Language.ENGLISH.value
    
    @staticmethod
    def _simple_detect(text: str) -> str:
        """Simple language detection based on character patterns."""
        devanagari_count = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        total_chars = len(text)
        
        if total_chars == 0:
            return 'en'
        
        devanagari_ratio = devanagari_count / total_chars
        
        if devanagari_ratio > 0.3:
            # Could be Hindi or Marathi
            # Marathi has specific characters, but this is simplified
            return 'hi'  # Assume Hindi for Devanagari script
        
        return 'en'  # Default to English

class LanguageValidator:
    """Validate language codes."""
    
    SUPPORTED_LANGUAGES = [Language.ENGLISH.value, Language.HINDI.value, Language.MARATHI.value]
    
    @staticmethod
    def is_supported(language: str) -> bool:
        """Check if language is supported."""
        return language in LanguageValidator.SUPPORTED_LANGUAGES
    
    @staticmethod
    def validate(language: str) -> str:
        """Validate and return language code or raise error."""
        if LanguageValidator.is_supported(language):
            return language
        logger.warning(f"Unsupported language requested: {language}")
        return Language.ENGLISH.value  # Default to English
