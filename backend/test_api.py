#!/usr/bin/env python3
"""
test_api.py — Integration test toàn bộ Auth API
================================================
Chạy: python test_api.py

Yêu cầu:
  - Server đang chạy ở BASE_URL (mặc định localhost:8000)
  - SMS_ENABLED=false (dùng OTP bypass 999999)
  - DB đã migrate

Flow test:
  1. Health check
  2. Send OTP (register)
  3. Verify OTP → otp_token
  4. Register → access_token + refresh_token + session_id
  5. GET /me (authenticated)
  6. GET /auth/sessions (list thiết bị)
  7. Refresh token → token mới
  8. Logout (revoke session)
  9. Verify logout (token cũ không dùng được)
 10. Register user 2 để test login
 11. Send OTP (login)
 12. Login by OTP
 13. Login by Password
 14. Logout All
 15. OAuth endpoints (chỉ test response code, không cần real token)
"""

import asyncio
import json
import sys
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import httpx

# ─── Config ───────────────────────────────────────────────────────────────────

BASE_URL = "http://localhost:8000/api/v1"
OTP_BYPASS = "999999"

# Dùng phone unique mỗi lần chạy để tránh conflict
_RUN_ID = str(int(time.time()))[-6:]
TEST_PHONE = f"+8490{_RUN_ID}"
TEST_EMAIL = f"test_{_RUN_ID}@example.com"
TEST_PASSWORD = "TestPass1"
TEST_NAME = "Test User"

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
        print(f"       Response: {json.dumps(response, ensure_ascii=False, indent=2)[:300]}")
    return r


def section(title: str) -> None:
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ─── Test runner ──────────────────────────────────────────────────────────────

async def run_tests() -> None:
    print(f"\n🚀 Auth API Integration Test")
    print(f"   Base URL : {BASE_URL}")
    print(f"   Phone    : {TEST_PHONE}")
    print(f"   Email    : {TEST_EMAIL}")
    print(f"   Run ID   : {_RUN_ID}\n")

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=15.0) as client:
        # Shared state between tests
        state: dict[str, Any] = {}

        # ── 1. Health Check ───────────────────────────────────────────────────
        section("1. Health Check")
        resp = await client.get("http://localhost:8000/health")
        if resp.status_code == 200:
            ok("GET /health", resp.status_code, resp.json())
        else:
            fail("GET /health", resp.status_code, "Server không phản hồi", resp.json())
            print("\n⛔ Server không chạy. Abort.")
            return

        # ── 2. Send OTP (register) ────────────────────────────────────────────
        section("2. Send OTP — Register Flow")
        resp = await client.post("/auth/send-otp", json={
            "phone": TEST_PHONE,
            "purpose": "register",
        })
        data = resp.json()
        if resp.status_code == 200:
            ok("POST /auth/send-otp (register)", resp.status_code, data)
        else:
            fail("POST /auth/send-otp (register)", resp.status_code, str(data), data)

        # Test cooldown (gửi lại ngay → phải 429)
        resp2 = await client.post("/auth/send-otp", json={
            "phone": TEST_PHONE,
            "purpose": "register",
        })
        if resp2.status_code == 429:
            ok("POST /auth/send-otp cooldown (429)", resp2.status_code)
        else:
            fail("POST /auth/send-otp cooldown expected 429", resp2.status_code, "Cooldown không hoạt động")

        # ── 3. Verify OTP ─────────────────────────────────────────────────────
        section("3. Verify OTP")

        # Sai OTP → 400
        resp = await client.post("/auth/verify-otp", json={
            "phone": TEST_PHONE,
            "otp_code": "000000",
            "purpose": "register",
        })
        if resp.status_code == 400:
            ok("POST /auth/verify-otp (wrong OTP → 400)", resp.status_code)
        else:
            fail("POST /auth/verify-otp wrong OTP", resp.status_code, "Expected 400", resp.json())

        # Đúng OTP (bypass)
        resp = await client.post("/auth/verify-otp", json={
            "phone": TEST_PHONE,
            "otp_code": OTP_BYPASS,
            "purpose": "register",
        })
        data = resp.json()
        if resp.status_code == 200 and "otp_token" in data:
            ok("POST /auth/verify-otp (correct OTP → otp_token)", resp.status_code, data)
            state["otp_token_register"] = data["otp_token"]
        else:
            fail("POST /auth/verify-otp correct OTP", resp.status_code, str(data), data)
            print("\n⛔ Không lấy được otp_token. Abort register flow.")
            return

        # ── 4. Register ───────────────────────────────────────────────────────
        section("4. Register")
        resp = await client.post("/auth/register", json={
            "otp_token": state["otp_token_register"],
            "full_name": TEST_NAME,
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "device_type": "ANDROID",
            "device_name": "Test Device",
            "device_token": "fcm_test_token_123",
        })
        data = resp.json()
        if resp.status_code == 201 and "access_token" in data:
            ok("POST /auth/register", resp.status_code)
            state["access_token"] = data["access_token"]
            state["refresh_token"] = data["refresh_token"]
            state["session_id"] = data.get("session_id")
            print(f"       session_id: {state['session_id']}")
        else:
            fail("POST /auth/register", resp.status_code, str(data), data)
            return

        # Dùng token cũ → 409 (phone đã tồn tại)
        resp2 = await client.post("/auth/register", json={
            "otp_token": state["otp_token_register"],  # token đã dùng
            "full_name": TEST_NAME,
            "device_type": "ANDROID",
        })
        if resp2.status_code in (401, 409):
            ok(f"POST /auth/register duplicate (→ {resp2.status_code})", resp2.status_code)
        else:
            fail("POST /auth/register duplicate", resp2.status_code, "Expected 401 or 409", resp2.json())

        # ── 5. GET /me ────────────────────────────────────────────────────────
        section("5. GET /auth/me")
        auth_headers = {"Authorization": f"Bearer {state['access_token']}"}

        resp = await client.get("/auth/me", headers=auth_headers)
        data = resp.json()
        if resp.status_code == 200 and data.get("phone") == TEST_PHONE:
            ok("GET /auth/me (authenticated)", resp.status_code)
            print(f"       user: {data.get('full_name')} | phone: {data.get('phone')}")
        else:
            fail("GET /auth/me", resp.status_code, str(data), data)

        # Không có token → 401
        resp2 = await client.get("/auth/me")
        if resp2.status_code == 401:
            ok("GET /auth/me (no token → 401)", resp2.status_code)
        else:
            fail("GET /auth/me no token", resp2.status_code, "Expected 401")

        # ── 6. GET /auth/sessions ─────────────────────────────────────────────
        section("6. GET /auth/sessions (Multi-device list)")
        resp = await client.get("/auth/sessions", headers=auth_headers)
        data = resp.json()
        if resp.status_code == 200 and "sessions" in data:
            ok("GET /auth/sessions", resp.status_code)
            print(f"       Active sessions: {data.get('total')}")
            for s in data.get("sessions", []):
                current_marker = " ← current" if s.get("is_current") else ""
                print(f"         [{s['device_type']}] {s.get('device_name')} {current_marker}")
        else:
            fail("GET /auth/sessions", resp.status_code, str(data), data)

        # ── 7. Refresh Token ──────────────────────────────────────────────────
        section("7. Refresh Token (Rotating)")
        resp = await client.post("/auth/refresh", json={
            "refresh_token": state["refresh_token"],
            "device_type": "ANDROID",
        })
        data = resp.json()
        if resp.status_code == 200 and "access_token" in data:
            ok("POST /auth/refresh", resp.status_code)
            old_refresh = state["refresh_token"]
            state["access_token"] = data["access_token"]
            state["refresh_token"] = data["refresh_token"]
            state["session_id"] = data.get("session_id")
            auth_headers = {"Authorization": f"Bearer {state['access_token']}"}

            # Token cũ không dùng được nữa (rotating)
            resp2 = await client.post("/auth/refresh", json={
                "refresh_token": old_refresh,
                "device_type": "ANDROID",
            })
            if resp2.status_code == 401:
                ok("POST /auth/refresh old token (→ 401, rotation OK)", resp2.status_code)
            else:
                fail("POST /auth/refresh old token rotation", resp2.status_code, "Expected 401 — token cũ vẫn dùng được!")
        else:
            fail("POST /auth/refresh", resp.status_code, str(data), data)

        # ── 8. Login by OTP ───────────────────────────────────────────────────
        section("8. Login by OTP (passwordless)")

        # Send OTP login
        resp = await client.post("/auth/send-otp", json={
            "phone": TEST_PHONE,
            "purpose": "login",
        })
        if resp.status_code == 200:
            ok("POST /auth/send-otp (login)", resp.status_code)
        else:
            fail("POST /auth/send-otp login", resp.status_code, str(resp.json()), resp.json())

        # Verify OTP login
        resp = await client.post("/auth/verify-otp", json={
            "phone": TEST_PHONE,
            "otp_code": OTP_BYPASS,
            "purpose": "login",
        })
        data = resp.json()
        if resp.status_code == 200 and "otp_token" in data:
            ok("POST /auth/verify-otp (login)", resp.status_code)
            state["otp_token_login"] = data["otp_token"]
        else:
            fail("POST /auth/verify-otp login", resp.status_code, str(data), data)
            state["otp_token_login"] = None

        if state.get("otp_token_login"):
            resp = await client.post("/auth/login/otp", json={
                "otp_token": state["otp_token_login"],
                "device_type": "IOS",
                "device_name": "iPhone Test",
                "device_token": "apns_test_token_456",
            })
            data = resp.json()
            if resp.status_code == 200 and "access_token" in data:
                ok("POST /auth/login/otp", resp.status_code)
                state["refresh_token_ios"] = data["refresh_token"]
                print(f"       session_id: {data.get('session_id')}")
            else:
                fail("POST /auth/login/otp", resp.status_code, str(data), data)

        # ── 9. Login by Password ──────────────────────────────────────────────
        section("9. Login by Password")

        # Sai password → 401
        resp = await client.post("/auth/login/password", json={
            "email": TEST_EMAIL,
            "password": "WrongPass9",
            "device_type": "WEB",
        })
        if resp.status_code == 401:
            ok("POST /auth/login/password (wrong → 401)", resp.status_code)
        else:
            fail("POST /auth/login/password wrong", resp.status_code, "Expected 401", resp.json())

        # Đúng password → 200
        resp = await client.post("/auth/login/password", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "device_type": "WEB",
            "device_name": "Chrome Test",
        })
        data = resp.json()
        if resp.status_code == 200 and "access_token" in data:
            ok("POST /auth/login/password (correct)", resp.status_code)
            state["refresh_token_web"] = data["refresh_token"]
        else:
            fail("POST /auth/login/password", resp.status_code, str(data), data)

        # ── 10. Sessions list (multi-device) ──────────────────────────────────
        section("10. Sessions — Multi-device verification")
        resp = await client.get("/auth/sessions", headers=auth_headers)
        data = resp.json()
        if resp.status_code == 200:
            total = data.get("total", 0)
            ok(f"GET /auth/sessions (total: {total} active)", resp.status_code)
            for s in data.get("sessions", []):
                current_marker = " ← CURRENT" if s.get("is_current") else ""
                print(f"         [{s['id'][:8]}...] {s['device_type']} | {s.get('device_name')}{current_marker}")

            # Revoke session cụ thể (IOS session nếu có)
            ios_sessions = [s for s in data["sessions"] if s["device_type"] == "IOS" and not s.get("is_current")]
            if ios_sessions:
                target_id = ios_sessions[0]["id"]
                resp2 = await client.delete(f"/auth/sessions/{target_id}", headers=auth_headers)
                if resp2.status_code == 204:
                    ok(f"DELETE /auth/sessions/{target_id[:8]}... (IOS)", resp2.status_code)
                else:
                    fail(f"DELETE /auth/sessions/{target_id[:8]}...", resp2.status_code, resp2.text)

            # Test IDOR protection (revoke session với random UUID)
            fake_id = str(uuid.uuid4())
            resp3 = await client.delete(f"/auth/sessions/{fake_id}", headers=auth_headers)
            if resp3.status_code == 404:
                ok("DELETE /auth/sessions/{fake_id} IDOR → 404", resp3.status_code)
            else:
                fail("IDOR protection", resp3.status_code, f"Expected 404, got {resp3.status_code}")
        else:
            fail("GET /auth/sessions multi-device", resp.status_code, str(data), data)

        # ── 11. Logout ────────────────────────────────────────────────────────
        section("11. Logout")
        resp = await client.post("/auth/logout", json={
            "refresh_token": state["refresh_token"],
            "device_type": "ANDROID",
        })
        if resp.status_code == 204:
            ok("POST /auth/logout (current session)", resp.status_code)
        else:
            fail("POST /auth/logout", resp.status_code, resp.text)

        # Verify: refresh token cũ không dùng được
        resp2 = await client.post("/auth/refresh", json={
            "refresh_token": state["refresh_token"],
            "device_type": "ANDROID",
        })
        if resp2.status_code == 401:
            ok("POST /auth/refresh after logout (→ 401)", resp2.status_code)
        else:
            fail("Refresh after logout", resp2.status_code, "Token vẫn còn hiệu lực sau logout!")

        # ── 12. Logout All ────────────────────────────────────────────────────
        section("12. Logout All Devices")
        # Lấy token mới bằng password login
        resp = await client.post("/auth/login/password", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "device_type": "ANDROID",
        })
        if resp.status_code == 200:
            new_token = resp.json()["access_token"]
            new_headers = {"Authorization": f"Bearer {new_token}"}

            resp2 = await client.post("/auth/logout-all", headers=new_headers)
            if resp2.status_code == 204:
                ok("POST /auth/logout-all", resp2.status_code)
            else:
                fail("POST /auth/logout-all", resp2.status_code, resp2.text)
        else:
            fail("Login before logout-all", resp.status_code, resp.text)

        # ── 13. OAuth endpoints (structure test) ──────────────────────────────
        section("13. OAuth Endpoints (config check)")

        resp = await client.get("/auth/oauth/google/url")
        if resp.status_code in (200, 503):
            status_label = "configured" if resp.status_code == 200 else "not configured (503 expected)"
            ok(f"GET /auth/oauth/google/url ({status_label})", resp.status_code)
        else:
            fail("GET /auth/oauth/google/url", resp.status_code, resp.text)

        resp = await client.get("/auth/oauth/github/url")
        if resp.status_code in (200, 503):
            status_label = "configured" if resp.status_code == 200 else "not configured (503 expected)"
            ok(f"GET /auth/oauth/github/url ({status_label})", resp.status_code)
        else:
            fail("GET /auth/oauth/github/url", resp.status_code, resp.text)

        # POST với token giả → 503 (not configured) hoặc 401 (configured nhưng token sai)
        resp = await client.post("/auth/oauth/google", json={
            "id_token": "fake_token",
            "device_type": "ANDROID",
        })
        if resp.status_code in (401, 503):
            ok(f"POST /auth/oauth/google fake token (→ {resp.status_code})", resp.status_code)
        else:
            fail("POST /auth/oauth/google", resp.status_code, resp.text[:200])

        resp = await client.post("/auth/oauth/github", json={
            "code": "fake_code",
            "device_type": "ANDROID",
        })
        if resp.status_code in (401, 503):
            ok(f"POST /auth/oauth/github fake code (→ {resp.status_code})", resp.status_code)
        else:
            fail("POST /auth/oauth/github", resp.status_code, resp.text[:200])

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
