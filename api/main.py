"""
FastAPI application entry point for rankstuff.io.

Run with: cd api && uv run uvicorn main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import close_database_connection, connect_to_database
from routers import auth_router, chart_router, poll_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    """
    await connect_to_database()
    yield
    await close_database_connection()


app = FastAPI(
    title=settings.app_name,
    description="A ranking and polling API using Borda count",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(poll_router)
app.include_router(chart_router)


@app.get("/", tags=["Health"])
async def root() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "app": settings.app_name}


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0",
    }
