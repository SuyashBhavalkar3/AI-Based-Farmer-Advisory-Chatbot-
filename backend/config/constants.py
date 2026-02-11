"""Application constants and enumerations."""

from enum import Enum

class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    HINDI = "hi"
    MARATHI = "mr"

class AdvisoryCategory(str, Enum):
    """Farmer advisory categories."""
    GOVERNMENT_SCHEMES = "government_schemes"
    CROP_ADVISORY = "crop_advisory"
    POLICY_EXPLANATION = "policy_explanation"
    SUBSIDY_INFORMATION = "subsidy_information"
    LAND_AND_LEGAL = "land_and_legal"
    INSURANCE_ASSISTANCE = "insurance_assistance"
    BEST_PRACTICES = "best_practices"

class ErrorCode(str, Enum):
    """Application error codes."""
    INVALID_INPUT = "INVALID_INPUT"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    NOT_FOUND = "NOT_FOUND"
    FILE_UPLOAD_ERROR = "FILE_UPLOAD_ERROR"
    RAG_ERROR = "RAG_ERROR"
    TRANSLATION_ERROR = "TRANSLATION_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

# Farmer Advisory System Prompts
FARMER_SYSTEM_PROMPT = """You are an expert Farmer Advisory Chatbot providing guidance on:
- Government schemes and subsidies
- Crop advisory and best practices
- Land and legal matters
- Agricultural policies
- Insurance assistance
- Sustainable farming techniques

Provide clear, practical advice suitable for Indian farmers in {language}.
Keep responses concise (max 100 words) and actionable.
When referencing government schemes, provide scheme names and eligibility criteria.
Always cite relevant government sources when available."""

# Chunk sizes by language (different word lengths)
LANGUAGE_CHUNK_CONFIG = {
    "en": {"chunk_size": 500, "overlap": 50},
    "hi": {"chunk_size": 300, "overlap": 30},  # Hindi text denser
    "mr": {"chunk_size": 350, "overlap": 35},  # Marathi text denser
}

# Government Schemes Database (Sample)
GOVERNMENT_SCHEMES = {
    "PM-KISAN": {
        "name": "Pradhan Mantri Kisan Samman Nidhi",
        "description": "Direct income support to farmers",
        "benefit": "₹6000/year in 3 installments",
        "eligibility": ["Landholding farmers", "All states"]
    },
    "PM-FASAL-BIMA": {
        "name": "Pradhan Mantri Fasal Bima Yojana",
        "description": "Crop insurance scheme",
        "benefit": "Insurance coverage against crop loss",
        "eligibility": ["Farmers with agricultural land"]
    },
    "KUSUM": {
        "name": "Kisan Urja Suraksha evam Utthaan Mahaabhiyaan",
        "description": "Solar energy for farmers",
        "benefit": "Solar pumps installation subsidy",
        "eligibility": ["Agricultural land owners"]
    },
}

# Response Templates
RESPONSE_TEMPLATE = {
    "success": True,
    "data": None,
    "meta": {
        "timestamp": None,
        "version": "1.0",
        "language": None,
    },
    "error": None
}

ERROR_RESPONSE_TEMPLATE = {
    "success": False,
    "data": None,
    "error": {
        "code": None,
        "message": None,
        "details": None
    }
}
