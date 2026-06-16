"""
api/v1/auth.py — Auth Router (Production)
==========================================
Endpoints:
  POST /auth/send-otp          → gửi OTP (SMS + email)
  POST /auth/verify-otp        → xác thực OTP → trả otp_token
  POST /auth/register          → hoàn tất đăng ký (dùng otp_token)
  POST /auth/login/otp         → đăng nhập bằng OTP
  POST /auth/login/password    → đăng nhập bằng email + password
  POST /auth/refresh           → rotating refresh token
  POST /auth/logout            → revoke 1 session
  POST /auth/logout-all        → revoke tất cả sessions
  GET  /auth/me                → profile user hiện tại
"""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, Request, Response, UploadFile, status

from app.core.dependencies import CurrentUserID, DBSession
from app.core.auth_utils import set_auth_cookies, clear_auth_cookies
from app.core.config import settings
from app.core.logging import logger
from app.schemas.auth import (
    AuthenticateRequest,
    PasswordLoginRequest,
    RefreshTokenRequest,
    SendOtpRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserPublicResponse,
    VerifyOtpRequest,
    VerifyOtpResponse,
    AvatarUploadResponse,
    CoverUploadResponse,
    UserProfileSummaryResponse,
)
from app.services.auth import AuthService
from app.services.otp import OtpService
from app.services.storage import StorageService

router = APIRouter(prefix="/auth", tags=["Auth"])


# ─── OTP Flow ─────────────────────────────────────────────────────────────────

@router.post(
    "/send-otp",
    summary="Gửi OTP qua SMS hoặc Email",
    status_code=status.HTTP_200_OK,
)
async def send_otp(payload: SendOtpRequest, request: Request, db: DBSession):
    """
    **Bước 1** của register/login flow.
    - Chấp nhận `phone` hoặc `email`.
    - Lưu OTP vào Redis (TTL 5p).
    - Rate-limit (cooldown) qua Redis.
    """
    try:
        service = OtpService(db)
        ip = request.client.host if request.client else None
        
        # Ưu tiên email nếu có, không thì dùng phone
        identifier = payload.email if payload.email else payload.phone
        if not identifier:
            raise HTTPException(
                status_code=400, 
                detail={"code": "IDENTIFIER_REQUIRED", "message": "Cần cung cấp phone hoặc email"}
            )
            
        return await service.send_otp(
            identifier=identifier,
            purpose=payload.purpose,
            ip_address=ip,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_otp: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/verify-otp",
    response_model=VerifyOtpResponse,
    summary="Xác thực OTP code",
)
async def verify_otp(payload: VerifyOtpRequest, db: DBSession):
    """
    **Bước 2**: nhập OTP code → nhận `otp_token` (JWT).
    """
    try:
        service = OtpService(db)
        identifier = payload.email if payload.email else payload.phone
        if not identifier:
            raise HTTPException(status_code=400, detail="Cần cung cấp phone hoặc email")

        otp_token = await service.verify_otp(
            identifier=identifier,
            plain_otp=payload.otp_code,
            purpose=payload.purpose,
        )
        return VerifyOtpResponse(
            otp_token=otp_token, 
            phone=payload.phone if payload.phone else "",
            email=payload.email if payload.email else ""
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in verify_otp: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/authenticate",
    response_model=TokenResponse,
    summary="Xác thực người dùng (Login/Register) bằng OTP",
)
async def authenticate_by_otp(
    payload: AuthenticateRequest, 
    request: Request, 
    response: Response,
    db: DBSession
):
    """
    Xác thực người dùng (Login/Register là một).
    Flow: `/send-otp` → `/verify-otp` → `/authenticate`
    """
    try:
        service = AuthService(db)
        tokens = await service.authenticate_otp(payload, request=request)
        
        # Set cookies cho Web client
        set_auth_cookies(
            response=response, 
            access_token=tokens.access_token, 
            refresh_token=tokens.refresh_token
        )
        
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in authenticate_by_otp: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/login/password",
    response_model=TokenResponse,
    summary="Đăng nhập bằng email + mật khẩu (Admin/Staff)",
)
async def login_by_password(
    payload: PasswordLoginRequest,
    request: Request,
    response: Response,
    db: DBSession
):
    """
    Đăng nhập truyền thống cho hệ thống quản trị.
    - Chỉ cho phép các tài khoản có quyền Admin/Staff.
    - Trả về token + set cookies.
    """
    try:
        service = AuthService(db)
        tokens = await service.authenticate_password(payload, request=request)
        
        # Set cookies cho Web client
        set_auth_cookies(
            response=response, 
            access_token=tokens.access_token, 
            refresh_token=tokens.refresh_token
        )
        
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login_by_password: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ─── Token Management ─────────────────────────────────────────────────────────

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Làm mới access token",
)
async def refresh_token(
    payload: RefreshTokenRequest, 
    request: Request,
    response: Response,
    db: DBSession
):
    """
    Rotating refresh token pattern:
    - Gửi `refresh_token` cũ → nhận cặp token mới
    - Token cũ bị revoke ngay sau khi refresh
    """
    try:
        service = AuthService(db)
        
        # Lấy refresh token từ payload hoặc cookie
        token = payload.refresh_token
        if not token:
            token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
            
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail={"code": "REFRESH_TOKEN_REQUIRED", "message": "Cần cung cấp refresh token"}
            )

        tokens = await service.refresh(token, device_type=payload.device_type)
        
        # Cập nhật cookies mới
        set_auth_cookies(
            response=response, 
            access_token=tokens.access_token, 
            refresh_token=tokens.refresh_token
        )
        
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in refresh_token: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Đăng xuất thiết bị hiện tại",
)
async def logout(
    payload: RefreshTokenRequest, 
    request: Request,
    response: Response,
    db: DBSession
):
    """Revoke session của thiết bị hiện tại."""
    try:
        service = AuthService(db)
        
        # Lấy refresh token từ payload hoặc cookie
        token = payload.refresh_token
        if not token:
            token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
            
        if token:
            await service.logout(token)
            
        # Xóa cookies
        clear_auth_cookies(response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Đăng xuất tất cả thiết bị",
)
async def logout_all(current_user_id: CurrentUserID, db: DBSession):
    """Revoke tất cả sessions — dùng khi phát hiện tài khoản bị xâm phạm."""
    try:
        service = AuthService(db)
        await service.logout_all(current_user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in logout_all: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ─── Profile ──────────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserPublicResponse,
    summary="Thông tin người dùng hiện tại",
)
async def get_me(current_user_id: CurrentUserID, db: DBSession):
    """Trả về profile + roles của user đang đăng nhập."""
    try:
        service = AuthService(db)
        return await service.get_me(current_user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_me: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/profile-summary",
    response_model=UserProfileSummaryResponse,
    summary="Thông tin cơ bản của user (Header/Home)",
)
async def get_profile_summary(current_user_id: CurrentUserID, db: DBSession):
    """Lấy avatar và tên rút gọn để hiển thị ở trang chủ."""
    try:
        service = AuthService(db)
        return await service.get_profile_summary(current_user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_profile_summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch(
    "/profile",
    response_model=UserPublicResponse,
    summary="Cập nhật thông tin profile (Hoàn tất đăng ký)",
)
async def update_profile(
    payload: UpdateProfileRequest,
    current_user_id: CurrentUserID,
    db: DBSession
):
    """
    Cập nhật thông tin bắt buộc để kích hoạt tài khoản hoàn toàn.
    """
    try:
        service = AuthService(db)
        return await service.update_profile(current_user_id, payload)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_profile: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/avatar", response_model=AvatarUploadResponse, status_code=status.HTTP_200_OK)
async def upload_avatar(
    current_user_id: CurrentUserID,
    db: DBSession,
    file: UploadFile = File(...),
) -> AvatarUploadResponse:
    """Upload user avatar and link it to the user record."""
    # 1. Validation
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_FILE_TYPE", "message": "Chỉ chấp nhận file ảnh."}
        )

    try:
        storage = StorageService()
        auth_service = AuthService(db)
        
        # 2. Upload file
        url = await storage.upload_avatar(file)
        
        # 3. Persist to DB immediately
        await auth_service.update_avatar_url(current_user_id, url)
        
        return AvatarUploadResponse(avatar_url=url)
    except Exception as e:
        logger.error(f"Avatar upload failed for user {current_user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "UPLOAD_FAILED", "message": f"Upload thất bại: {str(e)}"}
        )

@router.post("/cover", response_model=CoverUploadResponse, status_code=status.HTTP_200_OK)
async def upload_cover(
    current_user_id: CurrentUserID,
    db: DBSession,
    file: UploadFile = File(...),
) -> CoverUploadResponse:
    """Upload user profile cover and link it to the user record."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_FILE_TYPE", "message": "Chỉ chấp nhận file ảnh."}
        )

    try:
        storage = StorageService()
        auth_service = AuthService(db)
        url = await storage.upload_cover(file)
        await auth_service.update_cover_url(current_user_id, url)
        return CoverUploadResponse(cover_url=url)
    except Exception as e:
        logger.error(f"Cover upload failed for user {current_user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "UPLOAD_FAILED", "message": f"Upload thất bại: {str(e)}"}
        )

@router.get("/check-username", summary="Kiểm tra username đã tồn tại chưa")
async def check_username(username: str, db: DBSession):
    try:
        service = AuthService(db)
        available = await service.check_username_availability(username)
        return {"available": available}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in check_username: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
