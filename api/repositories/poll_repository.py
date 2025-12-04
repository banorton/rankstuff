"""
Repository for poll and vote data access.
"""

from __future__ import annotations

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from models.polls import PollInDB, PollStatus, VoteInDB

from .base import BaseRepository


class PollRepository(BaseRepository[PollInDB]):
    """Repository for poll CRUD operations."""

    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "polls")
        self.votes_collection = database["votes"]

    def _doc_to_poll(self, doc: dict) -> PollInDB:
        """Convert MongoDB document to PollInDB model."""
        doc["id"] = str(doc.pop("_id"))
        return PollInDB(**doc)

    def _doc_to_vote(self, doc: dict) -> VoteInDB:
        """Convert MongoDB document to VoteInDB model."""
        doc["id"] = str(doc.pop("_id"))
        return VoteInDB(**doc)

    async def create(self, entity: PollInDB) -> PollInDB:
        """Create a new poll."""
        doc = entity.model_dump(exclude={"id"})
        result = await self.collection.insert_one(doc)
        entity.id = str(result.inserted_id)
        return entity

    async def get_by_id(self, entity_id: str) -> PollInDB | None:
        """Get a poll by its ID."""
        doc = await self.collection.find_one({"_id": ObjectId(entity_id)})
        if doc is None:
            return None
        return self._doc_to_poll(doc)

    async def update(self, entity_id: str, entity: PollInDB) -> PollInDB | None:
        """Update an existing poll."""
        doc = entity.model_dump(exclude={"id"})
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(entity_id)},
            {"$set": doc},
            return_document=ReturnDocument.AFTER,
        )
        if result is None:
            return None
        return self._doc_to_poll(result)

    async def delete(self, entity_id: str) -> bool:
        """Delete a poll by its ID."""
        result = await self.collection.delete_one({"_id": ObjectId(entity_id)})
        return result.deleted_count > 0

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict | None = None,
    ) -> list[PollInDB]:
        """List polls with pagination."""
        cursor = self.collection.find(filters or {}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_poll(doc) for doc in docs]

    async def get_by_owner(
        self,
        owner_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PollInDB]:
        """Get all polls owned by a specific user."""
        cursor = self.collection.find({"owner_id": owner_id}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_poll(doc) for doc in docs]

    async def get_open_polls(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PollInDB]:
        """Get all currently open polls."""
        cursor = self.collection.find({"status": PollStatus.OPEN.value}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_poll(doc) for doc in docs]

    async def update_status(
        self,
        poll_id: str,
        status: PollStatus,
    ) -> PollInDB | None:
        """Update a poll's status."""
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(poll_id)},
            {"$set": {"status": status.value}},
            return_document=ReturnDocument.AFTER,
        )
        if result is None:
            return None
        return self._doc_to_poll(result)

    # --- Vote Operations ---

    async def create_vote(self, vote: VoteInDB) -> VoteInDB:
        """Create a new vote for a poll."""
        doc = vote.model_dump(exclude={"id"})
        result = await self.votes_collection.insert_one(doc)
        vote.id = str(result.inserted_id)
        return vote

    async def get_vote(self, poll_id: str, user_id: str) -> VoteInDB | None:
        """Get a user's vote for a specific poll."""
        doc = await self.votes_collection.find_one({
            "poll_id": poll_id,
            "user_id": user_id,
        })
        if doc is None:
            return None
        return self._doc_to_vote(doc)

    async def get_votes_for_poll(self, poll_id: str) -> list[VoteInDB]:
        """Get all votes for a specific poll."""
        cursor = self.votes_collection.find({"poll_id": poll_id})
        docs = await cursor.to_list(length=None)
        return [self._doc_to_vote(doc) for doc in docs]

    async def count_votes(self, poll_id: str) -> int:
        """Count the total number of votes for a poll."""
        return await self.votes_collection.count_documents({"poll_id": poll_id})
