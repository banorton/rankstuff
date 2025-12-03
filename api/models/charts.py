"""
Pydantic models for charts (aggregated rankings).
"""

from datetime import datetime

from pydantic import BaseModel, Field


# --- Embedded Models ---

class ChartEntry(BaseModel):
    """Schema for a single entry in a chart."""

    rank: int
    item_id: str
    label: str
    score: float
    previous_rank: int | None = None  # For tracking movement


# --- Request Models ---

class ChartCreate(BaseModel):
    """Schema for chart creation request."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    poll_ids: list[str] = Field(..., min_length=1)  # Polls to aggregate


class ChartUpdate(BaseModel):
    """Schema for chart update request."""

    title: str | None = None
    description: str | None = None
    poll_ids: list[str] | None = None


# --- Response Models ---

class ChartResponse(BaseModel):
    """Schema for chart data in API responses."""

    id: str
    title: str
    description: str | None
    entries: list[ChartEntry]
    poll_ids: list[str]
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Database Models ---

class ChartInDB(BaseModel):
    """Schema for chart document stored in MongoDB."""

    id: str = Field(default=None, alias="_id")
    title: str
    description: str | None = None
    entries: list[ChartEntry] = []
    poll_ids: list[str]
    owner_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        populate_by_name = True
