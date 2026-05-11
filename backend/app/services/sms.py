"""
services/sms.py — SMS Service (Twilio)
=======================================
Gửi SMS bất đồng bộ qua Twilio REST API.
KHÔNG chứa business logic — chỉ là delivery layer.

Patterns:
- Nếu SMS_ENABLED=False → log + trả về OTP_DEV_BYPASS (dev mode)
- Dùng httpx async thay vì Twilio SDK sync để không block event loop
- Rate limit và retry được handle ở tầng gọi (OTP service)
"""

from __future__ import annotations

import base64

import httpx

from app.core.config import settings
from app.core.logging import logger

# ─── Twilio REST endpoint ─────────────────────────────────────────────────────

_TWILIO_BASE = "https://api.twilio.com/2010-04-01"


def _twilio_auth() -> str:
    """Basic auth header value cho Twilio."""
    creds = f"{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}"
    return "Basic " + base64.b64encode(creds.encode()).decode()


# ─── Core Send ────────────────────────────────────────────────────────────────

async def _send_sms(to: str, body: str) -> None:
    """
    Gửi SMS thật qua Twilio REST API (async httpx).
    Raises ValueError nếu Twilio trả lỗi.
    """
    url = f"{_TWILIO_BASE}/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"

    payload: dict[str, str] = {
        "To":   to,
        "Body": body,
    }
    # Dùng Messaging Service SID nếu có (khuyến nghị), fallback to From number
    if settings.TWILIO_MESSAGING_SID:
        payload["MessagingServiceSid"] = settings.TWILIO_MESSAGING_SID
    else:
        payload["From"] = settings.TWILIO_FROM_NUMBER

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            url,
            data=payload,
            headers={"Authorization": _twilio_auth()},
        )

    if response.status_code not in (200, 201):
        error_data = response.json()
        logger.error(
            "sms.twilio_error",
            to=to,
            status=response.status_code,
            code=error_data.get("code"),
            message=error_data.get("message"),
        )
        raise ValueError(f"SMS send failed: {error_data.get('message', 'Unknown error')}")

    sid = response.json().get("sid")
    logger.info("sms.sent", to=to, sid=sid)


# ─── Public API ───────────────────────────────────────────────────────────────

async def send_otp_sms(
    *,
    phone: str,
    otp_code: str,
    purpose: str,
    expire_minutes: int | None = None,
) -> None:
    """
    Gửi SMS chứa OTP.
    Dev mode (SMS_ENABLED=False): chỉ log, KHÔNG gửi thật.
    """
    try:
        expire = expire_minutes or settings.OTP_EXPIRE_MINUTES

        message_map = {
            "register":
                f"[{settings.APP_NAME}] Mã xác thực đăng ký: {otp_code}. "
                f"Hết hạn sau {expire} phút. Không chia sẻ mã này.",
            "login":
                f"[{settings.APP_NAME}] Mã đăng nhập: {otp_code}. "
                f"Hết hạn sau {expire} phút.",
            "reset_password":
                f"[{settings.APP_NAME}] Mã đặt lại mật khẩu: {otp_code}. "
                f"Hết hạn sau {expire} phút. Không chia sẻ mã này.",
        }
        body = message_map.get(
            purpose,
            f"[{settings.APP_NAME}] Mã xác thực: {otp_code}. Hết hạn sau {expire} phút.",
        )

        if not settings.SMS_ENABLED:
            logger.info(
                "sms.skipped_dev_mode",
                phone=phone,
                purpose=purpose,
                otp_preview=otp_code,        # safe to log in dev
                dev_bypass=settings.OTP_DEV_BYPASS,
                message=body,
            )
            return

        # Validate minimal Twilio config
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            logger.error("sms.twilio_not_configured")
            raise ValueError("SMS service is not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.")

        await _send_sms(to=phone, body=body)
    except Exception as e:
        logger.error(f"Error in send_otp_sms: {str(e)}", exc_info=True)
        raise


async def send_custom_sms(*, phone: str, message: str) -> None:
    """Generic: gửi bất kỳ SMS nào — dùng cho notification, alert."""
    try:
        if not settings.SMS_ENABLED:
            logger.info("sms.skipped_dev_mode", phone=phone, message=message)
            return
        await _send_sms(to=phone, body=message)
    except Exception as e:
        logger.error(f"Error in send_custom_sms: {str(e)}", exc_info=True)
        raise
