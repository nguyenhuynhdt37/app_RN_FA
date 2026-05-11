# 📱 Auth API — Hướng dẫn tích hợp React Native

> Base URL: `http://YOUR_SERVER:8000/api/v1`
> Tất cả request body đều là **JSON** (`Content-Type: application/json`)
> Authenticated endpoints cần header: `Authorization: Bearer <access_token>`

---

## 📋 Mục lục

1. [Token & Session — Khái niệm](#1-token--session--khái-niệm)
2. [Flow đăng ký (Register)](#2-flow-đăng-ký-register)
3. [Flow đăng nhập bằng OTP](#3-flow-đăng-nhập-bằng-otp-passwordless)
4. [Flow đăng nhập bằng Password](#4-flow-đăng-nhập-bằng-password)
5. [Flow OAuth — Google & GitHub](#5-flow-oauth--google--github)
6. [Refresh Token (Auto-login)](#6-refresh-token-auto-login)
7. [Quản lý thiết bị (Sessions)](#7-quản-lý-thiết-bị-sessions)
8. [Logout](#8-logout)
9. [Lấy thông tin user](#9-lấy-thông-tin-user)
10. [Error Codes Reference](#10-error-codes-reference)
11. [Ví dụ code React Native](#11-ví-dụ-code-react-native)

---

## 1. Token & Session — Khái niệm

Sau khi đăng nhập thành công, server trả về 3 thứ:

| Trường | Ý nghĩa | TTL |
|--------|---------|-----|
| `access_token` | JWT dùng gọi API (Bearer token) | 60 phút |
| `refresh_token` | Token để lấy `access_token` mới | 7 ngày |
| `session_id` | ID của phiên đăng nhập hiện tại | — |

**Lưu trữ khuyến nghị (React Native):**
```
access_token   → memory hoặc MMKV (tốc độ cao)
refresh_token  → MMKV encrypted / Keychain (bảo mật)
session_id     → MMKV (optional, dùng cho session management)
```

**Quy tắc:**
- `access_token` hết hạn → tự động gọi `/auth/refresh` để lấy cặp mới
- `refresh_token` hết hạn hoặc bị revoke → bắt user đăng nhập lại

---

## 2. Flow đăng ký (Register)

> 3 bước: Gửi OTP → Xác thực OTP → Hoàn tất đăng ký

### Bước 1 — Gửi OTP

```
POST /auth/send-otp
```

**Request:**
```json
{
  "phone": "+84901234567",
  "purpose": "register"
}
```

**Response 200 OK:**
```json
{
  "message": "OTP đã gửi đến +84901234567. Hết hạn sau 5 phút.",
  "expires_in": 300
}
```

**Errors:**

| Code | HTTP | Ý nghĩa |
|------|------|---------|
| `OTP_COOLDOWN` | 429 | Gửi lại quá sớm (chờ 60 giây) |
| `VALIDATION_ERROR` | 422 | Số điện thoại không đúng format |

---

### Bước 2 — Xác thực OTP

```
POST /auth/verify-otp
```

**Request:**
```json
{
  "phone": "+84901234567",
  "otp_code": "123456",
  "purpose": "register"
}
```

**Response 200 OK:**
```json
{
  "verified": true,
  "otp_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "phone": "+84901234567",
  "message": "OTP xác thực thành công"
}
```

> `otp_token` có hiệu lực **10 phút**. Lưu tạm để dùng bước 3.

**Errors:**

| Code | HTTP | Ý nghĩa |
|------|------|---------|
| `OTP_INVALID` | 400 | OTP sai (response có thêm `attempts_left`) |
| `OTP_NOT_FOUND` | 400 | OTP hết hạn hoặc chưa gửi |
| `OTP_MAX_ATTEMPTS` | 429 | Thử sai quá 3 lần, cần gửi OTP mới |

---

### Bước 3 — Hoàn tất đăng ký

```
POST /auth/register
```

**Request:**
```json
{
  "otp_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "full_name": "Nguyễn Văn A",
  "email": "user@example.com",
  "password": "SecurePass1",
  "device_type": "ANDROID",
  "device_name": "Samsung Galaxy S24",
  "device_token": "fcm_push_token_from_firebase"
}
```

| Trường | Bắt buộc | Ghi chú |
|--------|---------|---------|
| `otp_token` | ✅ | Từ bước 2 |
| `full_name` | ✅ | 2–120 ký tự |
| `email` | ❌ | Email hợp lệ |
| `password` | ❌ | ≥8 ký tự, có chữ hoa + số |
| `device_type` | ✅ | `"IOS"` hoặc `"ANDROID"` hoặc `"WEB"` |
| `device_name` | ❌ | Tên thiết bị hiển thị |
| `device_token` | ❌ | FCM token (push notification) |

**Response 201 Created:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "refresh_token": "a3f8e2d1c4b5...",
  "token_type": "bearer",
  "expires_in": 3600,
  "session_id": "ab4806e1-476d-492a-942a-c0f491ac2ad9"
}
```

**Errors:**

| Code | HTTP | Ý nghĩa |
|------|------|---------|
| `OTP_TOKEN_INVALID` | 401 | otp_token hết hạn hoặc đã dùng |
| `PHONE_EXISTS` | 409 | Số điện thoại đã được đăng ký |

---

## 3. Flow đăng nhập bằng OTP (Passwordless)

> 3 bước: Gửi OTP → Xác thực OTP → Đăng nhập

**Bước 1 & 2:** Giống như Register, nhưng `purpose` = `"login"`

### Bước 3 — Đăng nhập

```
POST /auth/login/otp
```

**Request:**
```json
{
  "otp_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "device_type": "ANDROID",
  "device_name": "Samsung Galaxy S24",
  "device_token": "fcm_push_token"
}
```

**Response 200 OK:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "refresh_token": "a3f8e2d1c4b5...",
  "token_type": "bearer",
  "expires_in": 3600,
  "session_id": "ef0cb1b0-9766-4fad-989e-46be86f15022"
}
```

**Errors:**

| Code | HTTP | Ý nghĩa |
|------|------|---------|
| `OTP_TOKEN_INVALID` | 401 | otp_token hết hạn |
| `USER_NOT_FOUND` | 404 | Phone chưa đăng ký |
| `ACCOUNT_BLOCKED` | 403 | Tài khoản bị khóa |

---

## 4. Flow đăng nhập bằng Password

```
POST /auth/login/password
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass1",
  "device_type": "ANDROID",
  "device_name": "Samsung Galaxy S24",
  "device_token": "fcm_push_token"
}
```

**Response 200 OK:** (giống Login OTP)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "refresh_token": "a3f8e2d1c4b5...",
  "token_type": "bearer",
  "expires_in": 3600,
  "session_id": "2eea31f5-..."
}
```

**Errors:**

| Code | HTTP | Ý nghĩa |
|------|------|---------|
| `INVALID_CREDENTIALS` | 401 | Email hoặc password sai |
| `NO_PASSWORD` | 400 | Tài khoản đăng ký bằng OTP/OAuth, chưa có password |

---

## 5. Flow OAuth — Google & GitHub

### 5a. Mobile Flow (Khuyến nghị cho React Native)

App dùng SDK của Google/GitHub để lấy token, sau đó gửi lên backend.

#### Google (dùng `@react-native-google-signin/google-signin`)

```
POST /auth/oauth/google
```

**Request:**
```json
{
  "id_token": "google_id_token_from_sdk",
  "device_type": "ANDROID",
  "device_name": "Samsung Galaxy S24",
  "device_token": "fcm_push_token"
}
```

**Response 200 OK:** (giống Login)

**Errors:**

| Code | HTTP | Ý nghĩa |
|------|------|---------|
| `GOOGLE_NOT_CONFIGURED` | 503 | Server chưa cấu hình Google OAuth |
| `GOOGLE_TOKEN_INVALID` | 401 | id_token không hợp lệ hoặc hết hạn |

#### GitHub (dùng `expo-auth-session`)

```
POST /auth/oauth/github
```

**Request:**
```json
{
  "code": "github_authorization_code",
  "device_type": "ANDROID",
  "device_name": "Samsung Galaxy S24",
  "device_token": "fcm_push_token"
}
```

**Response 200 OK:** (giống Login)

---

### 5b. Web Redirect Flow

```
GET /auth/oauth/google/url  → trả về URL redirect đến Google
GET /auth/oauth/github/url  → trả về URL redirect đến GitHub
```

**Response:**
```json
{
  "url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "provider": "google"
}
```

Sau khi user đăng nhập, provider redirect về:
```
GET /auth/oauth/callback?provider=google&code=xxx&state=yyy
```

---

## 6. Refresh Token (Auto-login)

> Gọi khi nhận được lỗi `401 UNAUTHORIZED` từ bất kỳ API nào.

```
POST /auth/refresh
```

**Request:**
```json
{
  "refresh_token": "a3f8e2d1c4b5...",
  "device_type": "ANDROID"
}
```

**Response 200 OK:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "refresh_token": "NEW_REFRESH_TOKEN_HERE",
  "token_type": "bearer",
  "expires_in": 3600,
  "session_id": "new-session-id"
}
```

> **Rotating token**: `refresh_token` CŨ bị vô hiệu ngay sau khi refresh. Luôn lưu `refresh_token` mới.

**Errors:**

| Code | HTTP | Ý nghĩa |
|------|------|---------|
| `REFRESH_TOKEN_INVALID` | 401 | Token hết hạn, bị revoke → bắt user đăng nhập lại |

---

## 7. Quản lý thiết bị (Sessions)

### Xem danh sách thiết bị đang đăng nhập

```
GET /auth/sessions
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "sessions": [
    {
      "id": "ab4806e1-476d-492a-942a-c0f491ac2ad9",
      "device_type": "ANDROID",
      "device_name": "Samsung Galaxy S24",
      "ip_address": "192.168.1.1",
      "user_agent": "okhttp/4.12.0",
      "last_used_at": "2026-05-08T20:30:00Z",
      "created_at": "2026-05-08T14:00:00Z",
      "is_current": true
    },
    {
      "id": "ef0cb1b0-9766-4fad-989e-46be86f15022",
      "device_type": "IOS",
      "device_name": "iPhone 15 Pro",
      "ip_address": "192.168.1.2",
      "user_agent": null,
      "last_used_at": "2026-05-08T18:00:00Z",
      "created_at": "2026-05-07T10:00:00Z",
      "is_current": false
    }
  ],
  "total": 2
}
```

> `is_current: true` = thiết bị đang gọi request này.

---

### Đăng xuất 1 thiết bị cụ thể

```
DELETE /auth/sessions/{session_id}
Authorization: Bearer <access_token>
```

**Response 204 No Content** (thành công, không có body)

**Errors:**

| Code | HTTP | Ý nghĩa |
|------|------|---------|
| `SESSION_NOT_FOUND` | 404 | Session không tồn tại hoặc không thuộc về bạn |

---

## 8. Logout

### Đăng xuất thiết bị hiện tại

```
POST /auth/logout
```

**Request:**
```json
{
  "refresh_token": "a3f8e2d1c4b5...",
  "device_type": "ANDROID"
}
```

**Response 204 No Content**

---

### Đăng xuất tất cả thiết bị

```
POST /auth/logout-all
Authorization: Bearer <access_token>
```

**Request:** (không cần body)

**Response 204 No Content**

---

## 9. Lấy thông tin user

```
GET /auth/me
Authorization: Bearer <access_token>
```

**Response 200 OK:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "phone": "+84901234567",
  "email": "user@example.com",
  "full_name": "Nguyễn Văn A",
  "avatar_url": null,
  "status": "ACTIVE",
  "is_verified": true,
  "roles": ["customer"],
  "created_at": "2026-05-08T14:00:00Z",
  "last_login_at": "2026-05-08T20:00:00Z"
}
```

---

## 10. Error Codes Reference

### Format lỗi chung

```json
{
  "status_code": 401,
  "code": "UNAUTHORIZED",
  "detail": "Authorization header bị thiếu."
}
```

### Danh sách error codes

| Code | HTTP | Khi nào |
|------|------|---------|
| `UNAUTHORIZED` | 401 | Không có hoặc sai Bearer token |
| `FORBIDDEN` | 403 | Tài khoản bị khóa/chưa active |
| `VALIDATION_ERROR` | 422 | Request body không đúng format |
| `OTP_COOLDOWN` | 429 | Gửi OTP quá nhanh (60s cooldown) |
| `OTP_INVALID` | 400 | OTP sai |
| `OTP_NOT_FOUND` | 400 | OTP hết hạn |
| `OTP_MAX_ATTEMPTS` | 429 | Sai OTP quá 3 lần |
| `OTP_TOKEN_INVALID` | 401 | otp_token hết hạn hoặc sai purpose |
| `PHONE_EXISTS` | 409 | Số điện thoại đã đăng ký |
| `USER_NOT_FOUND` | 404 | User không tồn tại |
| `INVALID_CREDENTIALS` | 401 | Email/password sai |
| `NO_PASSWORD` | 400 | Tài khoản chưa có mật khẩu |
| `ACCOUNT_BLOCKED` | 403 | Tài khoản bị khóa |
| `ACCOUNT_PENDING` | 403 | Tài khoản chưa kích hoạt |
| `REFRESH_TOKEN_INVALID` | 401 | Refresh token hết hạn/đã dùng |
| `SESSION_NOT_FOUND` | 404 | Session không tồn tại |
| `GOOGLE_TOKEN_INVALID` | 401 | Google id_token không hợp lệ |
| `GOOGLE_NOT_CONFIGURED` | 503 | Server chưa cài Google OAuth |
| `GITHUB_NOT_CONFIGURED` | 503 | Server chưa cài GitHub OAuth |

---

## 11. Ví dụ code React Native

### Setup API client với auto-refresh

```typescript
// lib/apiClient.ts
import axios, { AxiosInstance } from 'axios';
import { storage } from './storage'; // MMKV

const BASE_URL = 'http://YOUR_SERVER:8000/api/v1';

export const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

// Gắn access_token vào mỗi request
api.interceptors.request.use((config) => {
  const token = storage.getString('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-refresh khi nhận 401
let isRefreshing = false;
let failedQueue: any[] = [];

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;

    if (error.response?.status === 401 && !original._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          original.headers.Authorization = `Bearer ${token}`;
          return api(original);
        });
      }

      original._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = storage.getString('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');

        const { data } = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
          device_type: 'ANDROID',
        });

        storage.set('access_token', data.access_token);
        storage.set('refresh_token', data.refresh_token);
        storage.set('session_id', data.session_id);

        failedQueue.forEach((p) => p.resolve(data.access_token));
        failedQueue = [];

        original.headers.Authorization = `Bearer ${data.access_token}`;
        return api(original);
      } catch (refreshError) {
        failedQueue.forEach((p) => p.reject(refreshError));
        failedQueue = [];
        storage.clearAll();
        // TODO: navigate về màn Login
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
```

---

### Hook đăng ký (Register flow)

```typescript
// hooks/useRegister.ts
import { useState } from 'react';
import { api } from '../lib/apiClient';
import { storage } from '../lib/storage';

export function useRegister() {
  const [loading, setLoading] = useState(false);

  const sendOtp = async (phone: string) => {
    setLoading(true);
    try {
      await api.post('/auth/send-otp', { phone, purpose: 'register' });
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async (phone: string, otpCode: string): Promise<string> => {
    setLoading(true);
    try {
      const { data } = await api.post('/auth/verify-otp', {
        phone,
        otp_code: otpCode,
        purpose: 'register',
      });
      return data.otp_token;
    } finally {
      setLoading(false);
    }
  };

  const register = async (params: {
    otpToken: string;
    fullName: string;
    email?: string;
    password?: string;
    deviceToken?: string;
  }) => {
    setLoading(true);
    try {
      const { data } = await api.post('/auth/register', {
        otp_token: params.otpToken,
        full_name: params.fullName,
        email: params.email,
        password: params.password,
        device_type: 'ANDROID',
        device_name: 'My Device',
        device_token: params.deviceToken,
      });

      storage.set('access_token', data.access_token);
      storage.set('refresh_token', data.refresh_token);
      storage.set('session_id', data.session_id);

      return data;
    } finally {
      setLoading(false);
    }
  };

  return { sendOtp, verifyOtp, register, loading };
}
```

---

### Hook đăng nhập Google (Mobile)

```typescript
// hooks/useGoogleLogin.ts
import { GoogleSignin } from '@react-native-google-signin/google-signin';
import { api } from '../lib/apiClient';
import { storage } from '../lib/storage';

GoogleSignin.configure({
  webClientId: 'YOUR_GOOGLE_WEB_CLIENT_ID',
});

export function useGoogleLogin() {
  const loginWithGoogle = async (deviceToken?: string) => {
    await GoogleSignin.hasPlayServices();
    const { idToken } = await GoogleSignin.signIn();

    const { data } = await api.post('/auth/oauth/google', {
      id_token: idToken,
      device_type: 'ANDROID',
      device_name: 'My Device',
      device_token: deviceToken,
    });

    storage.set('access_token', data.access_token);
    storage.set('refresh_token', data.refresh_token);
    storage.set('session_id', data.session_id);

    return data;
  };

  return { loginWithGoogle };
}
```

---

### Hook quản lý thiết bị

```typescript
// hooks/useSessions.ts
import { useState, useEffect } from 'react';
import { api } from '../lib/apiClient';

export function useSessions() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/auth/sessions');
      setSessions(data.sessions);
    } finally {
      setLoading(false);
    }
  };

  const revokeSession = async (sessionId: string) => {
    await api.delete(`/auth/sessions/${sessionId}`);
    await fetchSessions();
  };

  useEffect(() => { fetchSessions(); }, []);

  return { sessions, loading, revokeSession, refresh: fetchSessions };
}
```

---

### Xử lý lỗi API (helper)

```typescript
// lib/apiError.ts
export function getApiError(error: any): string {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string') return detail;

  const code = error?.response?.data?.code;
  const messages: Record<string, string> = {
    OTP_INVALID: 'Mã OTP không đúng',
    OTP_NOT_FOUND: 'Mã OTP đã hết hạn, vui lòng gửi lại',
    OTP_MAX_ATTEMPTS: 'Đã thử quá 3 lần, vui lòng gửi OTP mới',
    OTP_COOLDOWN: 'Vui lòng chờ 60 giây trước khi gửi lại',
    PHONE_EXISTS: 'Số điện thoại đã được đăng ký',
    INVALID_CREDENTIALS: 'Email hoặc mật khẩu không đúng',
    ACCOUNT_BLOCKED: 'Tài khoản đã bị khóa',
    REFRESH_TOKEN_INVALID: 'Phiên đăng nhập hết hạn',
  };

  return messages[code] || 'Có lỗi xảy ra, vui lòng thử lại';
}
```

---

## Quick Reference

```
REGISTER:   send-otp → verify-otp → register
LOGIN OTP:  send-otp → verify-otp → login/otp
LOGIN PASS: login/password
GOOGLE:     [Google SDK] id_token → oauth/google
GITHUB:     [GitHub OAuth] code → oauth/github
REFRESH:    refresh  (tự động, dùng interceptor)
LOGOUT:     logout (1 thiết bị) | logout-all (tất cả)
SESSIONS:   GET /auth/sessions | DELETE /auth/sessions/{id}
PROFILE:    GET /auth/me
```
