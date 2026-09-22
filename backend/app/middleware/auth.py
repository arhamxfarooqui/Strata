"""
JWT auth dependency for FastAPI — equivalent of Gin's AuthMiddleware.
Extracts Bearer token, validates it, returns the user_id.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from jose import JWTError

from app.utils.jwt import validate_token

bearer_scheme = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:
    """
    FastAPI dependency that extracts and validates a JWT Bearer token.
    Returns the authenticated user_id or raises 401.

    Usage:
        @router.get("/protected")
        async def endpoint(user_id: int = Depends(get_current_user_id)):
            ...
    """
    try:
        payload = validate_token(credentials.credentials)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return int(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
