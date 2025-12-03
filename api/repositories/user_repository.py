"""
Repository for user data access.
"""

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from api.models.auth import UserInDB

from .base import BaseRepository


class UserRepository(BaseRepository[UserInDB]):
    """Repository for user CRUD operations."""

    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "users")

    def _doc_to_model(self, doc: dict) -> UserInDB:
        """Convert MongoDB document to UserInDB model."""
        doc["id"] = str(doc.pop("_id"))
        return UserInDB(**doc)

    async def create(self, entity: UserInDB) -> UserInDB:
        """Create a new user."""
        doc = entity.model_dump(exclude={"id"})
        result = await self.collection.insert_one(doc)
        entity.id = str(result.inserted_id)
        return entity

    async def get_by_id(self, entity_id: str) -> UserInDB | None:
        """Get a user by their ID."""
        doc = await self.collection.find_one({"_id": ObjectId(entity_id)})
        if doc is None:
            return None
        return self._doc_to_model(doc)

    async def get_by_email(self, email: str) -> UserInDB | None:
        """Get a user by their email address."""
        doc = await self.collection.find_one({"email": email})
        if doc is None:
            return None
        return self._doc_to_model(doc)

    async def get_by_username(self, username: str) -> UserInDB | None:
        """Get a user by their username."""
        doc = await self.collection.find_one({"username": username})
        if doc is None:
            return None
        return self._doc_to_model(doc)

    async def update(self, entity_id: str, entity: UserInDB) -> UserInDB | None:
        """Update an existing user."""
        doc = entity.model_dump(exclude={"id"})
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(entity_id)},
            {"$set": doc},
            return_document=True,
        )
        if result is None:
            return None
        return self._doc_to_model(result)

    async def delete(self, entity_id: str) -> bool:
        """Delete a user by their ID."""
        result = await self.collection.delete_one({"_id": ObjectId(entity_id)})
        return result.deleted_count > 0

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict | None = None,
    ) -> list[UserInDB]:
        """List users with pagination."""
        cursor = self.collection.find(filters or {}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_model(doc) for doc in docs]
