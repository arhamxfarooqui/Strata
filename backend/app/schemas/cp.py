"""Pydantic schemas for CP wing endpoints."""

from pydantic import BaseModel


class UpdateStatusInput(BaseModel):
    status: str  # "solved" or "skipped"


class MockContestInput(BaseModel):
    rating: int
