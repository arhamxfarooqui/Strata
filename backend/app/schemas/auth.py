"""Pydantic schemas for auth endpoints."""

from pydantic import BaseModel, EmailStr


class RegisterInput(BaseModel):
    name: str
    email: EmailStr
    password: str
    college_id: str
    wings: list[str] = []
    codeforces_handle: str
    codechef_handle: str = ""
    github_handle: str
    kaggle_handle: str = ""
    ctf_handle: str = ""


class LoginInput(BaseModel):
    email: EmailStr
    password: str
