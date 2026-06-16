#!/usr/bin/env python3
"""
test_course_api.py — Test Course Admin API
=========================================
Chạy: python test_course_api.py

Yêu cầu:
  - Server đang chạy ở localhost:8000
  - Database đã migrate
  - Có tài khoản admin (hoặc chạy test_auth.py trước)
"""

import asyncio
import json
import sys
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

# ─── Config ───────────────────────────────────────────────────────────────────

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "Huynh@2004"

# ─── Result tracker ───────────────────────────────────────────────────────────

@dataclass
class TestResult:
    name: str
    passed: bool
    status_code: int | None = None
    detail: str = ""
    response: dict = field(default_factory=dict)

results: list[TestResult] = []


def ok(name: str, status_code: int, response: dict = {}) -> TestResult:
    r = TestResult(name=name, passed=True, status_code=status_code, response=response)
    results.append(r)
    print(f"  ✅  {name} [{status_code}]")
    return r


def fail(name: str, status_code: int | None, detail: str, response: dict = {}) -> TestResult:
    r = TestResult(name=name, passed=False, status_code=status_code, detail=detail, response=response)
    results.append(r)
    print(f"  ❌  {name} [{status_code}] → {detail}")
    if response:
        print(f"       Response: {json.dumps(response, ensure_ascii=False, indent=2)[:500]}")
    return r


def section(title: str) -> None:
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ─── Admin Login ───────────────────────────────────────────────────────────────

async def admin_login(client: httpx.AsyncClient) -> str:
    """Login as admin and return access_token."""
    resp = await client.post("/auth/login/password", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "device_type": "WEB",
        "device_name": "Test Script",
    })
    if resp.status_code == 200:
        return resp.json()["access_token"]
    return ""


# ─── Test runner ──────────────────────────────────────────────────────────────

async def run_tests() -> None:
    print(f"\n🚀 Course Admin API Test")
    print(f"   Base URL : {BASE_URL}\n")

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        state: dict[str, Any] = {}

        # ── 1. Health Check ───────────────────────────────────────────────────
        section("1. Health Check")
        resp = await client.get("http://localhost:8000/health")
        if resp.status_code == 200:
            ok("GET /health", resp.status_code, resp.json())
        else:
            fail("GET /health", resp.status_code, "Server không phản hồi")
            print("\n⛔ Server không chạy. Abort.")
            return

        # ── 2. Admin Login ───────────────────────────────────────────────────
        section("2. Admin Login")
        resp = await client.post("/auth/login/password", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "device_type": "WEB",
        })
        data = resp.json()
        if resp.status_code == 200 and "access_token" in data:
            ok("POST /auth/login/password (admin)", resp.status_code)
            state["access_token"] = data["access_token"]
            state["headers"] = {"Authorization": f"Bearer {data['access_token']}"}
        else:
            fail("POST /auth/login/password (admin)", resp.status_code, str(data), data)
            print("\n⛔ Không login được admin. Abort.")
            return

        # ── 3. List Categories ──────────────────────────────────────────────
        section("3. Categories API")
        resp = await client.get("/admin/categories/")
        if resp.status_code == 200:
            data = resp.json()
            ok("GET /admin/categories/", resp.status_code)
            print(f"       Total categories: {data.get('total', 0)}")
            state["categories"] = data.get("categories", [])
        else:
            fail("GET /admin/categories/", resp.status_code, resp.text)
            state["categories"] = []

        # ── 4. Search Categories ────────────────────────────────────────────
        section("4. Search Categories")
        resp = await client.get("/admin/categories/search/", params={"q": "ielts"})
        if resp.status_code == 200:
            ok("GET /admin/categories/search?q=ielts", resp.status_code)
            print(f"       Found: {len(resp.json().get('categories', []))} categories")
        else:
            fail("GET /admin/categories/search/", resp.status_code, resp.text)

        # ── 5. Preview AI Analysis ───────────────────────────────────────────
        section("5. AI Course Analysis (Preview)")
        
        test_title = "IELTS Writing Band 7+ Complete Course"
        test_desc = """
        Khóa học luyện viết IELTS từ cơ bản đến nâng cao, giúp học viên đạt band 7+ trong kỳ thi IELTS.
        
        Nội dung bao gồm:
        - Cấu trúc bài viết IELTS Writing Task 1 và Task 2
        - Từ vựng học thuật chuyên ngành
        - Grammar nâng cao cho writing
        - Luyện tập với đề thi thật
        - Chữa bài và feedback chi tiết
        
        Khóa học phù hợp với người đã có nền tảng tiếng Anh cơ bản, muốn cải thiện kỹ năng viết.
        """
        
        resp = await client.post("/admin/courses/preview-analysis", params={
            "title": test_title,
            "description": test_desc,
        })
        if resp.status_code == 200:
            data = resp.json()
            ok("POST /admin/courses/preview-analysis", resp.status_code)
            analysis = data.get("data", {})
            
            # Show categories
            cats = analysis.get("categories", {})
            print(f"       Existing categories: {len(cats.get('existing', []))}")
            print(f"       New categories: {len(cats.get('new', []))}")
            if cats.get("new"):
                for c in cats["new"]:
                    print(f"         + {c['name']} (will be created)")
            
            # Show translations
            trans = analysis.get("translations", {})
            print(f"       Languages: {list(trans.keys())}")
            if "vi" in trans:
                print(f"       VI title: {trans['vi'].get('title', '')[:50]}...")
            if "en" in trans:
                print(f"       EN title: {trans['en'].get('title', '')[:50]}...")
            
            # Show suggestions
            sugg = analysis.get("suggestions", {})
            print(f"       Level: {sugg.get('level')}")
            print(f"       Tags: {sugg.get('tags', [])[:5]}")
            print(f"       Confidence: {analysis.get('confidence_score', 0):.2f}")
            
            state["analysis"] = analysis
        else:
            fail("POST /admin/courses/preview-analysis", resp.status_code, resp.text)
            if resp.status_code == 401:
                print("\n⛔ Unauthorized. Check admin credentials.")
            state["analysis"] = None

        # ── 6. Create Course with Analysis ───────────────────────────────────
        section("6. Create Course with AI Analysis")
        
        if state.get("analysis"):
            # Đã có analysis, gọi create
            course_title = state["analysis"].get("translations", {}).get("vi", {}).get("title", "Test Course")
            course_desc = test_desc
            
            resp = await client.post("/admin/courses/create-with-analysis", 
                headers=state["headers"],
                json={
                    "title": course_title,
                    "description": course_desc,
                    "base_price": 599000,
                    "is_published": True,
                }
            )
            if resp.status_code == 201:
                data = resp.json()
                ok("POST /admin/courses/create-with-analysis", resp.status_code)
                course = data.get("data", {})
                state["course_id"] = course.get("id")
                print(f"       Course ID: {course.get('id')}")
                print(f"       Title: {course.get('translations', {}).get('vi', {}).get('title', '')}")
                print(f"       Price: {course.get('base_price')} VND ({course.get('price_coin')} coins)")
                
                # Check categories
                cat_ids = course.get("category_ids", [])
                print(f"       Categories: {len(cat_ids)}")
            else:
                fail("POST /admin/courses/create-with-analysis", resp.status_code, resp.text)
                print(f"       Response: {resp.text[:300]}")
        else:
            print("       ⏭️  Skipped (no analysis data)")

        # ── 7. List Courses ─────────────────────────────────────────────────
        section("7. List Courses")
        resp = await client.get("/admin/courses/", headers=state["headers"])
        if resp.status_code == 200:
            data = resp.json()
            ok("GET /admin/courses/", resp.status_code)
            print(f"       Total courses: {data.get('total', 0)}")
            print(f"       Page: {data.get('page')}/{data.get('total_pages')}")
        else:
            fail("GET /admin/courses/", resp.status_code, resp.text)

        # ── 8. Get Course Stats ─────────────────────────────────────────────
        section("8. Course Statistics")
        resp = await client.get("/admin/courses/stats", headers=state["headers"])
        if resp.status_code == 200:
            data = resp.json()
            ok("GET /admin/courses/stats", resp.status_code)
            print(f"       Total courses: {data.get('total_courses')}")
            print(f"       Total enrolls: {data.get('total_enrolls')}")
            print(f"       Total revenue: {data.get('total_revenue'):,} VND")
        else:
            fail("GET /admin/courses/stats", resp.status_code, resp.text)

        # ── 9. Get Course Detail ─────────────────────────────────────────────
        section("9. Get Course Detail")
        if state.get("course_id"):
            resp = await client.get(f"/admin/courses/{state['course_id']}", headers=state["headers"])
            if resp.status_code == 200:
                ok("GET /admin/courses/{id}", resp.status_code)
                course = resp.json()
                print(f"       Title: {course.get('translations', {}).get('vi', {}).get('title', '')}")
                print(f"       Level: {course.get('level')}")
                print(f"       Tags: {course.get('tags', [])[:3]}")
            else:
                fail("GET /admin/courses/{id}", resp.status_code, resp.text)
        else:
            print("       ⏭️  Skipped (no course_id)")

        # ── 10. Coin Balance ─────────────────────────────────────────────────
        section("10. Coin API (User)")
        resp = await client.get("/coin/balance", headers=state["headers"])
        if resp.status_code == 200:
            ok("GET /coin/balance", resp.status_code)
            print(f"       Balance: {resp.json().get('balance')} coins")
        else:
            print(f"       ⏭️  GET /coin/balance: {resp.status_code}")

        # ── 11. Coin Packages ────────────────────────────────────────────────
        section("11. Coin Packages")
        resp = await client.get("/coin/packages")
        if resp.status_code == 200:
            ok("GET /coin/packages", resp.status_code)
            packages = resp.json()
            for pkg in packages:
                print(f"       {pkg['name']}: {pkg['coin_amount']} coins = {pkg['price_vnd']:,} VND")
        else:
            print(f"       ⏭️  GET /coin/packages: {resp.status_code}")

        # ── 12. Coin Stats (Admin) ───────────────────────────────────────────
        section("12. Coin Statistics (Admin)")
        resp = await client.get("/admin/coin/stats", headers=state["headers"])
        if resp.status_code == 200:
            ok("GET /admin/coin/stats", resp.status_code)
            stats = resp.json()
            print(f"       Total purchased: {stats.get('total_coin_purchased')} coins")
            print(f"       Total spent: {stats.get('total_coin_spent')} coins")
            print(f"       Active users: {stats.get('total_active_users')}")
        else:
            print(f"       ⏭️  GET /admin/coin/stats: {resp.status_code}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    total = len(results)
    print(f"  RESULTS: {passed}/{total} passed | {failed} failed")
    print(f"{'='*60}")

    if failed:
        print(f"\n❌ Failed tests:")
        for r in results:
            if not r.passed:
                print(f"   • {r.name} [{r.status_code}]: {r.detail}")
        sys.exit(1)
    else:
        print(f"\n✅ All {total} tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(run_tests())
