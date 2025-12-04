"""
Pytest fixtures for API tests.
"""

import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

# Ensure api/ is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core import database
from routers import auth_router, poll_router, chart_router


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing endpoints."""
    # Create a fresh MongoDB client for this test's event loop
    mongo_client = AsyncIOMotorClient(settings.mongodb_url)

    # Override the global client in the database module
    database._client = mongo_client

    @asynccontextmanager
    async def test_lifespan(app: FastAPI):
        """Test lifespan - client already connected."""
        yield

    app = FastAPI(lifespan=test_lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth_router)
    app.include_router(poll_router)
    app.include_router(chart_router)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    # Cleanup
    mongo_client.close()
    database._client = None


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict:
    """Register a test user and return auth headers."""
    unique = uuid.uuid4().hex[:8]

    # Register
    await client.post("/auth/register", json={
        "email": f"test_{unique}@example.com",
        "username": f"testuser_{unique}",
        "password": "testpass123",
    })

    # Login
    response = await client.post("/auth/login", json={
        "identifier": f"test_{unique}@example.com",
        "password": "testpass123",
    })

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
