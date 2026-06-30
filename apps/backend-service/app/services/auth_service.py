"""
Authentication service — registration, login, token refresh.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.portfolio import Portfolio
from app.models.user import User
from app.models.watchlist import Watchlist
from app.schemas.user import (
    AuthResponse,
    TokenResponse,
    UserRegisterRequest,
    UserResponse,
)

settings = get_settings()


class AuthService:
    """Handles user registration, login, and token management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: UserRegisterRequest) -> AuthResponse:
        """
        Register a new user.

        Creates the user record, a default portfolio with virtual cash,
        and a default watchlist. Returns the user profile with JWT tokens.
        """
        # Check for existing email
        result = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        if result.scalar_one_or_none():
            raise ValueError("An account with this email already exists")

        # Check for existing username
        result = await self.db.execute(
            select(User).where(User.username == data.username)
        )
        if result.scalar_one_or_none():
            raise ValueError("This username is already taken")

        # Create user
        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            initial_balance=settings.default_virtual_balance,
        )
        self.db.add(user)
        await self.db.flush()  # Get user.id before creating related objects

        # Create default portfolio
        portfolio = Portfolio(
            user_id=user.id,
            name="Default Portfolio",
            cash_balance=settings.default_virtual_balance,
            initial_balance=settings.default_virtual_balance,
        )
        self.db.add(portfolio)

        # Create default watchlist
        watchlist = Watchlist(
            user_id=user.id,
            name="My Watchlist",
        )
        self.db.add(watchlist)

        await self.db.flush()

        # Generate tokens
        tokens = self._create_tokens(str(user.id))

        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    async def login(self, email: str, password: str) -> AuthResponse:
        """
        Authenticate a user by email and password.

        Returns user profile with fresh JWT tokens.
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if user is None or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is deactivated")

        tokens = self._create_tokens(str(user.id))

        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Issue new access + refresh tokens using a valid refresh token.
        """
        payload = decode_token(refresh_token)

        if payload is None:
            raise ValueError("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Token is not a refresh token")

        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token payload")

        # Verify user still exists and is active
        result = await self.db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()

        if user is None or not user.is_active:
            raise ValueError("User not found or inactive")

        return self._create_tokens(user_id)

    def _create_tokens(self, user_id: str) -> TokenResponse:
        """Generate an access + refresh token pair."""
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
