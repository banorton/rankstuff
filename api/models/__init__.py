"""
Pydantic models for request/response schemas and database documents.
"""

from .auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserInDB,
    Token,
    TokenPayload,
)
from .polls import (
    PollOption,
    PollCreate,
    PollResponse,
    PollInDB,
    VoteCreate,
    VoteResponse,
    VoteInDB,
    PollResults,
)
from .charts import (
    AlgorithmComparisonChart,
    VoteDistributionChart,
)

__all__ = [
    # Auth
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserInDB",
    "Token",
    "TokenPayload",
    # Polls
    "PollOption",
    "PollCreate",
    "PollResponse",
    "PollInDB",
    "VoteCreate",
    "VoteResponse",
    "VoteInDB",
    "PollResults",
    # Charts
    "AlgorithmComparisonChart",
    "VoteDistributionChart",
]
