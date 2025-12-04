"""
Tests for authentication endpoints.
"""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    unique = uuid.uuid4().hex[:8]

    response = await client.post("/auth/register", json={
        "email": f"newuser_{unique}@example.com",
        "username": f"newuser_{unique}",
        "password": "password123",
    })

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == f"newuser_{unique}@example.com"
    assert data["username"] == f"newuser_{unique}"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email fails."""
    unique = uuid.uuid4().hex[:8]
    email = f"dupe_{unique}@example.com"

    # First registration
    await client.post("/auth/register", json={
        "email": email,
        "username": f"user1_{unique}",
        "password": "password123",
    })

    # Duplicate email
    response = await client.post("/auth/register", json={
        "email": email,
        "username": f"user2_{unique}",
        "password": "password123",
    })

    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login returns token."""
    unique = uuid.uuid4().hex[:8]

    # Register
    await client.post("/auth/register", json={
        "email": f"login_{unique}@example.com",
        "username": f"loginuser_{unique}",
        "password": "password123",
    })

    # Login with email
    response = await client.post("/auth/login", json={
        "identifier": f"login_{unique}@example.com",
        "password": "password123",
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_with_username(client: AsyncClient):
    """Test login with username instead of email."""
    unique = uuid.uuid4().hex[:8]

    # Register
    await client.post("/auth/register", json={
        "email": f"user_{unique}@example.com",
        "username": f"myusername_{unique}",
        "password": "password123",
    })

    # Login with username
    response = await client.post("/auth/login", json={
        "identifier": f"myusername_{unique}",
        "password": "password123",
    })

    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Test login with wrong password fails."""
    unique = uuid.uuid4().hex[:8]

    # Register
    await client.post("/auth/register", json={
        "email": f"wrong_{unique}@example.com",
        "username": f"wrongpass_{unique}",
        "password": "password123",
    })

    # Wrong password
    response = await client.post("/auth/login", json={
        "identifier": f"wrong_{unique}@example.com",
        "password": "wrongpassword",
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers: dict):
    """Test getting current user with valid token."""
    response = await client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert "username" in data
