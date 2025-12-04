"""
Poll router - API endpoints for polls and voting.
"""

from fastapi import APIRouter, Depends

from dependencies import get_current_user, get_poll_service
from models.auth import UserResponse
from models.polls import (
    PollCreate,
    PollResponse,
    PollResults,
    VoteCreate,
    VoteResponse,
)
from services.poll_service import PollService

router = APIRouter(prefix="/polls", tags=["Polls"])


@router.post("", status_code=201)
async def create_poll(
    poll_data: PollCreate,
    current_user: UserResponse = Depends(get_current_user),
    poll_service: PollService = Depends(get_poll_service),
) -> PollResponse:
    """
    Create a new poll.

    The poll is created in DRAFT status. Use the open endpoint to start accepting votes.

    - **title**: Poll title (1-200 characters)
    - **description**: Optional description
    - **options**: List of options (minimum 2)
    - **closes_at**: Optional automatic close datetime
    """
    return await poll_service.create_poll(poll_data, current_user.id)


@router.get("/{poll_id}")
async def get_poll(
    poll_id: str,
    poll_service: PollService = Depends(get_poll_service),
) -> PollResponse:
    """
    Get a poll by its ID.

    Returns the poll details including current vote count.
    """
    return await poll_service.get_poll(poll_id)


@router.post("/{poll_id}/open")
async def open_poll(
    poll_id: str,
    current_user: UserResponse = Depends(get_current_user),
    poll_service: PollService = Depends(get_poll_service),
) -> PollResponse:
    """
    Open a poll for voting.

    Only the poll owner can open a poll. The poll must be in DRAFT status.
    """
    return await poll_service.open_poll(poll_id, current_user.id)


@router.post("/{poll_id}/close")
async def close_poll(
    poll_id: str,
    current_user: UserResponse = Depends(get_current_user),
    poll_service: PollService = Depends(get_poll_service),
) -> PollResponse:
    """
    Close a poll to stop accepting votes.

    Only the poll owner can close a poll. The poll must be in OPEN status.
    """
    return await poll_service.close_poll(poll_id, current_user.id)


@router.post("/{poll_id}/vote", status_code=201)
async def submit_vote(
    poll_id: str,
    vote_data: VoteCreate,
    current_user: UserResponse = Depends(get_current_user),
    poll_service: PollService = Depends(get_poll_service),
) -> VoteResponse:
    """
    Submit a ranked vote for a poll.

    Rank your preferred options from 1 (most preferred) to n.
    Each user can only vote once per poll.

    - **rankings**: List of option IDs with their ranks
    """
    # Ensure poll_id in path matches vote data
    vote_data.poll_id = poll_id
    return await poll_service.submit_vote(vote_data, current_user.id)


@router.get("/{poll_id}/results")
async def get_results(
    poll_id: str,
    poll_service: PollService = Depends(get_poll_service),
) -> PollResults:
    """
    Get the poll results calculated using Borda count.

    Results show each option's score and final ranking.
    """
    return await poll_service.get_results(poll_id)
