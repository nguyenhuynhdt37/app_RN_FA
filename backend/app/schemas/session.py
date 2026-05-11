"""
schemas/session.py — Pydantic V2 schemas cho Session Management
===============================================================
Dùng để list / revoke sessions (quản lý thiết bị đăng nhập).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ─── Session Response ─────────────────────────────────────────────────────────

class SessionResponse(BaseModel):
    """Thông tin 1 session / thiết bị đang đăng nhập."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    device_type: str
    device_name: str | None
    ip_address: str | None
    user_agent: str | None = None
    last_used_at: datetime | None
    created_at: datetime
    is_current: bool = False        # True nếu đây là session đang gọi request


class SessionListResponse(BaseModel):
    """Danh sách tất cả active sessions của user."""
    sessions: list[SessionResponse]
    total: int
