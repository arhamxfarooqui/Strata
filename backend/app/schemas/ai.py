"""Pydantic schemas for AI endpoints."""

from pydantic import BaseModel


class CodeSenseiInput(BaseModel):
    message: str
    wing: str = ""


class AnalyzeInput(BaseModel):
    prompt: str
    domain: str | None = None  # Optional user-tagged domain for routing accuracy


class SubTaskResult(BaseModel):
    description: str
    target_wing: str
    action_type: str
    status: str
    result: str
