"""
Category API routes - GET endpoints với pagination, filter, sort.
"""
from __future__ import annotations

import math
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.error_codes import ErrorCodes
from app.core.dependencies import DBSession
from app.core.dependencies import RequireRole
from app.schemas.category import (
    CategoryCreateFromVietnamese,
    CategoryDetail,
    CategoryDetailStats,
    CategoryFilters,
    CategoryFullDetail,
    CategoryListResponse,
    CategoryCourseSummary,
    CategoryCourseTranslationSummary,
    CategoryRead,
    CategoryStats,
    CategoryStatsResponse,
    CategoryTranslationSummary,
    CategoryUpdateFromVietnamese,
)
from app.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])
AdminUser = Annotated[UUID, Depends(RequireRole(["admin"]))]


def _build_translations_dict(category, lang: str = "vi") -> dict[str, CategoryTranslationSummary]:
    """Build translations dict từ category object."""
    translations = {}
    for t in category.category_translations:
        translations[t.lang] = CategoryTranslationSummary(
            lang=t.lang,
            name=t.name or "",
            description=t.description,
        )
    return translations


def _get_course_count(category, course_counts: dict) -> int:
    """Get course count cho category."""
    return course_counts.get(category.id, 0)


def _build_category_detail(category, course_counts: dict) -> CategoryDetail:
    from app.schemas.category import CategoryTranslationRead

    return CategoryDetail(
        id=category.id,
        icon=category.icon,
        created_at=category.created_at,
        updated_at=category.updated_at,
        translations=_build_translations_dict(category),
        course_count=_get_course_count(category, course_counts),
        translations_full=[
            CategoryTranslationRead(
                id=t.id,
                category_id=t.category_id,
                lang=t.lang,
                name=t.name or "",
                description=t.description,
                is_auto_translated=t.is_auto_translated or False,
                created_at=t.created_at or category.created_at,
                updated_at=t.updated_at or category.updated_at,
            )
            for t in category.category_translations
        ],
    )


def _build_course_translations_dict(course) -> dict[str, CategoryCourseTranslationSummary]:
    """Build compact course translation map."""
    translations = {}
    for translation in course.course_translations:
        translations[translation.lang] = CategoryCourseTranslationSummary(
            lang=translation.lang,
            title=translation.title or "",
            subtitle=translation.subtitle,
            description=translation.description,
            slug=translation.slug,
        )
    return translations


def _build_course_summary(course) -> CategoryCourseSummary:
    """Build embedded course summary for category detail."""
    return CategoryCourseSummary(
        id=course.id,
        default_slug=course.default_slug,
        thumbnail_url=course.thumbnail_url,
        level=getattr(course.level, "value", str(course.level)),
        is_published=course.is_published,
        approval_status=course.approval_status,
        base_price=course.base_price or 0,
        currency=course.currency,
        estimated_duration=course.estimated_duration,
        lessons_count=course.lessons_count or 0,
        views=course.views or 0,
        total_enrolls=course.total_enrolls or 0,
        revenue=course.revenue or 0,
        rating_avg=float(course.rating_avg or 0),
        created_at=course.created_at,
        updated_at=course.updated_at,
        translations=_build_course_translations_dict(course),
    )


def _build_category_full_detail(
    category,
    course_counts: dict,
    stats: dict[str, int | float],
    courses: list,
) -> CategoryFullDetail:
    from datetime import datetime
    from app.schemas.category import CategoryTranslationRead

    return CategoryFullDetail(
        id=category.id,
        icon=category.icon,
        created_at=category.created_at,
        updated_at=category.updated_at,
        translations=_build_translations_dict(category),
        course_count=_get_course_count(category, course_counts),
        translations_full=[
            CategoryTranslationRead(
                id=t.id,
                category_id=t.category_id,
                lang=t.lang,
                name=t.name or "",
                description=t.description,
                is_auto_translated=t.is_auto_translated or False,
                created_at=t.created_at or category.created_at,
                updated_at=t.updated_at or category.updated_at,
            )
            for t in category.category_translations
        ],
        stats=CategoryDetailStats(
            total_courses=int(stats.get("total_courses", 0)),
            published_courses=int(stats.get("published_courses", 0)),
            draft_courses=int(stats.get("draft_courses", 0)),
            total_enrolls=int(stats.get("total_enrolls", 0)),
            total_revenue=int(stats.get("total_revenue", 0)),
            total_views=int(stats.get("total_views", 0)),
            avg_rating=float(stats.get("avg_rating", 0)),
        ),
        courses=[_build_course_summary(course) for course in courses],
        generated_at=datetime.utcnow(),
    )


@router.post(
    "",
    response_model=CategoryDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create category from Vietnamese input",
    description="Admin nhập name/description tiếng Việt, AI tự sinh bản dịch tiếng Anh",
)
async def create_category(
    payload: CategoryCreateFromVietnamese,
    db: DBSession,
    _: AdminUser,
) -> CategoryDetail:
    """
    Create category with required Vietnamese translation and generated English translation.
    """
    service = CategoryService(db)
    category = await service.create_category_from_vietnamese(payload)
    course_counts = await service.get_course_counts([category.id])
    return _build_category_detail(category, course_counts)


@router.patch(
    "/{category_id}",
    response_model=CategoryFullDetail,
    summary="Update category Vietnamese content",
    description="Admin chỉ sửa tiếng Việt; nếu nội dung đổi, AI tự sinh lại bản tiếng Anh",
)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdateFromVietnamese,
    db: DBSession,
    _: AdminUser,
    lang: Annotated[str, Query(description="Primary language")] = "vi",
    course_limit: Annotated[
        int,
        Query(ge=0, le=100, description="Maximum related courses to include"),
    ] = 20,
) -> CategoryFullDetail:
    """Patch Vietnamese category content and return the full category resource."""
    service = CategoryService(db)
    category = await service.update_category_from_vietnamese(category_id, payload)
    course_counts = await service.get_course_counts([category.id])
    stats = await service.get_category_detail_stats(category.id)
    courses = await service.get_category_courses(category.id, limit=course_limit)
    return _build_category_full_detail(category, course_counts, stats, courses)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete category",
    description="Xoa category khi category chua co khoa hoc nao lien ket. Tra ve 409 neu co khoa hoc.",
)
async def delete_category(
    category_id: UUID,
    db: DBSession,
    _: AdminUser,
) -> None:
    """Xoa category khi khong co khoa hoc lien ket."""
    try:
        service = CategoryService(db)
        await service.delete_category(category_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": ErrorCodes.CATEGORY_DELETE_FAILED,
                "message": "Could not delete category.",
            },
        )


@router.get(
    "",
    response_model=CategoryListResponse,
    summary="Get all categories",
    description="Paginated list với filter, sort, search, course count",
)
async def get_categories(
    db: DBSession,
    lang: Annotated[
        str,
        Query(description="Language code (vi|en|jp...)", examples=["vi", "en"])
    ] = "vi",
    page: Annotated[
        int,
        Query(ge=1, description="Page number")
    ] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100, description="Items per page")
    ] = 20,
    search: Annotated[
        Optional[str],
        Query(description="Search in category name")
    ] = None,
    has_courses: Annotated[
        Optional[bool],
        Query(description="Filter: only categories with/without courses")
    ] = None,
    min_course_count: Annotated[
        Optional[int],
        Query(ge=0, description="Minimum course count")
    ] = None,
    sort_by: Annotated[
        str,
        Query(description="Sort by: created_at|updated_at|name")
    ] = "created_at",
    sort_order: Annotated[
        str,
        Query(pattern="^(asc|desc)$", description="Sort direction")
    ] = "desc",
) -> CategoryListResponse:
    """
    Get paginated categories với đầy đủ tính năng:
    
    - **page/page_size**: Phân trang
    - **lang**: Ngôn ngữ cho translations
    - **search**: Tìm kiếm theo tên
    - **has_courses**: Lọc categories có/không có khóa học
    - **min_course_count**: Lọc theo số khóa học tối thiểu
    - **sort_by/sort_order**: Sắp xếp
    """
    filters = CategoryFilters(
        lang=lang,
        search=search,
        has_courses=has_courses,
        min_course_count=min_course_count,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    service = CategoryService(db)
    categories, total = await service.get_categories(
        page=page,
        page_size=page_size,
        filters=filters,
    )

    # Get course counts for the categories on this page.
    course_counts = await service.get_course_counts([cat.id for cat in categories])

    # Build response
    items = [
        CategoryRead(
            id=cat.id,
            icon=cat.icon,
            created_at=cat.created_at,
            updated_at=cat.updated_at,
            translations=_build_translations_dict(cat, lang),
            course_count=_get_course_count(cat, course_counts),
        )
        for cat in categories
    ]

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return CategoryListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get(
    "/all",
    response_model=list[CategoryRead],
    summary="Get all categories (no pagination)",
    description="Lấy tất cả categories, không phân trang (cho dropdown/cache)",
)
async def get_all_categories(
    db: DBSession,
    lang: Annotated[str, Query(description="Language code")] = "vi",
    include_stats: Annotated[
        bool,
        Query(description="Include course counts")
    ] = False,
) -> list[CategoryRead]:
    """
    Get all categories without pagination.
    Phù hợp cho dropdown lists hoặc caching.
    """
    service = CategoryService(db)
    categories = await service.get_all_categories(lang=lang, include_stats=include_stats)

    course_counts = await service.get_course_counts([cat.id for cat in categories])

    return [
        CategoryRead(
            id=cat.id,
            icon=cat.icon,
            created_at=cat.created_at,
            updated_at=cat.updated_at,
            translations=_build_translations_dict(cat, lang),
            course_count=_get_course_count(cat, course_counts),
        )
        for cat in categories
    ]


@router.get(
    "/stats",
    response_model=CategoryStatsResponse,
    summary="Get category statistics",
    description="Thống kê số khóa học, enrollments, revenue cho tất cả categories",
)
async def get_category_stats(
    db: DBSession,
) -> CategoryStatsResponse:
    """Get statistics cho all categories."""
    from datetime import datetime

    service = CategoryService(db)
    stats = await service.get_category_stats()

    category_stats = [
        CategoryStats(
            category_id=cat_id,
            total_courses=data.get("total_courses", 0),
            total_enrolls=data.get("total_enrolls", 0),
            total_revenue=data.get("total_revenue", 0),
        )
        for cat_id, data in stats.items()
    ]

    return CategoryStatsResponse(
        stats=category_stats,
        generated_at=datetime.utcnow(),
    )


@router.get(
    "/{category_id}",
    response_model=CategoryFullDetail,
    summary="Get category by ID",
    description="Lấy chi tiết một category với translations, thống kê và khóa học liên quan",
)
async def get_category_by_id(
    category_id: UUID,
    db: DBSession,
    lang: Annotated[str, Query(description="Primary language")] = "vi",
    course_limit: Annotated[
        int,
        Query(ge=0, le=100, description="Maximum related courses to include"),
    ] = 20,
) -> CategoryFullDetail:
    """Get complete category detail by UUID."""
    try:
        service = CategoryService(db)
        category = await service.get_category_by_id(category_id, lang)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": ErrorCodes.CATEGORY_NOT_FOUND,
                    "message": f"Category {category_id} not found",
                },
            )

        course_counts = await service.get_course_counts([category.id])
        stats = await service.get_category_detail_stats(category.id)
        courses = await service.get_category_courses(category.id, limit=course_limit)

        return _build_category_full_detail(category, course_counts, stats, courses)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": ErrorCodes.CATEGORY_DETAIL_FAILED,
                "message": "Could not load category detail.",
            },
        )
