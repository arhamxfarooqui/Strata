"""CP Wing routes — /api/wings/cp/*."""

import json
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.database import get_db
from app.middleware.auth import get_current_user_id
from app.models.user import User
from app.models.upsolve_task import UpsolveTask
from app.schemas.cp import UpdateStatusInput, MockContestInput
from app.tasks.cf_sync import sync_user_cf

router = APIRouter(prefix="/api/wings/cp", tags=["cp"])


@router.get("/upsolves")
async def get_upsolve_queue(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(UpsolveTask).where(
        UpsolveTask.user_id == user_id, UpsolveTask.status == "pending"
    )
    result = await db.execute(stmt)
    tasks = result.scalars().all()
    return [t.to_dict() for t in tasks]


@router.post("/upsolves/{task_id}/status")
async def update_upsolve_status(
    task_id: int,
    input: UpdateStatusInput,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        update(UpsolveTask)
        .where(UpsolveTask.id == task_id, UpsolveTask.user_id == user_id)
        .values(status=input.status)
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found or unauthorized")
    return {"message": "Status updated successfully"}


@router.post("/sync", status_code=202)
async def sync_upsolves(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.codeforces_handle:
        raise HTTPException(status_code=400, detail="Codeforces handle not linked")

    # Dispatch async Celery task — returns 202 immediately
    sync_user_cf.delay(user_id, user.codeforces_handle)
    return {"message": "Sync queued. Problems will appear shortly."}


@router.post("/mock")
async def generate_mock_contest(
    input: MockContestInput,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch solved problems
    solved_problems: set[str] = set()
    if user.codeforces_handle:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    f"https://codeforces.com/api/user.status?handle={user.codeforces_handle}"
                )
                data = resp.json()
                if data.get("status") == "OK":
                    for sub in data.get("result", []):
                        if sub.get("verdict") == "OK":
                            p = sub.get("problem", {})
                            solved_problems.add(f"{p.get('contestId', 0)}{p.get('index', '')}")
        except Exception:
            pass

    # Fetch global problemset
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get("https://codeforces.com/api/problemset.problems")
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch Codeforces problemset")
        ps = resp.json()

    pool = []
    for p in ps.get("result", {}).get("problems", []):
        pid = f"{p.get('contestId', 0)}{p.get('index', '')}"
        rating = p.get("rating", 0)
        contest_id = p.get("contestId", 0)
        if (
            contest_id >= 2050
            and pid not in solved_problems
            and rating >= input.rating - 200
            and rating <= input.rating + 200
        ):
            pool.append(p)

    if len(pool) < 4:
        raise HTTPException(
            status_code=404,
            detail="Not enough fresh unsolved problems found for this rating range",
        )

    random.shuffle(pool)
    return {"target_rating": input.rating, "problems": pool[:4]}
