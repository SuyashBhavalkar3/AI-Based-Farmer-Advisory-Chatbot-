"""FastAPI dependencies for authentication."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.base import get_db
from auth.jwt_handler import decode_access_token
from auth.auth_service import AuthService
from database.models import User
from logger.setup import get_logger

logger = get_logger(__name__)

security = HTTPBearer(auto_error=True)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    try:
        token = credentials.credentials
        email = decode_access_token(token)
        user = AuthService.get_current_user(db, email)
        return user
    except Exception as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user_id(
    current_user: User = Depends(get_current_user)
) -> int:
    """Get current user ID."""
    return current_user.id
