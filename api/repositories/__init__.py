"""
Repository layer - Abstract database access.
"""

from .base import BaseRepository
from .user_repository import UserRepository
from .poll_repository import PollRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "PollRepository",
]
