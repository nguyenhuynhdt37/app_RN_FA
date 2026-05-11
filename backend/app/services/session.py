"""
services/session.py — Session Management Service
=================================================
Quản lý sessions đa thiết bị:
  - List active sessions của user (với is_current flag)
  - Revoke 1 session cụ thể (với IDOR protection)
  - Cleanup expired/revoked sessions (dành cho cron job)

Single Responsibility: chỉ xử lý session CRUD, không xử lý auth logic.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.database import Sessions
from app.schemas.session import SessionListResponse, SessionResponse


class SessionService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ─── List Active Sessions ─────────────────────────────────────────────────

    async def list_active_sessions(
        self,
        user_id: uuid.UUID,
        current_session_id: uuid.UUID | None = None,
    ) -> SessionListResponse:
        """
        Trả về tất cả sessions chưa revoked và chưa expired của user.
        Đánh dấu is_current=True cho session đang gọi request.
        """
        try:
            stmt = (
                select(Sessions)
                .where(
                    Sessions.user_id == user_id,
                    Sessions.revoked_at.is_(None),
                    Sessions.expires_at > datetime.now(timezone.utc),
                )
                .order_by(Sessions.last_used_at.desc())
            )
            result = await self._db.execute(stmt)
            sessions = result.scalars().all()

            response_items = [
                SessionResponse(
                    id=s.id,
                    device_type=s.device_type.value if hasattr(s.device_type, "value") else s.device_type,
                    device_name=s.device_name,
                    ip_address=str(s.ip_address) if s.ip_address else None,
                    user_agent=s.user_agent,
                    last_used_at=s.last_used_at,
                    created_at=s.created_at,
                    is_current=(s.id == current_session_id),
                )
                for s in sessions
            ]

            return SessionListResponse(sessions=response_items, total=len(response_items))
        except Exception as e:
            logger.error(f"Error in list_active_sessions: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error fetching active sessions")

    # ─── Revoke Session ───────────────────────────────────────────────────────

    async def revoke_session(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """
        Revoke 1 session cụ thể.
        IDOR protection: chỉ cho phép revoke session thuộc về user_id.
        """
        try:
            stmt = select(Sessions).where(
                Sessions.id == session_id,
                Sessions.user_id == user_id,   # ← ngăn user revoke session người khác
                Sessions.revoked_at.is_(None),
            )
            result = await self._db.execute(stmt)
            session = result.scalar_one_or_none()

            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"code": "SESSION_NOT_FOUND", "message": "Session không tồn tại hoặc đã bị revoke."},
                )

            await self._db.execute(
                update(Sessions)
                .where(Sessions.id == session_id)
                .values(revoked_at=datetime.now(timezone.utc))
            )
            await self._db.commit()
            logger.info("session.revoked", session_id=str(session_id), user_id=str(user_id))
        except HTTPException:
            await self._db.rollback()
            raise
        except Exception as e:
            await self._db.rollback()
            logger.error(f"Error in revoke_session: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error revoking session")

    # ─── Cleanup Expired Sessions ─────────────────────────────────────────────

    async def cleanup_expired_sessions(self) -> int:
        """
        Xóa vĩnh viễn các sessions đã:
          - Hết hạn (expires_at < now) VÀ
          - Đã revoked (revoked_at IS NOT NULL)
        Trả về số rows bị xóa.
        Dùng trong background task hoặc cron job.
        """
        try:
            now = datetime.now(timezone.utc)
            stmt = delete(Sessions).where(
                Sessions.expires_at < now,
                Sessions.revoked_at.is_not(None),
            )
            result = await self._db.execute(stmt)
            await self._db.commit()
            deleted = result.rowcount
            if deleted > 0:
                logger.info("session.cleanup", deleted=deleted)
            return deleted
        except Exception as e:
            await self._db.rollback()
            logger.error(f"Error in cleanup_expired_sessions: {str(e)}", exc_info=True)
            return 0
