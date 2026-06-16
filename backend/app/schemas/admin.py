from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID


class UpdateUserRolesRequest(BaseModel):
    roles: List[str]


# ─── Admin Course Schemas ──────────────────────────────────────────────────────

class AdminCourseListResponse(BaseModel):
    """Response cho danh sách khóa học (admin)."""
    courses: List[Dict[str, Any]]
    total: int
    page: int = 1
    page_size: int = 20
    total_pages: int = 0

    model_config = {"from_attributes": True}


class AdminCourseStatsResponse(BaseModel):
    """Response thống kê khóa học (admin)."""
    total_courses: int
    total_enrolls: int
    total_revenue: int
    avg_rating: float

    model_config = {"from_attributes": True}


class AdminTranslationResponse(BaseModel):
    """Response sau khi thêm/cập nhật translation."""
    lang: str
    title: str
    message: str


class AdminCoursePriceResponse(BaseModel):
    """Response thông tin giá khóa học (admin)."""
    course_id: UUID
    base_price: int
    currency: str
    price_coin: int
    price_formatted: str

    model_config = {"from_attributes": True}


class AdminCourseFilterParams(BaseModel):
    """Filter params cho list khóa học admin."""
    search: Optional[str] = None
    status: Optional[str] = None
    level: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 20
