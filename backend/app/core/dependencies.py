from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db

# HTTPBearer thay OAuth2PasswordBearer — cleaner cho mobile apps
oauth2_scheme = HTTPBearer(auto_error=False)


# ─── Current User Dependency ────────────────────────────────────────────────────

async def get_current_user_id(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(oauth2_scheme)],
) -> uuid.UUID:
    """
    Extract và validate JWT token; return user UUID.
    Hỗ trợ cả Bearer Token (Mobile) và Cookies (Web).
    """
    token = None

    # 1. Ưu tiên Authorization Header
    if credentials:
        token = credentials.credentials
    
    # 2. Fallback về Cookie nếu Header thiếu (cho Web)
    if not token:
        token = request.cookies.get(settings.AUTH_COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Yêu cầu đăng nhập để tiếp tục."},
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise ValueError("Token không phải là access token")
        return uuid.UUID(payload["sub"])
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ─── Current Session ID Dependency ──────────────────────────────────────────────

async def get_current_session_id(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(oauth2_scheme)],
) -> uuid.UUID | None:
    """
    Extract session_id từ JWT payload (field 'sid').
    Hỗ trợ cả Bearer và Cookies.
    """
    token = None
    if credentials:
        token = credentials.credentials
    if not token:
        token = request.cookies.get(settings.AUTH_COOKIE_NAME)
    
    if not token:
        return None

    try:
        payload = decode_token(token)
        sid = payload.get("sid")
        return uuid.UUID(sid) if sid else None
    except Exception:
        return None


# ─── Role Check Dependency ────────────────────────────────────────────────────

class RequireRole:
    """
    Dependency to check if the current user has at least one of the allowed roles.
    Roles are extracted from the JWT payload ('roles' field).
    """
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = set(allowed_roles)

    async def __call__(
        self,
        request: Request,
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(oauth2_scheme)],
    ) -> uuid.UUID:
        token = None
        if credentials:
            token = credentials.credentials
        if not token:
            token = request.cookies.get(settings.AUTH_COOKIE_NAME)

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "UNAUTHORIZED", "message": "Yêu cầu đăng nhập để tiếp tục."},
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                raise ValueError("Token không phải là access token")
            
            user_roles = payload.get("roles", [])
            if not isinstance(user_roles, list):
                user_roles = []
                
            # If user has 'admin' role, they bypass all checks
            if "admin" in user_roles:
                return uuid.UUID(payload["sub"])
                
            # Check intersection
            if not self.allowed_roles.intersection(set(user_roles)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"code": "FORBIDDEN", "message": "Bạn không có quyền truy cập tài nguyên này."},
                )
                
            return uuid.UUID(payload["sub"])
        except (ValueError, KeyError) as exc:
            if isinstance(exc, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "UNAUTHORIZED", "message": str(exc)},
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc


# ─── Type Aliases ─────────────────────────────────────────────────────────────

CurrentUserID = Annotated[uuid.UUID, Depends(get_current_user_id)]
CurrentSessionID = Annotated[uuid.UUID | None, Depends(get_current_session_id)]
DBSession = Annotated[AsyncSession, Depends(get_db)]
