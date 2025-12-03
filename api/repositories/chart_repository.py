"""
Repository for chart data access.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase

from api.models.charts import ChartInDB

from .base import BaseRepository


class ChartRepository(BaseRepository[ChartInDB]):
    """Repository for chart CRUD operations."""

    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "charts")

    async def create(self, entity: ChartInDB) -> ChartInDB:
        """Create a new chart."""
        # TODO: Implement - insert document and return with generated ID
        raise NotImplementedError

    async def get_by_id(self, entity_id: str) -> ChartInDB | None:
        """Get a chart by its ID."""
        # TODO: Implement - query by _id
        raise NotImplementedError

    async def update(self, entity_id: str, entity: ChartInDB) -> ChartInDB | None:
        """Update an existing chart."""
        # TODO: Implement - update document by _id
        raise NotImplementedError

    async def delete(self, entity_id: str) -> bool:
        """Delete a chart by its ID."""
        # TODO: Implement - delete document by _id
        raise NotImplementedError

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict | None = None,
    ) -> list[ChartInDB]:
        """List charts with pagination."""
        # TODO: Implement - query with skip/limit
        raise NotImplementedError

    async def get_by_owner(
        self,
        owner_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ChartInDB]:
        """
        Get all charts owned by a specific user.

        Args:
            owner_id: The ID of the chart owner.
            skip: Number of charts to skip.
            limit: Maximum number of charts to return.

        Returns:
            List of charts owned by the user.
        """
        # TODO: Implement - query by owner_id
        raise NotImplementedError

    async def get_by_poll_id(self, poll_id: str) -> list[ChartInDB]:
        """
        Get all charts that include a specific poll.

        Args:
            poll_id: The ID of the poll.

        Returns:
            List of charts containing the poll.
        """
        # TODO: Implement - query where poll_ids contains poll_id
        raise NotImplementedError
