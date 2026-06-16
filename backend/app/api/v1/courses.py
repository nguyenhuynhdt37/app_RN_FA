"""
Course Admin API routes - GET endpoints với pagination, filter, sort.
"""
from __future__ import annotations

import math
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from app.core.dependencies import DBSession, CurrentUserID, RequireRole
from app.schemas.course import (
    CourseCreate,
    AdminCourseListResponse,
    AdminCourseRead,
    AdminCourseStats,
    AdminCourseStatsResponse,
    AdminCourseTranslationSummary,
    AdminInstructorSummary,
    CourseFilters,
    CourseListResponse,
    CoursePublicRead,
    CourseSort,
    CategorySummary,
    InstructorShort,
)
from app.services.course_service import CourseService

router = APIRouter(prefix="/admin/courses", tags=["courses"])
public_router = APIRouter(prefix="/courses", tags=["courses"])
# Public endpoints — admin dashboard không cần auth cho đọc (auth check ở middleware)


def _get_translation_fallback(translations: list, lang: str) -> Optional[Any]:
    """Lấy translation theo lang, fallback sang 'en', rồi đến bản đầu tiên."""
    if not translations:
        return None
    
    # 1. Tìm đúng lang
    for t in translations:
        if t.lang == lang:
            return t
            
    # 2. Fallback sang 'en'
    for t in translations:
        if t.lang == 'en':
            return t
            
    # 3. Bản đầu tiên
    return translations[0]


def _build_public_course_read(course, lang: str = "vi") -> CoursePublicRead:
    """Build CoursePublicRead với fallback translation logic."""
    trans = _get_translation_fallback(course.course_translations, lang)
    
    instructor = None
    if course.instructor:
        instructor = InstructorShort(
            id=course.instructor.id,
            full_name=course.instructor.full_name or "",
            avatar_url=course.instructor.avatar_url,
            instructor_metadata=course.instructor.instructor_metadata or {},
        )

    categories = []
    if course.course_categories:
        for cc in course.course_categories:
            c_trans = _get_translation_fallback(cc.category.category_translations, lang)
            categories.append(CategorySummary(
                id=cc.category.id,
                name=c_trans.name if c_trans else str(cc.category.id),
                icon=cc.category.icon
            ))

    return CoursePublicRead(
        id=course.id,
        thumbnail_url=course.thumbnail_url,
        level=course.level,
        base_price=course.base_price or 0,
        currency=course.currency or "VND",
        estimated_duration=course.estimated_duration,
        rating_avg=float(course.rating_avg or 0),
        total_enrolls=course.total_enrolls or 0,
        lessons_count=course.lessons_count or 0,
        created_at=course.created_at,
        title=trans.title if trans else "",
        subtitle=trans.subtitle if trans else None,
        description=trans.description if trans else None,
        slug=trans.slug if trans else course.default_slug,
        instructor=instructor,
        categories=categories,
    )


def _build_course_read(course, lang: str = "vi") -> AdminCourseRead:
    """Build AdminCourseRead từ course model."""
    translations = {}
    for t in course.course_translations:
        translations[t.lang] = AdminCourseTranslationSummary(
            lang=t.lang,
            title=t.title or "",
            subtitle=t.subtitle,
            description=t.description,
            slug=t.slug,
        )

    instructor = None
    if course.instructor:
        instructor = AdminInstructorSummary(
            id=course.instructor.id,
            full_name=course.instructor.full_name or "",
            avatar_url=course.instructor.avatar_url,
        )

    category_ids = [cc.category_id for cc in course.course_categories] if course.course_categories else []

    return AdminCourseRead(
        id=course.id,
        slug=course.default_slug,
        thumbnail_url=course.thumbnail_url,
        preview_video_type=course.preview_video_type or 1,
        language=lang,
        level=getattr(course.level, "value", str(course.level)),
        is_published=course.is_published,
        approval_status=course.approval_status,
        base_price=course.base_price or 0,
        currency=course.currency or "VND",
        estimated_duration=course.estimated_duration,
        views=course.views or 0,
        total_enrolls=course.total_enrolls or 0,
        revenue=course.revenue or 0,
        rating_avg=float(course.rating_avg or 0),
        lessons_count=course.lessons_count or 0,
        instructor_id=course.instructor_id,
        created_at=course.created_at,
        updated_at=course.updated_at,
        translations=translations,
        category_ids=category_ids,
        instructor=instructor,
    )


@router.get(
    "",
    response_model=AdminCourseListResponse,
    summary="Get paginated courses",
    description="Paginated course list cho admin dashboard với filter, sort, search",
)
async def get_courses(
    db: DBSession,
    lang: Annotated[str, Query(description="Language code (vi|en)")] = "vi",
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    search: Annotated[Optional[str], Query(description="Search in course title")] = None,
    status: Annotated[
        Optional[str],
        Query(description="Filter: published|draft|all"),
    ] = "all",
    level: Annotated[Optional[str], Query(description="Filter by level")] = None,
    category_id: Annotated[Optional[UUID], Query(description="Filter by category")] = None,
    sort_by: Annotated[
        str,
        Query(description="Sort: created_at|updated_at|revenue|views|total_enrolls|rating_avg|name"),
    ] = "created_at",
    sort_order: Annotated[str, Query(pattern="^(asc|desc)$", description="Sort direction")] = "desc",
) -> AdminCourseListResponse:
    """
    Get paginated courses với đầy đủ tính năng:
    
    - **page/page_size**: Phân trang
    - **lang**: Ngôn ngữ cho translations
    - **search**: Tìm kiếm theo tên khóa học
    - **status**: Lọc theo trạng thái (published|draft|all)
    - **level**: Lọc theo cấp độ
    - **category_id**: Lọc theo danh mục
    - **sort_by/sort_order**: Sắp xếp
    """
    filters = CourseFilters(
        lang=lang,
        search=search,
        status=status,
        level=level,
        category_id=category_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    service = CourseService(db)
    courses, total = await service.get_courses(
        page=page,
        page_size=page_size,
        filters=filters,
    )

    items = [_build_course_read(course, lang) for course in courses]

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return AdminCourseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@public_router.get(
    "",
    response_model=CourseListResponse,
    summary="Get public courses",
    description="Danh sách khóa học công khai với đầy đủ filter, sort, search và translation fallback",
)
async def get_public_courses(
    db: DBSession,
    lang: Annotated[str, Query(description="Ngôn ngữ ưu tiên")] = "vi",
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    category_id: Annotated[Optional[UUID], Query()] = None,
    instructor_id: Annotated[Optional[UUID], Query()] = None,
    level: Annotated[Optional[str], Query()] = None,
    search: Annotated[Optional[str], Query()] = None,
    sort: Annotated[CourseSort, Query()] = CourseSort.NEWEST,
) -> CourseListResponse:
    """
    API lấy danh sách khóa học công khai:
    
    - **Pagination**: Phân trang chuẩn.
    - **Translation Fallback**: Tự động chuyển sang tiếng Anh nếu không có tiếng Việt.
    - **Performance**: Tối ưu query PostgreSQL, không bị N+1.
    - **Filtering**: Theo category, instructor, level.
    - **Sorting**: Mới nhất, phổ biến nhất, đánh giá cao, giá tăng/giảm.
    """
    filters = CourseFilters(
        lang=lang,
        search=search,
        status="published",
        level=level,
        category_id=category_id,
        instructor_id=instructor_id,
        sort_by=sort.value,
        sort_order="desc" if sort in [CourseSort.NEWEST, CourseSort.POPULAR, CourseSort.RATING, CourseSort.PRICE_DESC] else "asc",
    )

    service = CourseService(db)
    courses, total = await service.get_courses(
        page=page,
        page_size=page_size,
        filters=filters,
    )

    items = [_build_public_course_read(course, lang) for course in courses]
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return CourseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/all",
    response_model=list[AdminCourseRead],
    summary="Get all courses (no pagination)",
    description="Lấy tất cả courses, không phân trang (cho dropdown/cache)",
)
async def get_all_courses(
    db: DBSession,
    lang: Annotated[str, Query(description="Language code")] = "vi",
) -> list[AdminCourseRead]:
    """Get all courses without pagination."""
    service = CourseService(db)
    courses = await service.get_all_courses(lang=lang)
    return [_build_course_read(course, lang) for course in courses]


@router.get(
    "/stats",
    response_model=AdminCourseStatsResponse,
    summary="Get course statistics",
    description="Thống kê tổng quan tất cả courses",
)
async def get_course_stats(db: DBSession) -> AdminCourseStatsResponse:
    """Get aggregate statistics across all courses."""
    service = CourseService(db)
    stats = await service.get_course_stats()

    return AdminCourseStatsResponse(
        stats=AdminCourseStats(
            total_courses=int(stats.get("total_courses", 0)),
            published_courses=int(stats.get("published_courses", 0)),
            draft_courses=int(stats.get("draft_courses", 0)),
            total_enrolls=int(stats.get("total_enrolls", 0)),
            total_revenue=int(stats.get("total_revenue", 0)),
            avg_rating=float(stats.get("avg_rating", 0)),
        ),
        generated_at=datetime.utcnow(),
    )
@router.post(
    "",
    response_model=AdminCourseRead,
    status_code=201,
    summary="Create a new course",
    description="Tạo khóa học mới (draft), đồng bộ AI enrichment (EN translation + tags) trước khi trả về.",
)
async def create_course(
    db: DBSession,
    course_in: CourseCreate,
    current_user_id: CurrentUserID,
    _ = Depends(RequireRole(["admin", "teacher"]))
) -> AdminCourseRead:
    """
    API tạo khóa học mới:
    
    1. **Transactional**: Tạo course, translations, tags, outcomes trong 1 transaction.
    2. **Slug Strategy**: Tự động gen slug từ title, xử lý trùng bằng suffix hex.
    3. **Synchronous AI**: Đợi AI gen xong EN translation + tags rồi mới trả về,
       đảm bảo response luôn có đầy đủ dữ liệu đa ngôn ngữ.
    """
    service = CourseService(db)
    new_course = await service.create_course(course_in, current_user_id)
    
    # AI enrichment đồng bộ — đợi cho xong rồi mới trả về
    await service.enrich_course_with_ai(new_course.id)

    # Reload lại sau khi AI cập nhật
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models import CourseCategories, Categories
    reload_query = (
        select(Courses)
        .options(
            selectinload(Courses.course_translations),
            selectinload(Courses.instructor),
            selectinload(Courses.course_categories)
            .joinedload(CourseCategories.category)
            .selectinload(Categories.category_translations),
        )
        .where(Courses.id == new_course.id)
    )
    result = await db.execute(reload_query)
    enriched_course = result.scalar_one()

    return _build_course_read(enriched_course)
