from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class CategoryTranslationBase(BaseModel):
    """Base translation schema."""
    lang: str = Field(..., description="vi|en|jp|kr|fr...")
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class CategoryTranslationCreate(CategoryTranslationBase):
    pass


class CategoryTranslationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class CategoryTranslationRead(CategoryTranslationBase):
    id: UUID
    category_id: UUID
    is_auto_translated: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryTranslationSummary(BaseModel):
    """Compact translation info for category list."""
    lang: str
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ─── Category Base/Read Schemas ────────────────────────────────────────────

class CategoryBase(BaseModel):
    icon: Optional[str] = None


class CategoryRead(CategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    translations: dict[str, CategoryTranslationSummary] = {}
    course_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class CategoryDetail(CategoryRead):
    """Full category với tất cả translations."""
    translations_full: List[CategoryTranslationRead] = []

    model_config = ConfigDict(from_attributes=True)


class CategoryCourseTranslationSummary(BaseModel):
    """Compact multilingual course content for category detail."""
    lang: str
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CategoryCourseSummary(BaseModel):
    """Course summary embedded in full category detail."""
    id: UUID
    default_slug: Optional[str] = None
    thumbnail_url: Optional[str] = None
    level: str
    is_published: bool
    approval_status: Optional[str] = None
    base_price: int = 0
    currency: str = "VND"
    estimated_duration: Optional[int] = None
    lessons_count: int = 0
    views: int = 0
    total_enrolls: int = 0
    revenue: int = 0
    rating_avg: float = 0.0
    created_at: datetime
    updated_at: datetime
    translations: dict[str, CategoryCourseTranslationSummary] = {}


class CategoryDetailStats(BaseModel):
    """Aggregated learning/business metrics for one category."""
    total_courses: int = 0
    published_courses: int = 0
    draft_courses: int = 0
    total_enrolls: int = 0
    total_revenue: int = 0
    total_views: int = 0
    avg_rating: float = 0.0


class CategoryFullDetail(CategoryDetail):
    """Admin-grade category detail with translations, stats and related courses."""
    stats: CategoryDetailStats
    courses: List[CategoryCourseSummary] = []
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    """Response cho list categories."""
    items: List[CategoryRead]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ─── Create/Update Schemas ───────────────────────────────────────────────────

class CategoryCreate(CategoryBase):
    translations: dict[str, CategoryTranslationCreate] = Field(
        ..., 
        min_length=1,
        description="Ít nhất 1 translation (thường là 'vi')"
    )


class CategoryCreateFromVietnamese(BaseModel):
    """Admin input: nhập tiếng Việt, hệ thống tự sinh bản dịch tiếng Anh."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    auto_translate_en: bool = Field(
        True,
        description="Tự động dùng AI dịch name/description sang tiếng Anh",
    )

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())
        if not normalized:
            raise ValueError("CATEGORY_NAME_REQUIRED")
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class CategoryUpdateFromVietnamese(BaseModel):
    """Admin update: chỉ sửa tiếng Việt, hệ thống tự sinh lại tiếng Anh nếu có thay đổi."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = " ".join(value.strip().split())
        if not normalized:
            raise ValueError("CATEGORY_NAME_REQUIRED")
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class CategoryUpdate(BaseModel):
    icon: Optional[str] = None
    translations: Optional[dict[str, CategoryTranslationUpdate]] = None


class CategoryBulkUpdate(BaseModel):
    """Bulk update positions hoặc icons."""
    updates: List[dict] = Field(
        ...,
        description="List of {id, icon?, position?} objects"
    )


# ─── Filter/Sort Schemas ────────────────────────────────────────────────────

class CategoryFilters(BaseModel):
    """Query params cho filtering."""
    lang: Optional[str] = Field("vi", description="Language code (vi|en|jp...)")
    search: Optional[str] = Field(None, description="Search in name/description")
    has_courses: Optional[bool] = Field(None, description="Filter categories with/without courses")
    min_course_count: Optional[int] = Field(None, ge=0, description="Min course count")
    sort_by: str = Field("created_at", description="Sort field: created_at|updated_at|name|position|course_count")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort direction")


class CategoryStats(BaseModel):
    """Statistics cho một category."""
    category_id: UUID
    total_courses: int
    total_enrolls: int
    total_revenue: int

    model_config = ConfigDict(from_attributes=True)


class CategoryStatsResponse(BaseModel):
    """Response cho stats endpoint."""
    stats: List[CategoryStats]
    generated_at: datetime
