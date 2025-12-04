"""
Poll service - Business logic for polls and voting.
"""

from datetime import datetime, timezone

from fastapi import HTTPException, status

from models.polls import (
    OptionResult,
    PollCreate,
    PollInDB,
    PollResponse,
    PollResults,
    PollStatus,
    VoteCreate,
    VoteInDB,
    VoteResponse,
)
from repositories.poll_repository import PollRepository


class PollService:
    """Service for poll and voting operations."""

    def __init__(self, poll_repository: PollRepository):
        """
        Initialize the poll service.

        Args:
            poll_repository: Repository for poll data access.
        """
        self.poll_repository = poll_repository

    async def create_poll(
        self,
        poll_data: PollCreate,
        owner_id: str,
    ) -> PollResponse:
        """
        Create a new poll.

        Args:
            poll_data: The poll creation data.
            owner_id: The ID of the poll owner.

        Returns:
            The created poll response.
        """
        poll_in_db = PollInDB(
            title=poll_data.title,
            description=poll_data.description,
            options=poll_data.options,
            status=PollStatus.DRAFT,
            owner_id=owner_id,
            closes_at=poll_data.closes_at,
        )

        created_poll = await self.poll_repository.create(poll_in_db)

        return self._to_response(created_poll, vote_count=0)

    async def get_poll(self, poll_id: str) -> PollResponse:
        """
        Get a poll by its ID.

        Args:
            poll_id: The poll's ID.

        Returns:
            The poll response.

        Raises:
            HTTPException: If poll not found.
        """
        poll = await self.poll_repository.get_by_id(poll_id)

        if not poll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Poll not found",
            )

        vote_count = await self.poll_repository.count_votes(poll_id)

        return self._to_response(poll, vote_count)

    async def open_poll(self, poll_id: str, user_id: str) -> PollResponse:
        """
        Open a poll for voting.

        Args:
            poll_id: The poll's ID.
            user_id: The ID of the requesting user.

        Returns:
            The updated poll response.

        Raises:
            HTTPException: If poll not found or user not authorized.
        """
        poll = await self._get_poll_with_auth(poll_id, user_id)

        if poll.status != PollStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft polls can be opened",
            )

        updated_poll = await self.poll_repository.update_status(
            poll_id,
            PollStatus.OPEN,
        )

        return self._to_response(updated_poll, vote_count=0)

    async def close_poll(self, poll_id: str, user_id: str) -> PollResponse:
        """
        Close a poll to stop accepting votes.

        Args:
            poll_id: The poll's ID.
            user_id: The ID of the requesting user.

        Returns:
            The updated poll response.

        Raises:
            HTTPException: If poll not found or user not authorized.
        """
        poll = await self._get_poll_with_auth(poll_id, user_id)

        if poll.status != PollStatus.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only open polls can be closed",
            )

        updated_poll = await self.poll_repository.update_status(
            poll_id,
            PollStatus.CLOSED,
        )

        vote_count = await self.poll_repository.count_votes(poll_id)

        return self._to_response(updated_poll, vote_count)

    async def submit_vote(
        self,
        vote_data: VoteCreate,
        user_id: str,
    ) -> VoteResponse:
        """
        Submit a ranked vote for a poll.

        Args:
            vote_data: The vote data with rankings.
            user_id: The ID of the voter.

        Returns:
            The vote confirmation response.

        Raises:
            HTTPException: If poll not open or user already voted.
        """
        poll = await self.poll_repository.get_by_id(vote_data.poll_id)

        if not poll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Poll not found",
            )

        if poll.status != PollStatus.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Poll is not open for voting",
            )

        # Check if user already voted
        existing_vote = await self.poll_repository.get_vote(
            vote_data.poll_id,
            user_id,
        )

        if existing_vote:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already voted in this poll",
            )

        # Validate that all ranked options exist in the poll
        poll_option_ids = {opt.id for opt in poll.options}
        for ranking in vote_data.rankings:
            if ranking.option_id not in poll_option_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid option ID: {ranking.option_id}",
                )

        vote_in_db = VoteInDB(
            poll_id=vote_data.poll_id,
            user_id=user_id,
            rankings=vote_data.rankings,
        )

        created_vote = await self.poll_repository.create_vote(vote_in_db)

        return VoteResponse(
            id=created_vote.id,
            poll_id=created_vote.poll_id,
            user_id=created_vote.user_id,
            submitted_at=created_vote.submitted_at,
        )

    async def get_results(self, poll_id: str) -> PollResults:
        """
        Calculate and return poll results using Borda count.

        The Borda count assigns points based on ranking position:
        - 1st place: n points (where n = number of options)
        - 2nd place: n-1 points
        - etc.

        Args:
            poll_id: The poll's ID.

        Returns:
            The poll results with ranked options.

        Raises:
            HTTPException: If poll not found or not closed.
        """
        poll = await self.poll_repository.get_by_id(poll_id)

        if not poll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Poll not found",
            )

        votes = await self.poll_repository.get_votes_for_poll(poll_id)

        # Calculate Borda count scores
        scores = self._calculate_borda_count(poll, votes)

        # Build sorted results
        option_labels = {opt.id: opt.label for opt in poll.options}
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        results = [
            OptionResult(
                option_id=option_id,
                label=option_labels[option_id],
                score=score,
                rank=idx + 1,
            )
            for idx, (option_id, score) in enumerate(sorted_results)
        ]

        return PollResults(
            poll_id=poll_id,
            title=poll.title,
            total_votes=len(votes),
            results=results,
            calculated_at=datetime.now(timezone.utc),
        )

    def _calculate_borda_count(
        self,
        poll: PollInDB,
        votes: list[VoteInDB],
    ) -> dict[str, float]:
        """
        Calculate Borda count scores for poll options.

        Args:
            poll: The poll with options.
            votes: List of votes with rankings.

        Returns:
            Dictionary mapping option IDs to their scores.
        """
        n_options = len(poll.options)
        scores: dict[str, float] = {opt.id: 0.0 for opt in poll.options}

        for vote in votes:
            for ranking in vote.rankings:
                # Borda count: n - rank + 1 points
                points = n_options - ranking.rank + 1
                scores[ranking.option_id] += points

        return scores

    async def _get_poll_with_auth(
        self,
        poll_id: str,
        user_id: str,
    ) -> PollInDB:
        """Get a poll and verify the user is the owner."""
        poll = await self.poll_repository.get_by_id(poll_id)

        if not poll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Poll not found",
            )

        if poll.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this poll",
            )

        return poll

    def _to_response(self, poll: PollInDB, vote_count: int) -> PollResponse:
        """Convert a poll database model to a response model."""
        return PollResponse(
            id=poll.id,
            title=poll.title,
            description=poll.description,
            options=poll.options,
            status=poll.status,
            owner_id=poll.owner_id,
            created_at=poll.created_at,
            closes_at=poll.closes_at,
            vote_count=vote_count,
        )
