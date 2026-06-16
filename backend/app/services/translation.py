"""
Translation Service - NeuralEarn LMS
Kiến trúc i18n theo style Netflix/Spotify/Duolingo.

Translating content = INSERT row mới, không cần ALTER TABLE.
"""

from typing import Dict, List, Optional, Any, TYPE_CHECKING
from uuid import UUID
from sqlalchemy import select, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import CourseTranslations, SectionTranslations, CategoryTranslations
from app.schemas.course import CourseTranslationInput, SectionTranslationRead, CategoryTranslationRead

if TYPE_CHECKING:
    from app.models.database import Courses, Sections, CourseCategories


# Supported languages
SUPPORTED_LANGS = ["vi", "en", "jp", "kr", "fr", "zh"]
DEFAULT_LANG = "vi"


class TranslationService:
    """
    Service thống nhất mọi thao tác với translations.
    
    Pattern:
    - get_or_fallback: Lấy translation, fallback nếu thiếu
    - upsert: Update hoặc insert translation
    - bulk_translate: AI translate hàng loạt
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # COURSE TRANSLATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    @staticmethod
    async def get_course_translation(
        db: AsyncSession,
        course_id: UUID,
        lang: str
    ) -> Optional[CourseTranslations]:
        """Lấy translation cụ thể của course."""
        result = await db.execute(
            select(CourseTranslations).where(
                and_(
                    CourseTranslations.course_id == course_id,
                    CourseTranslations.lang == lang
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_course_translations(
        db: AsyncSession,
        course_id: UUID
    ) -> Dict[str, CourseTranslations]:
        """Lấy tất cả translations của course, trả về dict theo lang."""
        result = await db.execute(
            select(CourseTranslations).where(
                CourseTranslations.course_id == course_id
            )
        )
        translations = result.scalars().all()
        return {t.lang: t for t in translations}

    @staticmethod
    async def get_course_title(
        db: AsyncSession,
        course_id: UUID,
        lang: str = DEFAULT_LANG
    ) -> str:
        """Lấy title với fallback logic."""
        translation = await TranslationService.get_course_translation(db, course_id, lang)
        if translation and translation.title:
            return translation.title
        
        # Fallback: thử Vietnamese
        if lang != DEFAULT_LANG:
            vi_trans = await TranslationService.get_course_translation(db, course_id, DEFAULT_LANG)
            if vi_trans and vi_trans.title:
                return vi_trans.title
        
        # Fallback: bất kỳ ngôn ngữ nào
        all_trans = await TranslationService.get_all_course_translations(db, course_id)
        for t in all_trans.values():
            if t.title:
                return t.title
        
        return "Untitled Course"

    @staticmethod
    async def upsert_course_translation(
        db: AsyncSession,
        course_id: UUID,
        lang: str,
        trans_in: CourseTranslationInput,
        is_ai: bool = False,
        auto_commit: bool = True
    ) -> CourseTranslations:
        """
        Upsert translation cho course.
        """
        existing = await TranslationService.get_course_translation(db, course_id, lang)
        
        if existing:
            # Update
            existing.title = trans_in.title or existing.title
            if trans_in.subtitle is not None:
                existing.subtitle = trans_in.subtitle
            if trans_in.description is not None:
                existing.description = trans_in.description
            if trans_in.learning_outcomes is not None:
                existing.learning_outcomes = trans_in.learning_outcomes
            if trans_in.prerequisites is not None:
                existing.prerequisites = trans_in.prerequisites
            if trans_in.slug is not None:
                existing.slug = trans_in.slug
            
            if is_ai:
                existing.is_ai_generated = True
                from datetime import datetime
                existing.ai_generated_at = datetime.utcnow()
                
            translation = existing
        else:
            # Insert
            translation = CourseTranslations(
                course_id=course_id,
                lang=lang,
                title=trans_in.title or "",
                subtitle=trans_in.subtitle,
                description=trans_in.description,
                slug=trans_in.slug,
                is_ai_generated=is_ai
            )
            db.add(translation)
        
        if auto_commit:
            await db.commit()
            await db.refresh(translation)
        
        return translation

    @staticmethod
    async def delete_course_translation(
        db: AsyncSession,
        course_id: UUID,
        lang: str
    ) -> bool:
        """Xóa translation cụ thể."""
        result = await db.execute(
            delete(CourseTranslations).where(
                and_(
                    CourseTranslations.course_id == course_id,
                    CourseTranslations.lang == lang
                )
            )
        )
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def get_course_slug_for_lang(
        db: AsyncSession,
        course_id: UUID,
        lang: str
    ) -> Optional[str]:
        """Lấy slug của course theo ngôn ngữ (dùng cho SEO)."""
        translation = await TranslationService.get_course_translation(db, course_id, lang)
        return translation.slug if translation else None

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION TRANSLATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    @staticmethod
    async def get_section_translation(
        db: AsyncSession,
        section_id: UUID,
        lang: str
    ) -> Optional[SectionTranslations]:
        """Lấy translation cụ thể của section."""
        result = await db.execute(
            select(SectionTranslations).where(
                and_(
                    SectionTranslations.section_id == section_id,
                    SectionTranslations.lang == lang
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_section_translations(
        db: AsyncSession,
        section_id: UUID
    ) -> Dict[str, SectionTranslations]:
        """Lấy tất cả translations của section."""
        result = await db.execute(
            select(SectionTranslations).where(
                SectionTranslations.section_id == section_id
            )
        )
        translations = result.scalars().all()
        return {t.lang: t for t in translations}

    @staticmethod
    async def upsert_section_translation(
        db: AsyncSession,
        section_id: UUID,
        lang: str,
        title: str,
        auto_commit: bool = True
    ) -> SectionTranslations:
        """Upsert translation cho section."""
        existing = await TranslationService.get_section_translation(db, section_id, lang)
        
        if existing:
            existing.title = title or existing.title
            translation = existing
        else:
            translation = SectionTranslations(
                section_id=section_id,
                lang=lang,
                title=title or "",
            )
            db.add(translation)
        
        if auto_commit:
            await db.commit()
            await db.refresh(translation)
        
        return translation

    @staticmethod
    async def get_section_title(
        db: AsyncSession,
        section_id: UUID,
        lang: str = DEFAULT_LANG
    ) -> str:
        """Lấy title của section với fallback."""
        translation = await TranslationService.get_section_translation(db, section_id, lang)
        if translation and translation.title:
            return translation.title
        
        if lang != DEFAULT_LANG:
            vi_trans = await TranslationService.get_section_translation(db, section_id, DEFAULT_LANG)
            if vi_trans and vi_trans.title:
                return vi_trans.title
        
        return "Untitled Section"

    # ═══════════════════════════════════════════════════════════════════════════
    # CATEGORY TRANSLATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    @staticmethod
    async def get_category_translation(
        db: AsyncSession,
        category_id: UUID,
        lang: str
    ) -> Optional[CategoryTranslations]:
        """Lấy translation cụ thể của category."""
        result = await db.execute(
            select(CategoryTranslations).where(
                and_(
                    CategoryTranslations.category_id == category_id,
                    CategoryTranslations.lang == lang
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def upsert_category_translation(
        db: AsyncSession,
        category_id: UUID,
        lang: str,
        name: str,
        description: Optional[str] = None,
        auto_commit: bool = True
    ) -> CategoryTranslations:
        """Upsert translation cho category."""
        existing = await TranslationService.get_category_translation(db, category_id, lang)
        
        if existing:
            existing.name = name or existing.name
            if description is not None:
                existing.description = description
            translation = existing
        else:
            translation = CategoryTranslations(
                category_id=category_id,
                lang=lang,
                name=name or "",
                description=description,
            )
            db.add(translation)
        
        if auto_commit:
            await db.commit()
            await db.refresh(translation)
        
        return translation

    @staticmethod
    async def get_category_name(
        db: AsyncSession,
        category_id: UUID,
        lang: str = DEFAULT_LANG
    ) -> str:
        """Lấy name của category với fallback."""
        translation = await TranslationService.get_category_translation(db, category_id, lang)
        if translation and translation.name:
            return translation.name
        
        if lang != DEFAULT_LANG:
            vi_trans = await TranslationService.get_category_translation(db, category_id, DEFAULT_LANG)
            if vi_trans and vi_trans.name:
                return vi_trans.name
        
        return "Untitled Category"

    # ═══════════════════════════════════════════════════════════════════════════
    # BULK OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    @staticmethod
    async def create_course_with_translations(
        db: AsyncSession,
        translations: Dict[str, CourseTranslationInput],
        default_lang: str = DEFAULT_LANG,
        auto_commit: bool = True
    ) -> Dict[str, CourseTranslations]:
        """
        Tạo nhiều translations cho một course mới.
        """
        result = {}
        
        for lang, data in translations.items():
            if lang not in SUPPORTED_LANGS:
                continue
            
            translation = CourseTranslations(
                course_id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder
                lang=lang,
                title=data.title or "",
                subtitle=data.subtitle,
                description=data.description,
                slug=data.slug,
            )
            db.add(translation)
            result[lang] = translation
        
        if auto_commit:
            await db.commit()
            for t in result.values():
                await db.refresh(t)
        
        return result


# Singleton instance
translation_service = TranslationService()
