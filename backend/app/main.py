"""
Strata — FastAPI application entry point.
Replaces the Go/Gin main.go bootstrap sequence.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.cache.redis_client import get_redis, close_redis
from app.cache.cache_aside import metrics as cache_metrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle events."""
    # --- Startup ---
    logger.info("Strata starting up...")

    # Initialize Redis connection
    redis = await get_redis()
    if redis:
        logger.info("Redis connected successfully")
    else:
        logger.warning("Redis unavailable — caching disabled")

    logger.info("Strata ready on port 8081")

    yield

    # --- Shutdown ---
    logger.info("Strata shutting down...")
    logger.info("Cache metrics: %s", cache_metrics.to_dict())
    await close_redis()
    logger.info("Strata shutdown complete")


app = FastAPI(
    title="Strata",
    description="AI-powered tutoring platform for competitive programmers",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins to match the Go backend behavior
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

# Mount all API routes
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "strata"}


@app.get("/api/metrics/cache")
async def get_cache_metrics():
    """Expose cache-aside instrumentation metrics."""
    return cache_metrics.to_dict()
