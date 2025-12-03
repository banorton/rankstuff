"""
MongoDB database connection and session management.
"""

from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import settings

# Global client instance
_client: AsyncIOMotorClient | None = None


async def get_database() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Dependency that provides a MongoDB database instance.

    Yields:
        AsyncIOMotorDatabase: The MongoDB database instance.
    """
    global _client

    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_url)

    yield _client[settings.mongodb_database]


async def connect_to_database() -> None:
    """Initialize the database connection on application startup."""
    global _client
    _client = AsyncIOMotorClient(settings.mongodb_url)


async def close_database_connection() -> None:
    """Close the database connection on application shutdown."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
