from __future__ import annotations

from typing import Any, Optional
import datetime
import enum
import uuid

from sqlalchemy import (
    ARRAY, Boolean, CheckConstraint, Column, Date, DateTime, Enum,
    ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String,
    Table, Text, UniqueConstraint, Uuid, text,
)
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class DeviceType(str, enum.Enum):
    WEB = 'WEB'
    IOS = 'IOS'
    ANDROID = 'ANDROID'


class OtpType(str, enum.Enum):
    REGISTER = 'REGISTER'
    LOGIN = 'LOGIN'
    RESET_PASSWORD = 'RESET_PASSWORD'


class UserStatus(str, enum.Enum):
    PENDING = 'PENDING'
    ACTIVE = 'ACTIVE'
    BLOCKED = 'BLOCKED'


class LoginAttempts(Base):
    __tablename__ = 'login_attempts'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='login_attempts_pkey'),
        Index('idx_login_attempts_identifier', 'identifier', 'created_at'),
        Index('idx_login_attempts_ip', 'ip_address', 'created_at'),
        {
            'comment': 'Audit log đăng nhập — dùng để detect brute force & suspicious activity',
            'schema': 'public',
        }
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    ip_address: Mapped[Optional[Any]] = mapped_column(INET)
    device_type: Mapped[Optional[str]] = mapped_column(String(10))
    failure_reason: Mapped[Optional[str]] = mapped_column(String(50))


class PhoneVerifications(Base):
    __tablename__ = 'phone_verifications'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='phone_verifications_pkey'),
        Index('idx_phone_verif_expires', 'expires_at'),
        Index('idx_phone_verif_phone_purpose', 'phone', 'purpose'),
        {
            'comment': 'OTP pre-register: dùng trước khi user được tạo. Sau khi verify → tạo user.',
            'schema': 'public',
        }
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    otp_hash: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str] = mapped_column(String(30), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    ip_address: Mapped[Optional[Any]] = mapped_column(INET)


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pkey'),
        UniqueConstraint('name', name='roles_name_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)

    user_roles: Mapped[list['UserRoles']] = relationship('UserRoles', back_populates='role')


t_user_with_roles = Table(
    'user_with_roles', Base.metadata,
    Column('id', Uuid),
    Column('email', String(255)),
    Column('phone', String(20)),
    Column('full_name', String(120)),
    Column('status', Enum(UserStatus, values_callable=lambda cls: [member.value for member in cls], name='user_status')),
    Column('is_verified', Boolean),
    Column('avatar_url', Text),
    Column('device_platform', String(10)),
    Column('roles', ARRAY(String())),
    Column('created_at', DateTime(True)),
    Column('last_login_at', DateTime(True)),
    schema='public'
)


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint('email IS NOT NULL OR phone IS NOT NULL', name='users_email_or_phone_required'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        UniqueConstraint('phone', name='users_phone_key'),
        UniqueConstraint('username', name='users_username_key'),
        Index('idx_users_email', 'email'),
        Index('idx_users_phone', 'phone'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, values_callable=lambda cls: [member.value for member in cls], name='user_status'),
        nullable=False, server_default=text("'PENDING'::user_status"),
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    preferred_lang: Mapped[str] = mapped_column(String(5), nullable=False, server_default=text("'vi'::character varying"))
    preferred_currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default=text("'VND'::character varying"))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    password_hash: Mapped[Optional[str]] = mapped_column(Text)
    full_name: Mapped[Optional[str]] = mapped_column(String(120))
    username: Mapped[Optional[str]] = mapped_column(String(50))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    is_profile_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    learning_goals: Mapped[Optional[str]] = mapped_column(Text)
    interests: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('30'))
    preferred_learning_style: Mapped[Optional[str]] = mapped_column(String(20))
    social_links: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    last_login_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    date_of_birth: Mapped[Optional[datetime.date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    # device_token + device_platform đã chuyển sang Sessions

    oauth_accounts: Mapped[list['OauthAccounts']] = relationship('OauthAccounts', back_populates='user')
    otp_logs: Mapped[list['OtpLogs']] = relationship('OtpLogs', back_populates='user')
    sessions: Mapped[list['Sessions']] = relationship('Sessions', back_populates='user')
    user_roles_assigned_by: Mapped[list['UserRoles']] = relationship('UserRoles', foreign_keys='[UserRoles.assigned_by]', back_populates='users')
    user_roles_user: Mapped[list['UserRoles']] = relationship('UserRoles', foreign_keys='[UserRoles.user_id]', back_populates='user')
    specializations: Mapped[list['UserSpecializations']] = relationship('UserSpecializations', back_populates='user', cascade='all, delete-orphan')


class UserSpecializations(Base):
    __tablename__ = 'user_specializations'
    __table_args__ = (
        ForeignKeyConstraint(['specialization_id'], ['public.specializations_reference.id'], ondelete='CASCADE', name='user_specializations_spec_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='user_specializations_user_id_fkey'),
        PrimaryKeyConstraint('id', name='user_specializations_pkey'),
        Index('idx_user_specializations_user_id', 'user_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    specialization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    level: Mapped[str] = mapped_column(String(50), nullable=False)
    skills: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    user: Mapped['Users'] = relationship('Users', back_populates='specializations')
    specialization: Mapped['SpecializationsReference'] = relationship('SpecializationsReference')


class OauthAccounts(Base):
    __tablename__ = 'oauth_accounts'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='oauth_accounts_user_id_fkey'),
        PrimaryKeyConstraint('id', name='oauth_accounts_pkey'),
        UniqueConstraint('provider', 'provider_uid', name='oauth_accounts_provider_provider_uid_key'),
        Index('idx_oauth_user_id', 'user_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_uid: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    provider_email: Mapped[Optional[str]] = mapped_column(String(255))
    access_token: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    token_expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    user: Mapped['Users'] = relationship('Users', back_populates='oauth_accounts')


class OtpLogs(Base):
    __tablename__ = 'otp_logs'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='otp_logs_user_id_fkey'),
        PrimaryKeyConstraint('id', name='otp_logs_pkey'),
        Index('idx_otp_logs_user_id', 'user_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    otp_hash: Mapped[str] = mapped_column(String(10), nullable=False, comment='SHA-256 hash của OTP code — KHÔNG lưu plain text')
    type: Mapped[OtpType] = mapped_column(
        Enum(OtpType, values_callable=lambda cls: [member.value for member in cls], name='otp_type'),
        nullable=False,
    )
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    phone: Mapped[Optional[str]] = mapped_column(String(20))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='otp_logs')


class Sessions(Base):
    """
    1 user → nhiều sessions (multi-device).
    - refresh_token_hash: unique index để lookup O(log n)
    - device_token: FCM/APNS push token cho TỪNG thiết bị riêng biệt
    - revoked_at IS NULL: partial index để query active sessions nhanh
    """
    __tablename__ = 'sessions'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='sessions_user_id_fkey'),
        PrimaryKeyConstraint('id', name='sessions_pkey'),
        UniqueConstraint('refresh_token_hash', name='sessions_refresh_token_hash_key'),
        Index('idx_sessions_expires_at', 'expires_at'),
        Index('idx_sessions_user_id', 'user_id'),
        # Partial index: chỉ index active sessions (revoked_at IS NULL)
        Index('idx_sessions_active', 'user_id', postgresql_where=text('revoked_at IS NULL')),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    refresh_token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    device_type: Mapped[DeviceType] = mapped_column(
        Enum(DeviceType, values_callable=lambda cls: [member.value for member in cls], name='device_type'),
        nullable=False,
    )
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    # Per-device push notification token
    device_token: Mapped[Optional[str]] = mapped_column(Text, comment='FCM (Android/Web) hoặc APNS (iOS) push token')
    push_provider: Mapped[Optional[str]] = mapped_column(String(10), comment='FCM | APNS | None')
    device_name: Mapped[Optional[str]] = mapped_column(String(255))
    ip_address: Mapped[Optional[Any]] = mapped_column(INET)
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    last_used_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    revoked_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    user: Mapped['Users'] = relationship('Users', back_populates='sessions')


class UserRoles(Base):
    __tablename__ = 'user_roles'
    __table_args__ = (
        ForeignKeyConstraint(['assigned_by'], ['public.users.id'], ondelete='SET NULL', name='user_roles_assigned_by_fkey'),
        ForeignKeyConstraint(['role_id'], ['public.roles.id'], ondelete='CASCADE', name='user_roles_role_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='user_roles_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'role_id', name='user_roles_pkey'),
        Index('idx_user_roles_role_id', 'role_id'),
        Index('idx_user_roles_user_id', 'user_id'),
        {'schema': 'public'}
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    assigned_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    assigned_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[assigned_by], back_populates='user_roles_assigned_by')
    role: Mapped['Roles'] = relationship('Roles', back_populates='user_roles')
    user: Mapped['Users'] = relationship('Users', foreign_keys=[user_id], back_populates='user_roles_user')


class SpecializationsReference(Base):
    __tablename__ = 'specializations_reference'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='specializations_reference_pkey'),
        UniqueConstraint('code', name='specializations_reference_code_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_vi: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))


class SkillsReference(Base):
    __tablename__ = 'skills_reference'
    __table_args__ = (
        ForeignKeyConstraint(['specialization_id'], ['public.specializations_reference.id'], ondelete='CASCADE', name='skills_reference_specialization_id_fkey'),
        PrimaryKeyConstraint('id', name='skills_reference_pkey'),
        Index('idx_skills_ref_specialization', 'specialization_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    specialization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_vi: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))


class InterestsReference(Base):
    __tablename__ = 'interests_reference'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='interests_reference_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_vi: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
