"""Master router — aggregates all route modules."""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.ai import router as ai_router
from app.api.cp import router as cp_router
from app.api.dev import router as dev_router
from app.api.ml import router as ml_router
from app.api.leaderboard import router as leaderboard_router
from app.api.resource import router as resource_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(ai_router)
api_router.include_router(cp_router)
api_router.include_router(dev_router)
api_router.include_router(ml_router)
api_router.include_router(leaderboard_router)
api_router.include_router(resource_router)
