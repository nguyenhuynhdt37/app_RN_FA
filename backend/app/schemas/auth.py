"""
schemas/auth.py — Pydantic V2 request/response schemas cho Auth
================================================================
Flow: Phone OTP → Register / Login / Refresh / Logout / Me
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, date
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ─── Validators ───────────────────────────────────────────────────────────────

_PHONE_RE = re.compile(r"^\+?[0-9]{8,15}$")


def _validate_phone(v: str) -> str:
    v = v.strip().replace(" ", "").replace("-", "")
    if not _PHONE_RE.match(v):
        raise ValueError("Số điện thoại không hợp lệ. VD: +84901234567 hoặc 0901234567")
    return v


# ─── OTP Requests ─────────────────────────────────────────────────────────────

class SendOtpRequest(BaseModel):
    """Yêu cầu gửi OTP — bước đầu của xác thực qua phone hoặc email."""
    phone: str | None = Field(None, examples=["+84901234567"])
    email: EmailStr | None = Field(None, examples=["user@example.com"])
    purpose: Literal["authenticate", "reset_password"]

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validate_phone(v)


class VerifyOtpRequest(BaseModel):
    """Xác thực OTP code — trả về otp_token để dùng ở bước tiếp theo."""
    phone: str | None = None
    email: EmailStr | None = None
    otp_code: str = Field(..., min_length=4, max_length=10)
    purpose: Literal["authenticate", "reset_password"]

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validate_phone(v)


class VerifyOtpResponse(BaseModel):
    """Trả về sau khi OTP verify thành công."""
    verified: bool = True
    otp_token: str          # short-lived JWT dùng cho complete_register / login_by_otp
    phone: str | None = ""
    email: str | None = ""
    message: str = "OTP xác thực thành công"


class AuthenticateRequest(BaseModel):
    """Xác thực (Login/Register) bằng OTP."""
    otp_token: str                                      # JWT từ verify_otp
    device_type: Literal["IOS", "ANDROID", "WEB"] = "ANDROID"
    device_name: str | None = None
    device_token: str | None = None                     # FCM/APNS push token


# ─── Token ────────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int             # access token TTL (seconds)
    session_id: uuid.UUID       # ID của session hiện tại — dùng để revoke


class RefreshTokenRequest(BaseModel):
    refresh_token: str
    device_type: Literal["IOS", "ANDROID", "WEB"] = "ANDROID"


# ─── Password Reset ───────────────────────────────────────────────────────────

class ResetPasswordRequest(BaseModel):
    otp_token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ hoa")
        if not any(c.isdigit() for c in v):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ số")
        return v


# ─── User Profile ─────────────────────────────────────────────────────────────

class UserSpecializationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    specialization_id: uuid.UUID
    level: str = Field(..., min_length=2, max_length=50)
    skill_ids: list[uuid.UUID] = []

class SkillResponse(BaseModel):
    id: uuid.UUID
    name: str
    name_en: str
    name_vi: str

class SpecializationResponse(BaseModel):
    specialization_id: uuid.UUID
    name: str
    name_en: str
    name_vi: str
    level: str # the key
    level_label: str
    skills: list[SkillResponse] = []


class UpdateProfileRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr | None = None
    bio: str | None = None
    specializations: list[UserSpecializationSchema] = Field(..., min_length=1)
    learning_goals: str = Field(..., min_length=10)
    interest_ids: list[uuid.UUID] = []
    daily_goal_minutes: int = 30
    preferred_learning_style: str | None = None
    avatar_url: str | None = None
    social_links: dict[str, str] = {}
    date_of_birth: date | None = None
    gender: str | None = None


class UserProfileSummaryResponse(BaseModel):
    full_name: str | None
    avatar_url: str | None
    username: str | None

    @field_validator("avatar_url", mode="after")
    @classmethod
    def prefix_avatar_url(cls, v: str | None) -> str | None:
        if v and not v.startswith(("http://", "https://")):
            from app.core.config import settings
            return f"{settings.BACKEND_URL.rstrip('/')}/{v.lstrip('/')}"
        return v


class AvatarUploadResponse(BaseModel):
    avatar_url: str

    @field_validator("avatar_url", mode="after")
    @classmethod
    def prefix_avatar_url(cls, v: str) -> str:
        if v and not v.startswith(("http://", "https://")):
            from app.core.config import settings
            return f"{settings.BACKEND_URL.rstrip('/')}/{v.lstrip('/')}"
        return v


class UserPublicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phone: str | None
    email: str | None
    full_name: str | None
    preferred_lang: str = "vi"
    preferred_currency: str = "VND"
    username: str | None = None
    bio: str | None = None
    is_profile_completed: bool = False
    specializations: list[SpecializationResponse] = []
    learning_goals: str | None = None
    interest_ids: list[uuid.UUID] = []
    interests: list[SkillResponse] = [] # Reusing SkillResponse for ID+Name
    daily_goal_minutes: int = 30
    preferred_learning_style: str | None = None
    social_links: dict[str, str] = {}
    avatar_url: str | None = None
    status: str
    is_verified: bool
    roles: list[str] = []
    created_at: datetime
    last_login_at: datetime | None = None
    date_of_birth: date | None = None
    gender: str | None = None

    @field_validator("avatar_url", mode="after")
    @classmethod
    def prefix_avatar_url(cls, v: str | None) -> str | None:
        if v and not v.startswith(("http://", "https://")):
            from app.core.config import settings
            return f"{settings.BACKEND_URL.rstrip('/')}/{v.lstrip('/')}"
        return v
