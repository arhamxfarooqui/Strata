"""Leaderboard routes — /api/public/leaderboard with Redis cache-aside."""

import json
import time

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.cache.cache_aside import cache_aside_get, cache_aside_set, record_db_latency, metrics

router = APIRouter(prefix="/api/public", tags=["leaderboard"])


@router.get("/leaderboard")
async def get_overall_leaderboard(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"leaderboard:global:{page}:{limit}"

    # 1. Cache hit check
    cached = await cache_aside_get(cache_key)
    if cached is not None:
        return json.loads(cached)

    # 2. Cache miss — query DB
    offset = (page - 1) * limit
    db_start = time.monotonic()

    stmt = select(User).order_by(User.axios_rating.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    users = result.scalars().all()

    db_elapsed_ms = (time.monotonic() - db_start) * 1000
    record_db_latency(db_elapsed_ms)

    data = [u.to_dict() for u in users]

    # 3. Populate cache (5 minute TTL)
    await cache_aside_set(cache_key, json.dumps(data), ttl=300)

    return data


@router.get("/leaderboard/wing")
async def get_wing_leaderboard(
    wing: str = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"leaderboard:{wing.lower()}:{page}:{limit}"

    cached = await cache_aside_get(cache_key)
    if cached is not None:
        return json.loads(cached)

    offset = (page - 1) * limit
    db_start = time.monotonic()

    wing_lower = wing.lower()
    wing_map = {
        "cp": ("Competitive Programming", "codeforces_rating"),
        "dev": ("Web Development", "github_repos"),
        "web": ("Web Development", "github_repos"),
        "ml": ("Machine Learning", "axios_rating"),
    }

    wing_name, order_col = wing_map.get(wing_lower, (wing, "axios_rating"))
    filter_json = f'["{wing_name}"]'

    stmt = (
        select(User)
        .where(User.wings.op("@>")(filter_json))
        .order_by(text(f"{order_col} desc"))
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    users = result.scalars().all()

    db_elapsed_ms = (time.monotonic() - db_start) * 1000
    record_db_latency(db_elapsed_ms)

    data = [u.to_dict() for u in users]
    await cache_aside_set(cache_key, json.dumps(data), ttl=300)

    return data
