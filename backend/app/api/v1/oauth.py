"""
api/v1/oauth.py — OAuth2 Router (Google + GitHub)
==================================================
Endpoints:
  POST /auth/oauth/google      → Mobile: verify id_token từ Google SDK
  POST /auth/oauth/github      → Mobile: exchange code từ GitHub OAuth
  GET  /auth/oauth/google/url  → Web: lấy authorization URL đến Google
  GET  /auth/oauth/github/url  → Web: lấy authorization URL đến GitHub
  GET  /auth/oauth/callback    → Web: nhận code redirect từ Google/GitHub
"""
from __future__ import annotations

from fastapi import APIRouter, Request, status, HTTPException
from fastapi.responses import RedirectResponse

from app.core.dependencies import DBSession
from app.schemas.auth import TokenResponse
from app.schemas.oauth import GitHubMobileRequest, GoogleMobileRequest, OAuthUrlResponse
from app.services.oauth import (
    GitHubOAuthService,
    GoogleOAuthService,
    OAuthUpsertService,
    generate_oauth_state,
)
from app.core.logging import logger

router = APIRouter(prefix="/auth/oauth", tags=["OAuth2"])


# ─── Mobile Flow: Google ──────────────────────────────────────────────────────

@router.post(
    "/google",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập bằng Google (Mobile — id_token)",
)
async def login_with_google(
    payload: GoogleMobileRequest,
    request: Request,
    db: DBSession,
) -> TokenResponse:
    """
    **Mobile flow** — React Native dùng Google SDK để lấy `id_token`,
    sau đó gửi lên đây để backend verify và tạo session.

    **Cách dùng với React Native:**
    ```
    import { GoogleSignin } from '@react-native-google-signin/google-signin';
    const { idToken } = await GoogleSignin.signIn();
    // Gửi idToken lên POST /auth/oauth/google
    ```
    """
    try:
        google_service = GoogleOAuthService(db)
        user_info = await google_service.verify_id_token(payload.id_token)

        upsert_service = OAuthUpsertService(db)
        return await upsert_service.upsert_and_login(
            user_info=user_info,
            device_type=payload.device_type,
            device_name=payload.device_name,
            device_token=payload.device_token,
            request=request,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login_with_google: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ─── Mobile Flow: GitHub ──────────────────────────────────────────────────────

@router.post(
    "/github",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập bằng GitHub (Mobile — authorization code)",
)
async def login_with_github(
    payload: GitHubMobileRequest,
    request: Request,
    db: DBSession,
) -> TokenResponse:
    """
    **Mobile flow** — App mở GitHub OAuth URL, lấy authorization `code` từ redirect,
    sau đó gửi lên đây để backend exchange lấy access_token và verify user.

    **Cách dùng với React Native (expo-auth-session):**
    ```
    const result = await AuthSession.startAsync({
      authUrl: 'https://github.com/login/oauth/authorize?client_id=...'
    });
    // result.params.code gửi lên POST /auth/oauth/github
    ```
    """
    try:
        github_service = GitHubOAuthService(db)
        user_info = await github_service.verify_code(payload.code)

        upsert_service = OAuthUpsertService(db)
        return await upsert_service.upsert_and_login(
            user_info=user_info,
            device_type=payload.device_type,
            device_name=payload.device_name,
            device_token=payload.device_token,
            request=request,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login_with_github: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ─── Web Flow: Authorization URLs ─────────────────────────────────────────────

@router.get(
    "/google/url",
    response_model=OAuthUrlResponse,
    summary="Lấy URL đăng nhập Google (Web flow)",
)
async def google_auth_url(db: DBSession) -> OAuthUrlResponse:
    """
    Trả về Google OAuth authorization URL.
    Frontend redirect user đến URL này.
    State token được generate tự động (CSRF protection).
    """
    try:
        state = generate_oauth_state()
        service = GoogleOAuthService(db)
        return service.get_authorization_url(state=state)
    except Exception as e:
        logger.error(f"Error in google_auth_url: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/github/url",
    response_model=OAuthUrlResponse,
    summary="Lấy URL đăng nhập GitHub (Web flow)",
)
async def github_auth_url(db: DBSession) -> OAuthUrlResponse:
    """
    Trả về GitHub OAuth authorization URL.
    Frontend redirect user đến URL này.
    """
    try:
        state = generate_oauth_state()
        service = GitHubOAuthService(db)
        return service.get_authorization_url(state=state)
    except Exception as e:
        logger.error(f"Error in github_auth_url: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ─── Web Flow: Callback ───────────────────────────────────────────────────────

@router.get(
    "/callback",
    response_model=TokenResponse,
    summary="OAuth2 Callback (Web flow — Google + GitHub)",
    include_in_schema=True,
)
async def oauth_callback(
    code: str,
    request: Request,
    db: DBSession,
    provider: str = "google",
    state: str | None = None,
) -> TokenResponse:
    """
    Callback endpoint cho cả Google và GitHub web redirect flow.
    Provider được phân biệt qua query param `provider`.

    URL ví dụ nhận được:
    ```
    /api/v1/auth/oauth/callback?provider=google&code=xxx&state=yyy
    /api/v1/auth/oauth/callback?provider=github&code=xxx&state=yyy
    ```
    """
    try:
        upsert_service = OAuthUpsertService(db)

        if provider == "google":
            google_service = GoogleOAuthService(db)
            user_info = await google_service.exchange_code(code)
        elif provider == "github":
            github_service = GitHubOAuthService(db)
            user_info = await github_service.exchange_code_web(code)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_PROVIDER", "message": f"Provider không hợp lệ: {provider}"},
            )

        return await upsert_service.upsert_and_login(
            user_info=user_info,
            device_type="WEB",
            device_name="Web Browser",
            device_token=None,
            request=request,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in oauth_callback: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
