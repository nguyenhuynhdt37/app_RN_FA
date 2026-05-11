from __future__ import annotations

import asyncio
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.core.redis import redis_client
from app.core.security import (
    create_otp_token,
    generate_otp,
    normalize_identifier,
)
from app.services.email import send_otp_email
from app.services.sms import send_otp_sms


class OtpService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ─── Redis Keys ───────────────────────────────────────────────────────────
    
    def _get_otp_key(self, identifier: str, purpose: str) -> str:
        return f"otp:{purpose}:{identifier}"

    def _get_cooldown_key(self, identifier: str, purpose: str) -> str:
        return f"otp_cooldown:{purpose}:{identifier}"

    # ─── Send OTP ─────────────────────────────────────────────────────────────

    async def send_otp(
        self,
        identifier: str,
        purpose: str,
        full_name: str | None = None,
        ip_address: str | None = None,
    ) -> dict:
        try:
            identifier = normalize_identifier(identifier)
            otp_key = self._get_otp_key(identifier, purpose)
            cooldown_key = self._get_cooldown_key(identifier, purpose)

            # 1. Kiểm tra trạng thái hiện tại trong Redis
            existing_otp = await redis_client.get(otp_key)
            cooldown_ttl = await redis_client.ttl(cooldown_key)
            otp_ttl = await redis_client.ttl(otp_key)

            # 2. Logic: Nếu đang trong thời gian Cooldown (vừa gửi mã xong)
            # Cho phép "qua bước này" mà không báo lỗi, chỉ trả về thông tin để User nhập mã cũ
            if existing_otp and cooldown_ttl > 0:
                logger.info("otp.resend_blocked_by_cooldown", identifier=identifier, cooldown_left=cooldown_ttl)
                return {
                    "message": f"Mã xác thực đã được gửi trước đó. Vui lòng kiểm tra {identifier}.",
                    "otp_expires_in": otp_ttl if otp_ttl > 0 else 0,
                    "resend_available_in": cooldown_ttl,
                    "is_new_otp": False,
                    # Trả về preview nếu đang dev để tiện test
                    "otp_preview": existing_otp if not settings.is_production else None
                }

            # 3. Tạo mã mới (nếu không có mã cũ hoặc đã hết cooldown)
            if not settings.SMS_ENABLED and not identifier.count("@"):
                raw_otp = settings.OTP_DEV_BYPASS
            else:
                raw_otp = generate_otp()

            # 4. Lưu vào Redis
            await redis_client.setex(otp_key, settings.OTP_EXPIRE_MINUTES * 60, raw_otp)
            await redis_client.setex(cooldown_key, settings.OTP_RESEND_COOLDOWN_SECONDS, "1")

            # 5. Gửi mã thực tế
            is_email = "@" in identifier
            try:
                if is_email:
                    await send_otp_email(
                        to=identifier,
                        otp_code=raw_otp,
                        purpose=purpose,
                        full_name=full_name,
                        expire_minutes=settings.OTP_EXPIRE_MINUTES,
                    )
                else:
                    await send_otp_sms(
                        phone=identifier,
                        otp_code=raw_otp,
                        purpose=purpose,
                        expire_minutes=settings.OTP_EXPIRE_MINUTES,
                    )
                logger.info("otp.sent_success", identifier=identifier, purpose=purpose)
            except Exception as exc:
                logger.error("otp.send_error", identifier=identifier, error=str(exc))
                if settings.is_production:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={"code": "SEND_OTP_FAILED", "message": "Không thể gửi mã xác thực. Vui lòng thử lại sau."}
                    )

            return {
                "message": f"Mã xác thực mới đã được gửi đến {identifier}.",
                "otp_expires_in": settings.OTP_EXPIRE_MINUTES * 60,
                "resend_available_in": settings.OTP_RESEND_COOLDOWN_SECONDS,
                "is_new_otp": True,
                "otp_preview": raw_otp if not settings.is_production else None
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in send_otp: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error sending OTP")

    # ─── Verify OTP ───────────────────────────────────────────────────────────

    async def verify_otp(
        self,
        identifier: str,
        plain_otp: str,
        purpose: str,
    ) -> str:
        """Xác thực mã OTP và xóa khỏi Redis nếu thành công."""
        try:
            identifier = normalize_identifier(identifier)
            otp_key = self._get_otp_key(identifier, purpose)
            stored_otp = await redis_client.get(otp_key)

            if not stored_otp:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": "OTP_EXPIRED", "message": "Mã xác thực đã hết hạn hoặc không tồn tại."},
                )

            if stored_otp != plain_otp:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": "OTP_INVALID", "message": "Mã xác thực không chính xác."},
                )

            # Xóa OTP và Cooldown sau khi xác thực thành công
            await redis_client.delete(otp_key)
            await redis_client.delete(self._get_cooldown_key(identifier, purpose))

            return create_otp_token(identifier, purpose)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in verify_otp: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error verifying OTP")
