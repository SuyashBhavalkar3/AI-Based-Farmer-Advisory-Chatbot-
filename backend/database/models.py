"""Enhanced ORM models with proper indexing."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, server_default='true', index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), default="New Conversation")
    language = Column(String(5), default="en")  # Language of conversation
    is_deleted = Column(Boolean, default=False)  # Soft delete
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_conversation_user_created', 'user_id', 'created_at'),
        Index('idx_conversation_user_active', 'user_id', 'is_deleted'),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    message_metadata = Column(Text, nullable=True)  # JSON metadata (language, tokens, etc.)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    conversation = relationship("Conversation", back_populates="messages")
    
    __table_args__ = (
        Index('idx_message_conversation_created', 'conversation_id', 'created_at'),
    )


class Document(Base):
    """Track uploaded documents for RAG."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(10))  # pdf, docx, txt
    file_size = Column(Integer)  # in bytes
    num_chunks = Column(Integer, default=0)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_document_user_created', 'user_id', 'created_at'),
    )


class VectorMetadata(Base):
    """Track vector embeddings metadata."""
    __tablename__ = "vector_metadata"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    chunk_index = Column(Integer)  # Order of chunk in document
    text_preview = Column(String(255))  # First 255 chars of chunk
    embedding_model = Column(String(100))  # Model used for embedding
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_vector_document_chunk', 'document_id', 'chunk_index'),
    )

class Scheme(Base):
    """Government schemes and subsidies."""
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    eligibility = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    application_process = Column(Text, nullable=True)
    scheme_type = Column(String(100), default="subsidy")  # subsidy, insurance, credit, etc.
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = relationship("SchemeDocument", back_populates="scheme", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_scheme_name', 'name'),
        Index('idx_scheme_type', 'scheme_type'),
    )


class SchemeDocument(Base):
    """Documents required for government schemes."""
    __tablename__ = "scheme_documents"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False, index=True)
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=True)  # Local file path
    file_url = Column(String(512), nullable=True)  # External URL
    document_type = Column(String(50))  # pdf, docx, image, etc.
    file_size = Column(Integer)  # in bytes
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    scheme = relationship("Scheme", back_populates="documents")

    __table_args__ = (
        Index('idx_scheme_document_scheme', 'scheme_id', 'document_name'),
    )


class FarmerProfile(Base):
    """Farmer profile for personalized recommendations."""
    __tablename__ = "farmer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    land_size_hectares = Column(Integer, nullable=True)  # In hectares
    primary_crop = Column(String(100), nullable=True)
    secondary_crops = Column(String(500), nullable=True)  # Comma-separated
    farming_type = Column(String(50), nullable=True)  # organic, conventional, mixed
    annual_income = Column(Integer, nullable=True)
    dbt_eligible = Column(Boolean, default=False)
    bank_account_linked = Column(Boolean, default=False)
    aadhar_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_farmer_profile_state_district', 'state', 'district'),
    )


class ConversationSummary(Base):
    """AI-generated summaries of conversations for memory and insights."""
    __tablename__ = "conversation_summaries"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), unique=True, nullable=False, index=True)
    summary = Column(Text, nullable=False)
    key_topics = Column(String(1000), nullable=True)  # JSON list of topics
    schemes_discussed = Column(String(1000), nullable=True)  # JSON list of scheme IDs
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_summary_conversation', 'conversation_id'),
    )


class SourceCitation(Base):
    """Track sources/documents cited in responses for transparency."""
    __tablename__ = "source_citations"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, index=True)
    source_text = Column(Text, nullable=False)
    document_name = Column(String(255), nullable=True)
    confidence_score = Column(Integer, nullable=True)  # 0-100
    vector_similarity = Column(Integer, nullable=True)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_citation_message', 'message_id'),
    )


class UserInsight(Base):
    """Analytics and insights about user interactions."""
    __tablename__ = "user_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    total_conversations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    most_asked_scheme = Column(String(255), nullable=True)
    primary_interest = Column(String(100), nullable=True)  # crop_advisory, schemes, legal, etc.
    preferred_language = Column(String(5), nullable=True)
    last_active = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_insight_user', 'user_id'),
    )