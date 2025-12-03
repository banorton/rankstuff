"""
Repository for user data access.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase

from api.models.auth import UserInDB

from .base import BaseRepository


class UserRepository(BaseRepository[UserInDB]):
    """Repository for user CRUD operations."""

    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "users")

    async def create(self, entity: UserInDB) -> UserInDB:
        """Create a new user."""
        # TODO: Implement - insert document and return with generated ID
        raise NotImplementedError

    async def get_by_id(self, entity_id: str) -> UserInDB | None:
        """Get a user by their ID."""
        # TODO: Implement - query by _id
        raise NotImplementedError

    async def get_by_email(self, email: str) -> UserInDB | None:
        """
        Get a user by their email address.

        Args:
            email: The user's email address.

        Returns:
            The user if found, None otherwise.
        """
        # TODO: Implement - query by email field
        raise NotImplementedError

    async def get_by_username(self, username: str) -> UserInDB | None:
        """
        Get a user by their username.

        Args:
            username: The user's username.

        Returns:
            The user if found, None otherwise.
        """
        # TODO: Implement - query by username field
        raise NotImplementedError

    async def update(self, entity_id: str, entity: UserInDB) -> UserInDB | None:
        """Update an existing user."""
        # TODO: Implement - update document by _id
        raise NotImplementedError

    async def delete(self, entity_id: str) -> bool:
        """Delete a user by their ID."""
        # TODO: Implement - delete document by _id
        raise NotImplementedError

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict | None = None,
    ) -> list[UserInDB]:
        """List users with pagination."""
        # TODO: Implement - query with skip/limit
        raise NotImplementedError
