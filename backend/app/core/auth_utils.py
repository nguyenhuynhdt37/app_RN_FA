from fastapi import Response
from app.core.config import settings

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Set HttpOnly cookies for web clients."""
    # Set Access Token Cookie
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        max_age=60 * 60 * 24, # 24h as requested
        path="/",
    )
    
    # Set Refresh Token Cookie
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )

def clear_auth_cookies(response: Response):
    """Remove auth cookies from the client."""
    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        domain=settings.COOKIE_DOMAIN,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        domain=settings.COOKIE_DOMAIN,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )
