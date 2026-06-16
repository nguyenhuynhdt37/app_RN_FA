"""
AI Translation Service - NeuralEarn LMS
Tự động dịch nội dung khóa học sang nhiều ngôn ngữ.
"""

import json
import uuid
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.database import CourseCategories, CourseLevel, Categories
from app.schemas.course import (
    AIAnalysisResponse, 
    CourseTranslationInput,
)
from app.core.logging import logger as app_logger

try:
    from google import genai
    _USE_GENAI = True
except ImportError:
    import google.generativeai as genai
    _USE_GENAI = False

# Language pairs for translation
LANGUAGE_NAMES = {
    "vi": "Tiếng Việt",
    "en": "English",
    "jp": "日本語",
    "kr": "한국어",
    "fr": "Français",
    "zh": "中文",
}

# Supported target languages for auto-translation
AUTO_TRANSLATE_TARGETS = ["en"]  # Thêm more sau


def _detect_language(text: str) -> str:
    """Detect if text is primarily Vietnamese or English."""
    if not text:
        return "vi"
    vietnamese_chars = sum(1 for c in text if '\u00C0' <= c <= '\u1EF9')
    english_words = sum(1 for w in text.split() if w.lower() in {
        'the', 'is', 'are', 'was', 'were', 'and', 'or', 'but', 'in', 'on', 'at',
        'to', 'for', 'of', 'with', 'by', 'from', 'this', 'that', 'these', 'those',
    })
    return "en" if english_words > vietnamese_chars else "vi"


async def translate_text(
    text: str,
    source_lang: str,
    target_lang: str,
    style: str = "formal"
) -> str:
    """
    Translate text from source_lang to target_lang.
    
    Args:
        text: Text to translate
        source_lang: Source language code (vi, en, etc.)
        target_lang: Target language code
        style: Translation style (formal, casual, marketing)
    
    Returns:
        Translated text
    """
    if not text or not text.strip():
        return ""
    
    if source_lang == target_lang:
        return text
    
    source_name = LANGUAGE_NAMES.get(source_lang, source_lang)
    target_name = LANGUAGE_NAMES.get(target_lang, target_lang)
    
    style_instruction = ""
    if style == "casual":
        style_instruction = "Use casual, friendly tone."
    elif style == "marketing":
        style_instruction = "Use compelling marketing language, action-oriented."
    else:
        style_instruction = "Use professional, formal tone."
    
    prompt = f"""Translate the following text from {source_name} to {target_name}.

{style_instruction}

TEXT:
{text}

Return ONLY the translated text, without quotes or explanations."""

    try:
        if not settings.GEMINI_API_KEY:
            return f"[{target_lang.upper()}] {text[:50]}..."
        
        if _USE_GENAI:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
            )
            return response.text.strip()
        else:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            response = model.generate_content(prompt)
            return response.text.strip()
            
    except Exception as e:
        app_logger.error(f"Translation error {source_lang}->{target_lang}: {e}")
        return f"[{target_lang.upper()}] {text[:50]}..."


async def translate_category_content(
    name: str,
    description: Optional[str],
    source_lang: str = "vi",
    target_lang: str = "en",
) -> Dict[str, Optional[str]]:
    """
    Generate polished Vietnamese description and English localization.
    Admin may provide only a Vietnamese category name or a rough description.
    """
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY_NOT_CONFIGURED")

    prompt = f"""
You are a professional Vietnamese editor and English localization specialist for an LMS admin system.

Task:
Create polished category copy for a learning platform.

Rules:
- Return ONLY valid JSON.
- Do not use markdown code fences.
- Use the Vietnamese name as the source of truth.
- If the Vietnamese description is empty, write a new concise Vietnamese description from the name.
- If the Vietnamese description exists, improve it so it sounds natural, useful, and admin-ready.
- Vietnamese description should be one sentence, 12-35 words.
- Then translate/localize the final Vietnamese content to natural English.
- The English category name must be concise and suitable for navigation.
- The English description must be natural, clear, and professional.
- Do not include Vietnamese text in the English fields.
- Do not prefix the result with labels such as "[EN]".

Input:
{{
  "source_lang": "{source_lang}",
  "target_lang": "{target_lang}",
  "name": {json.dumps(name, ensure_ascii=False)},
  "description": {json.dumps(description, ensure_ascii=False)}
}}

Output JSON shape:
{{
  "vi_name": "Vietnamese category name",
  "vi_description": "Polished Vietnamese category description",
  "en_name": "English category name",
  "en_description": "English category description"
}}
"""

    try:
        if _USE_GENAI:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            raw_text = response.text.strip()
        else:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
            )
            raw_text = response.text.strip()
    except Exception as exc:
        app_logger.error(f"Category translation LLM error: {exc}")
        raise RuntimeError("CATEGORY_LLM_TRANSLATION_FAILED") from exc

    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        raw_text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("CATEGORY_LLM_TRANSLATION_INVALID_JSON") from exc

    vi_name = data.get("vi_name")
    vi_description = data.get("vi_description")
    translated_name = data.get("en_name")
    translated_description = data.get("en_description")

    if not isinstance(vi_name, str) or not vi_name.strip():
        raise RuntimeError("CATEGORY_VI_NAME_GENERATION_FAILED")
    if not isinstance(vi_description, str) or not vi_description.strip():
        raise RuntimeError("CATEGORY_VI_DESCRIPTION_GENERATION_FAILED")
    if not isinstance(translated_name, str) or not translated_name.strip():
        raise RuntimeError("CATEGORY_NAME_TRANSLATION_FAILED")
    if not isinstance(translated_description, str) or not translated_description.strip():
        raise RuntimeError("CATEGORY_DESCRIPTION_TRANSLATION_FAILED")

    return {
        "vi_name": vi_name.strip(),
        "vi_description": vi_description.strip(),
        "name": translated_name.strip(),
        "description": translated_description.strip(),
    }


async def translate_translation_data(
    source_data: CourseTranslationInput,
    source_lang: str,
    target_lang: str
) -> CourseTranslationInput:
    """
    Translate an entire CourseTranslationInput object.
    Translates title, subtitle, description, learning_outcomes, prerequisites.
    """
    # Translate title
    title = await translate_text(source_data.title, source_lang, target_lang)
    
    # Translate subtitle
    subtitle = None
    if source_data.subtitle:
        subtitle = await translate_text(source_data.subtitle, source_lang, target_lang)
    
    # Translate description
    description = None
    if source_data.description:
        description = await translate_text(source_data.description, source_lang, target_lang, style="marketing")
    
    # Translate learning outcomes
    learning_outcomes = []
    for outcome in (source_data.learning_outcomes or []):
        translated = await translate_text(outcome, source_lang, target_lang)
        if translated:
            learning_outcomes.append(translated)
    
    # Translate prerequisites
    prerequisites = []
    for prereq in (source_data.prerequisites or []):
        translated = await translate_text(prereq, source_lang, target_lang)
        if translated:
            prerequisites.append(translated)
    
    return CourseTranslationInput(
        lang=target_lang,
        title=title,
        subtitle=subtitle,
        description=description,
        learning_outcomes=learning_outcomes,
        prerequisites=prerequisites,
        slug=None,  # Slug cần generate riêng
    )


class AIService:
    """
    AI Service cho NeuralEarn LMS.
    - Tự nhận diện ngôn ngữ đầu vào
    - Phân tích & dịch nội dung khóa học
    - Auto-translate sang các ngôn ngữ khác
    """

    @staticmethod
    async def analyze_course_content(
        db: AsyncSession,
        title: str,
        description: str
    ) -> AIAnalysisResponse:
        """
        AI phân tích và dịch nội dung khóa học.
        Trả về structured response với translations dict.
        """
        # 1. Lấy tất cả categories có sẵn để AI tham chiếu
        result = await db.execute(
            select(Categories).options(selectinload(Categories.category_translations))
        )
        categories = result.scalars().all()
        categories_list = []
        for c in categories:
            # Lấy tên tiếng Việt hoặc bản đầu tiên
            name = ""
            for t in c.category_translations:
                if t.lang == "vi":
                    name = t.name
                    break
            if not name and c.category_translations:
                name = c.category_translations[0].name
                
            categories_list.append({"id": str(c.id), "name": name or str(c.id)})

        # 2. Detect ngôn ngữ
        lang = _detect_language(title or description)
        source_lang = lang
        target_lang = "en" if lang == "vi" else "vi"

        # 3. Build prompt
        prompt = f"""
Bạn là chuyên gia phân tích & dịch thuật cho hệ thống LMS NeuralEarn.

NHIỆM VỤ:
1. Phân tích nội dung khóa học
2. Dịch SONG NGỮ (VI ↔ EN) tự động

NGÔN NGỮ ĐẦU VÀO: {"Tiếng Việt" if lang == "vi" else "English"}

KHÓA HỌC ĐẦU VÀO:
- Tiêu đề: {title or "(trống)"}
- Mô tả: {description or "(trống)"}

DANH MỤC HIỆN CÓ:
{json.dumps(categories_list, ensure_ascii=False, indent=2)}

YÊU CẦU:
1. Dịch đầy đủ: title, subtitle, description, learning_outcomes, prerequisites
2. learning_outcomes: 3-5 items, bắt đầu "Sau khóa học..." (VI) / "After this course..." (EN)
3. prerequisites: 2-4 yêu cầu trước khi học
4. description: hỗ trợ markdown
5. Chọn category từ DANH MỤC HIỆN CÓ

TRẢ VỀ JSON HỢP LỆ (KHÔNG markdown code block):
{{
    "source_translation": {{
        "lang": "{source_lang}",
        "title": "Tiêu đề gốc",
        "subtitle": "Mô tả ngắn gốc",
        "description": "Mô tả chi tiết gốc (markdown)",
        "learning_outcomes": ["Kết quả 1", "Kết quả 2"],
        "prerequisites": ["Yêu cầu 1"]
    }},
    "translated_translation": {{
        "lang": "{target_lang}",
        "title": "Translated Title",
        "subtitle": "Translated Subtitle",
        "description": "Translated Description (markdown)",
        "learning_outcomes": ["Outcome 1", "Outcome 2"],
        "prerequisites": ["Prerequisite 1"]
    }},
    "existing_category_ids": ["uuid-hiện-có"],
    "new_categories": [],
    "suggested_tags": ["tag1", "tag2", "tag3"],
    "suggested_level": "BEGINNER",
    "difficulty_score": 5,
    "confidence_score": 0.95
}}
"""

        # 4. Gọi Gemini
        try:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is not configured")

            if _USE_GENAI:
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                raw_text = response.text.strip()
            else:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(settings.GEMINI_MODEL)
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                raw_text = response.text.strip()

            # Parse response
            if raw_text.startswith("```"):
                lines = raw_text.split('\n')
                raw_text = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])

            ai_data = json.loads(raw_text)

        except Exception as e:
            app_logger.error(f"AI Analysis Error: {str(e)}")
            return AIService._fallback_response(title, description, lang)

        # 5. Xử lý categories
        final_category_ids: List[uuid.UUID] = []
        for cid in ai_data.get("existing_category_ids", []):
            try:
                final_category_ids.append(uuid.UUID(cid))
            except (ValueError, TypeError):
                pass

        await db.commit()

        # 6. Build translations dict
        translations: Dict[str, CourseTranslationInput] = {
            source_lang: CourseTranslationInput(
                lang=source_lang,
                title=ai_data.get("source_translation", {}).get("title", title or ""),
                subtitle=ai_data.get("source_translation", {}).get("subtitle"),
                description=ai_data.get("source_translation", {}).get("description"),
                learning_outcomes=ai_data.get("source_translation", {}).get("learning_outcomes", []),
                prerequisites=ai_data.get("source_translation", {}).get("prerequisites", []),
            ),
            target_lang: CourseTranslationInput(
                lang=target_lang,
                title=ai_data.get("translated_translation", {}).get("title", ""),
                subtitle=ai_data.get("translated_translation", {}).get("subtitle"),
                description=ai_data.get("translated_translation", {}).get("description"),
                learning_outcomes=ai_data.get("translated_translation", {}).get("learning_outcomes", []),
                prerequisites=ai_data.get("translated_translation", {}).get("prerequisites", []),
            ),
        }

        return AIAnalysisResponse(
            suggested_category_ids=final_category_ids,
            new_categories=ai_data.get("new_categories", []),
            translations=translations,
            suggested_tags=ai_data.get("suggested_tags", []),
            suggested_level=CourseLevel(ai_data.get("suggested_level", "BEGINNER")),
            difficulty_score=ai_data.get("difficulty_score", 5),
            confidence_score=ai_data.get("confidence_score", 0.5),
        )

    @staticmethod
    async def auto_translate_course(
        db: AsyncSession,
        course_id: uuid.UUID,
        source_lang: str,
        target_langs: List[str] = None
    ) -> Dict[str, CourseTranslationInput]:
        """
        Tự động dịch course sang các ngôn ngữ khác.
        Dùng sau khi tạo course mới hoặc update translation.
        
        Args:
            db: Database session
            course_id: Course ID
            source_lang: Ngôn ngữ nguồn (đã có dữ liệu)
            target_langs: Danh sách ngôn ngữ cần dịch (mặc định: AUTO_TRANSLATE_TARGETS)
        
        Returns:
            Dict các translation đã dịch
        """
        if target_langs is None:
            target_langs = AUTO_TRANSLATE_TARGETS.copy()
        
        # Import ở đây để tránh circular import
        from app.services.translation import TranslationService
        
        # Lấy translation nguồn
        source_trans = await TranslationService.get_course_translation(db, course_id, source_lang)
        if not source_trans:
            app_logger.warning(f"No source translation found for course {course_id} in {source_lang}")
            return {}
        
        source_data = CourseTranslationInput(
            lang=source_lang,
            title=source_trans.title,
            subtitle=source_trans.subtitle,
            description=source_trans.description,
            learning_outcomes=source_trans.learning_outcomes or [],
            prerequisites=source_trans.prerequisites or [],
        )
        
        results = {}
        
        # Translate từng ngôn ngữ
        for target_lang in target_langs:
            if target_lang == source_lang:
                continue
            
            try:
                translated_data = await translate_translation_data(
                    source_data, source_lang, target_lang
                )
                
                # Upsert translation
                await TranslationService.upsert_course_translation(
                    db, course_id, target_lang, translated_data, auto_commit=False
                )
                
                results[target_lang] = translated_data
                app_logger.info(f"Auto-translated course {course_id} to {target_lang}")
                
            except Exception as e:
                app_logger.error(f"Failed to auto-translate to {target_lang}: {e}")
        
        await db.commit()
        return results

    @staticmethod
    def _fallback_response(title: str, description: str, lang: str) -> AIAnalysisResponse:
        """Fallback khi AI lỗi."""
        target = "en" if lang == "vi" else "vi"
        return AIAnalysisResponse(
            translations={
                lang: CourseTranslationInput(
                    lang=lang,
                    title=title or "",
                    description=description or "",
                ),
                target: CourseTranslationInput(
                    lang=target,
                    title=title or "",
                    description=description or "",
                ),
            },
            confidence_score=0.1,
        )


ai_service = AIService()
