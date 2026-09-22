"""
JWT generation and validation — HS256, 24-hour expiry, user_id claim.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


def generate_token(user_id: int) -> str:
    """Create a JWT with user_id claim and 24h expiry."""
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    payload = {
        "user_id": user_id,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def validate_token(token: str) -> dict:
    """Parse and verify a JWT. Returns the decoded payload or raises JWTError."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise JWTError("Missing user_id claim")
        return payload
    except JWTError:
        raise
