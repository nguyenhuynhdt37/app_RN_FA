"""
api/v1/sessions.py — Session Management Router
===============================================
Endpoints:
  GET    /auth/sessions              → Xem danh sách thiết bị đang đăng nhập
  DELETE /auth/sessions/{session_id} → Đăng xuất 1 thiết bị cụ thể
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Response, status, HTTPException

from app.core.dependencies import CurrentUserID, CurrentSessionID, DBSession
from app.core.auth_utils import clear_auth_cookies
from app.core.logging import logger
from app.schemas.session import SessionListResponse
from app.services.session import SessionService

router = APIRouter(prefix="/auth/sessions", tags=["Sessions"])


@router.get(
    "",
    response_model=SessionListResponse,
    summary="Danh sách thiết bị đang đăng nhập",
)
async def list_sessions(
    current_user_id: CurrentUserID,
    current_session_id: CurrentSessionID,
    db: DBSession,
) -> SessionListResponse:
    """
    Trả về tất cả active sessions của user hiện tại.
    Session đang gọi request sẽ có `is_current: true`.

    Dùng để hiện thị "Thiết bị đã đăng nhập" như Zalo/Google.
    """
    try:
        service = SessionService(db)
        return await service.list_active_sessions(
            user_id=current_user_id,
            current_session_id=current_session_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in list_sessions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Đăng xuất 1 thiết bị cụ thể",
)
async def revoke_session(
    session_id: uuid.UUID,
    current_user_id: CurrentUserID,
    current_session_id: CurrentSessionID,
    response: Response,
    db: DBSession,
) -> None:
    """
    Revoke (đăng xuất) 1 session theo ID.
    """
    try:
        service = SessionService(db)
        await service.revoke_session(
            session_id=session_id,
            user_id=current_user_id,
        )

        # Nếu user tự đá chính mình (hoặc logout session hiện tại) -> xóa cookies
        if session_id == current_session_id:
            clear_auth_cookies(response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in revoke_session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
