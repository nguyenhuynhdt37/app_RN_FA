from __future__ import annotations

from typing import Any, Optional
import datetime
import enum
import uuid

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Double, Enum, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Text, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class CoinTransactionType(str, enum.Enum):
    PURCHASE = 'PURCHASE'
    COURSE_PURCHASE = 'COURSE_PURCHASE'
    REFUND = 'REFUND'
    BONUS = 'BONUS'
    EARN = 'EARN'


class CourseLevel(str, enum.Enum):
    BEGINNER = 'BEGINNER'
    INTERMEDIATE = 'INTERMEDIATE'
    ADVANCED = 'ADVANCED'


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


class Categories(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='categories_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    icon: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))

    category_translations: Mapped[list['CategoryTranslations']] = relationship('CategoryTranslations', back_populates='category')
    course_categories: Mapped[list['CourseCategories']] = relationship('CourseCategories', back_populates='category')


class InterestsReference(Base):
    __tablename__ = 'interests_reference'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='interests_reference_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    icon_url: Mapped[Optional[str]] = mapped_column(Text)
    position: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))

    interest_translations: Mapped[list['InterestTranslations']] = relationship('InterestTranslations', back_populates='interest')
    user_interests: Mapped[list['UserInterests']] = relationship('UserInterests', back_populates='interest')


class LoginAttempts(Base):
    __tablename__ = 'login_attempts'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='login_attempts_pkey'),
        Index('idx_login_attempts_identifier', 'identifier', 'created_at'),
        Index('idx_login_attempts_ip', 'ip_address', 'created_at'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    failure_reason: Mapped[Optional[str]] = mapped_column(String(50))
    device_type: Mapped[Optional[str]] = mapped_column(String(10))
    ip_address: Mapped[Optional[Any]] = mapped_column(INET)


class PhoneVerifications(Base):
    __tablename__ = 'phone_verifications'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='phone_verifications_pkey'),
        Index('idx_phone_verif_expires', 'expires_at'),
        Index('idx_phone_verif_phone_purpose', 'phone', 'purpose'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    otp_hash: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str] = mapped_column(String(30), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    ip_address: Mapped[Optional[Any]] = mapped_column(INET)
    verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pkey'),
    UniqueConstraint('name', name='roles_name_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)

    user_roles: Mapped[list['UserRoles']] = relationship('UserRoles', back_populates='role')


class SpecializationsReference(Base):
    __tablename__ = 'specializations_reference'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='specializations_reference_pkey'),
    UniqueConstraint('code', name='specializations_reference_code_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    icon_url: Mapped[Optional[str]] = mapped_column(Text)
    position: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))

    skills_reference: Mapped[list['SkillsReference']] = relationship('SkillsReference', back_populates='specialization')
    specialization_translations: Mapped[list['SpecializationTranslations']] = relationship('SpecializationTranslations', back_populates='specialization')
    user_specializations: Mapped[list['UserSpecializations']] = relationship('UserSpecializations', back_populates='specialization')


class Tags(Base):
    __tablename__ = 'tags'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tags_pkey'),
    UniqueConstraint('slug', name='tags_slug_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    tag_translations: Mapped[list['TagTranslations']] = relationship('TagTranslations', back_populates='tag')
    course_tags: Mapped[list['CourseTags']] = relationship('CourseTags', back_populates='tag')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
    CheckConstraint('email IS NOT NULL OR phone IS NOT NULL', name='users_email_or_phone_required'),
        PrimaryKeyConstraint('id', name='users_pkey'),
    UniqueConstraint('email', name='users_email_key'),
    UniqueConstraint('phone', name='users_phone_key'),
    UniqueConstraint('username', name='users_username_key'),
        Index('idx_users_created_at', 'created_at'),
        Index('idx_users_email', 'email'),
        Index('idx_users_phone', 'phone'),
        Index('idx_users_status', 'status'),
        {'comment': 'Main user table with profile data', 'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, values_callable=lambda cls: [member.value for member in cls], name='user_status'), nullable=False, server_default=text("'PENDING'::user_status"))
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    preferred_lang: Mapped[str] = mapped_column(String(5), nullable=False, server_default=text("'vi'::character varying"))
    preferred_currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default=text("'VND'::character varying"))
    is_profile_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('30'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    username: Mapped[Optional[str]] = mapped_column(String(50))
    password_hash: Mapped[Optional[str]] = mapped_column(Text)
    full_name: Mapped[Optional[str]] = mapped_column(String(120))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    learning_goals: Mapped[Optional[str]] = mapped_column(Text)
    interests: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))
    preferred_learning_style: Mapped[Optional[str]] = mapped_column(String(20))
    social_links: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    cover_url: Mapped[Optional[str]] = mapped_column(Text)
    date_of_birth: Mapped[Optional[datetime.date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    instructor_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    last_login_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    coin_transactions: Mapped[list['CoinTransactions']] = relationship('CoinTransactions', back_populates='user')
    courses_created_by: Mapped[list['Courses']] = relationship('Courses', foreign_keys='[Courses.created_by]', back_populates='users')
    courses_instructor: Mapped[list['Courses']] = relationship('Courses', foreign_keys='[Courses.instructor_id]', back_populates='instructor')
    courses_updated_by: Mapped[list['Courses']] = relationship('Courses', foreign_keys='[Courses.updated_by]', back_populates='users_')
    oauth_accounts: Mapped[list['OauthAccounts']] = relationship('OauthAccounts', back_populates='user')
    otp_logs: Mapped[list['OtpLogs']] = relationship('OtpLogs', back_populates='user')
    sessions: Mapped[list['Sessions']] = relationship('Sessions', back_populates='user')
    user_interests: Mapped[list['UserInterests']] = relationship('UserInterests', back_populates='user')
    user_roles_assigned_by: Mapped[list['UserRoles']] = relationship('UserRoles', foreign_keys='[UserRoles.assigned_by]', back_populates='users')
    user_roles_user: Mapped[list['UserRoles']] = relationship('UserRoles', foreign_keys='[UserRoles.user_id]', back_populates='user')
    user_specializations: Mapped[list['UserSpecializations']] = relationship('UserSpecializations', back_populates='user')
    course_progress: Mapped[list['CourseProgress']] = relationship('CourseProgress', back_populates='user')


class CategoryTranslations(Base):
    __tablename__ = 'category_translations'
    __table_args__ = (
    CheckConstraint("lang::text = ANY (ARRAY['vi'::character varying, 'en'::character varying]::text[])", name='category_translations_lang_check'),
    ForeignKeyConstraint(['category_id'], ['public.categories.id'], ondelete='CASCADE', name='category_translations_category_id_fkey'),
        PrimaryKeyConstraint('id', name='category_translations_pkey'),
    UniqueConstraint('category_id', 'lang', name='category_translations_category_id_lang_key'),
        Index('idx_category_translations_category_lang', 'category_id', 'lang'),
        Index('idx_category_translations_lang', 'lang'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    category_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_auto_translated: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))

    category: Mapped['Categories'] = relationship('Categories', back_populates='category_translations')


class CoinTransactions(Base):
    __tablename__ = 'coin_transactions'
    __table_args__ = (
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='coin_transactions_user_id_fkey'),
        PrimaryKeyConstraint('id', name='coin_transactions_pkey'),
        Index('idx_coin_tx_created_at', 'created_at'),
        Index('idx_coin_tx_type', 'type'),
        Index('idx_coin_tx_user_id', 'user_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    type: Mapped[CoinTransactionType] = mapped_column(Enum(CoinTransactionType, values_callable=lambda cls: [member.value for member in cls], name='coin_transaction_type'), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    extra_data: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    description: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped['Users'] = relationship('Users', back_populates='coin_transactions')


class Courses(Base):
    __tablename__ = 'courses'
    __table_args__ = (
    ForeignKeyConstraint(['created_by'], ['public.users.id'], ondelete='SET NULL', name='courses_created_by_fkey'),
    ForeignKeyConstraint(['instructor_id'], ['public.users.id'], ondelete='SET NULL', name='courses_instructor_id_fkey'),
    ForeignKeyConstraint(['updated_by'], ['public.users.id'], ondelete='SET NULL', name='courses_updated_by_fkey'),
        PrimaryKeyConstraint('id', name='courses_pkey'),
    UniqueConstraint('default_slug', name='courses_default_slug_key'),
        Index('idx_courses_created_at', 'created_at'),
        Index('idx_courses_instructor', 'instructor_id'),
        Index('idx_courses_level', 'level'),
        Index('idx_courses_published', 'is_published', postgresql_where='(is_published = true)'),
        {'comment': 'Course catalog with pricing and analytics', 'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    level: Mapped[CourseLevel] = mapped_column(Enum(CourseLevel, values_callable=lambda cls: [member.value for member in cls], name='course_level'), nullable=False, server_default=text("'BEGINNER'::course_level"))
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default=text("'VND'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    default_slug: Mapped[Optional[str]] = mapped_column(String(255))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text)
    preview_video_type: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('1'))
    estimated_duration: Mapped[Optional[int]] = mapped_column(Integer)
    difficulty_score: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('1'))
    base_price: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    views: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    total_enrolls: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    revenue: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    rating_avg: Mapped[Optional[float]] = mapped_column(Double(53), server_default=text('0'))
    lessons_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    approval_status: Mapped[Optional[str]] = mapped_column(String(20))
    approval_note: Mapped[Optional[str]] = mapped_column(Text)
    instructor_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='courses_created_by')
    instructor: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[instructor_id], back_populates='courses_instructor')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='courses_updated_by')
    course_categories: Mapped[list['CourseCategories']] = relationship('CourseCategories', back_populates='course')
    course_learning_outcomes: Mapped[list['CourseLearningOutcomes']] = relationship('CourseLearningOutcomes', back_populates='course')
    course_prerequisites: Mapped[list['CoursePrerequisites']] = relationship('CoursePrerequisites', back_populates='course')
    course_tags: Mapped[list['CourseTags']] = relationship('CourseTags', back_populates='course')
    course_translations: Mapped[list['CourseTranslations']] = relationship('CourseTranslations', back_populates='course')
    sections: Mapped[list['Sections']] = relationship('Sections', back_populates='course')


class InterestTranslations(Base):
    __tablename__ = 'interest_translations'
    __table_args__ = (
    ForeignKeyConstraint(['interest_id'], ['public.interests_reference.id'], ondelete='CASCADE', name='interest_translations_interest_id_fkey'),
        PrimaryKeyConstraint('id', name='interest_translations_pkey'),
    UniqueConstraint('interest_id', 'lang', name='interest_translations_interest_id_lang_key'),
        Index('idx_interest_translations_lang', 'lang'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    interest_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)

    interest: Mapped['InterestsReference'] = relationship('InterestsReference', back_populates='interest_translations')


class OauthAccounts(Base):
    __tablename__ = 'oauth_accounts'
    __table_args__ = (
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='oauth_accounts_user_id_fkey'),
        PrimaryKeyConstraint('id', name='oauth_accounts_pkey'),
    UniqueConstraint('provider', 'provider_uid', name='oauth_accounts_provider_provider_uid_key'),
        Index('idx_oauth_user_id', 'user_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
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
        Index('idx_otp_logs_expires', 'expires_at'),
        Index('idx_otp_logs_user_id', 'user_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    type: Mapped[OtpType] = mapped_column(Enum(OtpType, values_callable=lambda cls: [member.value for member in cls], name='otp_type'), nullable=False)
    otp_hash: Mapped[str] = mapped_column(String(10), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='otp_logs')


class Sessions(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='sessions_user_id_fkey'),
        PrimaryKeyConstraint('id', name='sessions_pkey'),
    UniqueConstraint('refresh_token_hash', name='sessions_refresh_token_hash_key'),
        Index('idx_sessions_active', 'user_id', postgresql_where='(revoked_at IS NULL)'),
        Index('idx_sessions_expires_at', 'expires_at'),
        Index('idx_sessions_user_id', 'user_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    refresh_token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    device_type: Mapped[DeviceType] = mapped_column(Enum(DeviceType, values_callable=lambda cls: [member.value for member in cls], name='device_type'), nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    device_name: Mapped[Optional[str]] = mapped_column(String(255))
    device_token: Mapped[Optional[str]] = mapped_column(Text)
    push_provider: Mapped[Optional[str]] = mapped_column(String(10))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    ip_address: Mapped[Optional[Any]] = mapped_column(INET)
    revoked_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    last_used_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    user: Mapped['Users'] = relationship('Users', back_populates='sessions')


class SkillsReference(Base):
    __tablename__ = 'skills_reference'
    __table_args__ = (
    ForeignKeyConstraint(['specialization_id'], ['public.specializations_reference.id'], ondelete='CASCADE', name='skills_reference_specialization_id_fkey'),
        PrimaryKeyConstraint('id', name='skills_reference_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    specialization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    icon_url: Mapped[Optional[str]] = mapped_column(Text)
    position: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))

    specialization: Mapped['SpecializationsReference'] = relationship('SpecializationsReference', back_populates='skills_reference')
    skill_translations: Mapped[list['SkillTranslations']] = relationship('SkillTranslations', back_populates='skill')


class SpecializationTranslations(Base):
    __tablename__ = 'specialization_translations'
    __table_args__ = (
    ForeignKeyConstraint(['specialization_id'], ['public.specializations_reference.id'], ondelete='CASCADE', name='specialization_translations_specialization_id_fkey'),
        PrimaryKeyConstraint('id', name='specialization_translations_pkey'),
    UniqueConstraint('specialization_id', 'lang', name='specialization_translations_specialization_id_lang_key'),
        Index('idx_specialization_translations_lang', 'lang'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    specialization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)

    specialization: Mapped['SpecializationsReference'] = relationship('SpecializationsReference', back_populates='specialization_translations')


class TagTranslations(Base):
    __tablename__ = 'tag_translations'
    __table_args__ = (
    ForeignKeyConstraint(['tag_id'], ['public.tags.id'], ondelete='CASCADE', name='tag_translations_tag_id_fkey'),
        PrimaryKeyConstraint('id', name='tag_translations_pkey'),
    UniqueConstraint('tag_id', 'lang', name='tag_translations_tag_id_lang_key'),
        Index('idx_tag_translations_lang', 'lang'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    tag_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    tag: Mapped['Tags'] = relationship('Tags', back_populates='tag_translations')


class UserCoins(Base):
    __tablename__ = 'user_coins'
    __table_args__ = (
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='user_coins_user_id_fkey'),
        PrimaryKeyConstraint('user_id', name='user_coins_pkey'),
        {'schema': 'public'}
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    balance: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    total_purchased: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    total_spent: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))


class UserInterests(Base):
    __tablename__ = 'user_interests'
    __table_args__ = (
    ForeignKeyConstraint(['interest_id'], ['public.interests_reference.id'], ondelete='CASCADE', name='user_interests_interest_id_fkey'),
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='user_interests_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'interest_id', name='user_interests_pkey'),
        {'schema': 'public'}
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    interest_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    interest: Mapped['InterestsReference'] = relationship('InterestsReference', back_populates='user_interests')
    user: Mapped['Users'] = relationship('Users', back_populates='user_interests')


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


class UserSpecializations(Base):
    __tablename__ = 'user_specializations'
    __table_args__ = (
    ForeignKeyConstraint(['specialization_id'], ['public.specializations_reference.id'], ondelete='CASCADE', name='user_specializations_specialization_id_fkey'),
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='user_specializations_user_id_fkey'),
        PrimaryKeyConstraint('id', name='user_specializations_pkey'),
        Index('idx_user_specializations_spec_id', 'specialization_id'),
        Index('idx_user_specializations_user_id', 'user_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    specialization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    level: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    skills: Mapped[Optional[dict]] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))

    specialization: Mapped['SpecializationsReference'] = relationship('SpecializationsReference', back_populates='user_specializations')
    user: Mapped['Users'] = relationship('Users', back_populates='user_specializations')


class CourseCategories(Base):
    __tablename__ = 'course_categories'
    __table_args__ = (
    ForeignKeyConstraint(['category_id'], ['public.categories.id'], ondelete='CASCADE', name='course_categories_category_id_fkey'),
    ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='course_categories_course_id_fkey'),
        PrimaryKeyConstraint('course_id', 'category_id', name='course_categories_pkey'),
        {'schema': 'public'}
    )

    course_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    category_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    is_primary: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))

    category: Mapped['Categories'] = relationship('Categories', back_populates='course_categories')
    course: Mapped['Courses'] = relationship('Courses', back_populates='course_categories')


class CourseLearningOutcomes(Base):
    __tablename__ = 'course_learning_outcomes'
    __table_args__ = (
    ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='course_learning_outcomes_course_id_fkey'),
        PrimaryKeyConstraint('id', name='course_learning_outcomes_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    course: Mapped['Courses'] = relationship('Courses', back_populates='course_learning_outcomes')
    course_learning_outcome_translations: Mapped[list['CourseLearningOutcomeTranslations']] = relationship('CourseLearningOutcomeTranslations', back_populates='outcome')


class CoursePrerequisites(Base):
    __tablename__ = 'course_prerequisites'
    __table_args__ = (
    ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='course_prerequisites_course_id_fkey'),
        PrimaryKeyConstraint('id', name='course_prerequisites_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    course: Mapped['Courses'] = relationship('Courses', back_populates='course_prerequisites')
    course_prerequisite_translations: Mapped[list['CoursePrerequisiteTranslations']] = relationship('CoursePrerequisiteTranslations', back_populates='prerequisite')


class CourseTags(Base):
    __tablename__ = 'course_tags'
    __table_args__ = (
    ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='course_tags_course_id_fkey'),
    ForeignKeyConstraint(['tag_id'], ['public.tags.id'], ondelete='CASCADE', name='course_tags_tag_id_fkey'),
        PrimaryKeyConstraint('course_id', 'tag_id', name='course_tags_pkey'),
        Index('idx_course_tags_course', 'course_id'),
        Index('idx_course_tags_tag', 'tag_id'),
        {'schema': 'public'}
    )

    course_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    course: Mapped['Courses'] = relationship('Courses', back_populates='course_tags')
    tag: Mapped['Tags'] = relationship('Tags', back_populates='course_tags')


class CourseTranslations(Base):
    __tablename__ = 'course_translations'
    __table_args__ = (
    ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='course_translations_course_id_fkey'),
        PrimaryKeyConstraint('id', name='course_translations_pkey'),
    UniqueConstraint('course_id', 'lang', name='course_translations_course_id_lang_key'),
    UniqueConstraint('lang', 'slug', name='course_translations_lang_slug_key'),
        Index('idx_course_translations_course_lang', 'course_id', 'lang'),
        Index('idx_course_translations_lang', 'lang'),
        Index('idx_course_translations_lang_slug', 'lang', 'slug', postgresql_where='(slug IS NOT NULL)'),
        Index('idx_course_translations_slug', 'slug', postgresql_where='(slug IS NOT NULL)'),
        {'comment': 'Multilingual course content (Netflix/Netflix style)',
     'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    subtitle: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    slug: Mapped[Optional[str]] = mapped_column(String(255))
    ai_model: Mapped[Optional[str]] = mapped_column(String(100))
    ai_generated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    course: Mapped['Courses'] = relationship('Courses', back_populates='course_translations')


class Sections(Base):
    __tablename__ = 'sections'
    __table_args__ = (
    ForeignKeyConstraint(['course_id'], ['public.courses.id'], ondelete='CASCADE', name='sections_course_id_fkey'),
        PrimaryKeyConstraint('id', name='sections_pkey'),
        {'comment': 'Course sections - title moved to section_translations',
     'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    course: Mapped['Courses'] = relationship('Courses', back_populates='sections')
    learning_units: Mapped[list['LearningUnits']] = relationship('LearningUnits', back_populates='section')
    section_translations: Mapped[list['SectionTranslations']] = relationship('SectionTranslations', back_populates='section')


class SkillTranslations(Base):
    __tablename__ = 'skill_translations'
    __table_args__ = (
    ForeignKeyConstraint(['skill_id'], ['public.skills_reference.id'], ondelete='CASCADE', name='skill_translations_skill_id_fkey'),
        PrimaryKeyConstraint('id', name='skill_translations_pkey'),
    UniqueConstraint('skill_id', 'lang', name='skill_translations_skill_id_lang_key'),
        Index('idx_skill_translations_lang', 'lang'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    skill_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)

    skill: Mapped['SkillsReference'] = relationship('SkillsReference', back_populates='skill_translations')


class CourseLearningOutcomeTranslations(Base):
    __tablename__ = 'course_learning_outcome_translations'
    __table_args__ = (
    ForeignKeyConstraint(['outcome_id'], ['public.course_learning_outcomes.id'], ondelete='CASCADE', name='course_learning_outcome_translations_outcome_id_fkey'),
        PrimaryKeyConstraint('id', name='course_learning_outcome_translations_pkey'),
    UniqueConstraint('outcome_id', 'lang', name='course_learning_outcome_translations_outcome_id_lang_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    outcome_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    text_: Mapped[str] = mapped_column('text', Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    ai_model: Mapped[Optional[str]] = mapped_column(String(100))
    ai_generated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    outcome: Mapped['CourseLearningOutcomes'] = relationship('CourseLearningOutcomes', back_populates='course_learning_outcome_translations')


class CoursePrerequisiteTranslations(Base):
    __tablename__ = 'course_prerequisite_translations'
    __table_args__ = (
    ForeignKeyConstraint(['prerequisite_id'], ['public.course_prerequisites.id'], ondelete='CASCADE', name='course_prerequisite_translations_prerequisite_id_fkey'),
        PrimaryKeyConstraint('id', name='course_prerequisite_translations_pkey'),
    UniqueConstraint('prerequisite_id', 'lang', name='course_prerequisite_translations_prerequisite_id_lang_key'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    prerequisite_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    text_: Mapped[str] = mapped_column('text', Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    prerequisite: Mapped['CoursePrerequisites'] = relationship('CoursePrerequisites', back_populates='course_prerequisite_translations')


class LearningUnits(Base):
    __tablename__ = 'learning_units'
    __table_args__ = (
    ForeignKeyConstraint(['required_unit_id'], ['public.learning_units.id'], ondelete='SET NULL', name='learning_units_required_unit_id_fkey'),
    ForeignKeyConstraint(['section_id'], ['public.sections.id'], ondelete='CASCADE', name='learning_units_section_id_fkey'),
        PrimaryKeyConstraint('id', name='learning_units_pkey'),
        Index('idx_learning_units_section', 'section_id'),
        {'comment': 'Learning units - title moved to learning_unit_translations',
     'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    section_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    is_free: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    base_exp: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('50'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    required_unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    required_unit: Mapped[Optional['LearningUnits']] = relationship('LearningUnits', remote_side=[id], back_populates='required_unit_reverse')
    required_unit_reverse: Mapped[list['LearningUnits']] = relationship('LearningUnits', remote_side=[required_unit_id], back_populates='required_unit')
    section: Mapped['Sections'] = relationship('Sections', back_populates='learning_units')
    course_progress: Mapped[list['CourseProgress']] = relationship('CourseProgress', back_populates='unit')
    learning_blocks: Mapped[list['LearningBlocks']] = relationship('LearningBlocks', back_populates='unit')
    learning_unit_translations: Mapped[list['LearningUnitTranslations']] = relationship('LearningUnitTranslations', back_populates='unit')


class SectionTranslations(Base):
    __tablename__ = 'section_translations'
    __table_args__ = (
    ForeignKeyConstraint(['section_id'], ['public.sections.id'], ondelete='CASCADE', name='section_translations_section_id_fkey'),
        PrimaryKeyConstraint('id', name='section_translations_pkey'),
    UniqueConstraint('section_id', 'lang', name='section_translations_section_id_lang_key'),
        Index('idx_section_translations_lang', 'lang'),
        Index('idx_section_translations_section_lang', 'section_id', 'lang'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    section_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)

    section: Mapped['Sections'] = relationship('Sections', back_populates='section_translations')


class CourseProgress(Base):
    __tablename__ = 'course_progress'
    __table_args__ = (
    ForeignKeyConstraint(['unit_id'], ['public.learning_units.id'], ondelete='CASCADE', name='course_progress_unit_id_fkey'),
    ForeignKeyConstraint(['user_id'], ['public.users.id'], ondelete='CASCADE', name='course_progress_user_id_fkey'),
        PrimaryKeyConstraint('id', name='course_progress_pkey'),
    UniqueConstraint('user_id', 'unit_id', name='course_progress_user_id_unit_id_key'),
        Index('idx_course_progress_completed', 'is_completed', postgresql_where='(is_completed = true)'),
        Index('idx_course_progress_unit', 'unit_id'),
        Index('idx_course_progress_user', 'user_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    unit_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    current_state: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    total_exp_gained: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    last_accessed_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    unit: Mapped['LearningUnits'] = relationship('LearningUnits', back_populates='course_progress')
    user: Mapped['Users'] = relationship('Users', back_populates='course_progress')


class LearningBlocks(Base):
    __tablename__ = 'learning_blocks'
    __table_args__ = (
    ForeignKeyConstraint(['unit_id'], ['public.learning_units.id'], ondelete='CASCADE', name='learning_blocks_unit_id_fkey'),
        PrimaryKeyConstraint('id', name='learning_blocks_pkey'),
        Index('idx_learning_blocks_unit', 'unit_id'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    unit_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    block_type: Mapped[str] = mapped_column(String(50), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    content: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    unit: Mapped['LearningUnits'] = relationship('LearningUnits', back_populates='learning_blocks')


class LearningUnitTranslations(Base):
    __tablename__ = 'learning_unit_translations'
    __table_args__ = (
    ForeignKeyConstraint(['unit_id'], ['public.learning_units.id'], ondelete='CASCADE', name='learning_unit_translations_unit_id_fkey'),
        PrimaryKeyConstraint('id', name='learning_unit_translations_pkey'),
    UniqueConstraint('unit_id', 'lang', name='learning_unit_translations_unit_id_lang_key'),
        Index('idx_learning_unit_translations_lang', 'lang'),
        Index('idx_learning_unit_translations_unit_lang', 'unit_id', 'lang'),
        {'schema': 'public'}
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('uuid_generate_v4()'))
    unit_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text)

    unit: Mapped['LearningUnits'] = relationship('LearningUnits', back_populates='learning_unit_translations')

# === AUTO FIX SUMMARY ===
# Generated by fix_sqlacodegen_models.py v2
# • Fixed class inheritance → Base
# • Fixed indented ForeignKeyConstraint
# • Injected relationship() with back_populates
# • Fixed UUID / ARRAY / JSONB type hints
# • Added necessary imports
# ==========================
