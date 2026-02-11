"""Input validation utilities."""

from typing import Any
from exceptions.custom_exceptions import InvalidInputError

class Validator:
    """Input validation helpers."""
    
    @staticmethod
    def validate_string(value: Any, min_length: int = 1, max_length: int = None, field_name: str = "Field") -> str:
        """Validate string input."""
        if not isinstance(value, str):
            raise InvalidInputError(f"{field_name} must be a string")
        if len(value) < min_length:
            raise InvalidInputError(f"{field_name} must be at least {min_length} characters")
        if max_length and len(value) > max_length:
            raise InvalidInputError(f"{field_name} must be at most {max_length} characters")
        return value
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format."""
        if "@" not in email or "." not in email.split("@")[1]:
            raise InvalidInputError("Invalid email address")
        return email
    
    @staticmethod
    def validate_file_size(size_bytes: int, max_size_mb: int) -> bool:
        """Validate file size."""
        max_size_bytes = max_size_mb * 1024 * 1024
        if size_bytes > max_size_bytes:
            raise InvalidInputError(f"File size exceeds maximum of {max_size_mb}MB")
        return True
    
    @staticmethod
    def validate_file_type(filename: str, allowed_types: list) -> str:
        """Validate file type."""
        file_type = filename.split(".")[-1].lower()
        if file_type not in allowed_types:
            raise InvalidInputError(f"File type {file_type} not allowed. Allowed types: {', '.join(allowed_types)}")
        return file_type
