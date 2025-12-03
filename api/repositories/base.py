"""
Abstract base repository defining the interface for data access.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base class for all repositories.

    Provides a consistent interface for CRUD operations
    across different collections.
    """

    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str):
        """
        Initialize the repository.

        Args:
            database: The MongoDB database instance.
            collection_name: The name of the MongoDB collection.
        """
        self.database = database
        self.collection = database[collection_name]

    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        Create a new entity in the database.

        Args:
            entity: The entity to create.

        Returns:
            The created entity with its ID populated.
        """
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> T | None:
        """
        Retrieve an entity by its ID.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        pass

    @abstractmethod
    async def update(self, entity_id: str, entity: T) -> T | None:
        """
        Update an existing entity.

        Args:
            entity_id: The unique identifier of the entity.
            entity: The updated entity data.

        Returns:
            The updated entity if found, None otherwise.
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """
        Delete an entity by its ID.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            True if the entity was deleted, False otherwise.
        """
        pass

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict | None = None,
    ) -> list[T]:
        """
        List entities with optional pagination and filtering.

        Args:
            skip: Number of entities to skip.
            limit: Maximum number of entities to return.
            filters: Optional query filters.

        Returns:
            List of entities matching the criteria.
        """
        pass
