"""
Course service - Business logic cho course operations.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Optional
from uuid import UUID

from sqlalchemy import case, func, select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from slugify import slugify
import uuid
import datetime

from app.models import (
    Courses, 
    CourseTranslations, 
    CourseCategories, 
    Users, 
    CategoryTranslations, 
    Categories,
    Tags,
    CourseTags,
    CourseLearningOutcomes,
    CourseLearningOutcomeTranslations
)
from app.schemas.course import CourseFilters, CourseCreate


class CourseService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_courses(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[CourseFilters] = None,
    ) -> tuple[Sequence[Courses], int]:
        """
        Get paginated courses với filters, search, sort (dùng cho Admin).
        """
        if filters is None:
            filters = CourseFilters()

        query = (
            select(Courses)
            .options(
                selectinload(Courses.course_translations),
                selectinload(Courses.instructor),
                selectinload(Courses.course_categories).joinedload(CourseCategories.category).selectinload(Categories.category_translations),
            )
        )
        count_query = select(func.count(func.distinct(Courses.id))).select_from(Courses)
        joined_translations = False

        # Status filter
        if filters.status == "published":
            query = query.where(Courses.is_published == True)
            count_query = count_query.where(Courses.is_published == True)
        elif filters.status == "draft":
            query = query.where(Courses.is_published == False)
            count_query = count_query.where(Courses.is_published == False)
        
        # Public API mặc định chỉ lấy published
        if not filters.status:
            query = query.where(Courses.is_published == True)
            count_query = count_query.where(Courses.is_published == True)

        # Search filter
        if filters.search and filters.lang:
            search_term = f"%{filters.search.lower()}%"
            query = query.join(
                CourseTranslations,
                Courses.id == CourseTranslations.course_id,
            ).where(
                CourseTranslations.lang == filters.lang,
                func.lower(CourseTranslations.title).like(search_term),
            )
            count_query = (
                count_query.join(
                    CourseTranslations,
                    Courses.id == CourseTranslations.course_id,
                )
                .where(
                    CourseTranslations.lang == filters.lang,
                    func.lower(CourseTranslations.title).like(search_term),
                )
            )
            joined_translations = True

        # Level filter
        if filters.level:
            query = query.where(Courses.level == filters.level)
            count_query = count_query.where(Courses.level == filters.level)

        # Category filter
        if filters.category_id:
            query = query.join(
                CourseCategories,
                CourseCategories.course_id == Courses.id,
            ).where(CourseCategories.category_id == filters.category_id)
            count_query = (
                count_query.join(
                    CourseCategories,
                    CourseCategories.course_id == Courses.id,
                )
                .where(CourseCategories.category_id == filters.category_id)
            )

        # Instructor filter
        if filters.instructor_id:
            query = query.where(Courses.instructor_id == filters.instructor_id)
            count_query = count_query.where(Courses.instructor_id == filters.instructor_id)

        # Total count
        total_result = await self._db.execute(count_query)
        total = total_result.scalar() or 0

        # Sorting
        sort_column = Courses.created_at
        if filters.sort_by == "updated_at":
            sort_column = Courses.updated_at
        elif filters.sort_by == "revenue":
            sort_column = Courses.revenue
        elif filters.sort_by == "views" or filters.sort_by == "popular":
            sort_column = Courses.total_enrolls if filters.sort_by == "popular" else Courses.views
        elif filters.sort_by == "total_enrolls":
            sort_column = Courses.total_enrolls
        elif filters.sort_by == "rating" or filters.sort_by == "rating_avg":
            sort_column = Courses.rating_avg
        elif filters.sort_by == "price_asc":
            sort_column = Courses.base_price
            filters.sort_order = "asc"
        elif filters.sort_by == "price_desc":
            sort_column = Courses.base_price
            filters.sort_order = "desc"
        elif filters.sort_by == "name":
            if not joined_translations:
                query = query.join(
                    CourseTranslations,
                    Courses.id == CourseTranslations.course_id,
                ).where(CourseTranslations.lang == filters.lang)
            sort_column = CourseTranslations.title

        if filters.sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self._db.execute(query)
        courses = result.scalars().unique().all()

        return courses, total

    async def get_all_courses(
        self,
        lang: str = "vi",
        include_stats: bool = False,
    ) -> list[Courses]:
        """Get all courses (for dropdown/cache)."""
        query = (
            select(Courses)
            .options(
                selectinload(Courses.course_translations),
                selectinload(Courses.instructor),
                selectinload(Courses.course_categories),
            )
            .order_by(Courses.created_at.desc())
        )
        result = await self._db.execute(query)
        return list(result.scalars().unique().all())

    async def get_category_ids(
        self,
        course_ids: Sequence[UUID],
    ) -> dict[UUID, list[UUID]]:
        """Get category IDs per course."""
        query = (
            select(
                CourseCategories.course_id,
                CourseCategories.category_id,
            )
            .where(CourseCategories.course_id.in_(course_ids))
        )
        result = await self._db.execute(query)
        mapping: dict[UUID, list[UUID]] = {cid: [] for cid in course_ids}
        for course_id, category_id in result.all():
            if course_id in mapping:
                mapping[course_id].append(category_id)
        return mapping

    async def create_course(
        self,
        course_in: CourseCreate,
        current_user_id: UUID,
    ) -> Courses:
        """
        Tạo khóa học mới với đầy đủ logic: slug, tags, categories, outcomes.
        """
        # 1. Tạo bản ghi gốc Courses
        new_course = Courses(
            level=course_in.level,
            thumbnail_url=course_in.thumbnail_url,
            preview_video_type=course_in.preview_video_type,
            base_price=course_in.base_price,
            currency=course_in.currency,
            estimated_duration=course_in.estimated_duration,
            difficulty_score=course_in.difficulty_score,
            instructor_id=course_in.instructor_id or current_user_id,
            created_by=current_user_id,
            updated_by=current_user_id,
            is_published=False,  # Luôn bắt đầu là draft
            approval_status='draft',
        )
        self._db.add(new_course)
        await self._db.flush()  # Để lấy new_course.id

        # 2. Xử lý Translations & Slugs
        for lang, trans_in in course_in.translations.items():
            # Generate slug
            base_slug = trans_in.slug or slugify(trans_in.title)
            final_slug = base_slug
            
            # Collision check (đơn giản: loop tối đa 5 lần)
            for _ in range(5):
                check_query = select(CourseTranslations).where(
                    CourseTranslations.lang == lang,
                    CourseTranslations.slug == final_slug
                )
                existing = (await self._db.execute(check_query)).scalar_one_or_none()
                if not existing:
                    break
                final_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

            new_trans = CourseTranslations(
                course_id=new_course.id,
                lang=lang,
                title=trans_in.title,
                subtitle=trans_in.subtitle,
                description=trans_in.description,
                slug=final_slug,
                is_ai_generated=False,
            )
            self._db.add(new_trans)

        # 3. Xử lý Categories
        if course_in.category_ids:
            for cat_id in course_in.category_ids:
                course_cat = CourseCategories(
                    course_id=new_course.id,
                    category_id=cat_id,
                    is_primary=False
                )
                self._db.add(course_cat)

        # 4. Xử lý Tags (Sử dụng slug để check tồn tại)
        if course_in.tags:
            for tag_name in course_in.tags:
                tag_slug = slugify(tag_name)
                
                # Tìm tag hiện có
                tag_query = select(Tags).where(Tags.slug == tag_slug)
                tag_obj = (await self._db.execute(tag_query)).scalar_one_or_none()
                
                if not tag_obj:
                    tag_obj = Tags(slug=tag_slug)
                    self._db.add(tag_obj)
                    await self._db.flush()
                
                # Gắn tag vào course
                course_tag = CourseTags(
                    course_id=new_course.id,
                    tag_id=tag_obj.id
                )
                self._db.add(course_tag)

        # 5. Xử lý Learning Outcomes
        if course_in.learning_outcomes:
            for idx, outcome_in in enumerate(course_in.learning_outcomes):
                # Tạo outcome container
                outcome = CourseLearningOutcomes(
                    course_id=new_course.id,
                    position=idx
                )
                self._db.add(outcome)
                await self._db.flush()

                # Tạo translation cho outcome
                outcome_trans = CourseLearningOutcomeTranslations(
                    outcome_id=outcome.id,
                    lang=outcome_in.lang,
                    text_=outcome_in.content,
                    is_ai_generated=False
                )
                self._db.add(outcome_trans)

        await self._db.commit()
        await self._db.refresh(new_course)
        
        # Load relationships để trả về đầy đủ
        query = select(Courses).options(
            selectinload(Courses.course_translations),
            selectinload(Courses.course_categories),
            selectinload(Courses.instructor),
            selectinload(Courses.course_tags).joinedload(CourseTags.tag),
        ).where(Courses.id == new_course.id)
        
        result = await self._db.execute(query)
        return result.scalar_one()

    async def enrich_course_with_ai(self, course_id: UUID) -> None:
        """
        Đồng bộ AI enrichment: gen EN translation + tag gợi ý.
        Chạy đồng bộ (await) ngay sau create_course — API đợi xong rồi mới trả về.
        """
        from app.services.ai_service import ai_service
        from app.services.translation import TranslationService

        try:
            # 1. Lấy thông tin khóa học (sau commit của create_course)
            await self._db.expire_all()  # Làm mới sau commit trước
            query = select(Courses).options(
                selectinload(Courses.course_translations)
            ).where(Courses.id == course_id)
            
            result = await self._db.execute(query)
            course = result.scalar_one_or_none()
            if not course:
                return

            vi_trans = next((t for t in course.course_translations if t.lang == 'vi'), None)
            if not vi_trans:
                vi_trans = course.course_translations[0] if course.course_translations else None
            if not vi_trans:
                return

            # 2. Gọi AI Analysis
            analysis = await ai_service.analyze_course_content(
                self._db,
                title=vi_trans.title,
                description=vi_trans.description or ""
            )

            # 3. Upsert English translation (luôn tạo/cập nhật, dù có hay chưa)
            en_trans_data = analysis.translations.get('en')
            if en_trans_data:
                await TranslationService.upsert_course_translation(
                    self._db,
                    course_id=course_id,
                    lang='en',
                    trans_in=en_trans_data,
                    is_ai=True,
                    auto_commit=False
                )

            # 4. Bổ sung Tags gợi ý
            for tag_name in analysis.suggested_tags:
                tag_slug = slugify(tag_name)
                tag_obj = (await self._db.execute(
                    select(Tags).where(Tags.slug == tag_slug)
                )).scalar_one_or_none()
                if not tag_obj:
                    tag_obj = Tags(slug=tag_slug)
                    self._db.add(tag_obj)
                    await self._db.flush()
                
                exists_link = (await self._db.execute(
                    select(CourseTags).where(
                        CourseTags.course_id == course_id,
                        CourseTags.tag_id == tag_obj.id
                    )
                )).scalar_one_or_none()
                if not exists_link:
                    self._db.add(CourseTags(course_id=course_id, tag_id=tag_obj.id))

            # 5. Cập nhật Audit Info cho VI trans
            vi_trans.is_ai_generated = True
            vi_trans.ai_model = "gemini-flash"
            vi_trans.ai_generated_at = datetime.datetime.now(datetime.timezone.utc)

            await self._db.commit()

        except Exception as exc:
            # Không làm crash cả API nếu AI gặp lỗi
            await self._db.rollback()
            import logging
            logging.getLogger(__name__).warning(
                f"[enrich_course_with_ai] AI enrichment thất bại cho course {course_id}: {exc}"
            )
