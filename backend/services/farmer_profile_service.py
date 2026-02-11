"""Farmer profile service for eligibility checking and personalization."""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from database.models import FarmerProfile, User
from logger.setup import get_logger
import json

logger = get_logger(__name__)


class FarmerProfileService:
    """Manage farmer profiles and eligibility."""

    @staticmethod
    def create_or_update_profile(
        db: Session,
        user_id: int,
        state: str,
        district: str,
        land_size_hectares: int,
        primary_crop: str,
        secondary_crops: Optional[str] = None,
        farming_type: str = "conventional",
        annual_income: Optional[int] = None,
        dbt_eligible: bool = False,
        bank_account_linked: bool = False,
        aadhar_verified: bool = False,
    ) -> FarmerProfile:
        """Create or update farmer profile."""
        try:
            profile = db.query(FarmerProfile).filter(
                FarmerProfile.user_id == user_id
            ).first()

            if profile:
                profile.state = state
                profile.district = district
                profile.land_size_hectares = land_size_hectares
                profile.primary_crop = primary_crop
                profile.secondary_crops = secondary_crops
                profile.farming_type = farming_type
                profile.annual_income = annual_income
                profile.dbt_eligible = dbt_eligible
                profile.bank_account_linked = bank_account_linked
                profile.aadhar_verified = aadhar_verified
            else:
                profile = FarmerProfile(
                    user_id=user_id,
                    state=state,
                    district=district,
                    land_size_hectares=land_size_hectares,
                    primary_crop=primary_crop,
                    secondary_crops=secondary_crops,
                    farming_type=farming_type,
                    annual_income=annual_income,
                    dbt_eligible=dbt_eligible,
                    bank_account_linked=bank_account_linked,
                    aadhar_verified=aadhar_verified,
                )
                db.add(profile)

            db.commit()
            db.refresh(profile)
            logger.info(f"Profile created/updated for user {user_id}")
            return profile
        except Exception as e:
            logger.error(f"Error managing profile: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_profile(db: Session, user_id: int) -> Optional[FarmerProfile]:
        """Get farmer profile."""
        return db.query(FarmerProfile).filter(
            FarmerProfile.user_id == user_id
        ).first()

    @staticmethod
    def check_scheme_eligibility(
        profile: FarmerProfile,
        scheme_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if farmer is eligible for a scheme.

        Returns eligibility status and reasons.
        """
        try:
            eligible = True
            reasons = []
            missing_requirements = []

            # State eligibility
            if "states" in scheme_criteria:
                eligible_states = scheme_criteria["states"]
                if profile.state not in eligible_states:
                    eligible = False
                    missing_requirements.append(
                        f"Only available in: {', '.join(eligible_states)}"
                    )

            # Land size eligibility
            if "min_land_size" in scheme_criteria:
                if (
                    profile.land_size_hectares
                    and profile.land_size_hectares
                    < scheme_criteria["min_land_size"]
                ):
                    eligible = False
                    missing_requirements.append(
                        f"Minimum {scheme_criteria['min_land_size']} hectares required"
                    )

            if "max_land_size" in scheme_criteria:
                if (
                    profile.land_size_hectares
                    and profile.land_size_hectares
                    > scheme_criteria["max_land_size"]
                ):
                    eligible = False
                    missing_requirements.append(
                        f"Maximum {scheme_criteria['max_land_size']} hectares allowed"
                    )

            # Crop eligibility
            if "eligible_crops" in scheme_criteria:
                crops = [profile.primary_crop]
                if profile.secondary_crops:
                    crops.extend(
                        c.strip() for c in profile.secondary_crops.split(",")
                    )

                if not any(
                    crop in scheme_criteria["eligible_crops"] for crop in crops
                ):
                    eligible = False
                    missing_requirements.append(
                        f"Crops must be: {', '.join(scheme_criteria['eligible_crops'])}"
                    )

            # DBT eligibility
            if scheme_criteria.get("requires_dbt") and not profile.dbt_eligible:
                eligible = False
                missing_requirements.append("Direct Benefit Transfer (DBT) required")

            # Bank account requirement
            if scheme_criteria.get("requires_bank_account") and not profile.bank_account_linked:
                eligible = False
                missing_requirements.append("Bank account must be linked")

            # Income eligibility
            if "max_annual_income" in scheme_criteria:
                if profile.annual_income and profile.annual_income > scheme_criteria[
                    "max_annual_income"
                ]:
                    eligible = False
                    missing_requirements.append(
                        f"Income must not exceed ₹{scheme_criteria['max_annual_income']}"
                    )

            return {
                "eligible": eligible,
                "missing_requirements": missing_requirements,
                "profile_completeness": FarmerProfileService._calculate_profile_completeness(profile),
            }

        except Exception as e:
            logger.error(f"Error checking eligibility: {str(e)}")
            return {
                "eligible": False,
                "error": "Unable to check eligibility",
            }

    @staticmethod
    def _calculate_profile_completeness(profile: FarmerProfile) -> int:
        """Calculate profile completeness percentage."""
        fields = [
            profile.state,
            profile.district,
            profile.land_size_hectares,
            profile.primary_crop,
            profile.farming_type,
            profile.annual_income,
        ]
        completed = sum(1 for field in fields if field is not None)
        return (completed / len(fields)) * 100

    @staticmethod
    def get_dbt_readiness_score(profile: FarmerProfile) -> Dict[str, Any]:
        """Calculate DBT readiness score (0-100)."""
        try:
            score = 0
            details = []

            # Aadhar verification (30 points)
            if profile.aadhar_verified:
                score += 30
                details.append("✓ Aadhar verified")
            else:
                details.append("✗ Aadhar verification pending")

            # Bank account linked (30 points)
            if profile.bank_account_linked:
                score += 30
                details.append("✓ Bank account linked")
            else:
                details.append("✗ Bank account linking pending")

            # Profile completeness (40 points)
            completeness = FarmerProfileService._calculate_profile_completeness(profile)
            score += int((completeness / 100) * 40)
            details.append(f"Profile {completeness:.0f}% complete")

            return {
                "dbt_readiness_score": min(100, score),
                "details": details,
                "ready_for_dbt": score >= 80,
                "next_steps": FarmerProfileService._get_dbt_next_steps(
                    profile, score
                ),
            }

        except Exception as e:
            logger.error(f"Error calculating DBT score: {str(e)}")
            return {"dbt_readiness_score": 0, "error": "Unable to calculate score"}

    @staticmethod
    def _get_dbt_next_steps(profile: FarmerProfile, score: int) -> List[str]:
        """Get next steps to improve DBT readiness."""
        steps = []

        if not profile.aadhar_verified:
            steps.append("Verify Aadhar number with local authorities")

        if not profile.bank_account_linked:
            steps.append("Link bank account to Aadhar through NPCI")

        if FarmerProfileService._calculate_profile_completeness(profile) < 80:
            steps.append("Complete all profile fields for better scheme matching")

        return steps
