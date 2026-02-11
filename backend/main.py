"""Main FastAPI application - Production Ready Farmer Advisory Chatbot."""

import os
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

# Import configurations
from config.settings import settings
from logger.setup import app_logger, get_logger
from database.base import init_db, get_db
from database.models import User
from auth.dependencies import get_current_user
from middleware import LoggingMiddleware, ErrorHandlingMiddleware, RateLimitMiddleware

# Import routers
from auth.routes import router as auth_router
from conversations.routes import router as conversations_router

# Import services
from rag.rag_service import get_rag_service
from translation.language_detector import LanguageDetector
from translation.translator import get_translator
from services.farmer_advisory import FarmerAdvisoryService, SchemeAdvisoryService
from exceptions.custom_exceptions import InvalidInputError, NotFoundError, FileUploadError, to_http_exception
from utils.validators import Validator
from utils.formatters import format_success_response

logger = get_logger(__name__)

# Lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting Farmer Advisory Chatbot API")
    try:
        init_db()
        rag_service = get_rag_service()
        logger.info(f"RAG Service ready: {rag_service.get_vectorstore_stats()}")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise
    
    yield
    
    logger.info("Shutting down Farmer Advisory Chatbot API")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Based Farmer Advisory Chatbot with multilingual support",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(RateLimitMiddleware, requests=settings.RATE_LIMIT_REQUESTS, period=settings.RATE_LIMIT_PERIOD_SECONDS)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(conversations_router)

# Request schemas
class AdvisoryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    conversation_id: int
    language: str = Field("en", pattern="^(en|hi|mr)$")
    include_schemes: bool = False

# Endpoints
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": f"{settings.APP_NAME} is running!",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.post("/api/v1/advisory/ask")
def ask_advisory(
    request: AdvisoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ask for farmer advisory with RAG context."""
    try:
        # DEBUG: Log incoming request
        logger.info(f"[ADVISORY] Incoming request from user {current_user.email}")
        logger.info(f"[ADVISORY] Question: {request.question}")
        logger.info(f"[ADVISORY] Conversation ID: {request.conversation_id}")
        logger.info(f"[ADVISORY] Language: {request.language}")
        
        # Import Message model
        from database.models import Message
        
        # Step 1: Save user message to database
        logger.info(f"[ADVISORY] Saving user message to database...")
        user_message = Message(
            conversation_id=request.conversation_id,
            role="user",
            content=request.question
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        logger.info(f"[ADVISORY] User message saved with ID {user_message.id}")
        
        # Step 1.5: Generate conversation title if needed
        logger.info(f"[ADVISORY] Checking if title generation needed...")
        from database.models import Conversation
        from utils.title_generator import should_generate_title, generate_conversation_title
        
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id
        ).first()
        
        if conversation and should_generate_title(conversation.title):
            try:
                logger.info(f"[ADVISORY] Generating title for conversation {request.conversation_id}...")
                new_title = generate_conversation_title(request.question)
                conversation.title = new_title
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
                logger.info(f"[ADVISORY] Conversation title updated to: {new_title}")
            except Exception as e:
                logger.warning(f"[ADVISORY] Title generation failed: {str(e)}, continuing without title")
        else:
            logger.info(f"[ADVISORY] Skipping title generation (title already set or conversation not found)")
        
        # Detect language if not specified
        if not request.language:
            request.language = LanguageDetector.detect(request.question)
            logger.info(f"[ADVISORY] Detected language: {request.language}")
        
        # Translate to English if needed
        logger.info(f"[ADVISORY] Translating to English...")
        translator = get_translator()
        question_en = translator.translate_to_english(request.question, request.language)
        logger.info(f"[ADVISORY] Translated question: {question_en}")
        
        # Get RAG context
        logger.info(f"[ADVISORY] Fetching RAG context...")
        rag_service = get_rag_service()
        context = rag_service.get_context_string(question_en, language=request.language)
        logger.info(f"[ADVISORY] RAG context length: {len(context) if context else 0}")
        
        # Get advisory
        logger.info(f"[ADVISORY] Calling FarmerAdvisoryService...")
        advisory_service = FarmerAdvisoryService()
        response = advisory_service.get_advisory(question_en, language=request.language, context=context)
        logger.info(f"[ADVISORY] Got response from service")
        
        # Translate response back to user's language
        logger.info(f"[ADVISORY] Translating response back to {request.language}...")
        response_user_lang = translator.translate_from_english(response, request.language)
        logger.info(f"[ADVISORY] Response translated")
        
        # Step 2: Save assistant message to database
        logger.info(f"[ADVISORY] Saving assistant message to database...")
        assistant_message = Message(
            conversation_id=request.conversation_id,
            role="assistant",
            content=response_user_lang
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        logger.info(f"[ADVISORY] Assistant message saved with ID {assistant_message.id}")
        
        # Step 3: Return response
        logger.info(f"[ADVISORY] Returning response...")
        return format_success_response({
            "response": response_user_lang,
            "original_language": request.language,
            "context_used": bool(context),
            "schemes": advisory_service.find_relevant_schemes(request.question) if request.include_schemes else None
        }, {"language": request.language})
    except (InvalidInputError, NotFoundError) as e:
        logger.error(f"[ADVISORY] Known error: {str(e)}")
        db.rollback()
        raise to_http_exception(e)
    except Exception as e:
        logger.error(f"[ADVISORY] Unexpected error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get advisory: {str(e)}")

@app.post("/api/v1/advisory/ask-with-document")
async def ask_with_document(
    conversation_id: int = Form(...),
    question: str = Form(...),
    language: str = Form("en"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Ask advisory with uploaded document context."""
    try:
        # Validate inputs
        Validator.validate_string(question, min_length=1, max_length=1000, field_name="Question")
        
        # Validate file
        Validator.validate_file_size(len(file.file.read()), settings.MAX_UPLOAD_SIZE_MB)
        file.file.seek(0)  # Reset file pointer
        
        file_type = Validator.validate_file_type(file.filename, settings.ALLOWED_FILE_TYPES)
        
        # Process document
        from rag.document_processor import DocumentProcessor
        file_content = await file.read()
        document_text = DocumentProcessor.extract_text(file_content, file_type)
        
        # Store in RAG
        rag_service = get_rag_service()
        num_chunks = rag_service.process_and_store_document(document_text, language)
        
        # Get context from document
        translator = get_translator()
        question_en = translator.translate_to_english(question, language)
        context = rag_service.get_context_string(question_en, language=language)
        
        # Get advisory
        advisory_service = FarmerAdvisoryService()
        response = advisory_service.get_advisory(question_en, language=language, context=context)
        response_user_lang = translator.translate_from_english(response, language)
        
        return format_success_response({
            "response": response_user_lang,
            "chunks_processed": num_chunks,
            "language": language
        })
    except (InvalidInputError, FileUploadError) as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.error(f"Document advisory error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process document")

@app.get("/api/v1/advisory/schemes")
def list_schemes():
    """Get list of government schemes."""
    try:
        advisory_service = FarmerAdvisoryService()
        schemes = advisory_service.get_government_schemes()
        return format_success_response(schemes)
    except Exception as e:
        logger.error(f"Error listing schemes: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list schemes")

@app.get("/api/v1/advisory/schemes/{scheme_id}")
def get_scheme(scheme_id: str):
    """Get specific scheme details."""
    try:
        scheme = SchemeAdvisoryService.explain_scheme(scheme_id)
        if not scheme:
            raise NotFoundError(f"Scheme {scheme_id}")
        return format_success_response(scheme)
    except NotFoundError as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.error(f"Error getting scheme: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get scheme")


# ============================================
# SCHEMES ENDPOINTS
# ============================================

@app.get("/api/v1/schemes")
def get_schemes(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get list of all government schemes."""
    try:
        logger.info(f"[SCHEMES] Fetching schemes list - limit: {limit}, offset: {offset}")
        from database.models import Scheme
        
        schemes = db.query(Scheme).offset(offset).limit(limit).all()
        total = db.query(Scheme).count()
        
        schemes_data = [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description[:200] if s.description else "",
                "scheme_type": s.scheme_type,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in schemes
        ]
        
        logger.info(f"[SCHEMES] Retrieved {len(schemes_data)} schemes")
        return format_success_response({
            "schemes": schemes_data,
            "total": total,
            "limit": limit,
            "offset": offset
        })
    except Exception as e:
        logger.error(f"[SCHEMES] Error fetching schemes: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch schemes")


@app.get("/api/v1/schemes/{scheme_id}")
def get_scheme_details(
    scheme_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific scheme."""
    try:
        logger.info(f"[SCHEMES] Fetching scheme details - ID: {scheme_id}")
        from database.models import Scheme
        
        scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
        
        if not scheme:
            logger.warning(f"[SCHEMES] Scheme not found - ID: {scheme_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme not found")
        
        # Get related documents
        documents = [
            {
                "id": doc.id,
                "name": doc.document_name,
                "type": doc.document_type,
                "size": doc.file_size,
                "created_at": doc.created_at.isoformat() if doc.created_at else None
            }
            for doc in scheme.documents
        ]
        
        scheme_data = {
            "id": scheme.id,
            "name": scheme.name,
            "description": scheme.description,
            "eligibility": scheme.eligibility,
            "benefits": scheme.benefits,
            "application_process": scheme.application_process,
            "scheme_type": scheme.scheme_type,
            "documents": documents,
            "created_at": scheme.created_at.isoformat() if scheme.created_at else None
        }
        
        logger.info(f"[SCHEMES] Retrieved scheme details - {scheme.name}")
        return format_success_response(scheme_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SCHEMES] Error fetching scheme details: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch scheme details")


@app.get("/api/v1/schemes/{scheme_id}/documents")
def get_scheme_documents(
    scheme_id: int,
    db: Session = Depends(get_db)
):
    """Get all documents required for a scheme."""
    try:
        logger.info(f"[SCHEMES] Fetching documents for scheme - ID: {scheme_id}")
        from database.models import Scheme
        
        scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
        
        if not scheme:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme not found")
        
        documents = [
            {
                "id": doc.id,
                "name": doc.document_name,
                "type": doc.document_type,
                "size": doc.file_size,
                "has_file": doc.file_path is not None,
                "has_url": doc.file_url is not None,
                "url": doc.file_url
            }
            for doc in scheme.documents
        ]
        
        logger.info(f"[SCHEMES] Retrieved {len(documents)} documents for scheme {scheme_id}")
        return format_success_response({"documents": documents})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SCHEMES] Error fetching documents: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch documents")


@app.get("/api/v1/schemes/documents/{document_id}/download")
def download_scheme_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Download a scheme document."""
    try:
        logger.info(f"[SCHEMES] Download request for document - ID: {document_id}")
        from database.models import SchemeDocument
        
        document = db.query(SchemeDocument).filter(SchemeDocument.id == document_id).first()
        
        if not document:
            logger.warning(f"[SCHEMES] Document not found - ID: {document_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
        # If external URL, return redirect URL in JSON
        if document.file_url:
            logger.info(f"[SCHEMES] Returning redirect URL for external resource")
            return format_success_response({"redirect_url": document.file_url})
        
        # If local file
        if document.file_path and os.path.exists(document.file_path):
            logger.info(f"[SCHEMES] Serving file - {document.file_path}")
            return FileResponse(
                path=document.file_path,
                filename=document.document_name,
                media_type="application/octet-stream"
            )
        
        logger.warning(f"[SCHEMES] File not found - {document.file_path}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SCHEMES] Error downloading document: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to download document")

# Legacy endpoints removed - see conversation routes for conversation management

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=settings.DEBUG)

