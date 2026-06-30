"""
User schemas — request/response models for authentication and user profile.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ── Request Schemas ──

class UserRegisterRequest(BaseModel):
    """Registration payload."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=100)


class UserLoginRequest(BaseModel):
    """Login payload (accepts email or username)."""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token payload."""
    refresh_token: str


# ── Response Schemas ──

class UserResponse(BaseModel):
    """Public user profile."""
    id: uuid.UUID
    email: str
    username: str
    full_name: Optional[str] = None
    initial_balance: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token pair returned on login/register."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """Combined auth response with user profile + tokens."""
    user: UserResponse
    tokens: TokenResponse
