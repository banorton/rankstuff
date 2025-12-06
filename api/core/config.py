"""
Application configuration using Pydantic Settings.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "rankstuff.io"
    debug: bool = False

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "rankstuff"

    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:4200"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
