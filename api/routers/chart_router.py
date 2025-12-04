"""
Chart router - API endpoints for aggregated rankings.
"""

from fastapi import APIRouter, Depends, Query

from dependencies import get_chart_service, get_current_user
from models.auth import UserResponse
from models.charts import ChartCreate, ChartResponse
from services.chart_service import ChartService

router = APIRouter(prefix="/charts", tags=["Charts"])


@router.post("", status_code=201)
async def create_chart(
    chart_data: ChartCreate,
    current_user: UserResponse = Depends(get_current_user),
    chart_service: ChartService = Depends(get_chart_service),
) -> ChartResponse:
    """
    Create a new chart from poll results.

    A chart aggregates results from one or more polls into a combined ranking.

    - **title**: Chart title (1-200 characters)
    - **description**: Optional description
    - **poll_ids**: List of poll IDs to aggregate
    """
    return await chart_service.create_chart(chart_data, current_user.id)


@router.get("")
async def list_charts(
    owner_id: str | None = Query(None, description="Filter by owner ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum items to return"),
    chart_service: ChartService = Depends(get_chart_service),
) -> list[ChartResponse]:
    """
    List charts with optional filtering.

    Supports pagination and filtering by owner.
    """
    return await chart_service.list_charts(owner_id, skip, limit)


@router.get("/{chart_id}")
async def get_chart(
    chart_id: str,
    chart_service: ChartService = Depends(get_chart_service),
) -> ChartResponse:
    """
    Get a chart by its ID.

    Returns the chart with its current ranked entries.
    """
    return await chart_service.get_chart(chart_id)


@router.post("/{chart_id}/refresh")
async def refresh_chart(
    chart_id: str,
    current_user: UserResponse = Depends(get_current_user),
    chart_service: ChartService = Depends(get_chart_service),
) -> ChartResponse:
    """
    Refresh a chart's entries from current poll results.

    Recalculates rankings based on the latest poll data.
    Only the chart owner can refresh a chart.
    """
    return await chart_service.refresh_chart(chart_id, current_user.id)


@router.delete("/{chart_id}", status_code=204)
async def delete_chart(
    chart_id: str,
    current_user: UserResponse = Depends(get_current_user),
    chart_service: ChartService = Depends(get_chart_service),
) -> None:
    """
    Delete a chart.

    Only the chart owner can delete a chart.
    """
    await chart_service.delete_chart(chart_id, current_user.id)
