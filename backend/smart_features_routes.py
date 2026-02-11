"""Routes for advanced chatbot features."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List

from database.base import get_db
from auth.dependencies import get_current_user_id
from database.models import User, Conversation, Message
from logger.setup import get_logger
from utils.formatters import format_success_response
from exceptions.custom_exceptions import NotFoundError, to_http_exception

# Import new services
from services.farmer_profile_service import FarmerProfileService
from services.conversation_intelligence import ConversationIntelligenceService
from services.rag_enhancer import EnhancedRAGService
from services.analytics import AnalyticsService
from services.document_intelligence import DocumentIntelligenceService
from services.scheme_recommender import SchemeRecommendationService

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/smart", tags=["Smart Features"])

# ==================== SCHEMAS ====================


class FarmerProfileRequest(BaseModel):
    """Farmer profile input."""

    state: str = Field(..., min_length=2, max_length=100)
    district: str = Field(..., min_length=2, max_length=100)
    land_size_hectares: int = Field(..., ge=0)
    primary_crop: str = Field(..., min_length=2, max_length=100)
    secondary_crops: Optional[str] = Field(None, max_length=500)
    farming_type: str = Field("conventional", pattern="^(organic|conventional|mixed)$")
    annual_income: Optional[int] = Field(None, ge=0)
    dbt_eligible: bool = False
    bank_account_linked: bool = False
    aadhar_verified: bool = False


class SimplifyRequest(BaseModel):
    """Request to simplify text."""

    text: str = Field(..., min_length=1, max_length=5000)
    mode: str = Field("simple", pattern="^(simple|legal)$")
    language: str = Field("en", pattern="^(en|hi|mr)$")


class DocumentAnalysisRequest(BaseModel):
    """Request to analyze document."""

    document_text: str = Field(..., min_length=1)
    analysis_type: str = Field("full", pattern="^(full|risks|sections)$")


class DocumentMissingRequest(BaseModel):
    """Request to check for missing documents."""

    scheme_name: str = Field(..., min_length=1, max_length=255)
    uploaded_documents: List[str] = Field(default_factory=list)


# ==================== FARMER PROFILE ENDPOINTS ====================


@router.post("/profile")
def create_or_update_profile(
    request: FarmerProfileRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create or update farmer profile for personalized recommendations."""
    try:
        profile = FarmerProfileService.create_or_update_profile(
            db=db,
            user_id=user_id,
            state=request.state,
            district=request.district,
            land_size_hectares=request.land_size_hectares,
            primary_crop=request.primary_crop,
            secondary_crops=request.secondary_crops,
            farming_type=request.farming_type,
            annual_income=request.annual_income,
            dbt_eligible=request.dbt_eligible,
            bank_account_linked=request.bank_account_linked,
            aadhar_verified=request.aadhar_verified,
        )

        return format_success_response({
            "profile_id": profile.id,
            "state": profile.state,
            "district": profile.district,
            "land_size_hectares": profile.land_size_hectares,
            "primary_crop": profile.primary_crop,
            "farming_type": profile.farming_type,
            "completeness_percent": FarmerProfileService._calculate_profile_completeness(
                profile
            ),
        })
    except Exception as e:
        logger.error(f"Error creating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create profile",
        )


@router.get("/profile")
def get_profile(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get farmer profile."""
    try:
        profile = FarmerProfileService.get_profile(db, user_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )

        return format_success_response({
            "profile_id": profile.id,
            "state": profile.state,
            "district": profile.district,
            "land_size_hectares": profile.land_size_hectares,
            "primary_crop": profile.primary_crop,
            "secondary_crops": profile.secondary_crops,
            "farming_type": profile.farming_type,
            "annual_income": profile.annual_income,
            "dbt_eligible": profile.dbt_eligible,
            "bank_account_linked": profile.bank_account_linked,
            "aadhar_verified": profile.aadhar_verified,
            "completeness_percent": FarmerProfileService._calculate_profile_completeness(
                profile
            ),
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile",
        )


@router.get("/dbt-readiness")
def get_dbt_readiness(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get DBT readiness score and action items."""
    try:
        profile = FarmerProfileService.get_profile(db, user_id)

        if not profile:
            return format_success_response({
                "dbt_readiness_score": 0,
                "error": "Create profile first to check DBT readiness",
            })

        readiness = FarmerProfileService.get_dbt_readiness_score(profile)
        return format_success_response(readiness)

    except Exception as e:
        logger.error(f"Error getting DBT readiness: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate DBT readiness",
        )


# ==================== CONVERSATION INTELLIGENCE ENDPOINTS ====================


@router.post("/conversations/{conversation_id}/summarize")
def summarize_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Generate AI summary of entire conversation."""
    try:
        # Verify conversation ownership
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .first()
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        service = ConversationIntelligenceService()
        summary = service.generate_conversation_summary(db, conversation_id)

        if not summary:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate summary",
            )

        return format_success_response({
            "summary": summary.summary,
            "key_topics": summary.key_topics,
            "schemes_discussed": summary.schemes_discussed,
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to summarize conversation",
        )


@router.get("/conversations/{conversation_id}/follow-ups")
def get_follow_up_questions(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get smart follow-up question suggestions."""
    try:
        # Verify conversation ownership
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .first()
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        service = ConversationIntelligenceService()
        questions = service.get_suggested_follow_up_questions(conversation_id, db)

        return format_success_response({
            "suggested_questions": questions,
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting follow-ups: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate follow-up questions",
        )


@router.post("/simplify")
def simplify_text(
    request: SimplifyRequest,
):
    """Simplify text for low-literacy or legal simplification."""
    try:
        service = ConversationIntelligenceService()

        if request.mode == "simple":
            simplified = service.simplify_for_low_literacy(request.text, request.language)
        else:  # legal
            simplified = service.legally_simplify(request.text)

        return format_success_response({
            "original": request.text,
            "simplified": simplified,
            "mode": request.mode,
        })

    except Exception as e:
        logger.error(f"Error simplifying text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to simplify text",
        )


# ==================== RAG ENHANCEMENT ENDPOINTS ====================


@router.get("/search-with-citations")
def search_with_citations(
    query: str = Query(..., min_length=1, max_length=500),
    language: str = Query("en", pattern="^(en|hi|mr)$"),
    top_k: int = Query(5, ge=1, le=10),
):
    """Search RAG with source citations and confidence scores."""
    try:
        service = EnhancedRAGService()
        results = service.retrieve_with_citations(query, language, top_k)

        return format_success_response({
            "context": results["context"],
            "sources": results["sources"],
            "average_confidence": results["average_confidence"],
            "confidence_badge": service.generate_confidence_badge(
                results["average_confidence"]
            ),
        })

    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search",
        )


@router.get("/document-preview")
def get_document_preview(
    query: str = Query(..., min_length=1, max_length=500),
    language: str = Query("en", pattern="^(en|hi|mr)$"),
    top_k: int = Query(3, ge=1, le=5),
):
    """Get preview of top relevant documents."""
    try:
        service = EnhancedRAGService()
        previews = service.get_top_documents_preview(query, language, top_k)

        return format_success_response({
            "document_previews": previews,
        })

    except Exception as e:
        logger.error(f"Error getting previews: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document previews",
        )


# ==================== ANALYTICS ENDPOINTS ====================


@router.get("/dashboard")
def get_user_dashboard(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get personalized user dashboard."""
    try:
        # Update insights first
        AnalyticsService.update_user_insights(db, user_id)

        dashboard = AnalyticsService.get_user_dashboard(db, user_id)

        return format_success_response(dashboard)

    except Exception as e:
        logger.error(f"Error building dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to build dashboard",
        )


@router.get("/admin/trends")
def get_global_trends(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get global trends (admin only for now)."""
    try:
        # In production, add admin role check here
        trends = AnalyticsService.get_global_trends(db)

        return format_success_response(trends)

    except Exception as e:
        logger.error(f"Error getting trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trends",
        )


# ==================== DOCUMENT INTELLIGENCE ENDPOINTS ====================


@router.post("/document/analyze")
def analyze_document(
    request: DocumentAnalysisRequest,
):
    """Analyze land or legal document for key information and risks."""
    try:
        service = DocumentIntelligenceService()

        if request.analysis_type == "full":
            result = service.analyze_land_document(request.document_text)
        elif request.analysis_type == "risks":
            result = service.scan_for_risks(request.document_text)
        else:  # sections
            result = service.highlight_important_sections(request.document_text)

        return format_success_response({
            "analysis_type": request.analysis_type,
            "analysis": result,
        })

    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze document",
        )


@router.post("/document/missing-check")
def check_missing_documents(
    request: DocumentMissingRequest,
):
    """Check which documents might be missing for a scheme."""
    try:
        service = DocumentIntelligenceService()
        result = service.detect_missing_documents(
            request.scheme_name,
            request.uploaded_documents,
        )

        return format_success_response({
            "scheme": request.scheme_name,
            "analysis": result,
        })

    except Exception as e:
        logger.error(f"Error checking missing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check documents",
        )


@router.post("/document/explain-section")
def explain_document_section(
    section_text: str = Query(..., min_length=1),
    context: str = Query("", max_length=500),
):
    """Get plain-language explanation of document section."""
    try:
        service = DocumentIntelligenceService()
        explanation = service.explain_document_section(section_text, context)

        return format_success_response({
            "section": section_text[:100] + "..." if len(section_text) > 100 else section_text,
            "explanation": explanation,
        })

    except Exception as e:
        logger.error(f"Error explaining section: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to explain section",
        )


@router.get("/document/checklist")
def get_document_checklist(
    scheme_name: str = Query(..., min_length=1, max_length=255),
):
    """Get printable document checklist for a scheme."""
    try:
        service = DocumentIntelligenceService()
        result = service.generate_document_checklist(scheme_name)

        return format_success_response(result)

    except Exception as e:
        logger.error(f"Error generating checklist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate checklist",
        )


# ==================== SCHEME RECOMMENDATION ENDPOINTS ====================


@router.get("/schemes/eligible")
def get_eligible_schemes(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get all schemes farmer is eligible for."""
    try:
        result = SchemeRecommendationService.get_eligible_schemes(db, user_id)
        return format_success_response(result)

    except Exception as e:
        logger.error(f"Error getting eligible schemes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get schemes",
        )


@router.get("/schemes/top-matches")
def get_top_matching_schemes(
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get top matching schemes for farmer's profile."""
    try:
        schemes = SchemeRecommendationService.get_top_matching_schemes(
            db, user_id, limit
        )
        return format_success_response({
            "top_schemes": schemes,
            "count": len(schemes),
        })

    except Exception as e:
        logger.error(f"Error getting top schemes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get top schemes",
        )


@router.get("/schemes/{scheme_id}")
def get_scheme_details(
    scheme_id: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get detailed information about a specific scheme."""
    try:
        details = SchemeRecommendationService.get_scheme_details(
            scheme_id, db, user_id
        )

        if "error" in details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=details["error"],
            )

        return format_success_response(details)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scheme details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scheme details",
        )


@router.get("/schemes/{scheme_id}/documents")
def get_scheme_documents(
    scheme_id: str,
):
    """Get required documents for a specific scheme."""
    try:
        requirements = SchemeRecommendationService.get_scheme_document_requirements(
            scheme_id
        )

        if "error" in requirements:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=requirements["error"],
            )

        return format_success_response(requirements)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document requirements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document requirements",
        )
