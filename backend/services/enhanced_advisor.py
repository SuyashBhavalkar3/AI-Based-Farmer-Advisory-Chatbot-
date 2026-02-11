"""Enhanced farmer advisory service with all smart features."""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from openai import OpenAI
from database.models import (
    Conversation,
    Message,
    FarmerProfile,
)
from config.settings import settings
from services.farmer_profile_service import FarmerProfileService
from services.rag_enhancer import EnhancedRAGService
from services.conversation_intelligence import ConversationIntelligenceService
from services.analytics import AnalyticsService
from logger.setup import get_logger

logger = get_logger(__name__)


class EnhancedFarmerAdvisoryService:
    """Enhanced advisory service with personalization, profiling, and smarts."""

    def __init__(self):
        """Initialize service."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.rag_service = EnhancedRAGService()
        self.intel_service = ConversationIntelligenceService()

    def get_personalized_advisory(
        self,
        db: Session,
        user_id: int,
        conversation_id: int,
        question: str,
        language: str = "en",
        context: str = "",
        conversation_history: List[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Get personalized advisory with farmer profile integration.

        Returns:
            {
                "response": main advisory text,
                "language": user's language,
                "profile_used": whether farmer profile was used,
                "schemes_recommended": list of relevant schemes,
                "sources": source citations,
                "confidence": confidence score,
                "follow_up_questions": suggested follow-ups,
                "farmer_readiness": DBT readiness if applicable
            }
        """
        try:
            # Get farmer profile if exists
            profile = FarmerProfileService.get_profile(db, user_id)

            # Get enhanced RAG results with citations
            rag_results = self.rag_service.retrieve_with_citations(
                question, language=language, top_k=5
            )

            # Build system prompt with farmer context
            system_prompt = self._build_enhanced_system_prompt(profile, language)

            # Build messages
            messages = [{"role": "system", "content": system_prompt}]

            if conversation_history:
                messages.extend(conversation_history[-5:])

            # Build user message with context and profile info
            user_message = self._build_enhanced_user_message(
                question,
                rag_results["context"],
                profile,
            )
            messages.append({"role": "user", "content": user_message})

            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=settings.MAX_RESPONSE_TOKENS,
            )

            answer = response.choices[0].message.content.strip()
            logger.info(f"Enhanced advisory generated")

            # Get scheme recommendations
            schemes = self._recommend_schemes(db, question, profile)

            # Update user insights
            AnalyticsService.update_user_insights(db, user_id)

            return {
                "response": answer,
                "language": language,
                "profile_used": profile is not None,
                "schemes_recommended": schemes,
                "sources": rag_results["sources"],
                "confidence": rag_results["average_confidence"],
                "follow_up_questions": self.intel_service.get_suggested_follow_up_questions(
                    conversation_id, db
                ),
                "farmer_readiness": (
                    FarmerProfileService.get_dbt_readiness_score(profile)
                    if profile
                    else None
                ),
            }

        except Exception as e:
            logger.error(f"Error in enhanced advisory: {str(e)}")
            raise

    def _build_enhanced_system_prompt(
        self,
        profile: Optional[FarmerProfile],
        language: str,
    ) -> str:
        """Build system prompt with farmer-specific context."""
        base_prompt = f"""You are an expert Farmer Advisory AI assistant providing personalized guidance on:
- Government schemes and subsidies
- Crop advisory and best practices
- Land and legal matters
- Agricultural policies
- Insurance assistance
- Sustainable farming techniques

Language: {language}
Provide clear, practical, actionable advice suitable for Indian farmers.
Keep responses concise (max 150 words) and context-aware.
Cite relevant schemes and eligibility criteria when applicable.

"""

        if profile:
            context = f"""FARMER PROFILE CONTEXT:
- Location: {profile.state}, {profile.district}
- Farm Size: {profile.land_size_hectares} hectares
- Primary Crop: {profile.primary_crop}
- Farming Type: {profile.farming_type}
- DBT Eligible: {profile.dbt_eligible}

Tailor advice based on the farmer's specific situation. Recommend schemes relevant to their location, farm size, and crops.
"""
            base_prompt += context

        return base_prompt

    def _build_enhanced_user_message(
        self,
        question: str,
        rag_context: str,
        profile: Optional[FarmerProfile],
    ) -> str:
        """Build user message with RAG context and profile."""
        parts = []

        if rag_context:
            parts.append("RELEVANT INFORMATION:")
            parts.append(rag_context)
            parts.append("")

        if profile:
            parts.append(
                f"FARMER'S SITUATION: {profile.land_size_hectares}ha {profile.primary_crop} farm in {profile.state}"
            )
            parts.append("")

        parts.append(f"QUESTION: {question}")

        return "\n".join(parts)

    def _recommend_schemes(
        self,
        db: Session,
        question: str,
        profile: Optional[FarmerProfile],
    ) -> List[Dict[str, Any]]:
        """Recommend government schemes based on question and profile."""
        try:
            from services.farmer_advisory import FarmerAdvisoryService

            advisory = FarmerAdvisoryService()
            schemes = advisory.find_relevant_schemes(question)

            # Filter by profile eligibility if profile exists
            if profile and schemes:
                for scheme in schemes:
                    # Create scheme criteria dict (in real implementation, get from DB)
                    criteria = {
                        "states": [profile.state],  # Simplified for example
                    }

                    eligibility = FarmerProfileService.check_scheme_eligibility(
                        profile, criteria
                    )

                    scheme["eligibility"] = eligibility

            return schemes

        except Exception as e:
            logger.error(f"Error recommending schemes: {str(e)}")
            return []
