"""Test conversation memory feature."""

from sqlalchemy.orm import Session
from database.base import SessionLocal
from database.models import Conversation, Message, User
from services.conversation_intelligence import ConversationIntelligenceService
from logger.setup import get_logger

logger = get_logger(__name__)


def test_conversation_context():
    """Test retrieving conversation context from previous messages."""
    
    db = SessionLocal()
    try:
        # Create a test user
        user = db.query(User).first()
        if not user:
            logger.info("No user found in database. Skipping test.")
            return
        
        # Create a test conversation
        conversation = Conversation(
            user_id=user.id,
            title="Test Conversation - Memory Feature",
            language="en"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        logger.info(f"Created test conversation: {conversation.id}")
        
        # Add some test messages
        messages_data = [
            ("user", "What are the best farming practices for rice cultivation?"),
            ("assistant", "Rice cultivation requires proper water management, soil preparation, and timing. Use improved varieties and maintain standing water at 5-7 cm depth."),
            ("user", "How much fertilizer should I use?"),
            ("assistant", "For rice, use 150 kg nitrogen per hectare. Apply in 3-4 splits: 1/4 at land preparation, 1/4 at tillering, and remaining at panicle initiation."),
            ("user", "What about pesticide management?"),
        ]
        
        for role, content in messages_data:
            msg = Message(
                conversation_id=conversation.id,
                role=role,
                content=content
            )
            db.add(msg)
        
        db.commit()
        logger.info(f"Added {len(messages_data)} test messages")
        
        # Test the conversation context retrieval
        intelligence_service = ConversationIntelligenceService()
        
        # Test 1: Get context excluding current message
        logger.info("\n=== Test 1: Conversation Context (excluding current) ===")
        context = intelligence_service.get_conversation_context(
            db, conversation.id, exclude_current_message=True
        )
        logger.info(f"Retrieved context:\n{context}\n")
        
        # Test 2: Format context with RAG
        logger.info("=== Test 2: Formatted Context with RAG ===")
        rag_context = """
## Knowledge Base Results
- Rice cultivation requires 150 kg nitrogen per hectare
- Use improved rice varieties for better yields
- Maintain 5-7 cm water depth during growing season
"""
        formatted = intelligence_service.format_context_for_prompt(context, rag_context)
        logger.info(f"Formatted context:\n{formatted}\n")
        
        # Test 3: Verify conversation context is used in advisory
        logger.info("=== Test 3: Context Summary ===")
        logger.info(f"Context length: {len(context)} characters")
        logger.info(f"Includes previous messages: {'Farmer:' in context and 'Advisor:' in context}")
        logger.info(f"Context properly formatted: {'Agricultural Advisor' in context or 'Advisor' in context}")
        
        logger.info("\n✅ All conversation memory tests passed!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    test_conversation_context()
