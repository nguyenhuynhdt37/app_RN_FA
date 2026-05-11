"""
services/email.py — Email Service (FastAPI-Mail + Jinja2)
==========================================================
Gửi email bất đồng bộ với HTML templates.
KHÔNG chứa business logic — chỉ là delivery layer.

Patterns:
- Nếu MAIL_ENABLED=False → log thay vì gửi (dev mode)
- Tất cả methods đều async
- Template context được type-safe qua TypedDict
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings
from app.core.logging import logger

# ─── Template Engine ──────────────────────────────────────────────────────────

_TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "email"

_jinja_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
)

# ─── Mail Connection Config ───────────────────────────────────────────────────

_mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=bool(settings.MAIL_USERNAME),
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=str(_TEMPLATE_DIR),
)

_fastmail = FastMail(_mail_config)

# ─── Base Context ─────────────────────────────────────────────────────────────

def _base_context() -> dict[str, Any]:
    return {
        "app_name": settings.APP_NAME,
        "app_url": settings.FRONTEND_URL,
        "support_url": f"{settings.FRONTEND_URL}/support",
        "privacy_url": f"{settings.FRONTEND_URL}/privacy",
        "year": datetime.datetime.now().year,
    }


def _render_template(template_name: str, context: dict[str, Any]) -> str:
    """Render Jinja2 HTML template."""
    template = _jinja_env.get_template(template_name)
    return template.render(**{**_base_context(), **context})


# ─── Core Send Function ───────────────────────────────────────────────────────

async def _send(
    to: str | list[str],
    subject: str,
    html_body: str,
) -> None:
    """
    Internal send — logs instead of sending when MAIL_ENABLED=False.
    """
    recipients = [to] if isinstance(to, str) else to

    if not settings.MAIL_ENABLED:
        logger.info(
            "email.skipped_dev_mode",
            to=recipients,
            subject=subject,
            preview=html_body[:120].replace("\n", " "),
        )
        return

    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=html_body,
        subtype=MessageType.html,
    )
    try:
        await _fastmail.send_message(message)
        logger.info("email.sent", to=recipients, subject=subject)
    except Exception as exc:
        logger.error("email.send_failed", to=recipients, subject=subject, error=str(exc))
        raise


# ─── Public API ───────────────────────────────────────────────────────────────

async def send_otp_email(
    *,
    to: str,
    otp_code: str,
    purpose: str,                   # 'register' | 'login' | 'reset_password'
    full_name: str | None = None,
    expire_minutes: int | None = None,
) -> None:
    """Gửi email chứa OTP code."""
    html = _render_template("otp.html", {
        "otp_code": otp_code,
        "purpose": purpose,
        "full_name": full_name or "",
        "expire_minutes": expire_minutes or settings.OTP_EXPIRE_MINUTES,
    })
    subject_map = {
        "register":       f"[{settings.APP_NAME}] Xác thực đăng ký — {otp_code}",
        "login":          f"[{settings.APP_NAME}] Mã đăng nhập — {otp_code}",
        "reset_password": f"[{settings.APP_NAME}] Đặt lại mật khẩu — {otp_code}",
    }
    subject = subject_map.get(purpose, f"[{settings.APP_NAME}] Mã xác thực")
    await _send(to=to, subject=subject, html_body=html)


async def send_welcome_email(
    *,
    to: str,
    full_name: str,
) -> None:
    """Gửi email chào mừng sau khi đăng ký thành công."""
    html = _render_template("welcome.html", {"full_name": full_name})
    await _send(
        to=to,
        subject=f"Chào mừng đến với {settings.APP_NAME}! 🚗",
        html_body=html,
    )


async def send_custom_email(
    *,
    to: str | list[str],
    subject: str,
    template_name: str,
    context: dict[str, Any],
) -> None:
    """Generic: gửi bất kỳ template nào."""
    html = _render_template(template_name, context)
    await _send(to=to, subject=subject, html_body=html)
