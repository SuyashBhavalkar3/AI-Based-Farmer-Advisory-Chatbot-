"""Farmer advisory service with domain-specific logic."""

import os
from openai import OpenAI
from typing import Dict, Any, List
from config.constants import FARMER_SYSTEM_PROMPT, GOVERNMENT_SCHEMES
from config.settings import settings
from rag.retriever import Retriever
from logger.setup import get_logger

logger = get_logger(__name__)

class FarmerAdvisoryService:
    """Handle farmer-specific advisory and guidance."""
    
    def __init__(self):
        """Initialize advisory service with OpenAI client."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    def get_advisory(self, question: str, language: str = "en", context: str = "", 
                     conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Get farmer advisory response with RAG context.
        
        Args:
            question: Farmer's question
            language: Language code
            context: Retrieved RAG context
            conversation_history: Previous messages for context
        
        Returns:
            Advisory response
        """
        try:
            # Build system prompt with language
            system_prompt = FARMER_SYSTEM_PROMPT.format(language=language)
            
            # Build conversation history
            messages = [{"role": "system", "content": system_prompt}]
            
            if conversation_history:
                messages.extend(conversation_history[-5:])  # Last 5 messages for context
            
            # Build user message with RAG context
            user_message = self._build_user_message(question, context)
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=settings.MAX_RESPONSE_TOKENS,
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"Advisory generated for language: {language}")
            return answer
        except Exception as e:
            logger.error(f"Error generating advisory: {str(e)}")
            raise
    
    def _build_user_message(self, question: str, context: str) -> str:
        """Build user message with RAG context."""
        if context:
            return f"""Based on the following information, please answer the question:

Information:
{context}

Question:
{question}

Please provide clear, actionable advice suitable for a farmer. Keep response concise (max 100 words)."""
        else:
            return f"""{question}

Please provide clear, actionable advice suitable for a farmer. Keep response concise (max 100 words)."""
    
    def get_government_schemes(self) -> Dict[str, Any]:
        """Get government schemes information."""
        return GOVERNMENT_SCHEMES
    
    def find_relevant_schemes(self, query: str) -> List[Dict[str, Any]]:
        """Find relevant government schemes for query."""
        try:
            relevant_schemes = []
            query_lower = query.lower()
            
            for scheme_id, scheme_info in GOVERNMENT_SCHEMES.items():
                # Simple keyword matching
                if any(keyword in query_lower for keyword in [
                    scheme_info["name"].lower(),
                    scheme_info["description"].lower()
                ]):
                    relevant_schemes.append({
                        "id": scheme_id,
                        **scheme_info
                    })
            
            return relevant_schemes
        except Exception as e:
            logger.error(f"Error finding schemes: {str(e)}")
            return []

class CropAdvisoryService:
    """Provide crop-specific advisory."""
    
    @staticmethod
    def get_crop_advice(crop: str, issue: str, context: str = "") -> str:
        """Get advice for specific crop and issue."""
        try:
            # This would integrate with RAG to get crop-specific information
            logger.info(f"Crop advisory requested: {crop} - {issue}")
            return "Crop advisory would be provided based on RAG corpus"
        except Exception as e:
            logger.error(f"Error getting crop advice: {str(e)}")
            raise

class SchemeAdvisoryService:
    """Provide guidance on government schemes."""
    
    @staticmethod
    def explain_scheme(scheme_id: str) -> Dict[str, Any]:
        """Get details about a government scheme."""
        scheme = GOVERNMENT_SCHEMES.get(scheme_id)
        if not scheme:
            logger.warning(f"Scheme not found: {scheme_id}")
            return {}
        return scheme
    
    @staticmethod
    def check_eligibility(scheme_id: str, farmer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Check farmer eligibility for scheme."""
        scheme = GOVERNMENT_SCHEMES.get(scheme_id)
        if not scheme:
            return {"eligible": False, "reason": "Scheme not found"}
        
        # Simple eligibility check
        eligibility = {
            "eligible": True,
            "scheme": scheme_id,
            "details": scheme,
            "requirements": scheme.get("eligibility", [])
        }
        return eligibility

class PolicyAdvisoryService:
    """Explain policies and regulations."""
    
    @staticmethod
    def explain_policy(policy_name: str, context: str = "") -> str:
        """Explain a policy or regulation."""
        try:
            # Would use RAG to fetch policy details
            logger.info(f"Policy explanation requested: {policy_name}")
            return "Policy details would be provided based on RAG corpus"
        except Exception as e:
            logger.error(f"Error explaining policy: {str(e)}")
            raise
