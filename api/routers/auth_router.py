"""
Authentication router - API endpoints for auth.
"""

from fastapi import APIRouter, Depends

from dependencies import get_auth_service, get_current_user
from models.auth import Token, UserCreate, UserLogin, UserResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=201)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **username**: Username (3-50 characters, must be unique)
    - **password**: Password (minimum 8 characters)
    """
    return await auth_service.register(user_data)


@router.post("/login")
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """
    Authenticate and receive a JWT access token.

    - **email**: Registered email address
    - **password**: Account password
    """
    return await auth_service.login(credentials.email, credentials.password)


@router.get("/me")
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """
    Get the currently authenticated user's profile.

    Requires a valid JWT token in the Authorization header.
    """
    return current_user
