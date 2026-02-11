import logging
from typing import Optional

logger = logging.getLogger(__name__)


def should_generate_title(conversation_title: Optional[str]) -> bool:
    """Check if title needs to be generated."""
    return not conversation_title or conversation_title == "New Conversation"


def extract_meaningful_words(text: str, max_words: int = 7) -> list:
    """Extract meaningful words from text, filtering out stopwords."""
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'am', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'what', 'which', 'who', 'when',
        'where', 'why', 'how', 'if', 'as', 'just', 'only', 'so', 'than', 'this'
    }
    
    words = text.lower().split()
    meaningful = [w.strip('.,!?;:') for w in words if w.strip('.,!?;:').lower() not in stopwords and len(w.strip('.,!?;:')) > 2]
    return meaningful[:max_words]


def fallback_title_generation(message: str, max_chars: int = 40) -> str:
    """Fallback title generation using keyword extraction."""
    try:
        logger.info(f"[TITLE] Using fallback keyword extraction for: {message[:50]}")
        meaningful_words = extract_meaningful_words(message, max_words=6)
        
        if not meaningful_words:
            logger.warning("[TITLE] No meaningful words found, using 'Conversation'")
            return "Conversation"
        
        title = ' '.join(meaningful_words).title()
        
        if len(title) > max_chars:
            title = title[:max_chars].rsplit(' ', 1)[0]
        
        logger.info(f"[TITLE] Generated fallback title: {title}")
        return title
    except Exception as e:
        logger.error(f"[TITLE] Fallback generation error: {str(e)}")
        return "Conversation"


def generate_conversation_title(message: str, use_llm: bool = True) -> str:
    """
    Generate conversation title from user message.
    
    Attempts LLM generation first (preferred), falls back to keyword extraction if LLM fails.
    
    Args:
        message: User's first message
        use_llm: Whether to try LLM generation first (default: True)
    
    Returns:
        Generated title (3-6 words, max 60 chars)
    """
    if not message or not message.strip():
        return "Conversation"
    
    if use_llm:
        try:
            logger.info(f"[TITLE] Attempting LLM title generation for: {message[:50]}")
            
            from services.farmer_advisory import FarmerAdvisoryService
            
            service = FarmerAdvisoryService()
            
            prompt = f"""Generate a short 3-6 word title summarizing this user query. 
Only return the title, nothing else. No quotes, no punctuation.

Query: {message}

Title:"""
            
            title_response = service.advisory(prompt, context_docs=[])
            
            if title_response and isinstance(title_response, str):
                title = title_response.strip().strip('"\'').split('\n')[0].strip()
                
                # Clean up title
                if len(title) > 60:
                    title = title[:60].rsplit(' ', 1)[0]
                
                if title and len(title.split()) <= 8:
                    logger.info(f"[TITLE] Generated LLM title: {title}")
                    return title
                else:
                    logger.warning(f"[TITLE] LLM title too long or invalid, falling back")
        except Exception as e:
            logger.warning(f"[TITLE] LLM generation failed: {str(e)}, using fallback")
    
    # Fallback to keyword extraction
    return fallback_title_generation(message)
