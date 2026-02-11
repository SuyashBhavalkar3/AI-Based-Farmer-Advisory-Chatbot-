"""Conversation repository."""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models import Conversation, Message
from exceptions.custom_exceptions import NotFoundError, DatabaseError
from logger.setup import get_logger
from typing import List, Optional

logger = get_logger(__name__)

class ConversationRepository:
    """Conversation data access."""
    
    @staticmethod
    def create(db: Session, user_id: int, title: str, language: str = "en") -> Conversation:
        try:
            convo = Conversation(user_id=user_id, title=title, language=language)
            db.add(convo)
            db.commit()
            db.refresh(convo)
            logger.info(f"Conversation created: {convo.id} for user {user_id}")
            return convo
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating conversation: {str(e)}")
            raise DatabaseError("Failed to create conversation")
    
    @staticmethod
    def get_by_id(db: Session, conversation_id: int, user_id: int) -> Optional[Conversation]:
        return db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
            Conversation.is_deleted == False
        ).first()
    
    @staticmethod
    def list_by_user(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> tuple[List[Conversation], int]:
        query = db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.is_deleted == False
        )
        total = query.count()
        conversations = query.order_by(desc(Conversation.created_at)).limit(limit).offset(offset).all()
        return conversations, total
    
    @staticmethod
    def update_title(db: Session, conversation_id: int, title: str) -> Conversation:
        try:
            convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not convo:
                raise NotFoundError("Conversation")
            convo.title = title
            db.commit()
            db.refresh(convo)
            return convo
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating conversation: {str(e)}")
            raise DatabaseError("Failed to update conversation")
    
    @staticmethod
    def delete(db: Session, conversation_id: int, user_id: int):
        try:
            convo = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
            if not convo:
                raise NotFoundError("Conversation")
            convo.is_deleted = True
            db.commit()
            logger.info(f"Conversation deleted: {conversation_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting conversation: {str(e)}")
            raise DatabaseError("Failed to delete conversation")

class MessageRepository:
    """Message data access."""
    
    @staticmethod
    def create(db: Session, conversation_id: int, role: str, content: str, metadata: str = None) -> Message:
        try:
            message = Message(conversation_id=conversation_id, role=role, content=content, metadata=metadata)
            db.add(message)
            db.commit()
            db.refresh(message)
            return message
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating message: {str(e)}")
            raise DatabaseError("Failed to create message")
    
    @staticmethod
    def get_by_conversation(db: Session, conversation_id: int, limit: int = 100) -> List[Message]:
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).limit(limit).all()
    
    @staticmethod
    def get_last_n(db: Session, conversation_id: int, n: int = 10) -> List[Message]:
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.created_at)).limit(n).all()
        return list(reversed(messages))
