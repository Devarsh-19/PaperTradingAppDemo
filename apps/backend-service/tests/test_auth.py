"""
Tests for authentication endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepass123",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()

    assert "user" in data
    assert "tokens" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["username"] == "newuser"
    assert data["tokens"]["token_type"] == "bearer"
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test that registering with an existing email fails."""
    user_data = {
        "email": "dup@example.com",
        "username": "user1",
        "password": "securepass123",
    }
    await client.post("/api/v1/auth/register", json=user_data)

    user_data["username"] = "user2"
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login."""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "securepass123",
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "securepass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "tokens" in data
    assert data["user"]["email"] == "login@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Test that login with wrong password fails."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpw@example.com",
            "username": "wrongpwuser",
            "password": "securepass123",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpw@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    """Test getting current user profile."""
    # Register
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@example.com",
            "username": "meuser",
            "password": "securepass123",
        },
    )
    token = reg_response.json()["tokens"]["access_token"]

    # Get profile
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test that unauthenticated requests are rejected."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401  # No auth header
