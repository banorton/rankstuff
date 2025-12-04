"""
Chart router - API endpoints for visualization data.
"""

from fastapi import APIRouter, Depends

from dependencies import get_current_user
from models.auth import UserResponse
from models.charts import AlgorithmComparisonChart, VoteDistributionChart
from services.chart_service import ChartService

router = APIRouter(prefix="/charts", tags=["Charts"])


def get_chart_service() -> ChartService:
    """Dependency to get chart service."""
    return ChartService()


@router.get("/algorithm-comparison")
async def get_algorithm_comparison(
    current_user: UserResponse = Depends(get_current_user),
    chart_service: ChartService = Depends(get_chart_service),
) -> AlgorithmComparisonChart:
    """
    Get algorithm comparison chart data.

    Shows how the same votes produce different winners under
    Plurality, Borda Count, and Instant Runoff Voting.
    """
    return chart_service.get_algorithm_comparison()


@router.get("/vote-distribution")
async def get_vote_distribution(
    current_user: UserResponse = Depends(get_current_user),
    chart_service: ChartService = Depends(get_chart_service),
) -> VoteDistributionChart:
    """
    Get vote distribution chart data.

    Shows how voters distributed their rankings across options.
    """
    return chart_service.get_vote_distribution()
