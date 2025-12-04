"""
Dependency injection - FastAPI dependencies for services and auth.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_database
from core.security import verify_token
from models.auth import UserResponse
from repositories.chart_repository import ChartRepository
from repositories.poll_repository import PollRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.chart_service import ChartService
from services.poll_service import PollService

# Security scheme for JWT bearer token
security = HTTPBearer()


# --- Repository Dependencies ---


async def get_user_repository(
    database: AsyncIOMotorDatabase = Depends(get_database),
) -> UserRepository:
    """Get the user repository instance."""
    return UserRepository(database)


async def get_poll_repository(
    database: AsyncIOMotorDatabase = Depends(get_database),
) -> PollRepository:
    """Get the poll repository instance."""
    return PollRepository(database)


async def get_chart_repository(
    database: AsyncIOMotorDatabase = Depends(get_database),
) -> ChartRepository:
    """Get the chart repository instance."""
    return ChartRepository(database)


# --- Service Dependencies ---


async def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Get the auth service instance."""
    return AuthService(user_repository)


async def get_poll_service(
    poll_repository: PollRepository = Depends(get_poll_repository),
) -> PollService:
    """Get the poll service instance."""
    return PollService(poll_repository)


async def get_chart_service(
    chart_repository: ChartRepository = Depends(get_chart_repository),
    poll_repository: PollRepository = Depends(get_poll_repository),
) -> ChartService:
    """Get the chart service instance."""
    return ChartService(chart_repository, poll_repository)


# --- Authentication Dependencies ---


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """
    Validate JWT token and return the current user.

    This dependency should be used on protected endpoints.

    Raises:
        HTTPException: If token is invalid or user not found.
    """
    token = credentials.credentials

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await auth_service.get_current_user(user_id)


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        HTTPBearer(auto_error=False)
    ),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse | None:
    """
    Optionally validate JWT token and return the current user.

    Returns None if no token is provided. Use this for endpoints
    that have different behavior for authenticated vs anonymous users.
    """
    if credentials is None:
        return None

    token = credentials.credentials

    payload = verify_token(token)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    try:
        return await auth_service.get_current_user(user_id)
    except HTTPException:
        return None
