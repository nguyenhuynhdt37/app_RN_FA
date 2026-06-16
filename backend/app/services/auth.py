"""
services/auth.py — Auth Service (Production)
=============================================
Xử lý: Register, Login (OTP + Password), Refresh, Logout, Me.
Không chứa HTTP logic — chỉ business logic thuần.

Patterns:
- Mỗi method nhận raw data, trả về Pydantic schema hoặc dict
- Tất cả DB operations đều async (SQLAlchemy 2.0 style)
- Sessions lưu refresh_token_hash (không lưu raw)
- device_token lưu trong Sessions (không phải Users) → hỗ trợ multi-device push
- Login audit qua LoginAttempts table
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.logging import logger
from app.core.security import (
    create_access_token,
    decode_otp_token,
    decode_token,
    generate_refresh_token_raw,
    hash_password,
    hash_refresh_token,
    normalize_identifier,
    verify_password,
)
from app.models.database import (
    LoginAttempts,
    Roles,
    Sessions,
    UserRoles,
    Users,
    UserSpecializations,
    SpecializationsReference,
    SkillsReference,
    InterestsReference,
)
from app.schemas.auth import (
    AuthenticateRequest,
    PasswordLoginRequest,
    TokenResponse,
    UserPublicResponse,
    UpdateProfileRequest,
    UserSpecializationSchema,
    SkillResponse,
    SpecializationResponse,
    UserProfileSummaryResponse,
)
from app.services.email import send_welcome_email


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ─── Authenticate (OTP Upsert) ────────────────────────────────────────────
    async def authenticate_otp(
        self,
        payload: AuthenticateRequest,
        request: Request | None = None,
    ) -> TokenResponse:
        """
        Xác thực người dùng bằng OTP (Login/Register là một).
        1. Decode OTP token -> lấy identifier (phone hoặc email)
        2. Tìm người dùng theo identifier
        3. Nếu chưa có -> tạo mới (Register)
        4. Nếu đã có -> cập nhật last_login (Login)
        5. Tạo session và trả về tokens
        """
        # 1. Decode OTP token
        try:
            identifier = decode_otp_token(payload.otp_token, expected_purpose="authenticate")
            identifier = normalize_identifier(identifier)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "OTP_TOKEN_INVALID", "message": str(exc)},
            )

        try:
            # 2. Xác định loại identifier
            is_email = "@" in identifier
            
            # 3. Tìm hoặc tạo người dùng
            if is_email:
                user = await self._get_user_by_email(identifier)
            else:
                user = await self._get_user_by_phone(identifier)
                
            is_new_user = False

            if not user:
                # Create new user
                user_data = {
                    "id": uuid.uuid4(),
                    "status": "ACTIVE",
                    "is_verified": True,
                }
                if is_email:
                    user_data["email"] = identifier
                else:
                    user_data["phone"] = identifier
                    
                user = Users(**user_data)
                self._db.add(user)
                await self._db.flush()
                is_new_user = True
                logger.info("auth.upsert_register", user_id=str(user.id), identifier=identifier)
            else:
                self._assert_user_active(user)
                await self._update_last_login(user.id)
                logger.info("auth.upsert_login", user_id=str(user.id))

            await self._db.commit()
            await self._db.refresh(user)

            # 4. Tạo session
            return await self._create_session_tokens(
                user=user,
                device_type=payload.device_type,
                device_name=payload.device_name,
                device_token=payload.device_token,
                ip_address=self._get_ip(request),
                user_agent=self._get_ua(request),
            )
        except HTTPException:
            await self._db.rollback()
            raise
        except Exception as e:
            await self._db.rollback()
            logger.error(f"Error in authenticate_otp: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error during authentication")

    async def authenticate_password(
        self,
        payload: PasswordLoginRequest,
        request: Request | None = None,
    ) -> TokenResponse:
        """
        Đăng nhập bằng email + password (dành cho Admin/Staff).
        - Kiểm tra tài khoản tồn tại
        - Xác thực mật khẩu
        - Kiểm tra quyền (phải có 1 trong các quyền Admin/Staff)
        """
        email = normalize_identifier(payload.email)
        user = await self._get_user_by_email(email)
        
        if not user or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Email hoặc mật khẩu không chính xác."}
            )

        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Email hoặc mật khẩu không chính xác."}
            )

        self._assert_user_active(user)

        # ROLE CHECK: Chỉ cho phép các quyền Admin/Staff vào
        roles = await self._get_user_roles(user.id)
        allowed_admin_roles = ["admin", "moderator", "support", "finance"]
        
        if not any(role in allowed_admin_roles for role in roles):
            logger.warning(f"Unauthorized admin access attempt: user={email}, roles={roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCESS_DENIED", "message": "Tài khoản của bạn không có quyền truy cập hệ thống quản trị."}
            )

        await self._update_last_login(user.id)
        await self._db.commit()

        return await self._create_session_tokens(
            user=user,
            device_type=payload.device_type,
            device_name=payload.device_name,
            device_token=None,
            ip_address=self._get_ip(request),
            user_agent=self._get_ua(request),
        )

    # ─── Refresh Token ────────────────────────────────────────────────────────

    async def refresh(self, raw_refresh_token: str, device_type: str = "ANDROID") -> TokenResponse:
        """
        Rotating refresh token:
        - Tìm session theo hash (unique index → O(log n))
        - Revoke token cũ
        - Tạo token mới, giữ nguyên device info
        """
        try:
            token_hash = hash_refresh_token(raw_refresh_token)

            stmt = select(Sessions).where(
                Sessions.refresh_token_hash == token_hash,
                Sessions.revoked_at.is_(None),
                Sessions.expires_at > datetime.now(timezone.utc),
            )
            result = await self._db.execute(stmt)
            session: Sessions | None = result.scalar_one_or_none()

            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"code": "REFRESH_TOKEN_INVALID", "message": "Refresh token không hợp lệ hoặc đã hết hạn."},
                )

            # Load user
            user = await self._db.get(Users, session.user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "USER_NOT_FOUND"})

            self._assert_user_active(user)

            # Rotate: revoke old session, create new one
            await self._db.execute(
                update(Sessions)
                .where(Sessions.id == session.id)
                .values(revoked_at=datetime.now(timezone.utc))
            )

            new_raw = generate_refresh_token_raw()
            new_session = Sessions(
                id=uuid.uuid4(),
                user_id=user.id,
                refresh_token_hash=hash_refresh_token(new_raw),
                device_type=session.device_type,
                device_name=session.device_name,
                device_token=session.device_token,      # preserve push token
                push_provider=session.push_provider,
                ip_address=session.ip_address,
                expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                last_used_at=datetime.now(timezone.utc),
            )
            self._db.add(new_session)
            await self._db.commit()

            roles = await self._get_user_roles(user.id)
            access_token = create_access_token(str(user.id), session_id=str(new_session.id), roles=roles)
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_raw,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                session_id=new_session.id,
            )
        except HTTPException:
            await self._db.rollback()
            raise
        except Exception as e:
            await self._db.rollback()
            logger.error(f"Error in refresh: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error during token refresh")

    # ─── Logout ───────────────────────────────────────────────────────────────

    async def logout(self, raw_refresh_token: str) -> None:
        """Revoke session bằng refresh token."""
        try:
            token_hash = hash_refresh_token(raw_refresh_token)
            await self._db.execute(
                update(Sessions)
                .where(Sessions.refresh_token_hash == token_hash, Sessions.revoked_at.is_(None))
                .values(revoked_at=datetime.now(timezone.utc))
            )
            await self._db.commit()
        except Exception as e:
            await self._db.rollback()
            logger.error(f"Error in logout: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error during logout")

    async def logout_all(self, user_id: uuid.UUID) -> None:
        """Revoke tất cả sessions của user (logout tất cả thiết bị)."""
        try:
            await self._db.execute(
                update(Sessions)
                .where(Sessions.user_id == user_id, Sessions.revoked_at.is_(None))
                .values(revoked_at=datetime.now(timezone.utc))
            )
            await self._db.commit()
        except Exception as e:
            await self._db.rollback()
            logger.error(f"Error in logout_all: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error during logout_all")

    # ─── Get Me ───────────────────────────────────────────────────────────────

    async def get_me(self, user_id: uuid.UUID) -> UserPublicResponse:
        """Trả về profile của user hiện tại kèm roles và mapped metadata."""
        try:
            stmt = (
                select(Users)
                .options(selectinload(Users.specializations).selectinload(UserSpecializations.specialization))
                .where(Users.id == user_id)
            )
            result = await self._db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "USER_NOT_FOUND"})

            lang = user.preferred_lang if user.preferred_lang else "vi"
            roles = await self._get_user_roles(user_id)

            # Map Specializations
            mapped_specs = []
            for s in user.specializations:
                # Fetch skill names for this specialization
                skill_ids = s.skills if isinstance(s.skills, list) else []
                skill_names = []
                if skill_ids:
                    skill_stmt = select(SkillsReference).where(SkillsReference.id.in_(skill_ids))
                    skill_res = await self._db.execute(skill_stmt)
                    for sk in skill_res.scalars():
                        skill_names.append(SkillResponse(
                            id=sk.id,
                            name=sk.name_vi if lang == "vi" else sk.name_en,
                            name_en=sk.name_en,
                            name_vi=sk.name_vi
                        ))

                mapped_specs.append(SpecializationResponse(
                    specialization_id=s.specialization_id,
                    name=s.specialization.name_vi if lang == "vi" else s.specialization.name_en,
                    name_en=s.specialization.name_en,
                    name_vi=s.specialization.name_vi,
                    level=s.level,
                    level_label=s.level, # Frontend will translate the key
                    skills=skill_names,
                    skill_ids=skill_ids
                ))

            # Map Interests
            interest_ids = user.interests if isinstance(user.interests, list) else []
            mapped_interests = []
            if interest_ids:
                int_stmt = select(InterestsReference).where(InterestsReference.id.in_(interest_ids))
                int_res = await self._db.execute(int_stmt)
                for it in int_res.scalars():
                    mapped_interests.append(SkillResponse(
                        id=it.id,
                        name=it.name_vi if lang == "vi" else it.name_en,
                        name_en=it.name_en,
                        name_vi=it.name_vi
                    ))

            return UserPublicResponse(
                id=user.id,
                phone=user.phone,
                email=user.email,
                full_name=user.full_name,
                preferred_lang=user.preferred_lang,
                preferred_currency=user.preferred_currency,
                username=user.username,
                bio=user.bio,
                is_profile_completed=user.is_profile_completed,
                specializations=mapped_specs,
                learning_goals=user.learning_goals,
                interest_ids=interest_ids,
                interests=mapped_interests,
                daily_goal_minutes=user.daily_goal_minutes,
                preferred_learning_style=user.preferred_learning_style,
                social_links=user.social_links if user.social_links else {},
                avatar_url=user.avatar_url,
                cover_url=user.cover_url,
                status=user.status.value if hasattr(user.status, "value") else user.status,
                is_verified=user.is_verified,
                date_of_birth=user.date_of_birth,
                gender=user.gender,
                roles=roles,
                created_at=user.created_at,
                last_login_at=user.last_login_at,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_me: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error fetching user data")

    async def get_profile_summary(self, user_id: uuid.UUID) -> UserProfileSummaryResponse:
        """Trả về thông tin cơ bản (name, avatar) để hiển thị ở header/home."""
        try:
            user = await self._db.get(Users, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return UserProfileSummaryResponse(
                full_name=user.full_name,
                avatar_url=user.avatar_url,
                cover_url=user.cover_url,
                username=user.username
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_profile_summary: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    async def check_username_availability(self, username: str) -> bool:
        """Kiểm tra xem username đã có người dùng nào sử dụng chưa."""
        try:
            stmt = select(Users).where(Users.username == username)
            result = await self._db.execute(stmt)
            return result.scalar_one_or_none() is None
        except Exception as e:
            logger.error(f"Error in check_username_availability: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error checking username")

    async def update_profile(self, user_id: uuid.UUID, payload: UpdateProfileRequest) -> UserPublicResponse:
        """Cập nhật thông tin profile và đánh dấu hoàn tất."""
        try:
            user = await self._db.get(Users, user_id)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "USER_NOT_FOUND"})

            # Check username uniqueness if changed
            if payload.username and payload.username != user.username:
                existing = await self._db.execute(select(Users).where(Users.username == payload.username))
                if existing.scalar_one_or_none():
                    raise HTTPException(status_code=400, detail={"code": "USERNAME_TAKEN", "message": "Username đã tồn tại."})

            user.full_name = payload.full_name
            user.username = payload.username
            user.bio = payload.bio
            user.learning_goals = payload.learning_goals
            user.interests = [str(i) for i in payload.interest_ids]
            user.daily_goal_minutes = payload.daily_goal_minutes
            user.preferred_learning_style = payload.preferred_learning_style
            user.social_links = payload.social_links
            user.date_of_birth = payload.date_of_birth
            user.gender = payload.gender
            user.is_profile_completed = True

            # Sync specializations
            # Delete existing
            await self._db.execute(delete(UserSpecializations).where(UserSpecializations.user_id == user_id))
            
            # Add new
            for spec_data in payload.specializations:
                new_spec = UserSpecializations(
                    user_id=user_id,
                    specialization_id=spec_data.specialization_id,
                    level=spec_data.level,
                    skills=[str(s) for s in spec_data.skill_ids]
                )
                self._db.add(new_spec)
            
            if payload.email:
                user.email = payload.email
            if payload.avatar_url:
                user.avatar_url = payload.avatar_url
            if payload.cover_url:
                user.cover_url = payload.cover_url

            # Assign student role upon profile completion if they don't have it
            current_roles = await self._get_user_roles(user_id)
            if "student" not in current_roles:
                await self._assign_default_role(user_id, "student")

            await self._db.commit()
            await self._db.refresh(user)
            return await self.get_me(user.id)
        except HTTPException:
            await self._db.rollback()
            raise
        except Exception as e:
            await self._db.rollback()
            logger.error(f"Error in update_profile: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error updating profile")
            
    async def update_avatar_url(self, user_id: uuid.UUID, avatar_url: str) -> None:
        """Update user avatar URL in the database."""
        try:
            await self._db.execute(
                update(Users)
                .where(Users.id == user_id)
                .values(avatar_url=avatar_url)
            )
            await self._db.commit()
        except Exception as e:
            await self._db.rollback()
            logger.error(f"Error updating avatar_url: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error updating database with new avatar")

    async def update_cover_url(self, user_id: uuid.UUID, cover_url: str) -> None:
        """Update user cover URL in the database."""
        try:
            await self._db.execute(
                update(Users)
                .where(Users.id == user_id)
                .values(cover_url=cover_url)
            )
            await self._db.commit()
        except Exception as e:
            await self._db.rollback()
            logger.error(f"Error updating cover_url: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error updating database with new cover")

    # ─── Shared Session Creator ───────────────────────────────────────────────

    async def _create_session_tokens(
        self,
        user: Users,
        device_type: str,
        device_name: str | None,
        device_token: str | None,
        ip_address: str | None,
        user_agent: str | None = None,
        push_provider: str | None = None,
    ) -> TokenResponse:
        """
        Tạo access + refresh token, lưu session vào DB.
        device_token được lưu trên session → hỗ trợ push notification per-device.
        push_provider tự suy ra từ device_type nếu không truyền vào.
        """
        if push_provider is None and device_token:
            push_provider = "APNS" if device_type == "IOS" else "FCM"

        raw_refresh = generate_refresh_token_raw()
        session = Sessions(
            id=uuid.uuid4(),
            user_id=user.id,
            refresh_token_hash=hash_refresh_token(raw_refresh),
            device_type=device_type,
            device_name=device_name,
            device_token=device_token,
            push_provider=push_provider,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            last_used_at=datetime.now(timezone.utc),
        )
        self._db.add(session)
        await self._db.commit()

        roles = await self._get_user_roles(user.id)
        access_token = create_access_token(str(user.id), session_id=str(session.id), roles=roles)
        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            session_id=session.id,
        )

    # ─── Private Helpers ──────────────────────────────────────────────────────

    async def _get_user_by_phone(self, phone: str) -> Users | None:
        result = await self._db.execute(select(Users).where(Users.phone == phone))
        return result.scalar_one_or_none()

    async def _get_user_by_email(self, email: str) -> Users | None:
        result = await self._db.execute(select(Users).where(Users.email == email))
        return result.scalar_one_or_none()

    async def _get_user_roles(self, user_id: uuid.UUID) -> list[str]:
        stmt = (
            select(Roles.name)
            .join(UserRoles, Roles.id == UserRoles.role_id)
            .where(UserRoles.user_id == user_id, UserRoles.is_active.is_(True))
        )
        result = await self._db.execute(stmt)
        return [row[0] for row in result.all()]

    async def _assign_default_role(self, user_id: uuid.UUID, role_name: str) -> None:
        result = await self._db.execute(select(Roles).where(Roles.name == role_name))
        role = result.scalar_one_or_none()
        if role:
            user_role = UserRoles(user_id=user_id, role_id=role.id)
            self._db.add(user_role)

    async def _update_last_login(self, user_id: uuid.UUID) -> None:
        await self._db.execute(
            update(Users)
            .where(Users.id == user_id)
            .values(last_login_at=datetime.now(timezone.utc))
        )
        await self._db.commit()

    @staticmethod
    def _assert_user_active(user: Users) -> None:
        status_val = user.status.value if hasattr(user.status, "value") else user.status
        if status_val == "BLOCKED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCOUNT_BLOCKED", "message": "Tài khoản đã bị khóa. Vui lòng liên hệ hỗ trợ."},
            )
        if status_val == "PENDING":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ACCOUNT_PENDING", "message": "Tài khoản chưa được kích hoạt."},
            )

    @staticmethod
    def _get_ip(request: Request | None) -> str | None:
        if not request:
            return None
        forwarded = request.headers.get("X-Forwarded-For")
        return forwarded.split(",")[0].strip() if forwarded else request.client.host if request.client else None

    @staticmethod
    def _get_ua(request: Request | None) -> str | None:
        return request.headers.get("User-Agent") if request else None
