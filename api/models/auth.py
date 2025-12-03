"""
Pydantic models for authentication and user management.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# --- Request Models ---

class UserCreate(BaseModel):
    """Schema for user registration request."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Schema for user login request."""

    email: EmailStr
    password: str


# --- Response Models ---

class UserResponse(BaseModel):
    """Schema for user data in API responses."""

    id: str
    email: EmailStr
    username: str
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for decoded JWT token payload."""

    sub: str  # User ID
    exp: datetime


# --- Database Models ---

class UserInDB(BaseModel):
    """Schema for user document stored in MongoDB."""

    id: str = Field(default=None, alias="_id")
   email: EmailStr
    username: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Config:
        from_attributes = True
        populate_by_name = True
