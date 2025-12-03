"""
Chart service - Business logic for aggregated rankings.
"""

from datetime import datetime, timezone

from fastapi import HTTPException, status

from api.models.charts import ChartCreate, ChartEntry, ChartInDB, ChartResponse
from api.repositories.chart_repository import ChartRepository
from api.repositories.poll_repository import PollRepository


class ChartService:
    """Service for chart operations."""

    def __init__(
        self,
        chart_repository: ChartRepository,
        poll_repository: PollRepository,
    ):
        """
        Initialize the chart service.

        Args:
            chart_repository: Repository for chart data access.
            poll_repository: Repository for poll data access.
        """
        self.chart_repository = chart_repository
        self.poll_repository = poll_repository

    async def create_chart(
        self,
        chart_data: ChartCreate,
        owner_id: str,
    ) -> ChartResponse:
        """
        Create a new chart from poll results.

        Args:
            chart_data: The chart creation data.
            owner_id: The ID of the chart owner.

        Returns:
            The created chart response.

        Raises:
            HTTPException: If any referenced poll doesn't exist.
        """
        # Validate that all poll IDs exist
        for poll_id in chart_data.poll_ids:
            poll = await self.poll_repository.get_by_id(poll_id)
            if not poll:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Poll not found: {poll_id}",
                )

        chart_in_db = ChartInDB(
            title=chart_data.title,
            description=chart_data.description,
            poll_ids=chart_data.poll_ids,
            owner_id=owner_id,
            entries=[],  # Will be populated on refresh
        )

        created_chart = await self.chart_repository.create(chart_in_db)

        # Calculate initial entries
        return await self.refresh_chart(created_chart.id, owner_id)

    async def get_chart(self, chart_id: str) -> ChartResponse:
        """
        Get a chart by its ID.

        Args:
            chart_id: The chart's ID.

        Returns:
            The chart response.

        Raises:
            HTTPException: If chart not found.
        """
        chart = await self.chart_repository.get_by_id(chart_id)

        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart not found",
            )

        return self._to_response(chart)

    async def refresh_chart(self, chart_id: str, user_id: str) -> ChartResponse:
        """
        Refresh a chart's entries from current poll results.

        Args:
            chart_id: The chart's ID.
            user_id: The ID of the requesting user.

        Returns:
            The updated chart response.

        Raises:
            HTTPException: If chart not found or user not authorized.
        """
        chart = await self._get_chart_with_auth(chart_id, user_id)

        # Aggregate results from all polls
        entries = await self._aggregate_poll_results(chart.poll_ids)

        # Store previous ranks for movement tracking
        previous_ranks = {e.item_id: e.rank for e in chart.entries}

        # Update entries with previous rank info
        for entry in entries:
            entry.previous_rank = previous_ranks.get(entry.item_id)

        # Update chart
        chart.entries = entries
        chart.updated_at = datetime.now(timezone.utc)

        updated_chart = await self.chart_repository.update(chart_id, chart)

        return self._to_response(updated_chart)

    async def delete_chart(self, chart_id: str, user_id: str) -> None:
        """
        Delete a chart.

        Args:
            chart_id: The chart's ID.
            user_id: The ID of the requesting user.

        Raises:
            HTTPException: If chart not found or user not authorized.
        """
        await self._get_chart_with_auth(chart_id, user_id)
        await self.chart_repository.delete(chart_id)

    async def list_charts(
        self,
        owner_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ChartResponse]:
        """
        List charts with optional owner filter.

        Args:
            owner_id: Optional owner ID to filter by.
            skip: Number of charts to skip.
            limit: Maximum number of charts to return.

        Returns:
            List of chart responses.
        """
        if owner_id:
            charts = await self.chart_repository.get_by_owner(owner_id, skip, limit)
        else:
            charts = await self.chart_repository.list(skip, limit)

        return [self._to_response(chart) for chart in charts]

    async def _aggregate_poll_results(
        self,
        poll_ids: list[str],
    ) -> list[ChartEntry]:
        """
        Aggregate results from multiple polls into chart entries.

        Uses combined Borda count across all polls.

        Args:
            poll_ids: List of poll IDs to aggregate.

        Returns:
            Sorted list of chart entries.
        """
        # TODO: Implement aggregation logic
        # 1. Get results from each poll
        # 2. Combine scores (normalize if needed)
        # 3. Sort by combined score
        # 4. Return ranked entries
        raise NotImplementedError

    async def _get_chart_with_auth(
        self,
        chart_id: str,
        user_id: str,
    ) -> ChartInDB:
        """Get a chart and verify the user is the owner."""
        chart = await self.chart_repository.get_by_id(chart_id)

        if not chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chart not found",
            )

        if chart.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this chart",
            )

        return chart

    def _to_response(self, chart: ChartInDB) -> ChartResponse:
        """Convert a chart database model to a response model."""
        return ChartResponse(
            id=chart.id,
            title=chart.title,
            description=chart.description,
            entries=chart.entries,
            poll_ids=chart.poll_ids,
            owner_id=chart.owner_id,
            created_at=chart.created_at,
            updated_at=chart.updated_at,
        )
