"""
Test fixtures and configuration for pytest.
"""

import asyncio
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.user import User
from app.models.portfolio import Portfolio


# ── Use SQLite for tests (in-memory) ──
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client with dependency overrides."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user with a default portfolio."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hash_password("testpassword123"),
        full_name="Test User",
        initial_balance=100_000.00,
    )
    db_session.add(user)
    await db_session.flush()

    portfolio = Portfolio(
        user_id=user.id,
        name="Default Portfolio",
        cash_balance=100_000.00,
        initial_balance=100_000.00,
    )
    db_session.add(portfolio)
    await db_session.commit()

    return user


@pytest_asyncio.fixture
def auth_headers(test_user: User) -> dict:
    """Generate authorization headers for the test user."""
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}
