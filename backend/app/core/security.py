from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings


# ─── Password Hashing ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# ─── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
    session_id: str | None = None,
    roles: list[str] | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire, "type": "access"}
    if session_id:
        payload["sid"] = session_id      # session_id — dùng để identify thiết bị
    if roles is not None:
        payload["roles"] = roles
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str | Any) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {"sub": str(subject), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT. Raises ValueError on failure."""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except InvalidTokenError as exc:
        raise ValueError(f"Invalid or expired token: {exc}") from exc


# ─── OTP Helpers ───────────────────────────────────────────────────────────────

def generate_otp(length: int | None = None) -> str:
    """Generate a numeric OTP of given length (default from settings)."""
    n = length or settings.OTP_LENGTH
    # secrets.randbelow is CSPRNG-safe
    return str(secrets.randbelow(10 ** n)).zfill(n)


def hash_otp(otp: str) -> str:
    """SHA-256 hash of OTP — safe to store in DB."""
    return hashlib.sha256(otp.encode()).hexdigest()


def verify_otp(plain_otp: str, otp_hash: str) -> bool:
    """Compare plain OTP against stored SHA-256 hash."""
    return secrets.compare_digest(hash_otp(plain_otp), otp_hash)


# ─── Refresh Token Helpers ─────────────────────────────────────────────────────

def generate_refresh_token_raw() -> str:
    """Generate a cryptographically secure random refresh token (64 hex chars)."""
    return secrets.token_hex(32)            # 256-bit entropy


def hash_refresh_token(token: str) -> str:
    """SHA-256 hash of refresh token — store this in DB, never the raw value."""
    return hashlib.sha256(token.encode()).hexdigest()


# ─── OTP JWT (short-lived, phone-scoped) ──────────────────────────────────────

def create_otp_token(phone: str, purpose: str) -> str:
    """
    Short-lived JWT issued after OTP verify succeeds.
    Used as a proof-of-phone-ownership for complete_register / login_by_otp.
    TTL: 10 minutes.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    payload = {
        "sub": phone,
        "purpose": purpose,
        "type": "otp_verified",
        "exp": expire,
        "jti": os.urandom(8).hex(),     # unique per token
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def normalize_identifier(identifier: str) -> str:
    """
    Chuẩn hóa identifier (email hoặc phone) để đảm bảo tính nhất quán.
    - Email: lowercase, strip.
    - Phone: Loại bỏ khoảng trắng, dấu gạch ngang, đưa về chuẩn +84 (VN).
    """
    val = identifier.strip()
    if "@" in val:
        return val.lower()
    
    # Phone normalization
    val = val.replace(" ", "").replace("-", "").replace(".", "")
    if val.startswith("0"):
        return f"+84{val[1:]}"
    return val


def decode_otp_token(token: str, expected_purpose: str) -> str:
    """
    Validate OTP JWT and return phone number.
    Raises ValueError if invalid, expired, or wrong purpose.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except InvalidTokenError as exc:
        raise ValueError(f"OTP token không hợp lệ hoặc đã hết hạn: {exc}") from exc

    if payload.get("type") != "otp_verified":
        raise ValueError("Token không phải OTP verified token")
    if payload.get("purpose") != expected_purpose:
        raise ValueError(f"Token dùng sai mục đích. Expected: {expected_purpose}")

    return str(payload["sub"])  # phone
