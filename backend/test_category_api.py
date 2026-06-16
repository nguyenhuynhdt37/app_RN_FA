    #!/usr/bin/env python3
"""
test_category_api.py - Integration tests for Category API.

Run:
  DEBUG=false venv/bin/python test_category_api.py

What it verifies:
  1. Unauthenticated request is rejected.
  2. Non-admin request is forbidden.
  3. Admin can create category from Vietnamese input.
  4. Vietnamese and English translations are persisted with correct flags.
  5. Duplicate Vietnamese category name returns CATEGORY_ALREADY_EXISTS.
  6. Invalid payload returns validation error.

The test mocks AI translation to avoid external network/Gemini dependency.
Temporary database rows are cleaned up automatically.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy import delete, select

from app.core.security import create_access_token
from app.db.session import AsyncSessionLocal
from app.main import app
from app.models import (
    Categories,
    CategoryTranslations,
    CourseCategories,
    CourseLevel,
    Courses,
    CourseTranslations,
)
import app.services.category as category_service_module


BASE_URL = "http://testserver"


@dataclass
class TestResult:
    name: str
    passed: bool
    status_code: int | None = None
    detail: str = ""


results: list[TestResult] = []


def section(title: str) -> None:
    print(f"\n{'-' * 60}")
    print(f"  {title}")
    print(f"{'-' * 60}")


def ok(name: str, status_code: int | None = None) -> None:
    results.append(TestResult(name=name, passed=True, status_code=status_code))
    status = f" [{status_code}]" if status_code is not None else ""
    print(f"  OK  {name}{status}")


def fail(name: str, status_code: int | None, detail: str, response: Any = None) -> None:
    results.append(TestResult(name=name, passed=False, status_code=status_code, detail=detail))
    print(f"  FAIL {name} [{status_code}] -> {detail}")
    if response is not None:
        print(f"       Response: {json.dumps(response, ensure_ascii=False, indent=2)[:500]}")


async def fake_translate_category_content(
    name: str,
    description: str | None,
    source_lang: str = "vi",
    target_lang: str = "en",
) -> dict[str, str | None]:
    return {
        "vi_name": name,
        "vi_description": "Danh mục dành cho các khóa học lập trình, phát triển phần mềm và xây dựng sản phẩm số thực tế.",
        "name": "Programming",
        "description": "Courses about software development, backend systems, frontend apps, and mobile engineering.",
    }


async def fake_failed_translate_category_content(
    name: str,
    description: str | None,
    source_lang: str = "vi",
    target_lang: str = "en",
) -> dict[str, str | None]:
    return {
        "vi_name": name,
        "vi_description": description or "Mô tả lỗi không được lưu.",
        "name": f"[EN] {name}...",
        "description": f"[EN] {description}..." if description else None,
    }


async def cleanup_categories_by_names(names: set[str]) -> int:
    if not names:
        return 0

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Categories.id)
            .join(CategoryTranslations, Categories.id == CategoryTranslations.category_id)
            .where(CategoryTranslations.lang == "vi")
            .where(CategoryTranslations.name.in_(names))
        )
        category_ids = [row[0] for row in result.all()]

        if not category_ids:
            return 0

        await db.execute(delete(Categories).where(Categories.id.in_(category_ids)))
        await db.commit()
        return len(category_ids)


async def get_translation_rows(category_id: uuid.UUID) -> list[tuple[str, str, bool | None]]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(
                CategoryTranslations.lang,
                CategoryTranslations.name,
                CategoryTranslations.is_auto_translated,
            )
            .where(CategoryTranslations.category_id == category_id)
            .order_by(CategoryTranslations.lang)
        )
        return [(row.lang, row.name, row.is_auto_translated) for row in result.all()]


async def get_translation_detail_rows(category_id: uuid.UUID) -> list[tuple[str, str, str | None, bool | None]]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(
                CategoryTranslations.lang,
                CategoryTranslations.name,
                CategoryTranslations.description,
                CategoryTranslations.is_auto_translated,
            )
            .where(CategoryTranslations.category_id == category_id)
            .order_by(CategoryTranslations.lang)
        )
        return [(row.lang, row.name, row.description, row.is_auto_translated) for row in result.all()]


async def attach_temp_course(category_id: uuid.UUID) -> uuid.UUID:
    async with AsyncSessionLocal() as db:
        suffix = uuid.uuid4().hex[:10]
        course = Courses(
            level=CourseLevel.BEGINNER,
            is_published=True,
            default_slug=f"category-api-test-{suffix}",
            base_price=199000,
            views=123,
            total_enrolls=7,
            revenue=1393000,
            rating_avg=4.6,
            lessons_count=12,
            approval_status="approved",
        )
        db.add(course)
        await db.flush()
        db.add(CourseCategories(course_id=course.id, category_id=category_id))
        db.add(
            CourseTranslations(
                course_id=course.id,
                lang="vi",
                title="Khóa học lập trình API",
                subtitle="Xây dựng backend thực tế",
                description="Khóa học dùng để kiểm thử category detail.",
                slug=f"khoa-hoc-lap-trinh-api-{suffix}",
            )
        )
        db.add(
            CourseTranslations(
                course_id=course.id,
                lang="en",
                title="API Programming Course",
                subtitle="Build real backend services",
                description="Course row used to verify category detail.",
                slug=f"api-programming-course-{suffix}",
            )
        )
        await db.commit()
        return course.id


async def cleanup_courses(course_ids: set[uuid.UUID]) -> int:
    if not course_ids:
        return 0

    async with AsyncSessionLocal() as db:
        await db.execute(delete(Courses).where(Courses.id.in_(course_ids)))
        await db.commit()
        return len(course_ids)


async def run_tests() -> None:
    created_names: set[str] = set()
    created_course_ids: set[uuid.UUID] = set()
    original_translate = category_service_module.translate_category_content
    category_service_module.translate_category_content = fake_translate_category_content

    admin_token = create_access_token(str(uuid.uuid4()), roles=["admin"])
    student_token = create_access_token(str(uuid.uuid4()), roles=["student"])
    category_name = f"Danh mục API test {uuid.uuid4().hex[:8]}"
    created_names.add(category_name)

    request_body = {
        "name": category_name,
        "description": "Mô tả kiểm thử tạo danh mục.",
        "auto_translate_en": True,
    }

    try:
        await cleanup_categories_by_names(created_names)

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url=BASE_URL) as client:
            section("1. Auth guards")
            unauth = await client.post("/api/v1/categories", json=request_body)
            if unauth.status_code == 401:
                ok("POST /api/v1/categories rejects unauthenticated request", unauth.status_code)
            else:
                fail("Unauthenticated request should be 401", unauth.status_code, "Unexpected status", unauth.json())

            forbidden = await client.post(
                "/api/v1/categories",
                headers={"Authorization": f"Bearer {student_token}"},
                json=request_body,
            )
            if forbidden.status_code == 403:
                ok("POST /api/v1/categories rejects non-admin role", forbidden.status_code)
            else:
                fail("Student request should be 403", forbidden.status_code, "Unexpected status", forbidden.json())

            section("2. Successful create with AI-generated English")
            created = await client.post(
                "/api/v1/categories",
                headers={"Authorization": f"Bearer {admin_token}"},
                json=request_body,
            )
            created_payload = created.json()
            if created.status_code == 201:
                ok("POST /api/v1/categories creates category", created.status_code)
            else:
                fail("Create category should be 201", created.status_code, "Unexpected status", created_payload)
                return

            category_id = uuid.UUID(created_payload["id"])
            translations = created_payload.get("translations", {})
            if set(translations.keys()) == {"vi", "en"}:
                ok("Response includes vi and en translations")
            else:
                fail("Response translations mismatch", created.status_code, "Expected vi/en", created_payload)

            rows = await get_translation_rows(category_id)
            print(f"       DB translations: {rows}")
            if {row[0] for row in rows} == {"vi", "en"}:
                ok("Database persisted vi and en translations")
            else:
                fail("Database translations mismatch", None, "Expected vi/en", rows)

            if any(lang == "vi" and auto is False for lang, _, auto in rows):
                ok("Vietnamese translation is marked manual")
            else:
                fail("Vietnamese translation flag invalid", None, "Expected is_auto_translated=False", rows)

            if any(lang == "en" and auto is True for lang, _, auto in rows):
                ok("English translation is marked auto-translated")
            else:
                fail("English translation flag invalid", None, "Expected is_auto_translated=True", rows)

            detail_rows = await get_translation_detail_rows(category_id)
            if any(
                lang == "vi" and description == "Mô tả kiểm thử tạo danh mục."
                for lang, _, description, _ in detail_rows
            ):
                ok("Provided Vietnamese description is preserved before persistence")
            else:
                fail("Vietnamese description should be preserved", None, "Unexpected descriptions", detail_rows)

            section("3. Course count aggregation")
            course_id = await attach_temp_course(category_id)
            created_course_ids.add(course_id)
            counted = await client.get(
                "/api/v1/categories",
                params={"lang": "vi", "search": category_name, "page_size": 10},
            )
            counted_payload = counted.json()
            counted_items = counted_payload.get("items", [])
            matching_item = next((item for item in counted_items if item.get("id") == str(category_id)), None)
            if counted.status_code == 200 and matching_item and matching_item.get("course_count") == 1:
                ok("GET /api/v1/categories returns course_count per category", counted.status_code)
            else:
                fail("Category list should include course_count=1", counted.status_code, "Unexpected response", counted_payload)

            section("4. Full category detail")
            detail = await client.get(
                f"/api/v1/categories/{category_id}",
                params={"lang": "vi", "course_limit": 10},
            )
            detail_payload = detail.json()
            if detail.status_code == 200:
                ok("GET /api/v1/categories/{id} returns full detail", detail.status_code)
            else:
                fail("Full category detail should be 200", detail.status_code, "Unexpected response", detail_payload)

            detail_translations = detail_payload.get("translations_full", [])
            if {item.get("lang") for item in detail_translations} == {"vi", "en"}:
                ok("Full detail includes all category translations")
            else:
                fail("Full detail translations mismatch", detail.status_code, "Expected vi/en", detail_payload)

            detail_stats = detail_payload.get("stats", {})
            if (
                detail_stats.get("total_courses") == 1
                and detail_stats.get("published_courses") == 1
                and detail_stats.get("total_enrolls") == 7
                and detail_stats.get("total_revenue") == 1393000
                and detail_stats.get("total_views") == 123
            ):
                ok("Full detail aggregates course metrics")
            else:
                fail("Full detail stats mismatch", detail.status_code, "Unexpected stats", detail_payload)

            detail_courses = detail_payload.get("courses", [])
            first_course = detail_courses[0] if detail_courses else {}
            course_translations = first_course.get("translations", {})
            if (
                first_course.get("id") == str(course_id)
                and first_course.get("level") == "BEGINNER"
                and first_course.get("total_enrolls") == 7
                and set(course_translations.keys()) == {"vi", "en"}
            ):
                ok("Full detail embeds related course summaries with translations")
            else:
                fail("Full detail courses mismatch", detail.status_code, "Unexpected courses", detail_payload)

            missing_detail = await client.get(f"/api/v1/categories/{uuid.uuid4()}")
            missing_payload = missing_detail.json()
            missing_code = missing_payload.get("detail", {}).get("code")
            if missing_detail.status_code == 404 and missing_code == "CATEGORY_NOT_FOUND":
                ok("Full detail returns CATEGORY_NOT_FOUND for missing category", missing_detail.status_code)
            else:
                fail("Missing full detail should be CATEGORY_NOT_FOUND", missing_detail.status_code, "Unexpected response", missing_payload)

            section("5. Update Vietnamese content")
            update_source_name = f"Danh mục cập nhật nguồn {uuid.uuid4().hex[:8]}"
            update_target_name = f"Danh mục cập nhật mới {uuid.uuid4().hex[:8]}"
            created_names.update({update_source_name, update_target_name})
            update_source = await client.post(
                "/api/v1/categories",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "name": update_source_name,
                    "description": "Mô tả ban đầu để kiểm thử cập nhật.",
                    "auto_translate_en": True,
                },
            )
            update_source_payload = update_source.json()
            if update_source.status_code != 201:
                fail("Update source category should be created", update_source.status_code, "Unexpected response", update_source_payload)
                return

            update_category_id = uuid.UUID(update_source_payload["id"])
            forbidden_update = await client.patch(
                f"/api/v1/categories/{update_category_id}",
                headers={"Authorization": f"Bearer {student_token}"},
                json={"name": update_target_name},
            )
            if forbidden_update.status_code == 403:
                ok("PATCH /api/v1/categories/{id} rejects non-admin role", forbidden_update.status_code)
            else:
                fail("Student update should be 403", forbidden_update.status_code, "Unexpected response", forbidden_update.json())

            updated = await client.patch(
                f"/api/v1/categories/{update_category_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "name": update_target_name,
                    "description": "Admin sửa mô tả tiếng Việt.",
                },
            )
            updated_payload = updated.json()
            if updated.status_code == 200:
                ok("PATCH /api/v1/categories/{id} updates category", updated.status_code)
            else:
                fail("Update category should be 200", updated.status_code, "Unexpected response", updated_payload)

            updated_rows = await get_translation_detail_rows(update_category_id)
            if any(lang == "vi" and name == update_target_name for lang, name, _, _ in updated_rows):
                ok("Update persists Vietnamese name")
            else:
                fail("Updated Vietnamese name mismatch", None, "Unexpected translations", updated_rows)

            if any(
                lang == "vi" and description == "Admin sửa mô tả tiếng Việt."
                for lang, _, description, _ in updated_rows
            ):
                ok("Update preserves provided Vietnamese description")
            else:
                fail("Updated Vietnamese description should be preserved", None, "Unexpected translations", updated_rows)

            if any(lang == "en" and name == "Programming" and auto is True for lang, name, _, auto in updated_rows):
                ok("Update regenerates English translation with AI")
            else:
                fail("Updated English translation mismatch", None, "Unexpected translations", updated_rows)

            category_service_module.translate_category_content = fake_failed_translate_category_content
            unchanged = await client.patch(
                f"/api/v1/categories/{update_category_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"name": update_target_name},
            )
            if unchanged.status_code == 200:
                ok("PATCH without content changes skips AI regeneration", unchanged.status_code)
            else:
                fail("No-change update should not call failing AI", unchanged.status_code, "Unexpected response", unchanged.json())

            failed_update = await client.patch(
                f"/api/v1/categories/{update_category_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"description": "Mô tả mới nhưng AI trả kết quả lỗi."},
            )
            failed_update_payload = failed_update.json()
            failed_update_code = failed_update_payload.get("detail", {}).get("code")
            if failed_update.status_code == 502 and failed_update_code == "CATEGORY_TRANSLATION_FAILED":
                ok("Changed update rejects invalid AI translation", failed_update.status_code)
            else:
                fail("Failed update should be CATEGORY_TRANSLATION_FAILED", failed_update.status_code, "Unexpected response", failed_update_payload)

            rollback_rows = await get_translation_detail_rows(update_category_id)
            if rollback_rows == updated_rows:
                ok("Failed update rolls back translations")
            else:
                fail("Failed update should rollback translations", None, "Unexpected translations", rollback_rows)
            category_service_module.translate_category_content = fake_translate_category_content

            duplicate_update = await client.patch(
                f"/api/v1/categories/{update_category_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"name": category_name},
            )
            duplicate_update_payload = duplicate_update.json()
            duplicate_update_code = duplicate_update_payload.get("detail", {}).get("code")
            if duplicate_update.status_code == 409 and duplicate_update_code == "CATEGORY_ALREADY_EXISTS":
                ok("Update duplicate Vietnamese name returns CATEGORY_ALREADY_EXISTS", duplicate_update.status_code)
            else:
                fail(
                    "Duplicate update should be CATEGORY_ALREADY_EXISTS",
                    duplicate_update.status_code,
                    "Unexpected response",
                    duplicate_update_payload,
                )

            missing_update = await client.patch(
                f"/api/v1/categories/{uuid.uuid4()}",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"name": f"Danh mục không tồn tại {uuid.uuid4().hex[:8]}"},
            )
            missing_update_payload = missing_update.json()
            missing_update_code = missing_update_payload.get("detail", {}).get("code")
            if missing_update.status_code == 404 and missing_update_code == "CATEGORY_NOT_FOUND":
                ok("Update returns CATEGORY_NOT_FOUND for missing category", missing_update.status_code)
            else:
                fail("Missing update should be CATEGORY_NOT_FOUND", missing_update.status_code, "Unexpected response", missing_update_payload)

            section("6. Duplicate and validation")
            duplicate = await client.post(
                "/api/v1/categories",
                headers={"Authorization": f"Bearer {admin_token}"},
                json=request_body,
            )
            duplicate_payload = duplicate.json()
            duplicate_code = duplicate_payload.get("detail", {}).get("code")
            if duplicate.status_code == 409 and duplicate_code == "CATEGORY_ALREADY_EXISTS":
                ok("Duplicate Vietnamese name returns CATEGORY_ALREADY_EXISTS", duplicate.status_code)
            else:
                fail("Duplicate should be CATEGORY_ALREADY_EXISTS", duplicate.status_code, "Unexpected response", duplicate_payload)

            invalid = await client.post(
                "/api/v1/categories",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"name": "   ", "description": "Invalid blank name"},
            )
            if invalid.status_code == 422:
                ok("Blank category name returns validation error", invalid.status_code)
            else:
                fail("Blank name should be 422", invalid.status_code, "Unexpected status", invalid.json())

            section("10. Missing description")
            no_description_name = f"Danh mục thiếu mô tả {uuid.uuid4().hex[:8]}"
            created_names.add(no_description_name)
            no_description = await client.post(
                "/api/v1/categories",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "name": no_description_name,
                    "auto_translate_en": True,
                },
            )
            no_description_payload = no_description.json()
            if no_description.status_code == 201:
                ok("Category can be created without admin description", no_description.status_code)
                generated_rows = await get_translation_detail_rows(uuid.UUID(no_description_payload["id"]))
                if any(lang == "vi" and description for lang, _, description, _ in generated_rows):
                    ok("AI generates Vietnamese description when omitted")
                else:
                    fail("Missing description should be generated", None, "No vi description", generated_rows)
            else:
                fail("Missing description create should be 201", no_description.status_code, "Unexpected status", no_description_payload)

            section("8. Delete category")
            # 8a: delete category with no courses - success
            delete_target_name = f"Danh muc xoa {uuid.uuid4().hex[:8]}"
            created_names.add(delete_target_name)
            delete_create = await client.post(
                "/api/v1/categories",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "name": delete_target_name,
                    "description": "Danh muc de kiem tra xoa.",
                    "auto_translate_en": True,
                },
            )
            delete_create_payload = delete_create.json()
            if delete_create.status_code != 201:
                fail("Delete source category should be created", delete_create.status_code, "Unexpected response", delete_create_payload)
                return
            delete_category_id = uuid.UUID(delete_create_payload["id"])

            # 8b: unauthenticated delete rejected
            unauth_delete = await client.delete(f"/api/v1/categories/{delete_category_id}")
            if unauth_delete.status_code == 401:
                ok("DELETE /api/v1/categories/{id} rejects unauthenticated request", unauth_delete.status_code)
            else:
                fail("Unauthenticated delete should be 401", unauth_delete.status_code, "Unexpected status", unauth_delete.json())

            # 8c: non-admin delete rejected
            student_delete = await client.delete(
                f"/api/v1/categories/{delete_category_id}",
                headers={"Authorization": f"Bearer {student_token}"},
            )
            if student_delete.status_code == 403:
                ok("DELETE /api/v1/categories/{id} rejects non-admin role", student_delete.status_code)
            else:
                fail("Student delete should be 403", student_delete.status_code, "Unexpected status", student_delete.json())

            # 8d: successful delete returns 204
            deleted = await client.delete(
                f"/api/v1/categories/{delete_category_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            if deleted.status_code == 204:
                ok("DELETE /api/v1/categories/{id} returns 204 for empty category", deleted.status_code)
            else:
                fail("Delete empty category should be 204", deleted.status_code, "Unexpected status", deleted.json())

            # 8e: deleted category no longer exists
            after_delete = await client.get(f"/api/v1/categories/{delete_category_id}")
            after_delete_code = after_delete.json().get("detail", {}).get("code")
            if after_delete.status_code == 404 and after_delete_code == "CATEGORY_NOT_FOUND":
                ok("Deleted category returns CATEGORY_NOT_FOUND on GET")
            else:
                fail("Deleted category should be 404", after_delete.status_code, "Unexpected status", after_delete.json())

            # 8f: cannot delete category linked to courses (409)
            # category_id still has the temp course from section 3
            cannot_delete = await client.delete(
                f"/api/v1/categories/{category_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            cannot_delete_payload = cannot_delete.json()
            cannot_delete_code = cannot_delete_payload.get("detail", {}).get("code")
            if cannot_delete.status_code == 409 and cannot_delete_code == "CATEGORY_HAS_COURSES":
                ok("DELETE returns CATEGORY_HAS_COURSES when linked to courses", cannot_delete.status_code)
            else:
                fail("Category with courses should return CATEGORY_HAS_COURSES", cannot_delete.status_code, "Unexpected response", cannot_delete_payload)

            # 8g: delete non-existent category returns 404
            fake_id = uuid.uuid4()
            missing_delete = await client.delete(
                f"/api/v1/categories/{fake_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            missing_delete_code = missing_delete.json().get("detail", {}).get("code")
            if missing_delete.status_code == 404 and missing_delete_code == "CATEGORY_NOT_FOUND":
                ok("DELETE non-existent category returns CATEGORY_NOT_FOUND", missing_delete.status_code)
            else:
                fail("Missing delete should be CATEGORY_NOT_FOUND", missing_delete.status_code, "Unexpected response", missing_delete.json())

            section("9. AI translation failure")
            failed_name = f"Danh mục AI lỗi {uuid.uuid4().hex[:8]}"
            created_names.add(failed_name)
            category_service_module.translate_category_content = fake_failed_translate_category_content
            failed_translation = await client.post(
                "/api/v1/categories",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "name": failed_name,
                    "description": "Không được lưu khi AI lỗi.",
                    "auto_translate_en": True,
                },
            )
            failed_payload = failed_translation.json()
            failed_code = failed_payload.get("detail", {}).get("code")
            if failed_translation.status_code == 502 and failed_code == "CATEGORY_TRANSLATION_FAILED":
                ok("AI fallback translation is rejected", failed_translation.status_code)
            else:
                fail(
                    "AI fallback should be CATEGORY_TRANSLATION_FAILED",
                    failed_translation.status_code,
                    "Unexpected response",
                    failed_payload,
                )

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(CategoryTranslations.id)
                    .where(CategoryTranslations.lang == "vi")
                    .where(CategoryTranslations.name == failed_name)
                )
                if result.scalar_one_or_none() is None:
                    ok("AI failure rolls back category creation")
                else:
                    fail("AI failure should rollback category", None, "Found persisted failed category")
    finally:
        category_service_module.translate_category_content = original_translate
        cleaned_courses = await cleanup_courses(created_course_ids)
        cleaned = await cleanup_categories_by_names(created_names)
        print(f"\nCleanup deleted courses: {cleaned_courses}")
        print(f"\nCleanup deleted rows: {cleaned}")


async def main() -> None:
    print("\nCategory API Integration Test")
    await run_tests()

    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    print(f"\nSummary: {passed} passed, {failed} failed")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
