"""Authentication request/response schemas."""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: Optional['UserResponse'] = None

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[dict] = None
