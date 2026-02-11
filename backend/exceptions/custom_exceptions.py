"""Custom exception classes for the application."""

from fastapi import HTTPException, status
from config.constants import ErrorCode

class FarmerChatbotException(Exception):
    """Base exception for the application."""
    
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.INTERNAL_ERROR, status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(FarmerChatbotException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, ErrorCode.AUTHENTICATION_FAILED, status.HTTP_401_UNAUTHORIZED)

class InvalidInputError(FarmerChatbotException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str = "Invalid input"):
        super().__init__(message, ErrorCode.INVALID_INPUT, status.HTTP_400_BAD_REQUEST)

class NotFoundError(FarmerChatbotException):
    """Raised when resource is not found."""
    
    def __init__(self, resource: str = "Resource"):
        message = f"{resource} not found"
        super().__init__(message, ErrorCode.NOT_FOUND, status.HTTP_404_NOT_FOUND)

class FileUploadError(FarmerChatbotException):
    """Raised when file upload fails."""
    
    def __init__(self, message: str = "File upload failed"):
        super().__init__(message, ErrorCode.FILE_UPLOAD_ERROR, status.HTTP_400_BAD_REQUEST)

class RAGError(FarmerChatbotException):
    """Raised when RAG operations fail."""
    
    def __init__(self, message: str = "RAG operation failed"):
        super().__init__(message, ErrorCode.RAG_ERROR, status.HTTP_500_INTERNAL_SERVER_ERROR)

class TranslationError(FarmerChatbotException):
    """Raised when translation fails."""
    
    def __init__(self, message: str = "Translation failed"):
        super().__init__(message, ErrorCode.TRANSLATION_ERROR, status.HTTP_500_INTERNAL_SERVER_ERROR)

class DatabaseError(FarmerChatbotException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, ErrorCode.DATABASE_ERROR, status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExternalServiceError(FarmerChatbotException):
    """Raised when external services fail."""
    
    def __init__(self, service: str = "External service", message: str = None):
        msg = message or f"{service} is temporarily unavailable"
        super().__init__(msg, ErrorCode.EXTERNAL_SERVICE_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE)

class RateLimitError(FarmerChatbotException):
    """Raised when rate limit exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(message, ErrorCode.RATE_LIMIT_EXCEEDED, status.HTTP_429_TOO_MANY_REQUESTS)

def to_http_exception(exc: FarmerChatbotException) -> HTTPException:
    """Convert custom exception to HTTPException."""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "error_code": exc.error_code.value,
            "message": exc.message
        }
    )
