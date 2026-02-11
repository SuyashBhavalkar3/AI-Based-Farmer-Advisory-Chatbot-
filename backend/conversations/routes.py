"""Conversation routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database.base import get_db
from auth.dependencies import get_current_user_id
from conversations.service import ConversationService
from conversations.schemas import (
    ConversationCreate, ConversationOut, ConversationWithMessages, ConversationListResponse
)
from database.models import User
from exceptions.custom_exceptions import NotFoundError, to_http_exception
from logger.setup import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/conversations", tags=["Conversations"])

@router.post("/", response_model=ConversationOut)
def create_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_id)
):
    """Create new conversation."""
    try:
        convo = ConversationService.create_conversation(db, current_user, request.title, request.language or "en")
        return ConversationOut.from_orm(convo)
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create conversation")

@router.get("/", response_model=ConversationListResponse)
def list_conversations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """List user conversations."""
    try:
        conversations, total = ConversationService.list_conversations(db, user_id, limit, offset)
        return ConversationListResponse(
            conversations=[ConversationOut.from_orm(c) for c in conversations],
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list conversations")

@router.get("/{conversation_id}", response_model=ConversationWithMessages)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get conversation with messages."""
    try:
        convo = ConversationService.get_conversation(db, conversation_id, user_id)
        return ConversationWithMessages.from_orm(convo)
    except NotFoundError as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get conversation")

@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete conversation."""
    try:
        ConversationService.delete_conversation(db, conversation_id, user_id)
        return {"message": "Conversation deleted"}
    except NotFoundError as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete conversation")
