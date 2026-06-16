from __future__ import annotations

from typing import Any, Optional
import datetime
import enum
import uuid

from sqlalchemy import (
    ARRAY, Boolean, CheckConstraint, Column, Date, DateTime, Enum, ForeignKey,
    ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String,
    Table, Text, UniqueConstraint, Uuid, text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


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
    cover_url: Mapped[Optional[str]] = mapped_column(Text)
    date_of_birth: Mapped[Optional[datetime.date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    # metadata cho giảng viên: {"headline": "...", "rating": 4.5, "verified": true}
    instructor_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))

    oauth_accounts: Mapped[list['OauthAccounts']] = relationship('OauthAccounts', back_populates='user')
    otp_logs: Mapped[list['OtpLogs']] = relationship('OtpLogs', back_populates='user')
    sessions: Mapped[list['Sessions']] = relationship('Sessions', back_populates='user')
    user_roles_assigned_by: Mapped[list['UserRoles']] = relationship('UserRoles', foreign_keys='[UserRoles.assigned_by]', back_populates='users')
    user_roles_user: Mapped[list['UserRoles']] = relationship('UserRoles', foreign_keys='[UserRoles.user_id]', back_populates='user')
    specializations: Mapped[list['UserSpecializations']] = relationship('UserSpecializations', back_populates='user', cascade='all, delete-orphan')
    coin_account: Mapped[Optional['UserCoins']] = relationship('UserCoins', back_populates='user', uselist=False)
    coin_transactions: Mapped[list['CoinTransactions']] = relationship('CoinTransactions', back_populates='user')


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

class CourseLevel(str, enum.Enum):
    BEGINNER = 'BEGINNER'
    INTERMEDIATE = 'INTERMEDIATE'
    ADVANCED = 'ADVANCED'


# ══════════════════════════════════════════════════════════════════════════════
# TRANSLATION MODELS - i18n Architecture (Netflix/Spotify/Duolingo style)
# ══════════════════════════════════════════════════════════════════════════════

class CourseTranslation(Base):
    """Dịch khóa học theo ngôn ngữ. Mỗi khóa có thể có nhiều bản dịch."""
    __tablename__ = 'course_translations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='course_translations_pkey'),
        UniqueConstraint('course_id', 'lang', name='uq_course_translation_lang'),
        Index('ix_course_translations_course_id', 'course_id'),
        Index('ix_course_translations_lang', 'lang'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('public.courses.id', ondelete='CASCADE'), nullable=False)
    lang: Mapped[str] = mapped_column(String(5), nullable=False, comment='vi|en|jp|kr|fr...')
    title: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))
    subtitle: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    learning_outcomes: Mapped[list[str]] = mapped_column(ARRAY(String), server_default=text("'{}'::text[]"))
    prerequisites: Mapped[list[str]] = mapped_column(ARRAY(String), server_default=text("'{}'::text[]"))
    slug: Mapped[Optional[str]] = mapped_column(String(255))

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    course: Mapped['Courses'] = relationship('Courses', back_populates='translations')


class SectionTranslation(Base):
    """Dịch phần (section) theo ngôn ngữ."""
    __tablename__ = 'section_translations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='section_translations_pkey'),
        UniqueConstraint('section_id', 'lang', name='uq_section_translation_lang'),
        Index('ix_section_translations_section_id', 'section_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    section_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('public.sections.id', ondelete='CASCADE'), nullable=False)
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    section: Mapped['Sections'] = relationship('Sections', back_populates='translations')


class CategoryTranslation(Base):
    """Dịch danh mục theo ngôn ngữ."""
    __tablename__ = 'category_translations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='category_translations_pkey'),
        UniqueConstraint('category_id', 'lang', name='uq_category_translation_lang'),
        Index('ix_category_translations_category_id', 'category_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    category_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('public.course_categories.id', ondelete='CASCADE'), nullable=False)
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, server_default=text("''"))
    description: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    category: Mapped['CourseCategories'] = relationship('CourseCategories', back_populates='translations')


class CourseCategories(Base, TimestampMixin):
    __tablename__ = 'course_categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='course_categories_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    icon_url: Mapped[Optional[str]] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))

    # Translations
    translations: Mapped[list['CategoryTranslation']] = relationship(
        'CategoryTranslation', back_populates='category', cascade='all, delete-orphan'
    )


class Courses(Base):
    __tablename__ = 'courses'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='courses_pkey'),
        UniqueConstraint('default_slug', name='courses_slug_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    # Chuyển sang mảng ID danh mục để hỗ trợ đa danh mục
    category_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(postgresql.ARRAY(Uuid), server_default=text("'{}'::uuid[]"))
    default_slug: Mapped[Optional[str]] = mapped_column(String(255))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text)
    preview_video_type: Mapped[int] = mapped_column(Integer, server_default=text('1'), comment="1=Không có video, 2=Dùng video khóa học")
    level: Mapped[CourseLevel] = mapped_column(
        Enum(CourseLevel, values_callable=lambda cls: [member.value for member in cls], name='course_level'),
        nullable=False, server_default=text("'BEGINNER'::course_level")
    )
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer)
    difficulty_score: Mapped[int] = mapped_column(Integer, server_default=text('1'))
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    base_price: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default=text("'VND'::character varying"))
    views: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    total_enrolls: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    revenue: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    rating_avg: Mapped[float] = mapped_column(server_default=text('0'))
    lessons_count: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    approval_status: Mapped[Optional[str]] = mapped_column(String(20))
    approval_note: Mapped[Optional[str]] = mapped_column(Text)
    
    # Ownership & Audit
    instructor_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('public.users.id', ondelete='SET NULL'))
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('public.users.id', ondelete='SET NULL'))
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('public.users.id', ondelete='SET NULL'))
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    # Translations - mạnh hơn nhiều so với _vi/_en columns!
    translations: Mapped[list['CourseTranslation']] = relationship(
        'CourseTranslation', back_populates='course', cascade='all, delete-orphan'
    )
    sections: Mapped[list['Sections']] = relationship('Sections', back_populates='course', cascade='all, delete-orphan')
    instructor: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[instructor_id])
    creator: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by])
    updater: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by])


class Sections(Base):
    __tablename__ = 'sections'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='sections_pkey'),
        Index('ix_sections_course_position', 'course_id', 'position'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('public.courses.id', ondelete='CASCADE'), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    # Relationships
    course: Mapped['Courses'] = relationship('Courses', back_populates='sections')
    units: Mapped[list['LearningUnits']] = relationship('LearningUnits', back_populates='section', cascade='all, delete-orphan')
    translations: Mapped[list['SectionTranslation']] = relationship(
        'SectionTranslation', back_populates='section', cascade='all, delete-orphan'
    )


class LearningUnits(Base):
    __tablename__ = 'learning_units'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='learning_units_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    section_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('public.sections.id', ondelete='CASCADE'), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    is_free: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    base_exp: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('50'))
    required_unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey('public.learning_units.id', ondelete='SET NULL'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    section: Mapped['Sections'] = relationship('Sections', back_populates='units')
    blocks: Mapped[list['LearningBlocks']] = relationship('LearningBlocks', back_populates='unit', cascade='all, delete-orphan')


class LearningBlocks(Base):
    __tablename__ = 'learning_blocks'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='learning_blocks_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    unit_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('public.learning_units.id', ondelete='CASCADE'), nullable=False)
    block_type: Mapped[str] = mapped_column(String(50), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    unit: Mapped['LearningUnits'] = relationship('LearningUnits', back_populates='blocks')


class CourseProgress(Base):
    __tablename__ = 'course_progress'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='course_progress_pkey'),
        UniqueConstraint('user_id', 'unit_id', name='idx_user_unit_progress'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('public.users.id', ondelete='CASCADE'), nullable=False)
    unit_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('public.learning_units.id', ondelete='CASCADE'), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    current_state: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    total_exp_gained: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    last_accessed_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))


# ══════════════════════════════════════════════════════════════════════════════
# COIN SYSTEM - Mua khóa học bằng coin
# ══════════════════════════════════════════════════════════════════════════════

class CoinTransactionType(str, enum.Enum):
    PURCHASE = 'PURCHASE'           # Mua coin bằng VND
    COURSE_PURCHASE = 'COURSE_PURCHASE'  # Dùng coin mua khóa học
    REFUND = 'REFUND'               # Hoàn coin (hủy khóa học)
    BONUS = 'BONUS'                 # Bonus từ admin
    EARN = 'EARN'                   # Kiếm được coin (nếu cần)


class UserCoins(Base):
    """Số dư coin của user."""
    __tablename__ = 'user_coins'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='user_coins_pkey'),
        ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='user_coins_user_id_fkey'),
        {'schema': 'public'}
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    balance: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'), comment='Số coin hiện có')
    total_purchased: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'), comment='Tổng coin đã mua')
    total_spent: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'), comment='Tổng coin đã tiêu')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    user: Mapped['Users'] = relationship('Users', back_populates='coin_account')


class CoinTransactions(Base):
    """Lịch sử giao dịch coin."""
    __tablename__ = 'coin_transactions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='coin_transactions_pkey'),
        Index('idx_coin_tx_user_id', 'user_id'),
        Index('idx_coin_tx_type', 'type'),
        Index('idx_coin_tx_created_at', 'created_at'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('public.users.id', ondelete='CASCADE'), nullable=False)
    type: Mapped[CoinTransactionType] = mapped_column(
        Enum(CoinTransactionType, values_callable=lambda cls: [member.value for member in cls], name='coin_transaction_type'),
        nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False, comment='Số coin thay đổi (+/-)')
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False, comment='Số dư sau giao dịch')
    
    # Thông tin mở rộng (JSONB)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"), comment='Thông tin bổ sung: order_id, course_id, payment_info...')
    
    # Mô tả giao dịch
    description: Mapped[Optional[str]] = mapped_column(Text, comment='Mô tả: "Mua 100 coin", "Thanh toán khóa học IELTS"')
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    user: Mapped['Users'] = relationship('Users', back_populates='coin_transactions')
