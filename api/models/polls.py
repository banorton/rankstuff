"""
Pydantic models for polls and voting.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PollStatus(str, Enum):
    """Poll lifecycle status."""

    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"


# --- Embedded Models ---

class PollOption(BaseModel):
    """Schema for a single poll option."""

    id: str
    label: str
    description: str | None = None


class RankedChoice(BaseModel):
    """Schema for a ranked choice in a vote."""

    option_id: str
    rank: int = Field(..., ge=1)


# --- Request Models ---

class PollCreate(BaseModel):
    """Schema for poll creation request."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    options: list[PollOption] = Field(..., min_length=2)
    allow_multiple_votes: bool = False
    closes_at: datetime | None = None


class PollUpdate(BaseModel):
    """Schema for poll update request."""

    title: str | None = None
    description: str | None = None
    options: list[PollOption] | None = None
    status: PollStatus | None = None
    closes_at: datetime | None = None


class VoteCreate(BaseModel):
    """Schema for submitting a ranked vote."""

    poll_id: str
    rankings: list[RankedChoice] = Field(..., min_length=1)


# --- Response Models ---

class PollResponse(BaseModel):
    """Schema for poll data in API responses."""

    id: str
    title: str
    description: str | None
    options: list[PollOption]
    status: PollStatus
    owner_id: str
    created_at: datetime
    closes_at: datetime | None
    vote_count: int = 0

    class Config:
        from_attributes = True


class VoteResponse(BaseModel):
    """Schema for vote confirmation response."""

    id: str
    poll_id: str
    user_id: str
    submitted_at: datetime

    class Config:
        from_attributes = True


class OptionResult(BaseModel):
    """Schema for a single option's result in poll results."""

    option_id: str
    label: str
    score: float  # Borda count score
    rank: int


class PollResults(BaseModel):
    """Schema for poll results using Borda count."""

    poll_id: str
    title: str
    total_votes: int
    results: list[OptionResult]
    calculated_at: datetime


# --- Database Models ---

class PollInDB(BaseModel):
    """Schema for poll document stored in MongoDB."""

    id: str = Field(default=None, alias="_id")
    title: str
    description: str | None = None
    options: list[PollOption]
    status: PollStatus = PollStatus.DRAFT
    owner_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closes_at: datetime | None = None

    class Config:
        from_attributes = True
        populate_by_name = True


class VoteInDB(BaseModel):
    """Schema for vote document stored in MongoDB."""

    id: str = Field(default=None, alias="_id")
    poll_id: str
    user_id: str
    rankings: list[RankedChoice]
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        populate_by_name = True
