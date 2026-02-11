"""JWT and password utilities."""

from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import status
from config.settings import settings
from exceptions.custom_exceptions import AuthenticationError
from logger.setup import get_logger

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _truncate_password(password: str) -> str:
    """Truncate password to 72 bytes for bcrypt compatibility."""
    return password[:72]

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    try:
        return pwd_context.hash(_truncate_password(password))
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise AuthenticationError("Password hashing failed")

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    try:
        return pwd_context.verify(_truncate_password(password), hashed)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False

def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    """Create a JWT access token."""
    try:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": str(subject),
            "exp": int(expire.timestamp()),
            "iat": int(datetime.utcnow().timestamp())
        }
        
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        logger.info(f"Access token created for user: {subject}")
        return token
    except Exception as e:
        logger.error(f"Error creating token: {str(e)}")
        raise AuthenticationError("Token creation failed")

def decode_access_token(token: str) -> str:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise AuthenticationError("Invalid token format")
        return email
    except JWTError as e:
        error_msg = str(e).lower()
        if "expire" in error_msg:
            logger.warning("Token expired")
            raise AuthenticationError("Token has expired")
        logger.error(f"JWT decode error: {str(e)}")
        raise AuthenticationError("Invalid token")
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}")
        raise AuthenticationError("Token validation failed")
