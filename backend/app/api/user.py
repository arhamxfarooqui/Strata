"""User routes — /api/user/profile and /api/user/refresh."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.models.user import User
from app.services.codeforces import fetch_codeforces_rating, fetch_codeforces_solved
from app.services.github_service import fetch_github_repos_count
from app.cache.invalidation import invalidate_leaderboard_cache

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/profile")
async def get_profile(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user.to_dict()}


@router.post("/refresh")
async def refresh_stats(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    warnings = []

    if user.codeforces_handle:
        try:
            user.codeforces_rating = await fetch_codeforces_rating(user.codeforces_handle)
        except Exception as e:
            warnings.append(f"Codeforces Rating: {e}")

        try:
            user.total_solved = await fetch_codeforces_solved(user.codeforces_handle)
        except Exception as e:
            warnings.append(f"Codeforces Solved: {e}")

    if user.github_handle:
        try:
            user.github_repos = await fetch_github_repos_count(user.github_handle)
        except Exception as e:
            warnings.append(f"GitHub: {e}")

    await db.flush()

    # Invalidate leaderboard cache since ratings may have changed
    await invalidate_leaderboard_cache()

    return {"message": "Stats sync completed", "user": user.to_dict(), "warnings": warnings}
