-- ============================================================
-- MIGRATION: Auth System Fixes & Extensions
-- DB: mobility_app
-- ============================================================

BEGIN;

-- ============================================================
-- 1. FIX users table
-- ============================================================

-- password_hash nên nullable (user OTP-only không có password)
ALTER TABLE users
    ALTER COLUMN password_hash DROP NOT NULL;

-- Thêm fields còn thiếu
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS avatar_url         TEXT,
    ADD COLUMN IF NOT EXISTS device_token       TEXT,
    ADD COLUMN IF NOT EXISTS device_platform    VARCHAR(10),    -- 'ios','android','web'
    ADD COLUMN IF NOT EXISTS preferred_lang     VARCHAR(5)  NOT NULL DEFAULT 'vi',
    ADD COLUMN IF NOT EXISTS preferred_currency VARCHAR(3)  NOT NULL DEFAULT 'VND',
    ADD COLUMN IF NOT EXISTS date_of_birth      DATE,
    ADD COLUMN IF NOT EXISTS gender             VARCHAR(10);    -- 'male','female','other'

-- ============================================================
-- 2. FIX otp_logs table
-- ============================================================

-- user_id phải nullable (pre-register OTP chưa có user)
ALTER TABLE otp_logs
    ALTER COLUMN user_id DROP NOT NULL;

-- otp_code rename → otp_hash (lưu hash, không lưu raw)
ALTER TABLE otp_logs
    RENAME COLUMN otp_code TO otp_hash;

-- Thêm phone để lookup khi chưa có user_id
ALTER TABLE otp_logs
    ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

-- Thêm comment để rõ ràng
COMMENT ON COLUMN otp_logs.otp_hash IS 'SHA-256 hash của OTP code — KHÔNG lưu plain text';

-- ============================================================
-- 3. NEW TABLE: phone_verifications
-- Pre-register OTP — trước khi user tồn tại trong hệ thống
-- ============================================================

CREATE TABLE IF NOT EXISTS phone_verifications (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    phone       VARCHAR(20) NOT NULL,
    otp_hash    TEXT        NOT NULL,       -- sha256(otp_code)
    purpose     VARCHAR(30) NOT NULL,       -- 'register', 'login', 'reset_password'
    attempts    INT         NOT NULL DEFAULT 0,
    is_verified BOOLEAN     NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    expires_at  TIMESTAMPTZ NOT NULL,
    ip_address  INET,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_phone_verif_phone_purpose
    ON phone_verifications(phone, purpose);
CREATE INDEX IF NOT EXISTS idx_phone_verif_expires
    ON phone_verifications(expires_at);

COMMENT ON TABLE phone_verifications IS
    'OTP pre-register: dùng trước khi user được tạo. Sau khi verify → tạo user.';

-- ============================================================
-- 4. NEW TABLE: oauth_accounts
-- Google / Apple Sign-In
-- ============================================================

CREATE TABLE IF NOT EXISTS oauth_accounts (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider        VARCHAR(20) NOT NULL,       -- 'google', 'apple', 'facebook'
    provider_uid    VARCHAR(255) NOT NULL,       -- sub / uid từ provider
    provider_email  VARCHAR(255),               -- email provider trả về
    access_token    TEXT,                       -- short-lived, optional cache
    refresh_token   TEXT,
    token_expires_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(provider, provider_uid)
);

CREATE INDEX IF NOT EXISTS idx_oauth_user_id
    ON oauth_accounts(user_id);

-- ============================================================
-- 5. NEW TABLE: login_attempts
-- Brute force protection & security audit
-- ============================================================

CREATE TABLE IF NOT EXISTS login_attempts (
    id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    identifier     VARCHAR(255) NOT NULL,   -- email hoặc phone (không FK → users)
    success        BOOLEAN     NOT NULL,
    ip_address     INET,
    device_type    VARCHAR(10),
    failure_reason VARCHAR(50),             -- 'wrong_password','account_blocked','not_found'
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_login_attempts_identifier
    ON login_attempts(identifier, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_login_attempts_ip
    ON login_attempts(ip_address, created_at DESC);

COMMENT ON TABLE login_attempts IS
    'Audit log đăng nhập — dùng để detect brute force & suspicious activity';

-- ============================================================
-- 6. FIX user_roles: thêm metadata
-- ============================================================

ALTER TABLE user_roles
    ADD COLUMN IF NOT EXISTS assigned_by UUID REFERENCES users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS expires_at  TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS is_active   BOOLEAN NOT NULL DEFAULT TRUE;

-- ============================================================
-- 7. Update view user_with_roles (drop & recreate)
-- ============================================================

DROP VIEW IF EXISTS user_with_roles;

CREATE VIEW user_with_roles AS
SELECT
    u.id,
    u.email,
    u.phone,
    u.full_name,
    u.status,
    u.is_verified,
    u.avatar_url,
    u.device_platform,
    array_agg(r.name ORDER BY r.name) FILTER (WHERE r.name IS NOT NULL) AS roles,
    u.created_at,
    u.last_login_at
FROM users u
LEFT JOIN user_roles ur ON ur.user_id = u.id AND ur.is_active = TRUE
LEFT JOIN roles r       ON r.id = ur.role_id
GROUP BY u.id;

COMMIT;
