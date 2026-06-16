from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum
import math


class CourseLevel(str, Enum):
    BEGINNER = 'BEGINNER'
    INTERMEDIATE = 'INTERMEDIATE'
    ADVANCED = 'ADVANCED'


class CourseSort(str, Enum):
    NEWEST = 'newest'
    POPULAR = 'popular'
    RATING = 'rating'
    PRICE_ASC = 'price_asc'
    PRICE_DESC = 'price_desc'


# ─── Translation Schemas ─────────────────────────────────────────────────────

class TranslationBase(BaseModel):
    """Base cho translation schemas."""
    lang: str = Field(..., description="vi|en|jp|kr|fr...")
    title: str = ""


class CourseTranslationRead(BaseModel):
    """Translation cho khóa học."""
    lang: str
    title: str = ""
    subtitle: Optional[str] = None
    description: Optional[str] = None
    learning_outcomes: List[str] = []
    prerequisites: List[str] = []
    slug: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SectionTranslationRead(BaseModel):
    """Translation cho section."""
    lang: str
    title: str = ""

    model_config = ConfigDict(from_attributes=True)


class CategoryTranslationRead(BaseModel):
    """Translation cho category."""
    lang: str
    name: str = ""
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ─── Instructor Schemas ────────────────────────────────────────────────────────

class InstructorShort(BaseModel):
    id: UUID
    full_name: str
    avatar_url: Optional[str] = None
    instructor_metadata: Optional[Dict[str, Any]] = {}

    model_config = ConfigDict(from_attributes=True)


# ─── Learning Block Schemas ────────────────────────────────────────────────────

class LearningBlockRead(BaseModel):
    id: UUID
    block_type: str  # 'VIDEO', 'QUIZ', 'TEXT', 'FLASHCARD'
    position: int
    content: Dict[str, Any]
    
    model_config = ConfigDict(from_attributes=True)


# ─── Learning Unit Schemas ─────────────────────────────────────────────────────

class LearningUnitBase(BaseModel):
    title: str
    position: int
    is_free: bool = False
    base_exp: int = 50

class LearningUnitRead(LearningUnitBase):
    id: UUID
    required_unit_id: Optional[UUID] = None
    
    model_config = ConfigDict(from_attributes=True)

class LearningUnitDetail(LearningUnitRead):
    blocks: List[LearningBlockRead] = []


# ─── Section Schemas ───────────────────────────────────────────────────────────

class SectionRead(BaseModel):
    id: UUID
    position: int
    translations: Dict[str, SectionTranslationRead] = {}  # {"vi": {...}, "en": {...}}
    units: List[LearningUnitRead] = []
    
    model_config = ConfigDict(from_attributes=True)


# ─── Course Schemas ───────────────────────────────────────────────────────────

class CourseBase(BaseModel):
    """Base course - không có translations (truyền qua translations dict)."""
    default_slug: Optional[str] = Field(default=None, alias="slug")  # alias for backward compat
    thumbnail_url: Optional[str] = None
    preview_video_type: int = Field(default=1, description="1=Không có video, 2=Dùng video khóa học")
    level: CourseLevel = CourseLevel.BEGINNER
    tags: List[str] = Field(default_factory=list)
    estimated_duration: Optional[int] = None
    difficulty_score: int = 1
    base_price: int = 0
    currency: str = "VND"


class CourseTranslationsInput(BaseModel):
    """Input translations khi tạo/cập nhật course."""
    vi: Optional[Dict[str, Any]] = Field(default_factory=None, description="Translation tiếng Việt")
    en: Optional[Dict[str, Any]] = Field(default_factory=None, description="Translation tiếng Anh")
    # Có thể thêm: jp, kr, fr...


class CourseRead(CourseBase):
    id: UUID
    category_ids: List[UUID] = []
    translations: Dict[str, CourseTranslationRead] = {}  # {"vi": {...}, "en": {...}}
    instructor_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_published: bool
    created_at: datetime
    updated_at: datetime
    instructor: Optional[InstructorShort] = None
    views: int = 0
    total_enrolls: int = 0
    revenue: int = 0
    rating_avg: float = 0.0
    lessons_count: int = 0
    approval_status: Optional[str] = None
    approval_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @property
    def price_coin(self) -> int:
        """Tính giá coin tự động: base_price / 1000, làm tròn lên nếu dư."""
        if self.base_price == 0:
            return 0
        coin = self.base_price // 1000
        if self.base_price % 1000 > 0:
            coin += 1
        return coin


class CourseDetail(CourseRead):
    sections: List[SectionRead] = []


# ─── Progress Schemas ──────────────────────────────────────────────────────────

class CourseProgressRead(BaseModel):
    unit_id: UUID
    is_completed: bool
    current_state: Dict[str, Any]
    total_exp_gained: int
    completed_at: Optional[datetime] = None
    last_accessed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseCategoryRead(BaseModel):
    id: UUID
    translations: Dict[str, CategoryTranslationRead] = {}  # {"vi": {...}, "en": {...}}
    icon_url: Optional[str] = None
    position: int

    model_config = ConfigDict(from_attributes=True)


# ─── Admin Create/Update Schemas ───────────────────────────────────────────────

class LearningBlockCreate(BaseModel):
    block_type: str
    position: int
    content: Dict[str, Any]

class LearningUnitCreate(BaseModel):
    title: str
    position: int
    is_free: bool = False
    base_exp: int = 50


class SectionTranslationInput(BaseModel):
    """Input translation cho section."""
    lang: str
    title: str


class SectionCreate(BaseModel):
    translations: Dict[str, SectionTranslationInput] = {}  # {"vi": {...}, "en": {...}}
    position: int


class SectionUpdate(BaseModel):
    translations: Optional[Dict[str, SectionTranslationInput]] = None
    position: Optional[int] = None


class CourseOutcomeCreate(BaseModel):
    """Input để tạo learning outcome."""
    lang: str
    content: str


class CourseTranslationInput(BaseModel):
    """Input translation cho course."""
    lang: str
    title: str = ""
    subtitle: Optional[str] = None
    description: Optional[str] = None
    learning_outcomes: List[str] = []  # Danh sách chuỗi (cho AI process)
    prerequisites: List[str] = []
    slug: Optional[str] = None


class CourseCreate(CourseBase):
    """Input để tạo course mới."""
    translations: Dict[str, CourseTranslationInput] = {}  # {"vi": {...}, "en": {...}}
    category_ids: Optional[List[UUID]] = Field(default_factory=list)
    instructor_id: Optional[UUID] = None
    is_published: bool = False
    tags: List[str] = Field(default_factory=list)
    learning_outcomes: List[CourseOutcomeCreate] = Field(default_factory=list)


class CourseUpdate(BaseModel):
    """Input để cập nhật course."""
    translations: Optional[Dict[str, CourseTranslationInput]] = None
    thumbnail_url: Optional[str] = None
    preview_video_type: Optional[int] = None
    level: Optional[CourseLevel] = None
    is_published: Optional[bool] = None
    category_ids: Optional[List[UUID]] = None
    instructor_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    estimated_duration: Optional[int] = None
    difficulty_score: Optional[int] = None
    base_price: Optional[int] = None
    currency: Optional[str] = None
    approval_status: Optional[str] = None
    approval_note: Optional[str] = None


# ─── AI Analysis Schemas ───────────────────────────────────────────────────────

class AIAnalysisRequest(BaseModel):
    title: str
    description: str


class AIAnalysisResponse(BaseModel):
    suggested_category_ids: List[UUID] = []
    new_categories: List[Dict[str, str]] = []
    # Translation output
    translations: Dict[str, CourseTranslationInput] = {}  # {"vi": {...}, "en": {...}}
    suggested_tags: List[str] = []
    suggested_level: CourseLevel = CourseLevel.BEGINNER
    difficulty_score: int = 5
    confidence_score: float = 0.0


# ─── Admin Response Schemas ───────────────────────────────────────────────────

class AdminCourseTranslationSummary(BaseModel):
    lang: str
    title: str = ""
    subtitle: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AdminInstructorSummary(BaseModel):
    id: UUID
    full_name: str
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AdminCategorySummary(BaseModel):
    id: UUID
    name: str = ""
    icon: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AdminCourseRead(BaseModel):
    """Response schema cho admin course list."""
    id: UUID
    slug: Optional[str] = None
    thumbnail_url: Optional[str] = None
    preview_video_type: int = 1
    language: Optional[str] = None
    level: str
    is_published: bool
    approval_status: Optional[str] = None
    base_price: int = 0
    currency: str = "VND"
    estimated_duration: Optional[int] = None
    views: int = 0
    total_enrolls: int = 0
    revenue: int = 0
    rating_avg: float = 0.0
    lessons_count: int = 0
    instructor_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    translations: Dict[str, AdminCourseTranslationSummary] = {}
    category_ids: List[UUID] = []
    instructor: Optional[AdminInstructorSummary] = None

    model_config = ConfigDict(from_attributes=True)


class AdminCourseListResponse(BaseModel):
    items: List[AdminCourseRead]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class AdminCourseStats(BaseModel):
    total_courses: int = 0
    published_courses: int = 0
    draft_courses: int = 0
    total_enrolls: int = 0
    total_revenue: int = 0
    avg_rating: float = 0.0


class AdminCourseStatsResponse(BaseModel):
    stats: AdminCourseStats
    generated_at: datetime


class CourseFilters(BaseModel):
    lang: str = "vi"
    search: Optional[str] = None
    status: Optional[str] = None  # published | draft | all
    level: Optional[str] = None
    category_id: Optional[UUID] = None
    instructor_id: Optional[UUID] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


# ─── Public Response Schemas ──────────────────────────────────────────────────

class CourseTranslationSummary(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CategorySummary(BaseModel):
    id: UUID
    name: str
    icon: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CoursePublicRead(BaseModel):
    id: UUID
    thumbnail_url: Optional[str] = None
    level: CourseLevel
    base_price: int
    currency: str
    estimated_duration: Optional[int] = None
    rating_avg: float
    total_enrolls: int
    lessons_count: int
    created_at: datetime
    
    # Translated content
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    
    # Relationships
    instructor: Optional[InstructorShort] = None
    categories: List[CategorySummary] = []
    
    model_config = ConfigDict(from_attributes=True)

    @property
    def price_coin(self) -> int:
        if self.base_price == 0:
            return 0
        return math.ceil(self.base_price / 1000)


class CourseListResponse(BaseModel):
    items: List[CoursePublicRead]
    total: int
    page: int
    page_size: int
    total_pages: int

