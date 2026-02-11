"""Conversation service."""

from sqlalchemy.orm import Session
from conversations.repository import ConversationRepository, MessageRepository
from database.models import Conversation, Message
from exceptions.custom_exceptions import NotFoundError
from logger.setup import get_logger
from typing import List, Tuple

logger = get_logger(__name__)

class ConversationService:
    """Conversation business logic."""
    
    @staticmethod
    def create_conversation(db: Session, user_id: int, title: str = None, language: str = "en") -> Conversation:
        """Create new conversation."""
        title = title or f"Conversation {db.query(Conversation).filter(Conversation.user_id == user_id).count() + 1}"
        return ConversationRepository.create(db, user_id, title, language)
    
    @staticmethod
    def get_conversation(db: Session, conversation_id: int, user_id: int) -> Conversation:
        """Get conversation with authorization check."""
        convo = ConversationRepository.get_by_id(db, conversation_id, user_id)
        if not convo:
            raise NotFoundError("Conversation")
        return convo
    
    @staticmethod
    def list_conversations(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> Tuple[List[Conversation], int]:
        """List user conversations."""
        return ConversationRepository.list_by_user(db, user_id, limit, offset)
    
    @staticmethod
    def update_title(db: Session, conversation_id: int, user_id: int, title: str) -> Conversation:
        """Update conversation title."""
        convo = ConversationService.get_conversation(db, conversation_id, user_id)
        return ConversationRepository.update_title(db, conversation_id, title)
    
    @staticmethod
    def delete_conversation(db: Session, conversation_id: int, user_id: int):
        """Delete conversation."""
        ConversationRepository.delete(db, conversation_id, user_id)
    
    @staticmethod
    def add_message(db: Session, conversation_id: int, role: str, content: str) -> Message:
        """Add message to conversation."""
        return MessageRepository.create(db, conversation_id, role, content)
    
    @staticmethod
    def get_messages(db: Session, conversation_id: int, limit: int = 100) -> List[Message]:
        """Get conversation messages."""
        return MessageRepository.get_by_conversation(db, conversation_id, limit)
    
    @staticmethod
    def get_last_messages(db: Session, conversation_id: int, n: int = 10) -> List[Message]:
        """Get last N messages for context."""
        return MessageRepository.get_last_n(db, conversation_id, n)
