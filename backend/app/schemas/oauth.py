"""
schemas/oauth.py — Pydantic V2 schemas cho OAuth2 (Google + GitHub)
====================================================================
Hỗ trợ 2 flow:
  - Mobile: App dùng SDK → lấy id_token/access_token → gửi lên backend
  - Web: Backend redirect → provider → callback → trả token
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# ─── Mobile Flow ──────────────────────────────────────────────────────────────

class GoogleMobileRequest(BaseModel):
    """
    Mobile flow: React Native dùng expo-auth-session hoặc @react-native-google-signin/google-signin
    lấy id_token từ Google SDK, gửi lên backend để verify.
    """
    id_token: str = Field(..., description="Google ID token từ mobile SDK")
    device_type: Literal["IOS", "ANDROID", "WEB"] = "ANDROID"
    device_name: str | None = None
    device_token: str | None = Field(None, description="FCM/APNS push token")


class GitHubMobileRequest(BaseModel):
    """
    Mobile flow: App lấy authorization code từ GitHub OAuth,
    gửi lên backend để exchange lấy access_token và verify user.
    """
    code: str = Field(..., description="Authorization code từ GitHub OAuth")
    device_type: Literal["IOS", "ANDROID", "WEB"] = "ANDROID"
    device_name: str | None = None
    device_token: str | None = Field(None, description="FCM/APNS push token")


# ─── Web Redirect Flow ────────────────────────────────────────────────────────

class OAuthUrlResponse(BaseModel):
    """Trả về URL để redirect user đến provider (web flow)."""
    url: str
    provider: str


class OAuthCallbackResponse(BaseModel):
    """Trả về sau khi provider redirect về callback (web flow)."""
    code: str
    state: str | None = None


# ─── Shared ───────────────────────────────────────────────────────────────────

class OAuthUserInfo(BaseModel):
    """Thông tin user đã normalize từ bất kỳ provider nào."""
    provider: str                   # "google" | "github"
    provider_uid: str               # unique ID từ provider
    email: str | None = None
    full_name: str | None = None
    avatar_url: str | None = None
    provider_email: str | None = None
