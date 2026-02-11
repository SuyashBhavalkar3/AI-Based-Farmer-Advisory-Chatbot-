"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.base import get_db
from auth.auth_service import AuthService
from auth.schemas import SignupRequest, LoginRequest, TokenResponse, UserResponse, AuthResponse
from auth.dependencies import get_current_user
from database.models import User
from config.settings import settings
from logger.setup import get_logger
from exceptions.custom_exceptions import AuthenticationError, InvalidInputError, to_http_exception

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/signup", response_model=AuthResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Create new user account."""
    try:
        user = AuthService.signup(db, request.full_name, request.email, request.password)
        logger.info(f"User signup successful: {request.email}")
        return AuthResponse(
            success=True,
            message="User created successfully",
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name
                }
            }
        )
    except (AuthenticationError, InvalidInputError) as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Signup failed")

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    try:
        user, token = AuthService.login(db, request.email, request.password)
        logger.info(f"User login successful: {request.email}")
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.from_orm(user)
        )
    except AuthenticationError as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return UserResponse.from_orm(current_user)

@router.post("/logout", response_model=AuthResponse)
def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint (token invalidation on client side)."""
    logger.info(f"User logout: {current_user.email}")
    return AuthResponse(
        success=True,
        message="Logged out successfully"
    )
