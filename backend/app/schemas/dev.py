"""Pydantic schemas for Dev wing endpoints."""

from pydantic import BaseModel


class PRReviewInput(BaseModel):
    pr_url: str


class ResumeBulletsInput(BaseModel):
    repo_url: str
