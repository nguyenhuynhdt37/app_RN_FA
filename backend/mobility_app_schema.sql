-- Mobility App Database Schema
-- Generated: 2026-05-12

-- ═══════════════════════════════════════════
-- TABLES
-- ═══════════════════════════════════════════

CREATE TABLE alembic_version (
    version_num character varying(32),
    PRIMARY KEY (version_num)
);

CREATE TABLE course_progress (
    id uuid,
    user_id uuid,
    unit_id uuid,
    is_completed boolean,
    current_state jsonb,
    total_exp_gained integer,
    completed_at timestamp with time zone,
    last_accessed_at timestamp with time zone,
    PRIMARY KEY (id)
);

CREATE TABLE course_translations (
    id uuid,
    course_id uuid,
    lang character varying(5),
    title character varying(255),
    subtitle text,
    description text,
    learning_outcomes ARRAY,
    prerequisites ARRAY,
    slug character varying(255),
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    PRIMARY KEY (id)
);

CREATE TABLE courses (
    id uuid,
    thumbnail_url text,
    level USER-DEFINED,
    tags ARRAY,
    estimated_duration integer,
    difficulty_score integer,
    is_published boolean,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    instructor_id uuid,
    created_by uuid,
    updated_by uuid,
    category_ids ARRAY,
    preview_video_type integer,
    base_price integer,
    currency character varying(3),
    views integer,
    total_enrolls integer,
    revenue integer,
    rating_avg double precision,
    lessons_count integer,
    approval_status character varying(20),
    approval_note text,
    default_slug character varying(255),
    PRIMARY KEY (id)
);

CREATE TABLE interests_reference (
    id uuid,
    name_en character varying(100),
    name_vi character varying(100),
    is_active boolean,
    PRIMARY KEY (id)
);

CREATE TABLE learning_blocks (
    id uuid,
    unit_id uuid,
    block_type character varying(50),
    position integer,
    content jsonb,
    created_at timestamp with time zone,
    PRIMARY KEY (id)
);

CREATE TABLE learning_units (
    id uuid,
    section_id uuid,
    title character varying(255),
    position integer,
    is_free boolean,
    base_exp integer,
    required_unit_id uuid,
    created_at timestamp with time zone,
    PRIMARY KEY (id)
);

CREATE TABLE login_attempts (
    id uuid,
    identifier character varying(255),
    success boolean,
    ip_address inet,
    device_type character varying(10),
    failure_reason character varying(50),
    created_at timestamp with time zone,
    PRIMARY KEY (id)
);

CREATE TABLE oauth_accounts (
    id uuid,
    user_id uuid,
    provider character varying(20),
    provider_uid character varying(255),
    provider_email character varying(255),
    access_token text,
    refresh_token text,
    token_expires_at timestamp with time zone,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    PRIMARY KEY (id)
);

CREATE TABLE otp_logs (
    id uuid,
    user_id uuid,
    otp_hash character varying(10),
    type USER-DEFINED,
    expires_at timestamp with time zone,
    verified_at timestamp with time zone,
    attempts integer,
    created_at timestamp with time zone,
    phone character varying(20),
    PRIMARY KEY (id)
);

CREATE TABLE phone_verifications (
    id uuid,
    phone character varying(20),
    otp_hash text,
    purpose character varying(30),
    attempts integer,
    is_verified boolean,
    verified_at timestamp with time zone,
    expires_at timestamp with time zone,
    ip_address inet,
    created_at timestamp with time zone,
    PRIMARY KEY (id)
);

CREATE TABLE roles (
    id uuid,
    name character varying(50),
    description text,
    created_at timestamp with time zone,
    PRIMARY KEY (id)
);

CREATE TABLE section_translations (
    id uuid,
    section_id uuid,
    lang character varying(5),
    title character varying(255),
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    PRIMARY KEY (id)
);

CREATE TABLE sections (
    id uuid,
    course_id uuid,
    title character varying(255),
    position integer,
    created_at timestamp with time zone,
    PRIMARY KEY (id)
);

CREATE TABLE sessions (
    id uuid,
    user_id uuid,
    refresh_token_hash text,
    device_name character varying(255),
    device_type USER-DEFINED,
    ip_address inet,
    user_agent text,
    last_used_at timestamp with time zone,
    expires_at timestamp with time zone,
    revoked_at timestamp with time zone,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    device_token text,
    push_provider character varying(10),
    PRIMARY KEY (id)
);

CREATE TABLE skills_reference (
    id uuid,
    specialization_id uuid,
    name_en character varying(100),
    name_vi character varying(100),
    is_active boolean,
    PRIMARY KEY (id)
);

CREATE TABLE specializations_reference (
    id uuid,
    code character varying(50),
    name_en character varying(100),
    name_vi character varying(100),
    is_active boolean,
    created_at timestamp with time zone,
    PRIMARY KEY (id)
);

CREATE TABLE user_roles (
    user_id uuid,
    role_id uuid,
    assigned_at timestamp with time zone,
    assigned_by uuid,
    expires_at timestamp with time zone,
    is_active boolean,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE user_specializations (
    id uuid,
    user_id uuid,
    level character varying(50),
    skills jsonb,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    specialization_id uuid,
    PRIMARY KEY (id)
);

CREATE TABLE user_with_roles (
    id uuid,
    email character varying(255),
    phone character varying(20),
    full_name character varying(120),
    status USER-DEFINED,
    is_verified boolean,
    avatar_url text,
    roles ARRAY,
    created_at timestamp with time zone,
    last_login_at timestamp with time zone
);

CREATE TABLE users (
    id uuid,
    email character varying(255),
    phone character varying(20),
    password_hash text,
    full_name character varying(120),
    status USER-DEFINED,
    is_verified boolean,
    last_login_at timestamp with time zone,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    avatar_url text,
    preferred_lang character varying(5),
    preferred_currency character varying(3),
    date_of_birth date,
    gender character varying(10),
    username character varying(50),
    bio text,
    is_profile_completed boolean,
    learning_goals text,
    interests jsonb,
    daily_goal_minutes integer,
    preferred_learning_style character varying(20),
    social_links jsonb,
    cover_url text,
    instructor_metadata jsonb,
    PRIMARY KEY (id)
);

-- ═══════════════════════════════════════════
-- FOREIGN KEYS
-- ═══════════════════════════════════════════

ALTER TABLE course_progress ADD CONSTRAINT course_progress_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);
ALTER TABLE course_progress ADD CONSTRAINT course_progress_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES learning_units(id);
ALTER TABLE course_translations ADD CONSTRAINT fk_ct_course FOREIGN KEY (course_id) REFERENCES courses(id);
ALTER TABLE courses ADD CONSTRAINT courses_instructor_id_fkey FOREIGN KEY (instructor_id) REFERENCES users(id);
ALTER TABLE courses ADD CONSTRAINT courses_created_by_fkey FOREIGN KEY (created_by) REFERENCES users(id);
ALTER TABLE courses ADD CONSTRAINT courses_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES users(id);
ALTER TABLE learning_blocks ADD CONSTRAINT learning_blocks_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES learning_units(id);
ALTER TABLE learning_units ADD CONSTRAINT learning_units_section_id_fkey FOREIGN KEY (section_id) REFERENCES sections(id);
ALTER TABLE learning_units ADD CONSTRAINT learning_units_required_unit_id_fkey FOREIGN KEY (required_unit_id) REFERENCES learning_units(id);
ALTER TABLE oauth_accounts ADD CONSTRAINT oauth_accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);
ALTER TABLE otp_logs ADD CONSTRAINT otp_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);
ALTER TABLE section_translations ADD CONSTRAINT fk_st_section FOREIGN KEY (section_id) REFERENCES sections(id);
ALTER TABLE sections ADD CONSTRAINT sections_course_id_fkey FOREIGN KEY (course_id) REFERENCES courses(id);
ALTER TABLE sessions ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);
ALTER TABLE skills_reference ADD CONSTRAINT skills_reference_specialization_id_fkey FOREIGN KEY (specialization_id) REFERENCES specializations_reference(id);
ALTER TABLE user_roles ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);
ALTER TABLE user_roles ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES roles(id);
ALTER TABLE user_roles ADD CONSTRAINT user_roles_assigned_by_fkey FOREIGN KEY (assigned_by) REFERENCES users(id);
ALTER TABLE user_specializations ADD CONSTRAINT user_specializations_spec_id_fkey FOREIGN KEY (specialization_id) REFERENCES specializations_reference(id);
ALTER TABLE user_specializations ADD CONSTRAINT user_specializations_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);

-- ═══════════════════════════════════════════
-- INDEXES
-- ═══════════════════════════════════════════

CREATE UNIQUE INDEX alembic_version_pkc ON public.alembic_version USING btree (version_num);
CREATE UNIQUE INDEX course_progress_pkey ON public.course_progress USING btree (id);
CREATE UNIQUE INDEX idx_user_unit_progress ON public.course_progress USING btree (user_id, unit_id);
CREATE UNIQUE INDEX course_translations_course_id_lang_key ON public.course_translations USING btree (course_id, lang);
CREATE UNIQUE INDEX course_translations_pkey ON public.course_translations USING btree (id);
CREATE UNIQUE INDEX courses_pkey ON public.courses USING btree (id);
CREATE UNIQUE INDEX interests_reference_pkey ON public.interests_reference USING btree (id);
CREATE UNIQUE INDEX learning_blocks_pkey ON public.learning_blocks USING btree (id);
CREATE UNIQUE INDEX learning_units_pkey ON public.learning_units USING btree (id);
CREATE INDEX idx_login_attempts_identifier ON public.login_attempts USING btree (identifier, created_at);
CREATE INDEX idx_login_attempts_ip ON public.login_attempts USING btree (ip_address, created_at);
CREATE UNIQUE INDEX login_attempts_pkey ON public.login_attempts USING btree (id);
CREATE INDEX idx_oauth_user_id ON public.oauth_accounts USING btree (user_id);
CREATE UNIQUE INDEX oauth_accounts_pkey ON public.oauth_accounts USING btree (id);
CREATE UNIQUE INDEX oauth_accounts_provider_provider_uid_key ON public.oauth_accounts USING btree (provider, provider_uid);
CREATE INDEX idx_otp_logs_user_id ON public.otp_logs USING btree (user_id);
CREATE UNIQUE INDEX otp_logs_pkey ON public.otp_logs USING btree (id);
CREATE INDEX idx_phone_verif_expires ON public.phone_verifications USING btree (expires_at);
CREATE INDEX idx_phone_verif_phone_purpose ON public.phone_verifications USING btree (phone, purpose);
CREATE UNIQUE INDEX phone_verifications_pkey ON public.phone_verifications USING btree (id);
CREATE UNIQUE INDEX roles_name_key ON public.roles USING btree (name);
CREATE UNIQUE INDEX roles_pkey ON public.roles USING btree (id);
CREATE UNIQUE INDEX section_translations_pkey ON public.section_translations USING btree (id);
CREATE UNIQUE INDEX section_translations_section_id_lang_key ON public.section_translations USING btree (section_id, lang);
CREATE UNIQUE INDEX sections_pkey ON public.sections USING btree (id);
CREATE INDEX idx_sessions_active ON public.sessions USING btree (user_id) WHERE (revoked_at IS NULL);
CREATE INDEX idx_sessions_expires_at ON public.sessions USING btree (expires_at);
CREATE INDEX idx_sessions_user_id ON public.sessions USING btree (user_id);
CREATE UNIQUE INDEX sessions_pkey ON public.sessions USING btree (id);
CREATE UNIQUE INDEX sessions_refresh_token_hash_key ON public.sessions USING btree (refresh_token_hash);
CREATE INDEX idx_skills_ref_specialization ON public.skills_reference USING btree (specialization_id);
CREATE UNIQUE INDEX skills_reference_pkey ON public.skills_reference USING btree (id);
CREATE UNIQUE INDEX specializations_reference_code_key ON public.specializations_reference USING btree (code);
CREATE UNIQUE INDEX specializations_reference_pkey ON public.specializations_reference USING btree (id);
CREATE INDEX idx_user_roles_role_id ON public.user_roles USING btree (role_id);
CREATE INDEX idx_user_roles_user_id ON public.user_roles USING btree (user_id);
CREATE UNIQUE INDEX user_roles_pkey ON public.user_roles USING btree (user_id, role_id);
CREATE INDEX idx_user_specializations_user_id ON public.user_specializations USING btree (user_id);
CREATE UNIQUE INDEX user_specializations_pkey ON public.user_specializations USING btree (id);
CREATE INDEX idx_users_email ON public.users USING btree (email);
CREATE INDEX idx_users_phone ON public.users USING btree (phone);
CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email);
CREATE UNIQUE INDEX users_phone_key ON public.users USING btree (phone);
CREATE UNIQUE INDEX users_pkey ON public.users USING btree (id);
CREATE UNIQUE INDEX users_username_key ON public.users USING btree (username);

-- End of schema
