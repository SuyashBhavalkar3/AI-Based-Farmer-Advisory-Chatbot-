"""Repository pattern for database operations."""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models import User, Conversation, Message, Document
from exceptions.custom_exceptions import NotFoundError, DatabaseError
from logger.setup import get_logger
from typing import List, Optional

logger = get_logger(__name__)

class UserRepository:
    """User data access layer."""
    
    @staticmethod
    def create(db: Session, full_name: str, email: str, password_hash: str) -> User:
        try:
            user = User(full_name=full_name, email=email, password_hash=password_hash)
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"User created: {email}")
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise DatabaseError("Failed to create user")
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email, User.is_active == True).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()

class ConversationRepository:
    """Conversation data access layer."""
    
    @staticmethod
    def create(db: Session, user_id: int, title: str, language: str = "en") -> Conversation:
        try:
            convo = Conversation(user_id=user_id, title=title, language=language)
            db.add(convo)
            db.commit()
            db.refresh(convo)
            logger.info(f"Conversation created for user {user_id}: {convo.id}")
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
    def list_by_user(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> List[Conversation]:
        return db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.is_deleted == False
        ).order_by(desc(Conversation.created_at)).limit(limit).offset(offset).all()
    
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
            logger.error(f"Error updating conversation title: {str(e)}")
            raise DatabaseError("Failed to update conversation")
    
    @staticmethod
    def soft_delete(db: Session, conversation_id: int):
        try:
            convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
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
    """Message data access layer."""
    
    @staticmethod
    def create(db: Session, conversation_id: int, role: str, content: str, metadata: str = None) -> Message:
        try:
            message = Message(conversation_id=conversation_id, role=role, content=content, message_metadata=metadata)
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
    def get_last_n_messages(db: Session, conversation_id: int, n: int = 10) -> List[Message]:
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.created_at)).limit(n).all()
        return list(reversed(messages))  # Return in chronological order

class DocumentRepository:
    """Document management."""
    
    @staticmethod
    def create(db: Session, user_id: int, filename: str, file_path: str, 
               file_type: str, file_size: int) -> Document:
        try:
            doc = Document(user_id=user_id, filename=filename, file_path=file_path,
                          file_type=file_type, file_size=file_size)
            db.add(doc)
            db.commit()
            db.refresh(doc)
            return doc
        except Exception as e:
            db.rollback()
            raise DatabaseError("Failed to create document record")
    
    @staticmethod
    def mark_processed(db: Session, document_id: int, num_chunks: int):
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if doc:
                doc.is_processed = True
                doc.num_chunks = num_chunks
                db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error marking document as processed: {str(e)}")
