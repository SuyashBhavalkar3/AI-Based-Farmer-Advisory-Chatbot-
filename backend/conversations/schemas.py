"""Conversation schemas."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class MessageCreate(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=10000)

class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    language: Optional[str] = Field("en", pattern="^(en|hi|mr)$")

class ConversationOut(BaseModel):
    id: int
    title: str
    language: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConversationWithMessages(ConversationOut):
    messages: List[MessageOut] = []

class ConversationListResponse(BaseModel):
    conversations: List[ConversationOut]
    total: int
    limit: int
    offset: int
