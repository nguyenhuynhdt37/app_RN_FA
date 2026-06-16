"""
App models registry — import every model here so Alembic and Base.metadata
can discover all tables automatically.
"""

from app.models.database import (
    # Enums
    UserStatus,
    DeviceType,
    OtpType,
    CourseLevel,
    CoinTransactionType,
    # Users & Auth
    Users,
    Roles,
    UserRoles,
    Sessions,
    OtpLogs,
    OauthAccounts,
    PhoneVerifications,
    LoginAttempts,
    # Categories (reference table)
    Categories,
    CategoryTranslations,
    CourseCategories,
    # Tags
    Tags,
    TagTranslations,
    # References
    SpecializationsReference,
    SpecializationTranslations,
    SkillsReference,
    SkillTranslations,
    InterestsReference,
    InterestTranslations,
    # User Profile
    UserSpecializations,
    UserInterests,
    # Course
    Courses,
    CourseTranslations,
    CourseLearningOutcomes,
    CourseLearningOutcomeTranslations,
    CoursePrerequisites,
    CoursePrerequisiteTranslations,
    CourseTags,
    # Learning Content
    Sections,
    SectionTranslations,
    LearningUnits,
    LearningUnitTranslations,
    LearningBlocks,
    # Progress
    CourseProgress,
    # Coin
    UserCoins,
    CoinTransactions,
)
