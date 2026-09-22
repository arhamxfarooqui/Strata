"""Auth routes — /api/auth/register and /api/auth/login."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt

from app.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterInput, LoginInput
from app.utils.jwt import generate_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
async def register(input: RegisterInput, db: AsyncSession = Depends(get_db)):
    # Go's bcrypt silently truncates passwords at 72 bytes. Python's bcrypt throws an error.
    # We truncate it here to match the old backend's exact behavior.
    password_truncated = input.password[:72]
    pwd_bytes = password_truncated.encode('utf-8')
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode('utf-8')
    user = User(
        name=input.name,
        email=input.email,
        password=hashed,
        college_id=input.college_id,
        wings=input.wings,
        codeforces_handle=input.codeforces_handle,
        codechef_handle=input.codechef_handle,
        github_handle=input.github_handle,
        kaggle_handle=input.kaggle_handle,
        ctf_handle=input.ctf_handle,
    )
    db.add(user)
    try:
        await db.flush()
        await db.commit()
    except Exception as e:
        import traceback
        with open("error.log", "w") as f:
            f.write(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Registration successful"}


@router.post("/login")
async def login(input: LoginInput, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == input.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    pwd_bytes = input.password[:72].encode('utf-8')
    hash_bytes = user.password.encode('utf-8')
    if not bcrypt.checkpw(pwd_bytes, hash_bytes):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = generate_token(user.id)
    return {"token": token, "user": user.to_dict()}
