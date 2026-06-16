-- ============================================================================
-- NeuralEarn Database Schema v2
-- Improved: Multilingual, Normalized, Production-ready
-- Generated: 2026-05-12
-- ============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- ENUMS
-- ============================================================================
CREATE TYPE user_status AS ENUM ('PENDING', 'ACTIVE', 'BLOCKED');
CREATE TYPE device_type AS ENUM ('WEB', 'IOS', 'ANDROID');
CREATE TYPE otp_type AS ENUM ('REGISTER', 'LOGIN', 'RESET_PASSWORD');
CREATE TYPE course_level AS ENUM ('BEGINNER', 'INTERMEDIATE', 'ADVANCED');
CREATE TYPE coin_transaction_type AS ENUM ('PURCHASE', 'COURSE_PURCHASE', 'REFUND', 'BONUS', 'EARN');

-- ============================================================================
-- TABLES: Auth & Users
-- ============================================================================

-- Roles
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    status user_status NOT NULL DEFAULT 'PENDING',
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    preferred_lang VARCHAR(5) NOT NULL DEFAULT 'vi',
    preferred_currency VARCHAR(3) NOT NULL DEFAULT 'VND',
    
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    username VARCHAR(50) UNIQUE,
    password_hash TEXT,
    full_name VARCHAR(120),
    bio TEXT,
    
    is_profile_completed BOOLEAN NOT NULL DEFAULT FALSE,
    learning_goals TEXT,
    interests JSONB DEFAULT '[]',
    daily_goal_minutes INTEGER NOT NULL DEFAULT 30,
    preferred_learning_style VARCHAR(20),
    social_links JSONB DEFAULT '{}',
    
    avatar_url TEXT,
    cover_url TEXT,
    date_of_birth DATE,
    gender VARCHAR(10),
    instructor_metadata JSONB DEFAULT '{}',
    
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT users_email_or_phone_required CHECK (email IS NOT NULL OR phone IS NOT NULL)
);

-- User Roles (junction)
CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    assigned_by UUID REFERENCES users(id) ON DELETE SET NULL,
    expires_at TIMESTAMPTZ,
    PRIMARY KEY (user_id, role_id)
);

-- User Specializations
CREATE TABLE specializations_reference (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    icon_url TEXT,
    position INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Specialization Translations (NEW: multilingual)
CREATE TABLE specialization_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    specialization_id UUID NOT NULL REFERENCES specializations_reference(id) ON DELETE CASCADE,
    lang VARCHAR(5) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(specialization_id, lang)
);

-- Skills Reference
CREATE TABLE skills_reference (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    specialization_id UUID NOT NULL REFERENCES specializations_reference(id) ON DELETE CASCADE,
    icon_url TEXT,
    position INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Skill Translations (NEW: multilingual)
CREATE TABLE skill_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_id UUID NOT NULL REFERENCES skills_reference(id) ON DELETE CASCADE,
    lang VARCHAR(5) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(skill_id, lang)
);

-- User Specializations (user profile)
CREATE TABLE user_specializations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    specialization_id UUID NOT NULL REFERENCES specializations_reference(id) ON DELETE CASCADE,
    level VARCHAR(50) NOT NULL,
    skills JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Interests Reference (UPDATED: multilingual)
CREATE TABLE interests_reference (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    icon_url TEXT,
    position INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Interest Translations (NEW: multilingual)
CREATE TABLE interest_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interest_id UUID NOT NULL REFERENCES interests_reference(id) ON DELETE CASCADE,
    lang VARCHAR(5) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(interest_id, lang)
);

-- User Interests (junction)
CREATE TABLE user_interests (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    interest_id UUID NOT NULL REFERENCES interests_reference(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, interest_id)
);

-- ============================================================================
-- TABLES: OAuth & Sessions
-- ============================================================================

-- OAuth Accounts
CREATE TABLE oauth_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(20) NOT NULL,
    provider_uid VARCHAR(255) NOT NULL,
    provider_email VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(provider, provider_uid)
);

-- Sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash TEXT NOT NULL UNIQUE,
    device_type device_type NOT NULL,
    device_name VARCHAR(255),
    device_token TEXT,
    push_provider VARCHAR(10),
    user_agent TEXT,
    ip_address INET,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Login Attempts (audit)
CREATE TABLE login_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identifier VARCHAR(255) NOT NULL,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(50),
    device_type VARCHAR(10),
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- OTP Logs
CREATE TABLE otp_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type otp_type NOT NULL,
    otp_hash VARCHAR(10) NOT NULL,
    phone VARCHAR(20),
    attempts INTEGER NOT NULL DEFAULT 0,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verified_at TIMESTAMPTZ
);

-- Phone Verifications
CREATE TABLE phone_verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(20) NOT NULL,
    otp_hash TEXT NOT NULL,
    purpose VARCHAR(30) NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    ip_address INET,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verified_at TIMESTAMPTZ
);

-- ============================================================================
-- TABLES: Course Categories (UPDATED: normalized)
-- ============================================================================

-- Course Categories
CREATE TABLE course_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    icon_url TEXT,
    color VARCHAR(7) DEFAULT '#10b981',
    position INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_ai_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Category Translations
CREATE TABLE category_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID NOT NULL REFERENCES course_categories(id) ON DELETE CASCADE,
    lang VARCHAR(5) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(category_id, lang)
);

-- ============================================================================
-- TABLES: Courses
-- ============================================================================

-- Courses
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    default_slug VARCHAR(255),
    thumbnail_url TEXT,
    preview_video_type INTEGER DEFAULT 1,
    level course_level NOT NULL DEFAULT 'BEGINNER',
    estimated_duration INTEGER,
    difficulty_score INTEGER DEFAULT 1,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    base_price INTEGER DEFAULT 0,
    currency VARCHAR(3) NOT NULL DEFAULT 'VND',
    
    -- Analytics
    views INTEGER DEFAULT 0,
    total_enrolls INTEGER DEFAULT 0,
    revenue INTEGER DEFAULT 0,
    rating_avg FLOAT DEFAULT 0,
    lessons_count INTEGER DEFAULT 0,
    
    -- Approval workflow
    approval_status VARCHAR(20),
    approval_note TEXT,
    
    -- Ownership & Audit
    instructor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(default_slug)
);

-- Course Categories (junction - NEW: replaces category_ids ARRAY)
CREATE TABLE course_categories_junction (
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES course_categories(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (course_id, category_id)
);

-- Course Tags (NEW: replaces tags ARRAY)
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tag_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    lang VARCHAR(5) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tag_id, lang)
);

CREATE TABLE course_tags (
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (course_id, tag_id)
);

-- Course Translations
CREATE TABLE course_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    lang VARCHAR(5) NOT NULL,
    title VARCHAR(255) NOT NULL DEFAULT '',
    subtitle TEXT,
    description TEXT,
    slug VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(course_id, lang),
    UNIQUE(lang, slug)
);

-- Course Learning Outcomes (UPDATED: separate table for multilingual)
CREATE TABLE course_learning_outcomes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE course_learning_outcome_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    outcome_id UUID NOT NULL REFERENCES course_learning_outcomes(id) ON DELETE CASCADE,
    lang VARCHAR(5) NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(outcome_id, lang)
);

-- Course Prerequisites (UPDATED: separate table for multilingual)
CREATE TABLE course_prerequisites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE course_prerequisite_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prerequisite_id UUID NOT NULL REFERENCES course_prerequisites(id) ON DELETE CASCADE,
    lang VARCHAR(5) NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(prerequisite_id, lang)
);

-- ============================================================================
-- TABLES: Learning Content (UPDATED: multilingual)
-- ============================================================================

-- Sections (FIXED: no title - moved to translations)
CREATE TABLE sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Section Translations
CREATE TABLE section_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_id UUID NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    lang VARCHAR(5) NOT NULL,
    title VARCHAR(255) NOT NULL DEFAULT '',
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(section_id, lang)
);

-- Learning Units (FIXED: no title - moved to translations)
CREATE TABLE learning_units (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_id UUID NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    position INTEGER NOT NULL DEFAULT 0,
    is_free BOOLEAN NOT NULL DEFAULT FALSE,
    base_exp INTEGER NOT NULL DEFAULT 50,
    required_unit_id UUID REFERENCES learning_units(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Learning Unit Translations (NEW)
CREATE TABLE learning_unit_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unit_id UUID NOT NULL REFERENCES learning_units(id) ON DELETE CASCADE,
    lang VARCHAR(5) NOT NULL,
    title VARCHAR(255) NOT NULL DEFAULT '',
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(unit_id, lang)
);

-- Learning Blocks
CREATE TABLE learning_blocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unit_id UUID NOT NULL REFERENCES learning_units(id) ON DELETE CASCADE,
    block_type VARCHAR(50) NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    content JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- TABLES: Course Progress
-- ============================================================================

CREATE TABLE course_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    unit_id UUID NOT NULL REFERENCES learning_units(id) ON DELETE CASCADE,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    current_state JSONB NOT NULL DEFAULT '{}',
    total_exp_gained INTEGER NOT NULL DEFAULT 0,
    completed_at TIMESTAMPTZ,
    last_accessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, unit_id)
);

-- ============================================================================
-- TABLES: Coin System
-- ============================================================================

CREATE TABLE user_coins (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    balance INTEGER NOT NULL DEFAULT 0,
    total_purchased INTEGER NOT NULL DEFAULT 0,
    total_spent INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE coin_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type coin_transaction_type NOT NULL,
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    extra_data JSONB DEFAULT '{}',
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- TABLES: Alembic
-- ============================================================================

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
);

-- ============================================================================
-- INDEXES (Performance Optimization)
-- ============================================================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Sessions
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_sessions_active ON sessions(user_id) WHERE revoked_at IS NULL;

-- Login Attempts
CREATE INDEX idx_login_attempts_identifier ON login_attempts(identifier, created_at);
CREATE INDEX idx_login_attempts_ip ON login_attempts(ip_address, created_at);

-- OTP & Phone
CREATE INDEX idx_otp_logs_user_id ON otp_logs(user_id);
CREATE INDEX idx_otp_logs_expires ON otp_logs(expires_at);
CREATE INDEX idx_phone_verif_expires ON phone_verifications(expires_at);
CREATE INDEX idx_phone_verif_phone_purpose ON phone_verifications(phone, purpose);

-- User Roles
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);

-- OAuth
CREATE INDEX idx_oauth_user_id ON oauth_accounts(user_id);

-- User Specializations
CREATE INDEX idx_user_specializations_user_id ON user_specializations(user_id);
CREATE INDEX idx_user_specializations_spec_id ON user_specializations(specialization_id);

-- Course Categories
CREATE INDEX idx_category_translations_lang ON category_translations(lang);
CREATE INDEX idx_category_translations_category_lang ON category_translations(category_id, lang);

-- Courses
CREATE INDEX idx_courses_instructor ON courses(instructor_id);
CREATE INDEX idx_courses_level ON courses(level);
CREATE INDEX idx_courses_published ON courses(is_published) WHERE is_published = TRUE;
CREATE INDEX idx_courses_created_at ON courses(created_at);
CREATE INDEX idx_course_categories_junction_category ON course_categories_junction(category_id);
CREATE INDEX idx_course_categories_junction_course ON course_categories_junction(course_id);

-- Course Translations (multilingual indexes)
CREATE INDEX idx_course_translations_lang ON course_translations(lang);
CREATE INDEX idx_course_translations_slug ON course_translations(slug) WHERE slug IS NOT NULL;
CREATE INDEX idx_course_translations_course_lang ON course_translations(course_id, lang);
CREATE INDEX idx_course_translations_lang_slug ON course_translations(lang, slug) WHERE slug IS NOT NULL;

-- Section Translations
CREATE INDEX idx_section_translations_lang ON section_translations(lang);
CREATE INDEX idx_section_translations_section_lang ON section_translations(section_id, lang);

-- Learning Units
CREATE INDEX idx_learning_units_section ON learning_units(section_id);

-- Learning Unit Translations (NEW: multilingual indexes)
CREATE INDEX idx_learning_unit_translations_lang ON learning_unit_translations(lang);
CREATE INDEX idx_learning_unit_translations_unit_lang ON learning_unit_translations(unit_id, lang);

-- Learning Blocks
CREATE INDEX idx_learning_blocks_unit ON learning_blocks(unit_id);

-- Course Progress
CREATE INDEX idx_course_progress_user ON course_progress(user_id);
CREATE INDEX idx_course_progress_unit ON course_progress(unit_id);
CREATE INDEX idx_course_progress_completed ON course_progress(is_completed) WHERE is_completed = TRUE;

-- Coin Transactions
CREATE INDEX idx_coin_tx_user_id ON coin_transactions(user_id);
CREATE INDEX idx_coin_tx_type ON coin_transactions(type);
CREATE INDEX idx_coin_tx_created_at ON coin_transactions(created_at DESC);

-- Tags
CREATE INDEX idx_tag_translations_lang ON tag_translations(lang);
CREATE INDEX idx_course_tags_tag ON course_tags(tag_id);
CREATE INDEX idx_course_tags_course ON course_tags(course_id);

-- Specializations/Skills/Interests Translations
CREATE INDEX idx_specialization_translations_lang ON specialization_translations(lang);
CREATE INDEX idx_skill_translations_lang ON skill_translations(lang);
CREATE INDEX idx_interest_translations_lang ON interest_translations(lang);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE users IS 'Main user table with profile data';
COMMENT ON TABLE courses IS 'Course catalog with pricing and analytics';
COMMENT ON TABLE course_translations IS 'Multilingual course content (Netflix/Netflix style)';
COMMENT ON TABLE sections IS 'Course sections - title moved to section_translations';
COMMENT ON TABLE learning_units IS 'Learning units - title moved to learning_unit_translations';
COMMENT ON TABLE course_categories IS 'Normalized category system';
COMMENT ON TABLE course_categories_junction IS 'Many-to-many: courses to categories';
