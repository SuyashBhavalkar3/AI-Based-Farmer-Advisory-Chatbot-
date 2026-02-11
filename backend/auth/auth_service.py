"""Authentication service layer."""

from sqlalchemy.orm import Session
from database.repository import UserRepository
from auth.jwt_handler import hash_password, verify_password, create_access_token
from exceptions.custom_exceptions import AuthenticationError, InvalidInputError
from logger.setup import get_logger
from database.models import User

logger = get_logger(__name__)

class AuthService:
    """Authentication business logic."""
    
    @staticmethod
    def signup(db: Session, full_name: str, email: str, password: str) -> User:
        """Create new user account."""
        # Validate inputs
        if not email or "@" not in email:
            raise InvalidInputError("Invalid email address")
        if len(password) < 6:
            raise InvalidInputError("Password must be at least 6 characters")
        if not full_name or len(full_name) < 2:
            raise InvalidInputError("Full name is required")
        
        # Check if user exists
        existing_user = UserRepository.get_by_email(db, email)
        if existing_user:
            logger.warning(f"Signup attempt with existing email: {email}")
            raise AuthenticationError("Email already registered")
        
        # Create user
        hashed_password = hash_password(password)
        user = UserRepository.create(db, full_name, email, hashed_password)
        return user
    
    @staticmethod
    def login(db: Session, email: str, password: str) -> tuple[User, str]:
        """Authenticate user and return token."""
        # Get user
        user = UserRepository.get_by_email(db, email)
        if not user:
            logger.warning(f"Login failed - user not found: {email}")
            raise AuthenticationError("Invalid email or password")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            logger.warning(f"Login failed - invalid password: {email}")
            raise AuthenticationError("Invalid email or password")
        
        # Generate token
        token = create_access_token(email)
        logger.info(f"User logged in: {email}")
        return user, token
    
    @staticmethod
    def get_current_user(db: Session, email: str) -> User:
        """Get user by email."""
        user = UserRepository.get_by_email(db, email)
        if not user:
            raise AuthenticationError("User not found")
        return user
