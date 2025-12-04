"""
Authentication service - Business logic for user auth.
"""

from fastapi import HTTPException, status

from core.security import create_access_token, hash_password, verify_password
from models.auth import Token, UserCreate, UserInDB, UserResponse
from repositories.user_repository import UserRepository


class AuthService:
    """Service for authentication and user management."""

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the auth service.

        Args:
            user_repository: Repository for user data access.
        """
        self.user_repository = user_repository

    async def register(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user.

        Args:
            user_data: The registration data.

        Returns:
            The created user response.

        Raises:
            HTTPException: If email or username already exists.
        """
        # Check if email already exists
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Check if username already exists
        existing_user = await self.user_repository.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        # Create user with hashed password
        user_in_db = UserInDB(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hash_password(user_data.password),
        )

        created_user = await self.user_repository.create(user_in_db)

        return UserResponse(
            id=created_user.id,
            email=created_user.email,
            username=created_user.username,
            created_at=created_user.created_at,
            is_active=created_user.is_active,
        )

    async def login(self, identifier: str, password: str) -> Token:
        """
        Authenticate a user and return a JWT token.

        Args:
            identifier: The user's email or username.
            password: The user's password.

        Returns:
            A JWT token response.

        Raises:
            HTTPException: If credentials are invalid.
        """
        # Try email first, then username
        user = await self.user_repository.get_by_email(identifier)
        if not user:
            user = await self.user_repository.get_by_username(identifier)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        access_token = create_access_token(data={"sub": user.id})

        return Token(access_token=access_token)

    async def get_current_user(self, user_id: str) -> UserResponse:
        """
        Get the current authenticated user.

        Args:
            user_id: The user's ID from the JWT token.

        Returns:
            The user response.

        Raises:
            HTTPException: If user not found.
        """
        user = await self.user_repository.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            created_at=user.created_at,
            is_active=user.is_active,
        )
