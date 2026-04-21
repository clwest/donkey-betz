"""
Token authentication dependency for OBS Bridge.
"""

from fastapi import Header, HTTPException

from config import settings
from schemas import ErrorResponse, ErrorDetail


async def require_token(authorization: str | None = Header(default=None)) -> str:
    """Validate Bearer token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="UNAUTHORIZED",
                    message="Missing or malformed Authorization header",
                    detail="Expected: Authorization: Bearer <token>",
                )
            ).model_dump(),
        )

    token = authorization[7:]
    if token != settings.OBS_BRIDGE_TOKEN:
        raise HTTPException(
            status_code=401,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="UNAUTHORIZED",
                    message="Invalid token",
                )
            ).model_dump(),
        )

    return token
