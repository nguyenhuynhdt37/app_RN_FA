"""
services/oauth.py — OAuth2 Service (Google + GitHub)
=====================================================
Xử lý verify token/code từ provider và upsert user vào DB.

Flow:
  Google mobile: verify id_token → lấy user info → upsert → tạo session
  GitHub mobile: exchange code → lấy access_token → lấy user info → upsert → tạo session
  Web redirect:  tạo authorization URL với state (CSRF) → callback → exchange code

Patterns:
  - Dùng httpx.AsyncClient (không block event loop)
  - Không dùng Authlib starlette integration (phức tạp với mobile)
  - Dùng Google tokeninfo endpoint để verify id_token (đơn giản, không cần JWK)
  - Tất cả provider errors đều map về HTTPException 401/400
"""
from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.models.database import OauthAccounts, Sessions, Users
from app.schemas.auth import TokenResponse
from app.schemas.oauth import OAuthUrlResponse, OAuthUserInfo
from app.services.auth import AuthService
from app.core.security import (
    create_access_token,
    generate_refresh_token_raw,
    hash_refresh_token,
)


# ─── Google OAuth ─────────────────────────────────────────────────────────────

class GoogleOAuthService:
    """Xử lý Google OAuth2 — mobile (id_token) và web (authorization code)."""

    TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── Mobile: verify id_token ───────────────────────────────────────────────

    async def verify_id_token(self, id_token: str) -> OAuthUserInfo:
        """
        Verify Google id_token bằng Google tokeninfo endpoint.
        Đây là cách đơn giản nhất cho mobile — không cần JWK/JWKS.
        """
        if not settings.google_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "GOOGLE_NOT_CONFIGURED", "message": "Google OAuth chưa được cấu hình."},
            )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.TOKENINFO_URL, params={"id_token": id_token})

            if resp.status_code != 200:
                logger.warning("oauth.google.invalid_token", status=resp.status_code)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"code": "GOOGLE_TOKEN_INVALID", "message": "Google id_token không hợp lệ hoặc đã hết hạn."},
                )

            data = resp.json()

            # Verify audience (aud) phải là client_id của app
            if data.get("aud") != settings.GOOGLE_CLIENT_ID:
                logger.warning("oauth.google.wrong_audience", aud=data.get("aud"))
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"code": "GOOGLE_TOKEN_INVALID", "message": "Token không dành cho ứng dụng này."},
                )

            return OAuthUserInfo(
                provider="google",
                provider_uid=data["sub"],
                email=data.get("email"),
                full_name=data.get("name"),
                avatar_url=data.get("picture"),
                provider_email=data.get("email"),
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in Google verify_id_token: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error verifying Google token")

    # ── Web: generate authorization URL ──────────────────────────────────────

    def get_authorization_url(self, state: str) -> OAuthUrlResponse:
        """Tạo URL redirect đến Google consent screen (web flow)."""
        if not settings.google_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "GOOGLE_NOT_CONFIGURED", "message": "Google OAuth chưa được cấu hình."},
            )

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.OAUTH_REDIRECT_URI + "?provider=google",
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }
        from urllib.parse import urlencode
        url = self.AUTH_URL + "?" + urlencode(params)
        return OAuthUrlResponse(url=url, provider="google")

    # ── Web: exchange authorization code → user info ──────────────────────────

    async def exchange_code(self, code: str) -> OAuthUserInfo:
        """Exchange authorization code lấy access_token rồi lấy user info (web flow)."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                token_resp = await client.post(self.TOKEN_URL, data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.OAUTH_REDIRECT_URI + "?provider=google",
                    "grant_type": "authorization_code",
                })

            if token_resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"code": "GOOGLE_CODE_INVALID", "message": "Không thể exchange code với Google."},
                )

            tokens = token_resp.json()
            access_token = tokens.get("access_token")

            async with httpx.AsyncClient(timeout=10.0) as client:
                user_resp = await client.get(
                    self.USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )

            if user_resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"code": "GOOGLE_USERINFO_FAILED", "message": "Không thể lấy thông tin user từ Google."},
                )

            data = user_resp.json()
            return OAuthUserInfo(
                provider="google",
                provider_uid=data["sub"],
                email=data.get("email"),
                full_name=data.get("name"),
                avatar_url=data.get("picture"),
                provider_email=data.get("email"),
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in Google exchange_code: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error exchanging Google code")


# ─── GitHub OAuth ─────────────────────────────────────────────────────────────

class GitHubOAuthService:
    """Xử lý GitHub OAuth2 — mobile (authorization code) và web redirect."""

    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_URL = "https://api.github.com/user"
    EMAIL_URL = "https://api.github.com/user/emails"
    AUTH_URL = "https://github.com/login/oauth/authorize"

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _exchange_code_for_token(self, code: str, redirect_uri: str | None = None) -> str:
        """Exchange authorization code lấy GitHub access_token."""
        payload: dict = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
        }
        if redirect_uri:
            payload["redirect_uri"] = redirect_uri

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                self.TOKEN_URL,
                data=payload,
                headers={"Accept": "application/json"},
            )

        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "GITHUB_CODE_INVALID", "message": "Không thể exchange code với GitHub."},
            )

        data = resp.json()
        access_token = data.get("access_token")
        if not access_token:
            error = data.get("error_description", "Unknown error")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "GITHUB_TOKEN_MISSING", "message": f"GitHub không trả về access_token: {error}"},
            )
        return access_token

    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Lấy thông tin user từ GitHub API bằng access_token."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            user_resp = await client.get(self.USER_URL, headers=headers)

        if user_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "GITHUB_TOKEN_INVALID", "message": "GitHub access_token không hợp lệ."},
            )

        user_data = user_resp.json()

        # Email có thể private → phải gọi /user/emails riêng
        email = user_data.get("email")
        if not email:
            async with httpx.AsyncClient(timeout=10.0) as client:
                email_resp = await client.get(self.EMAIL_URL, headers=headers)
            if email_resp.status_code == 200:
                emails = email_resp.json()
                # Lấy primary verified email
                for e in emails:
                    if e.get("primary") and e.get("verified"):
                        email = e["email"]
                        break

        return OAuthUserInfo(
            provider="github",
            provider_uid=str(user_data["id"]),
            email=email,
            full_name=user_data.get("name") or user_data.get("login"),
            avatar_url=user_data.get("avatar_url"),
            provider_email=email,
        )

    async def verify_code(self, code: str) -> OAuthUserInfo:
        """Mobile flow: exchange code → access_token → user info."""
        if not settings.github_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "GITHUB_NOT_CONFIGURED", "message": "GitHub OAuth chưa được cấu hình."},
            )
        access_token = await self._exchange_code_for_token(code)
        return await self.get_user_info(access_token)

    async def exchange_code_web(self, code: str) -> OAuthUserInfo:
        """Web flow: exchange code với redirect_uri → user info."""
        if not settings.github_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "GITHUB_NOT_CONFIGURED", "message": "GitHub OAuth chưa được cấu hình."},
            )
        redirect_uri = settings.OAUTH_REDIRECT_URI + "?provider=github"
        access_token = await self._exchange_code_for_token(code, redirect_uri=redirect_uri)
        return await self.get_user_info(access_token)

    def get_authorization_url(self, state: str) -> OAuthUrlResponse:
        """Tạo URL redirect đến GitHub authorize (web flow)."""
        if not settings.github_enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"code": "GITHUB_NOT_CONFIGURED", "message": "GitHub OAuth chưa được cấu hình."},
            )
        from urllib.parse import urlencode
        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": settings.OAUTH_REDIRECT_URI + "?provider=github",
            "scope": "user:email",
            "state": state,
        }
        url = self.AUTH_URL + "?" + urlencode(params)
        return OAuthUrlResponse(url=url, provider="github")


# ─── OAuth User Upsert (shared) ───────────────────────────────────────────────

class OAuthUpsertService:
    """
    Tìm hoặc tạo user từ OAuth user info.
    Dùng oauth_accounts làm bảng trung gian (provider + provider_uid → user).
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._auth = AuthService(db)

    async def upsert_and_login(
        self,
        user_info: OAuthUserInfo,
        device_type: str,
        device_name: str | None,
        device_token: str | None,
        request: Request | None,
    ) -> TokenResponse:
        """
        Tìm hoặc tạo user dựa trên oauth_accounts.
        Trả về TokenResponse như các login flow khác.
        """
        try:
            # 1. Tìm oauth_account theo provider + provider_uid
            stmt = select(OauthAccounts).where(
                OauthAccounts.provider == user_info.provider,
                OauthAccounts.provider_uid == user_info.provider_uid,
            )
            result = await self._db.execute(stmt)
            oauth_account: OauthAccounts | None = result.scalar_one_or_none()

            if oauth_account:
                # User đã tồn tại → load user
                user = await self._db.get(Users, oauth_account.user_id)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={"code": "USER_NOT_FOUND", "message": "User liên kết với OAuth account không tồn tại."},
                    )
                self._auth._assert_user_active(user)
                logger.info("oauth.login", provider=user_info.provider, user_id=str(user.id))
            else:
                # Chưa có → tạo user mới (hoặc link với existing email)
                user = await self._find_or_create_user(user_info)
                # Tạo oauth_account
                new_oauth = OauthAccounts(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    provider=user_info.provider,
                    provider_uid=user_info.provider_uid,
                    provider_email=user_info.provider_email,
                )
                self._db.add(new_oauth)
                await self._db.commit()
                logger.info("oauth.register", provider=user_info.provider, user_id=str(user.id))

            await self._auth._update_last_login(user.id)

            return await self._auth._create_session_tokens(
                user=user,
                device_type=device_type,
                device_name=device_name,
                device_token=device_token,
                ip_address=self._auth._get_ip(request),
                user_agent=self._auth._get_ua(request),
            )
        except HTTPException:
            await self._db.rollback()
            raise
        except Exception as e:
            await self._db.rollback()
            logger.error(f"Error in upsert_and_login: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error during OAuth login")

    async def _find_or_create_user(self, user_info: OAuthUserInfo) -> Users:
        """
        Nếu email đã tồn tại → link OAuth vào user đó.
        Nếu chưa → tạo user mới (is_verified=True vì OAuth provider đã verify).
        """
        if user_info.email:
            stmt = select(Users).where(Users.email == user_info.email)
            result = await self._db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                return existing

        # Tạo mới
        user = Users(
            id=uuid.uuid4(),
            email=user_info.email,
            full_name=user_info.full_name,
            avatar_url=user_info.avatar_url,
            status="ACTIVE",
            is_verified=True,
        )
        self._db.add(user)
        await self._db.flush()

        await self._db.commit()
        await self._db.refresh(user)
        return user


# ─── State helpers (CSRF protection cho web flow) ─────────────────────────────

def generate_oauth_state() -> str:
    """Generate cryptographically secure state token (CSRF protection)."""
    return secrets.token_urlsafe(32)


def verify_oauth_state(state: str, expected: str) -> bool:
    """Constant-time compare để tránh timing attack."""
    return secrets.compare_digest(state, expected)
