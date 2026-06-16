"""
Category service - Business logic cho category operations.
"""
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import case, delete, func, select
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Categories, CategoryTranslations, CourseCategories, Courses
from app.core.error_codes import ErrorCodes
from app.core.logging import logger
from app.schemas.category import CategoryCreateFromVietnamese, CategoryFilters, CategoryUpdateFromVietnamese
from app.services.ai_service import translate_category_content


def _contains_vietnamese_text(value: str) -> bool:
    return any("\u00c0" <= char <= "\u1ef9" for char in value)


def _is_invalid_english_translation(source: Optional[str], translated: Optional[str]) -> bool:
    if not translated or not translated.strip():
        return bool(source)

    normalized = translated.strip()
    if normalized.startswith("[EN]"):
        return True
    if source and normalized.casefold() == source.strip().casefold():
        return True
    return _contains_vietnamese_text(normalized)


class CategoryService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create_category_from_vietnamese(
        self,
        payload: CategoryCreateFromVietnamese,
    ) -> Categories:
        """
        Create category from Vietnamese admin input and auto-generate English translation.
        """
        try:
            existing_query = (
                select(CategoryTranslations.id)
                .where(CategoryTranslations.lang == "vi")
                .where(func.lower(CategoryTranslations.name) == payload.name.lower())
                .limit(1)
            )
            existing_result = await self._db.execute(existing_query)
            if existing_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": ErrorCodes.CATEGORY_ALREADY_EXISTS,
                        "message": "Category name already exists.",
                    },
                )

            category = Categories()
            self._db.add(category)
            await self._db.flush()

            try:
                en_content = await translate_category_content(
                    name=payload.name,
                    description=payload.description,
                    source_lang="vi",
                    target_lang="en",
                )
                vi_name = payload.name
                vi_description = payload.description or en_content.get("vi_description")
                en_name = en_content.get("name")
                en_description = en_content.get("description")
                if not vi_name or not vi_name.strip():
                    raise RuntimeError("CATEGORY_VI_NAME_GENERATION_INVALID")
                if not vi_description:
                    raise RuntimeError("CATEGORY_VI_DESCRIPTION_GENERATION_INVALID")
                if payload.description is None and not _contains_vietnamese_text(vi_description):
                    raise RuntimeError("CATEGORY_VI_DESCRIPTION_GENERATION_INVALID")
                if _is_invalid_english_translation(payload.name, en_name):
                    raise RuntimeError("CATEGORY_NAME_TRANSLATION_INVALID")
                if _is_invalid_english_translation(vi_description, en_description):
                    raise RuntimeError("CATEGORY_DESCRIPTION_TRANSLATION_INVALID")
            except Exception as exc:
                logger.error("category_ai_translation_failed", error=str(exc), exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail={
                        "code": ErrorCodes.CATEGORY_TRANSLATION_FAILED,
                        "message": "Could not generate English category translation.",
                    },
                ) from exc

            vi_translation = CategoryTranslations(
                category_id=category.id,
                lang="vi",
                name=vi_name,
                description=vi_description,
                is_auto_translated=False,
            )
            self._db.add(vi_translation)

            en_translation = CategoryTranslations(
                category_id=category.id,
                lang="en",
                name=en_name,
                description=en_description,
                is_auto_translated=True,
            )
            self._db.add(en_translation)

            await self._db.commit()

            created = await self.get_category_by_id(category.id)
            if created is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": ErrorCodes.CATEGORY_CREATE_FAILED,
                        "message": "Category was created but could not be loaded.",
                    },
                )
            return created
        except HTTPException:
            await self._db.rollback()
            raise
        except Exception:
            await self._db.rollback()
            logger.error("create_category_from_vietnamese_failed", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": ErrorCodes.CATEGORY_CREATE_FAILED,
                    "message": "Could not create category.",
                },
            )

    async def get_categories(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[CategoryFilters] = None,
    ) -> tuple[Sequence[Categories], int]:
        """
        Get paginated categories với filters và course counts.
        
        Returns:
            Tuple of (categories, total_count)
        """
        if filters is None:
            filters = CategoryFilters()

        course_count_subquery = (
            select(
                CourseCategories.category_id.label("category_id"),
                func.count(CourseCategories.course_id).label("course_count"),
            )
            .group_by(CourseCategories.category_id)
            .subquery()
        )

        query = select(Categories).options(selectinload(Categories.category_translations))
        count_query = select(func.count(func.distinct(Categories.id))).select_from(Categories)
        joined_translations = False
        joined_course_counts = False

        # Search filter
        if filters.search and filters.lang:
            search_term = f"%{filters.search.lower()}%"
            query = query.join(
                CategoryTranslations,
                Categories.id == CategoryTranslations.category_id
            ).where(
                CategoryTranslations.lang == filters.lang,
                func.lower(CategoryTranslations.name).like(search_term)
            )
            joined_translations = True

            count_query = (
                count_query.join(
                    CategoryTranslations,
                    Categories.id == CategoryTranslations.category_id,
                )
                .where(
                    CategoryTranslations.lang == filters.lang,
                    func.lower(CategoryTranslations.name).like(search_term),
                )
            )

        # Course count filters must run before pagination so total stays correct.
        if filters.has_courses is not None or (
            filters.min_course_count is not None and filters.min_course_count > 0
        ):
            query = query.outerjoin(course_count_subquery, Categories.id == course_count_subquery.c.category_id)
            count_query = count_query.outerjoin(
                course_count_subquery,
                Categories.id == course_count_subquery.c.category_id,
            )
            joined_course_counts = True

            course_count_expr = func.coalesce(course_count_subquery.c.course_count, 0)
            if filters.has_courses is True:
                query = query.where(course_count_expr > 0)
                count_query = count_query.where(course_count_expr > 0)
            elif filters.has_courses is False:
                query = query.where(course_count_expr == 0)
                count_query = count_query.where(course_count_expr == 0)

            if filters.min_course_count is not None and filters.min_course_count > 0:
                query = query.where(course_count_expr >= filters.min_course_count)
                count_query = count_query.where(course_count_expr >= filters.min_course_count)

        total_result = await self._db.execute(count_query)
        total = total_result.scalar() or 0

        # Sorting
        sort_column = Categories.created_at
        if filters.sort_by == "updated_at":
            sort_column = Categories.updated_at
        elif filters.sort_by == "name":
            if not joined_translations:
                query = query.join(
                    CategoryTranslations,
                    Categories.id == CategoryTranslations.category_id,
                ).where(CategoryTranslations.lang == filters.lang)
            sort_column = CategoryTranslations.name
        elif filters.sort_by == "position":
            sort_column = Categories.id
        elif filters.sort_by == "course_count":
            if not joined_course_counts:
                query = query.outerjoin(
                    course_count_subquery,
                    Categories.id == course_count_subquery.c.category_id,
                )
            sort_column = func.coalesce(course_count_subquery.c.course_count, 0)

        if filters.sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self._db.execute(query)
        categories = result.scalars().unique().all()

        return categories, total

    async def update_category_from_vietnamese(
        self,
        category_id: UUID,
        payload: CategoryUpdateFromVietnamese,
    ) -> Categories:
        """
        Update Vietnamese category content and regenerate English translation when content changes.
        """
        try:
            category = await self.get_category_by_id(category_id)
            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": ErrorCodes.CATEGORY_NOT_FOUND,
                        "message": f"Category {category_id} not found.",
                    },
                )

            translations_by_lang = {
                translation.lang: translation
                for translation in category.category_translations
            }
            vi_translation = translations_by_lang.get("vi")
            en_translation = translations_by_lang.get("en")

            if vi_translation is None and "name" not in payload.model_fields_set:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "code": ErrorCodes.VALIDATION_MISSING_FIELD,
                        "message": "Vietnamese category name is required.",
                    },
                )

            current_vi_name = vi_translation.name if vi_translation else ""
            current_vi_description = vi_translation.description if vi_translation else None
            next_name = payload.name if "name" in payload.model_fields_set else current_vi_name
            next_description = (
                payload.description
                if "description" in payload.model_fields_set
                else current_vi_description
            )

            if not next_name:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "code": ErrorCodes.VALIDATION_MISSING_FIELD,
                        "message": "Vietnamese category name is required.",
                    },
                )

            name_changed = next_name != current_vi_name
            description_changed = next_description != current_vi_description
            if not name_changed and not description_changed:
                return category

            if name_changed:
                existing_query = (
                    select(CategoryTranslations.id)
                    .where(CategoryTranslations.lang == "vi")
                    .where(func.lower(CategoryTranslations.name) == next_name.lower())
                    .where(CategoryTranslations.category_id != category_id)
                    .limit(1)
                )
                existing_result = await self._db.execute(existing_query)
                if existing_result.scalar_one_or_none():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail={
                            "code": ErrorCodes.CATEGORY_ALREADY_EXISTS,
                            "message": "Category name already exists.",
                        },
                    )

            try:
                ai_content = await translate_category_content(
                    name=next_name,
                    description=next_description,
                    source_lang="vi",
                    target_lang="en",
                )
                vi_name = next_name
                vi_description = next_description or ai_content.get("vi_description")
                en_name = ai_content.get("name")
                en_description = ai_content.get("description")
                if not vi_name or not vi_name.strip():
                    raise RuntimeError("CATEGORY_VI_NAME_GENERATION_INVALID")
                if not vi_description:
                    raise RuntimeError("CATEGORY_VI_DESCRIPTION_GENERATION_INVALID")
                if next_description is None and not _contains_vietnamese_text(vi_description):
                    raise RuntimeError("CATEGORY_VI_DESCRIPTION_GENERATION_INVALID")
                if _is_invalid_english_translation(next_name, en_name):
                    raise RuntimeError("CATEGORY_NAME_TRANSLATION_INVALID")
                if _is_invalid_english_translation(vi_description, en_description):
                    raise RuntimeError("CATEGORY_DESCRIPTION_TRANSLATION_INVALID")
            except Exception as exc:
                logger.error("category_ai_translation_failed", error=str(exc), exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail={
                        "code": ErrorCodes.CATEGORY_TRANSLATION_FAILED,
                        "message": "Could not generate English category translation.",
                    },
                ) from exc

            now = datetime.utcnow()
            category.updated_at = now

            if vi_translation is None:
                vi_translation = CategoryTranslations(
                    category_id=category.id,
                    lang="vi",
                    is_auto_translated=False,
                )
                self._db.add(vi_translation)
            vi_translation.name = vi_name
            vi_translation.description = vi_description
            vi_translation.is_auto_translated = False
            vi_translation.updated_at = now

            if en_translation is None:
                en_translation = CategoryTranslations(
                    category_id=category.id,
                    lang="en",
                    is_auto_translated=True,
                )
                self._db.add(en_translation)
            en_translation.name = en_name
            en_translation.description = en_description
            en_translation.is_auto_translated = True
            en_translation.updated_at = now

            await self._db.commit()

            updated = await self.get_category_by_id(category.id)
            if updated is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "code": ErrorCodes.CATEGORY_UPDATE_FAILED,
                        "message": "Category was updated but could not be loaded.",
                    },
                )
            return updated
        except HTTPException:
            await self._db.rollback()
            raise
        except Exception:
            await self._db.rollback()
            logger.error("update_category_from_vietnamese_failed", category_id=str(category_id), exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": ErrorCodes.CATEGORY_UPDATE_FAILED,
                    "message": "Could not update category.",
                },
            )

    async def get_category_by_id(
        self,
        category_id: UUID,
        lang: str = "vi",
    ) -> Optional[Categories]:
        """Get single category by ID."""
        query = (
            select(Categories)
            .options(selectinload(Categories.category_translations))
            .where(Categories.id == category_id)
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_category_detail_stats(self, category_id: UUID) -> dict[str, int | float]:
        """Get aggregate course metrics for one category."""
        try:
            query = (
                select(
                    func.count(Courses.id).label("total_courses"),
                    func.coalesce(
                        func.sum(case((Courses.is_published.is_(True), 1), else_=0)),
                        0,
                    ).label("published_courses"),
                    func.coalesce(
                        func.sum(case((Courses.is_published.is_(False), 1), else_=0)),
                        0,
                    ).label("draft_courses"),
                    func.coalesce(func.sum(Courses.total_enrolls), 0).label("total_enrolls"),
                    func.coalesce(func.sum(Courses.revenue), 0).label("total_revenue"),
                    func.coalesce(func.sum(Courses.views), 0).label("total_views"),
                    func.coalesce(func.avg(Courses.rating_avg), 0).label("avg_rating"),
                )
                .select_from(CourseCategories)
                .join(Courses, CourseCategories.course_id == Courses.id)
                .where(CourseCategories.category_id == category_id)
            )
            result = await self._db.execute(query)
            row = result.one()
            return {
                "total_courses": int(row.total_courses or 0),
                "published_courses": int(row.published_courses or 0),
                "draft_courses": int(row.draft_courses or 0),
                "total_enrolls": int(row.total_enrolls or 0),
                "total_revenue": int(row.total_revenue or 0),
                "total_views": int(row.total_views or 0),
                "avg_rating": float(row.avg_rating or 0),
            }
        except Exception:
            logger.error("get_category_detail_stats_failed", category_id=str(category_id), exc_info=True)
            raise

    async def get_category_courses(
        self,
        category_id: UUID,
        limit: int = 20,
    ) -> list[Courses]:
        """Get recent courses attached to one category."""
        try:
            query = (
                select(Courses)
                .join(CourseCategories, CourseCategories.course_id == Courses.id)
                .options(selectinload(Courses.course_translations))
                .where(CourseCategories.category_id == category_id)
                .order_by(Courses.created_at.desc())
                .limit(limit)
            )
            result = await self._db.execute(query)
            return list(result.scalars().unique().all())
        except Exception:
            logger.error("get_category_courses_failed", category_id=str(category_id), exc_info=True)
            raise

    async def get_category_by_slug_or_id(
        self,
        identifier: str,
        lang: str = "vi",
    ) -> Optional[Categories]:
        """Get category by slug (translation) hoặc ID."""
        try:
            uid = UUID(identifier)
            return await self.get_category_by_id(uid, lang)
        except ValueError:
            pass

        query = (
            select(Categories)
            .options(selectinload(Categories.category_translations))
            .join(CategoryTranslations)
            .where(CategoryTranslations.slug == identifier)
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_categories(
        self,
        lang: str = "vi",
        include_stats: bool = False,
    ) -> list[Categories]:
        """Get all categories (for dropdown/cache)."""
        query = (
            select(Categories)
            .options(selectinload(Categories.category_translations))
            .order_by(Categories.created_at.desc())
        )
        result = await self._db.execute(query)
        return list(result.scalars().unique().all())

    async def get_category_stats(
        self,
        category_ids: Optional[list[UUID]] = None,
    ) -> dict[UUID, dict]:
        """Get statistics for categories."""
        # Get course counts
        course_counts_query = (
            select(
                CourseCategories.category_id,
                func.count(CourseCategories.course_id).label("course_count"),
                func.sum(Courses.total_enrolls).label("total_enrolls"),
                func.sum(Courses.revenue).label("total_revenue"),
            )
            .join(Courses, CourseCategories.course_id == Courses.id)
            .group_by(CourseCategories.category_id)
        )

        if category_ids:
            course_counts_query = course_counts_query.where(
                CourseCategories.category_id.in_(category_ids)
            )

        result = await self._db.execute(course_counts_query)
        stats = {}
        for row in result.all():
            stats[row.category_id] = {
                "total_courses": row.course_count or 0,
                "total_enrolls": row.total_enrolls or 0,
                "total_revenue": row.total_revenue or 0,
            }
        return stats

    async def get_course_counts(
        self,
        category_ids: Optional[Sequence[UUID]] = None,
    ) -> dict[UUID, int]:
        """Get course count per category."""
        query = (
            select(
                CourseCategories.category_id,
                func.count(CourseCategories.course_id).label("count")
            )
            .group_by(CourseCategories.category_id)
        )

        if category_ids:
            query = query.where(CourseCategories.category_id.in_(category_ids))

        result = await self._db.execute(query)
        return {row.category_id: row.count for row in result.all()}

    async def delete_category(self, category_id: UUID) -> None:
        """
        Xóa category khi không liên kết với khóa học nào.
        Raise HTTPException nếu category có khóa học liên kết hoặc không tồn tại.
        """
        try:
            # Query trực tiếp không eager-load để tránh conflict với delete.
            query = select(Categories).where(Categories.id == category_id)
            result = await self._db.execute(query)
            category = result.scalar_one_or_none()
            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": ErrorCodes.CATEGORY_NOT_FOUND,
                        "message": f"Category {category_id} not found.",
                    },
                )

            course_count = await self.get_course_counts([category_id])
            if course_count.get(category_id, 0) > 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": ErrorCodes.CATEGORY_HAS_COURSES,
                        "message": "Cannot delete category that is linked to courses.",
                    },
                )

            # Xóa translations trước rồi xóa category.
            await self._db.execute(
                delete(CategoryTranslations).where(
                    CategoryTranslations.category_id == category_id
                )
            )
            await self._db.execute(delete(Categories).where(Categories.id == category_id))
            await self._db.commit()
        except HTTPException:
            await self._db.rollback()
            raise
        except Exception:
            await self._db.rollback()
            logger.error("delete_category_failed", category_id=str(category_id), exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": ErrorCodes.CATEGORY_DELETE_FAILED,
                    "message": "Could not delete category.",
                },
            )
