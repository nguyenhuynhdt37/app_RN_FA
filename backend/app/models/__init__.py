"""
App models registry — import every model here so Alembic and Base.metadata
can discover all tables automatically.
"""

from app.models.database import (
    Users,
    Roles,
    UserRoles,
    Sessions,
    OtpLogs,
    OauthAccounts,
    PhoneVerifications,
    LoginAttempts,
    SpecializationsReference,
    SkillsReference,
    InterestsReference,
    UserSpecializations,
    UserStatus,
    DeviceType,
    OtpType,
)
