"""Smart scheme recommendation and eligibility checking."""

from typing import Dict, List, Any
from sqlalchemy.orm import Session
from database.models import FarmerProfile
from config.constants import GOVERNMENT_SCHEMES
from services.farmer_profile_service import FarmerProfileService
from logger.setup import get_logger

logger = get_logger(__name__)


class SchemeRecommendationService:
    """AI-powered scheme recommendations and eligibility."""

    @staticmethod
    def get_eligible_schemes(
        db: Session,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        Get all schemes farmer is eligible for based on profile.

        Returns list of schemes with eligibility status.
        """
        try:
            profile = FarmerProfileService.get_profile(db, user_id)

            if not profile:
                return {
                    "eligible_schemes": [],
                    "message": "Create farmer profile for scheme recommendations",
                }

            eligible_schemes = []
            ineligible_schemes = []

            for scheme_id, scheme_info in GOVERNMENT_SCHEMES.items():
                # Build eligibility criteria from scheme info
                criteria = SchemeRecommendationService._extract_criteria(scheme_info)

                eligibility = FarmerProfileService.check_scheme_eligibility(
                    profile, criteria
                )

                scheme_detail = {
                    "id": scheme_id,
                    "name": scheme_info.get("name"),
                    "description": scheme_info.get("description"),
                    "benefits": scheme_info.get("benefits"),
                    "scheme_type": scheme_info.get("scheme_type"),
                    "eligibility_status": eligibility["eligible"],
                    "missing_requirements": eligibility.get("missing_requirements", []),
                }

                if eligibility["eligible"]:
                    eligible_schemes.append(scheme_detail)
                else:
                    ineligible_schemes.append(scheme_detail)

            logger.info(
                f"Found {len(eligible_schemes)} eligible schemes for user {user_id}"
            )

            return {
                "eligible_schemes": eligible_schemes,
                "ineligible_schemes": ineligible_schemes,
                "total_eligible": len(eligible_schemes),
                "total_checked": len(GOVERNMENT_SCHEMES),
                "profile_completeness": FarmerProfileService._calculate_profile_completeness(
                    profile
                ),
            }

        except Exception as e:
            logger.error(f"Error getting eligible schemes: {str(e)}")
            return {"eligible_schemes": [], "error": str(e)}

    @staticmethod
    def get_scheme_details(
        scheme_id: str,
        db: Session = None,
        user_id: int = None,
    ) -> Dict[str, Any]:
        """Get detailed information about a specific scheme."""
        try:
            scheme = GOVERNMENT_SCHEMES.get(scheme_id)

            if not scheme:
                return {"error": f"Scheme {scheme_id} not found"}

            details = {
                "id": scheme_id,
                "name": scheme.get("name"),
                "description": scheme.get("description"),
                "benefits": scheme.get("benefits"),
                "eligibility": scheme.get("eligibility"),
                "application_process": scheme.get("application_process"),
                "scheme_type": scheme.get("scheme_type"),
                "documents_required": scheme.get("documents_required", []),
                "government_ministry": scheme.get("ministry"),
                "official_website": scheme.get("website"),
            }

            # Add farmer-specific eligibility if user_id provided
            if user_id and db:
                profile = FarmerProfileService.get_profile(db, user_id)
                if profile:
                    criteria = SchemeRecommendationService._extract_criteria(scheme)
                    eligibility = FarmerProfileService.check_scheme_eligibility(
                        profile, criteria
                    )
                    details["farmer_eligibility"] = eligibility

            logger.info(f"Retrieved details for scheme {scheme_id}")
            return details

        except Exception as e:
            logger.error(f"Error getting scheme details: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def _extract_criteria(scheme_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract eligibility criteria from scheme information."""
        criteria = {}

        # Try to extract from description/eligibility text
        if "eligibility" in scheme_info:
            eligibility_text = scheme_info["eligibility"].lower()

            # Check for state/region mentions
            if "state" in eligibility_text or "region" in eligibility_text:
                # In real implementation, parse from metadata
                criteria["states"] = ["ALL"]  # Default to all states

            # Check for land size requirements
            if "hectare" in eligibility_text or "acre" in eligibility_text:
                # Parse min/max land size
                if "minimum" in eligibility_text or "min" in eligibility_text:
                    criteria["min_land_size"] = 0  # Would parse actual value
                if "maximum" in eligibility_text or "max" in eligibility_text:
                    criteria["max_land_size"] = 1000000  # Default to high

            # Check for DBT requirement
            if "dbt" in eligibility_text or "direct benefit" in eligibility_text:
                criteria["requires_dbt"] = True

        return criteria

    @staticmethod
    def get_top_matching_schemes(
        db: Session,
        user_id: int,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get top matching schemes for farmer."""
        try:
            result = SchemeRecommendationService.get_eligible_schemes(db, user_id)

            eligible = result.get("eligible_schemes", [])
            # Sort by relevance (you could add scoring here)
            return eligible[:limit]

        except Exception as e:
            logger.error(f"Error getting top schemes: {str(e)}")
            return []

    @staticmethod
    def get_scheme_document_requirements(scheme_id: str) -> Dict[str, Any]:
        """Get detailed document requirements for a scheme."""
        try:
            scheme = GOVERNMENT_SCHEMES.get(scheme_id)

            if not scheme:
                return {"error": f"Scheme {scheme_id} not found"}

            documents = scheme.get("documents_required", [])

            return {
                "scheme_id": scheme_id,
                "scheme_name": scheme.get("name"),
                "documents": documents,
                "total_documents_needed": len(documents),
                "document_checklist": [
                    {
                        "name": doc,
                        "required": True,
                        "tips": SchemeRecommendationService._get_document_tips(doc),
                    }
                    for doc in documents
                ],
            }

        except Exception as e:
            logger.error(f"Error getting document requirements: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def _get_document_tips(document_name: str) -> str:
        """Get tips for obtaining a specific document."""
        tips_map = {
            "Aadhar": "Visit nearest UIDAI center or apply online at uidai.gov.in",
            "PAN": "Apply at nearest income tax office or online at incometaxindia.gov.in",
            "Bank Account": "Open at nearest bank branch with Aadhar + government ID",
            "Land Document": "Obtain from district collector or revenue office",
            "Passport": "Apply at nearest passport office",
            "Voter ID": "Register at local election commission office",
            "Caste Certificate": "Obtain from district collector or taluk office",
            "Income Certificate": "Obtain from revenue office",
            "Crop Insurance": "Register through nearest insurance company or bank",
        }

        return tips_map.get(
            document_name,
            "Contact your local agricultural office for this document",
        )
