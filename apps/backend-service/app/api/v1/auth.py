"""
Authentication routes — register, login, refresh, profile.
"""

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.api.deps import CurrentUser, DbSession
from app.schemas.user import (
    AuthResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
)
async def register(data: UserRegisterRequest, db: DbSession):
    """
    Create a new user account.

    Automatically creates a default portfolio with $100,000 virtual cash
    and a default watchlist.
    """
    try:
        service = AuthService(db)
        return await service.register(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Log in with email and password",
)
async def login(data: UserLoginRequest, db: DbSession):
    """Authenticate and receive JWT tokens."""
    try:
        service = AuthService(db)
        return await service.login(data.email, data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh an expired access token",
)
async def refresh_token(data: RefreshTokenRequest, db: DbSession):
    """Issue new access + refresh tokens using a valid refresh token."""
    try:
        service = AuthService(db)
        return await service.refresh_token(data.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(current_user: CurrentUser):
    """Return the authenticated user's profile."""
    return UserResponse.model_validate(current_user)
