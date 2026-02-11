"""Translation service for multilingual support."""

from typing import Optional
from config.constants import Language
from logger.setup import get_logger

logger = get_logger(__name__)

class TranslationService:
    """Handle language translation."""
    
    def __init__(self, service_type: str = "google"):
        """Initialize translation service."""
        self.service_type = service_type
        self._init_service()
    
    def _init_service(self):
        """Initialize the translation backend."""
        if self.service_type == "google":
            try:
                from google.cloud import translate_v2
                self.translator = translate_v2.Client()
                logger.info("Google Translate initialized")
            except ImportError:
                logger.warning("google-cloud-translate not installed, using mock translator")
                self.translator = None
        elif self.service_type == "local":
            try:
                from transformers import MarianMTModel, MarianTokenizer
                # This is a simplified example
                self.translator = None
                logger.info("Local translation service initialized")
            except ImportError:
                logger.warning("transformers not installed, using mock translator")
                self.translator = None
    
    def translate(self, text: str, source_language: str, target_language: str) -> str:
        """
        Translate text from source to target language.
        
        Args:
            text: Text to translate
            source_language: Source language code ('en', 'hi', 'mr')
            target_language: Target language code ('en', 'hi', 'mr')
        
        Returns:
            Translated text
        """
        # If source and target are the same, return as-is
        if source_language == target_language:
            return text
        
        try:
            if self.service_type == "google" and self.translator:
                return self._translate_google(text, source_language, target_language)
            else:
                # Mock translation for demo
                logger.debug(f"Mock translation: {source_language} -> {target_language}")
                return text
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            # Return original text on error
            return text
    
    def _translate_google(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate using Google Translate API."""
        try:
            # Map our language codes to Google's
            lang_map = {
                'en': 'en',
                'hi': 'hi',
                'mr': 'mr',
            }
            
            source = lang_map.get(source_lang, 'en')
            target = lang_map.get(target_lang, 'en')
            
            result = self.translator.translate_text(
                text,
                source_language=source,
                target_language=target
            )
            return result['translatedText']
        except Exception as e:
            logger.error(f"Google Translate error: {str(e)}")
            return text
    
    def translate_to_english(self, text: str, source_language: str) -> str:
        """Translate text to English."""
        return self.translate(text, source_language, Language.ENGLISH.value)
    
    def translate_from_english(self, text: str, target_language: str) -> str:
        """Translate text from English to target language."""
        return self.translate(text, Language.ENGLISH.value, target_language)

# Global translator instance
_translator = None

def get_translator() -> TranslationService:
    """Get or create translator instance."""
    global _translator
    if _translator is None:
        from config.settings import settings
        _translator = TranslationService(service_type=settings.TRANSLATION_SERVICE)
    return _translator
