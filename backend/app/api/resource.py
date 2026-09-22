"""Resource routes — /api/public/resources."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.resource import Resource

router = APIRouter(prefix="/api/public", tags=["resources"])


@router.get("/resources")
async def get_resources(
    subject: str = Query("", alias="subject"),
    year: str = Query("", alias="year"),
    wing: str = Query("", alias="wing"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Resource)
    if subject:
        stmt = stmt.where(Resource.subject == subject)
    if year:
        stmt = stmt.where(Resource.year == int(year))
    if wing:
        stmt = stmt.where(Resource.wing_id == wing)

    result = await db.execute(stmt)
    resources = result.scalars().all()
    return [r.to_dict() for r in resources]


@router.post("/resources")
async def create_resource(
    resource_data: dict,
    db: AsyncSession = Depends(get_db),
):
    resource = Resource(
        title=resource_data.get("title", ""),
        description=resource_data.get("description", ""),
        link=resource_data.get("link", ""),
        type=resource_data.get("type", ""),
        year=resource_data.get("year", 0),
        subject=resource_data.get("subject", ""),
        wing_id=resource_data.get("wing_id", ""),
        submitted_by_id=resource_data.get("submitted_by_id", 0),
        upvotes=resource_data.get("upvotes", 0),
        difficulty_level=resource_data.get("difficulty_level", ""),
    )
    db.add(resource)
    await db.flush()
    return resource.to_dict()
