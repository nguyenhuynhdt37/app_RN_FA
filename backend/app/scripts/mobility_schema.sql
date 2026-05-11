-- ============================================================
-- MOBILITY APP — PostgreSQL DDL Schema (Production)
-- Grab clone: Ride-hailing + Food Delivery + Parcel
-- ============================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- NOTE: PostGIS not available in pgvector image.
-- Proximity search handled in app layer (Haversine).
-- To enable PostGIS: switch Docker image to postgis/postgis:16-3.4

-- ============================================================
-- ENUMS
-- ============================================================

CREATE TYPE user_role AS ENUM (
    'customer',
    'driver',
    'merchant_owner',
    'merchant_staff',
    'fleet_owner',
    'corporate_admin',
    'corporate_user',
    'cs_agent',
    'finance',
    'operator',
    'super_admin'
);

CREATE TYPE kyc_level AS ENUM ('none', 'basic', 'full', 'enterprise');
CREATE TYPE platform_type AS ENUM ('ios', 'android', 'web');
CREATE TYPE gender_type AS ENUM ('male', 'female', 'other');

CREATE TYPE driver_approval_status AS ENUM (
    'pending_review',
    'approved',
    'rejected',
    'suspended',
    'banned'
);

CREATE TYPE driver_online_status AS ENUM ('offline', 'online', 'busy', 'on_break');

CREATE TYPE vehicle_type AS ENUM ('motorbike', 'car', 'van', 'truck', 'bicycle');

CREATE TYPE service_type AS ENUM ('ride', 'food_delivery', 'parcel', 'mart');

CREATE TYPE merchant_type AS ENUM ('restaurant', 'grocery', 'pharmacy', 'retail');

CREATE TYPE merchant_approval_status AS ENUM (
    'pending_review',
    'approved',
    'rejected',
    'suspended'
);

CREATE TYPE fleet_approval_status AS ENUM ('pending', 'approved', 'rejected', 'suspended');

CREATE TYPE payment_method AS ENUM ('cash', 'wallet', 'card', 'corporate');

CREATE TYPE billing_cycle AS ENUM ('weekly', 'monthly');

CREATE TYPE driver_doc_type AS ENUM (
    'id_card_front',
    'id_card_back',
    'license_front',
    'selfie',
    'vehicle_registration',
    'vehicle_insurance',
    'vehicle_photo'
);

CREATE TYPE merchant_staff_role AS ENUM ('owner', 'manager', 'staff');

CREATE TYPE corp_member_role AS ENUM ('admin', 'member');

CREATE TYPE trip_status AS ENUM (
    'searching',
    'driver_found',
    'driver_arrived',
    'in_progress',
    'completed',
    'cancelled_by_customer',
    'cancelled_by_driver',
    'cancelled_by_system'
);

CREATE TYPE order_status AS ENUM (
    'pending',
    'confirmed',
    'preparing',
    'ready_for_pickup',
    'picked_up',
    'delivering',
    'delivered',
    'cancelled_by_customer',
    'cancelled_by_merchant',
    'cancelled_by_system'
);

CREATE TYPE transaction_type AS ENUM (
    'trip_charge',
    'order_charge',
    'top_up',
    'withdrawal',
    'refund',
    'commission',
    'incentive',
    'adjustment'
);

CREATE TYPE wallet_owner_type AS ENUM ('customer', 'driver', 'merchant', 'fleet');

CREATE TYPE dispute_status AS ENUM (
    'open',
    'in_review',
    'resolved',
    'escalated',
    'closed'
);

CREATE TYPE notification_type AS ENUM (
    'trip_update',
    'order_update',
    'payment',
    'promotion',
    'system',
    'kyc_status'
);

-- ============================================================
-- CORE: USERS
-- ============================================================

CREATE TABLE users (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone               VARCHAR(20) UNIQUE NOT NULL,
    email               VARCHAR(255) UNIQUE,
    hashed_password     TEXT,                          -- NULL nếu OTP-only

    full_name           VARCHAR(150) NOT NULL,
    avatar_url          TEXT,
    date_of_birth       DATE,
    gender              gender_type,

    role                user_role NOT NULL DEFAULT 'customer',
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    is_phone_verified   BOOLEAN NOT NULL DEFAULT FALSE,
    is_email_verified   BOOLEAN NOT NULL DEFAULT FALSE,
    kyc_level           kyc_level NOT NULL DEFAULT 'none',

    device_token        TEXT,
    device_platform     platform_type,
    last_seen_at        TIMESTAMPTZ,

    preferred_lang      VARCHAR(5) NOT NULL DEFAULT 'vi',
    preferred_currency  VARCHAR(3) NOT NULL DEFAULT 'VND',

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);

-- ============================================================
-- OTP (Phone verification — Redis preferred, but DB fallback)
-- ============================================================

CREATE TABLE otp_codes (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone       VARCHAR(20) NOT NULL,
    code        VARCHAR(10) NOT NULL,
    purpose     VARCHAR(30) NOT NULL,      -- 'login', 'register', 'reset_password'
    attempts    SMALLINT NOT NULL DEFAULT 0,
    is_used     BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_otp_phone_purpose ON otp_codes(phone, purpose);

-- ============================================================
-- OAUTH (Google / Apple)
-- ============================================================

CREATE TABLE oauth_accounts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider        VARCHAR(20) NOT NULL,  -- 'google', 'apple'
    provider_uid    VARCHAR(255) NOT NULL,
    access_token    TEXT,
    refresh_token   TEXT,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(provider, provider_uid)
);

-- ============================================================
-- CUSTOMER
-- ============================================================

CREATE TABLE customer_profiles (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    home_address            TEXT,
    home_lat                DOUBLE PRECISION,
    home_lng                DOUBLE PRECISION,
    work_address            TEXT,
    work_lat                DOUBLE PRECISION,
    work_lng                DOUBLE PRECISION,

    default_payment         payment_method NOT NULL DEFAULT 'cash',

    rating                  NUMERIC(3,2) NOT NULL DEFAULT 5.00,
    rating_count            INT NOT NULL DEFAULT 0,
    total_trips             INT NOT NULL DEFAULT 0,
    total_orders            INT NOT NULL DEFAULT 0,
    loyalty_points          INT NOT NULL DEFAULT 0,

    preferred_vehicle_type  vehicle_type,
    is_pet_friendly         BOOLEAN NOT NULL DEFAULT FALSE,

    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE saved_places (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    label       VARCHAR(100) NOT NULL,
    address     TEXT NOT NULL,
    lat         DOUBLE PRECISION NOT NULL,
    lng         DOUBLE PRECISION NOT NULL,
    icon        VARCHAR(50),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_saved_places_user ON saved_places(user_id);

-- ============================================================
-- DRIVER
-- ============================================================

CREATE TABLE driver_profiles (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    fleet_id                UUID,                           -- FK added after fleets table

    -- KYC
    id_card_number          VARCHAR(20) UNIQUE NOT NULL,
    license_number          VARCHAR(30) UNIQUE NOT NULL,
    license_class           VARCHAR(5),                     -- A1, B1, B2...
    license_expiry          DATE,

    -- Approval
    approval_status         driver_approval_status NOT NULL DEFAULT 'pending_review',
    approved_at             TIMESTAMPTZ,
    approved_by             UUID REFERENCES users(id),
    rejection_reason        TEXT,
    suspension_reason       TEXT,
    suspension_until        TIMESTAMPTZ,

    -- Service
    service_types           service_type[] NOT NULL DEFAULT '{ride}',

    -- Vehicle
    vehicle_type            vehicle_type NOT NULL DEFAULT 'motorbike',
    vehicle_brand           VARCHAR(50),
    vehicle_model           VARCHAR(50),
    vehicle_year            SMALLINT,
    vehicle_plate           VARCHAR(20) UNIQUE NOT NULL,
    vehicle_color           VARCHAR(30),
    vehicle_insurance_expiry DATE,

    -- Realtime (updated frequently — consider Redis for hot path)
    is_online               BOOLEAN NOT NULL DEFAULT FALSE,
    current_status          driver_online_status NOT NULL DEFAULT 'offline',
    current_lat             DOUBLE PRECISION,
    current_lng             DOUBLE PRECISION,
    current_heading         REAL,
    last_location_at        TIMESTAMPTZ,

    -- Finance
    bank_account_number     VARCHAR(30),
    bank_name               VARCHAR(100),
    bank_account_name       VARCHAR(150),

    -- Stats
    rating                  NUMERIC(3,2) NOT NULL DEFAULT 5.00,
    rating_count            INT NOT NULL DEFAULT 0,
    total_trips             INT NOT NULL DEFAULT 0,
    total_distance_km       NUMERIC(10,2) NOT NULL DEFAULT 0,
    acceptance_rate         NUMERIC(4,3) NOT NULL DEFAULT 1.000,
    completion_rate         NUMERIC(4,3) NOT NULL DEFAULT 1.000,
    cancellation_count      INT NOT NULL DEFAULT 0,

    -- Today shift (reset at midnight by cron)
    shift_started_at        TIMESTAMPTZ,
    today_trips             INT NOT NULL DEFAULT 0,
    today_earnings          NUMERIC(12,2) NOT NULL DEFAULT 0,

    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_driver_approval ON driver_profiles(approval_status);
CREATE INDEX idx_driver_online ON driver_profiles(is_online, current_status);
-- Btree index on lat/lng for basic bounding-box filter (app does Haversine)
CREATE INDEX idx_driver_lat ON driver_profiles(current_lat) WHERE is_online = TRUE;
CREATE INDEX idx_driver_lng ON driver_profiles(current_lng) WHERE is_online = TRUE;

CREATE TABLE driver_documents (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    driver_id   UUID NOT NULL REFERENCES driver_profiles(id) ON DELETE CASCADE,
    doc_type    driver_doc_type NOT NULL,
    doc_url     TEXT NOT NULL,
    verified    BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    verified_by UUID REFERENCES users(id),
    expires_at  DATE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(driver_id, doc_type)
);

-- ============================================================
-- FLEET
-- ============================================================

CREATE TABLE fleets (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_user_id       UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    fleet_name          VARCHAR(150) NOT NULL,
    business_license    VARCHAR(50),
    approval_status     fleet_approval_status NOT NULL DEFAULT 'pending',
    commission_rate     NUMERIC(4,3) NOT NULL DEFAULT 0.100,   -- 10%
    total_drivers       INT NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Back-reference fleet FK on driver_profiles
ALTER TABLE driver_profiles
    ADD CONSTRAINT fk_driver_fleet
    FOREIGN KEY (fleet_id) REFERENCES fleets(id) ON DELETE SET NULL;

-- ============================================================
-- MERCHANT
-- ============================================================

CREATE TABLE merchant_businesses (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_name       VARCHAR(200) NOT NULL,
    business_type       merchant_type NOT NULL DEFAULT 'restaurant',
    tax_code            VARCHAR(20),
    business_license_url TEXT,
    approval_status     merchant_approval_status NOT NULL DEFAULT 'pending_review',
    commission_rate     NUMERIC(4,3) NOT NULL DEFAULT 0.200,   -- 20%
    bank_account_number VARCHAR(30),
    bank_name           VARCHAR(100),
    bank_account_name   VARCHAR(150),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE merchant_outlets (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id     UUID NOT NULL REFERENCES merchant_businesses(id) ON DELETE CASCADE,
    outlet_name     VARCHAR(200) NOT NULL,
    description     TEXT,
    phone           VARCHAR(20) NOT NULL,
    email           VARCHAR(255),
    avatar_url      TEXT,
    banner_url      TEXT,
    address         TEXT NOT NULL,
    lat             DOUBLE PRECISION NOT NULL,
    lng             DOUBLE PRECISION NOT NULL,
    city            VARCHAR(100),
    district        VARCHAR(100),
    is_open         BOOLEAN NOT NULL DEFAULT TRUE,
    is_busy         BOOLEAN NOT NULL DEFAULT FALSE,
    busy_until      TIMESTAMPTZ,
    -- {"MON":{"open":"08:00","close":"22:00"}, ...}
    operating_hours JSONB NOT NULL DEFAULT '{}',
    rating          NUMERIC(3,2) NOT NULL DEFAULT 5.00,
    rating_count    INT NOT NULL DEFAULT 0,
    total_orders    INT NOT NULL DEFAULT 0,
    avg_prep_time   SMALLINT NOT NULL DEFAULT 20,   -- minutes
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_outlet_lat ON merchant_outlets(lat);
CREATE INDEX idx_outlet_lng ON merchant_outlets(lng);
CREATE INDEX idx_outlet_open ON merchant_outlets(is_open, is_busy);

CREATE TABLE merchant_staff (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    outlet_id   UUID NOT NULL REFERENCES merchant_outlets(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    staff_role  merchant_staff_role NOT NULL DEFAULT 'staff',
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(outlet_id, user_id)
);

-- ============================================================
-- CORPORATE
-- ============================================================

CREATE TABLE corporate_accounts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_user_id   UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_name    VARCHAR(200) NOT NULL,
    tax_code        VARCHAR(20),
    billing_email   VARCHAR(255) NOT NULL,
    monthly_budget  NUMERIC(12,2),
    current_spent   NUMERIC(12,2) NOT NULL DEFAULT 0,
    billing_cycle   billing_cycle NOT NULL DEFAULT 'monthly',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE corporate_members (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    corporate_id    UUID NOT NULL REFERENCES corporate_accounts(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    member_role     corp_member_role NOT NULL DEFAULT 'member',
    trip_budget     NUMERIC(10,2),           -- per-trip limit, NULL = unlimited
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(corporate_id, user_id)
);

-- ============================================================
-- WALLET
-- ============================================================

CREATE TABLE wallets (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id        UUID NOT NULL,
    owner_type      wallet_owner_type NOT NULL,
    balance         NUMERIC(12,2) NOT NULL DEFAULT 0,
    currency        VARCHAR(3) NOT NULL DEFAULT 'VND',
    is_frozen       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(owner_id, owner_type)
);

CREATE TABLE wallet_transactions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id       UUID NOT NULL REFERENCES wallets(id),
    type            transaction_type NOT NULL,
    amount          NUMERIC(12,2) NOT NULL,      -- positive = credit, negative = debit
    balance_after   NUMERIC(12,2) NOT NULL,
    ref_id          UUID,                        -- trip_id / order_id / etc.
    ref_type        VARCHAR(30),                 -- 'trip', 'order', 'withdrawal'
    description     TEXT,
    metadata        JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_wallet_tx_wallet ON wallet_transactions(wallet_id, created_at DESC);
CREATE INDEX idx_wallet_tx_ref ON wallet_transactions(ref_id, ref_type);

-- ============================================================
-- TRIPS (Ride-hailing)
-- ============================================================

CREATE TABLE trips (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id         UUID NOT NULL REFERENCES users(id),
    driver_id           UUID REFERENCES users(id),
    corporate_id        UUID REFERENCES corporate_accounts(id),

    status              trip_status NOT NULL DEFAULT 'searching',
    vehicle_type        vehicle_type NOT NULL DEFAULT 'motorbike',

    -- Pickup
    pickup_address      TEXT NOT NULL,
    pickup_lat          DOUBLE PRECISION NOT NULL,
    pickup_lng          DOUBLE PRECISION NOT NULL,
    -- Destination
    dest_address        TEXT NOT NULL,
    dest_lat            DOUBLE PRECISION NOT NULL,
    dest_lng            DOUBLE PRECISION NOT NULL,

    -- Pricing
    estimated_distance  NUMERIC(8,2),           -- km
    estimated_duration  INT,                    -- seconds
    base_fare           NUMERIC(10,2),
    surge_multiplier    NUMERIC(4,2) DEFAULT 1.00,
    final_fare          NUMERIC(10,2),
    payment_method      payment_method NOT NULL DEFAULT 'cash',

    -- Timestamps
    driver_accepted_at  TIMESTAMPTZ,
    driver_arrived_at   TIMESTAMPTZ,
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    cancelled_at        TIMESTAMPTZ,
    cancel_reason       TEXT,

    -- Rating
    customer_rating     SMALLINT CHECK(customer_rating BETWEEN 1 AND 5),
    driver_rating       SMALLINT CHECK(driver_rating BETWEEN 1 AND 5),
    customer_review     TEXT,
    driver_review       TEXT,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_trips_customer ON trips(customer_id, created_at DESC);
CREATE INDEX idx_trips_driver ON trips(driver_id, created_at DESC);
CREATE INDEX idx_trips_status ON trips(status);

-- ============================================================
-- ORDERS (Food / Mart delivery)
-- ============================================================

CREATE TABLE orders (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id     UUID NOT NULL REFERENCES users(id),
    outlet_id       UUID NOT NULL REFERENCES merchant_outlets(id),
    driver_id       UUID REFERENCES users(id),
    corporate_id    UUID REFERENCES corporate_accounts(id),

    status          order_status NOT NULL DEFAULT 'pending',

    -- Delivery
    delivery_address    TEXT NOT NULL,
    delivery_lat        DOUBLE PRECISION NOT NULL,
    delivery_lng        DOUBLE PRECISION NOT NULL,
    delivery_notes      TEXT,

    -- Pricing
    subtotal            NUMERIC(10,2) NOT NULL DEFAULT 0,
    delivery_fee        NUMERIC(10,2) NOT NULL DEFAULT 0,
    discount_amount     NUMERIC(10,2) NOT NULL DEFAULT 0,
    total_amount        NUMERIC(10,2) NOT NULL DEFAULT 0,
    payment_method      payment_method NOT NULL DEFAULT 'cash',

    -- Timing
    estimated_prep_time     INT,            -- minutes
    estimated_delivery_time INT,            -- minutes
    confirmed_at            TIMESTAMPTZ,
    ready_at                TIMESTAMPTZ,
    picked_up_at            TIMESTAMPTZ,
    delivered_at            TIMESTAMPTZ,
    cancelled_at            TIMESTAMPTZ,
    cancel_reason           TEXT,

    -- Rating
    merchant_rating     SMALLINT CHECK(merchant_rating BETWEEN 1 AND 5),
    driver_rating       SMALLINT CHECK(driver_rating BETWEEN 1 AND 5),
    merchant_review     TEXT,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_customer ON orders(customer_id, created_at DESC);
CREATE INDEX idx_orders_outlet ON orders(outlet_id, created_at DESC);
CREATE INDEX idx_orders_driver ON orders(driver_id, created_at DESC);
CREATE INDEX idx_orders_status ON orders(status);

CREATE TABLE order_items (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id    UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id UUID NOT NULL,            -- FK → menu_items (future)
    item_name   VARCHAR(200) NOT NULL,     -- snapshot at order time
    unit_price  NUMERIC(10,2) NOT NULL,
    quantity    SMALLINT NOT NULL DEFAULT 1,
    subtotal    NUMERIC(10,2) NOT NULL,
    notes       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- MENU (Merchant)
-- ============================================================

CREATE TABLE menu_categories (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    outlet_id   UUID NOT NULL REFERENCES merchant_outlets(id) ON DELETE CASCADE,
    name        VARCHAR(100) NOT NULL,
    sort_order  SMALLINT NOT NULL DEFAULT 0,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE menu_items (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id     UUID NOT NULL REFERENCES menu_categories(id) ON DELETE CASCADE,
    outlet_id       UUID NOT NULL REFERENCES merchant_outlets(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    price           NUMERIC(10,2) NOT NULL,
    image_url       TEXT,
    is_available    BOOLEAN NOT NULL DEFAULT TRUE,
    is_featured     BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order      SMALLINT NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_menu_items_outlet ON menu_items(outlet_id, is_available);

-- ============================================================
-- PROMOTIONS / VOUCHERS
-- ============================================================

CREATE TABLE promotions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code            VARCHAR(50) UNIQUE,
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    discount_type   VARCHAR(20) NOT NULL,   -- 'percent', 'fixed'
    discount_value  NUMERIC(10,2) NOT NULL,
    min_order_value NUMERIC(10,2),
    max_discount    NUMERIC(10,2),
    usage_limit     INT,
    used_count      INT NOT NULL DEFAULT 0,
    start_at        TIMESTAMPTZ NOT NULL,
    end_at          TIMESTAMPTZ NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE promotion_usages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    promotion_id    UUID NOT NULL REFERENCES promotions(id),
    user_id         UUID NOT NULL REFERENCES users(id),
    ref_id          UUID NOT NULL,         -- trip_id / order_id
    ref_type        VARCHAR(20) NOT NULL,  -- 'trip' / 'order'
    discount_applied NUMERIC(10,2) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(promotion_id, user_id, ref_id)
);

-- ============================================================
-- DISPUTES / CS
-- ============================================================

CREATE TABLE disputes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reporter_id     UUID NOT NULL REFERENCES users(id),
    reported_id     UUID REFERENCES users(id),
    ref_id          UUID,                  -- trip_id / order_id
    ref_type        VARCHAR(20),
    subject         VARCHAR(255) NOT NULL,
    description     TEXT NOT NULL,
    status          dispute_status NOT NULL DEFAULT 'open',
    assigned_to     UUID REFERENCES users(id),    -- CS Agent
    resolution      TEXT,
    resolved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_disputes_status ON disputes(status);
CREATE INDEX idx_disputes_assigned ON disputes(assigned_to);

CREATE TABLE dispute_messages (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dispute_id  UUID NOT NULL REFERENCES disputes(id) ON DELETE CASCADE,
    sender_id   UUID NOT NULL REFERENCES users(id),
    message     TEXT NOT NULL,
    attachment_url TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================

CREATE TABLE notifications (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type        notification_type NOT NULL,
    title       VARCHAR(255) NOT NULL,
    body        TEXT NOT NULL,
    data        JSONB,                      -- deep link, ref_id, ref_type
    is_read     BOOLEAN NOT NULL DEFAULT FALSE,
    sent_at     TIMESTAMPTZ,
    read_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read, created_at DESC);

-- ============================================================
-- AUDIT LOG (Admin / CS / Finance actions)
-- ============================================================

CREATE TABLE audit_logs (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_id    UUID NOT NULL REFERENCES users(id),
    action      VARCHAR(100) NOT NULL,     -- 'driver.approve', 'refund.create'
    target_type VARCHAR(50),              -- 'user', 'trip', 'order'
    target_id   UUID,
    old_value   JSONB,
    new_value   JSONB,
    ip_address  INET,
    user_agent  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_actor ON audit_logs(actor_id, created_at DESC);
CREATE INDEX idx_audit_target ON audit_logs(target_type, target_id);

-- ============================================================
-- PRICING CONFIG (Admin configurable)
-- ============================================================

CREATE TABLE pricing_rules (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_type    service_type NOT NULL,
    vehicle_type    vehicle_type NOT NULL,
    city            VARCHAR(100) NOT NULL DEFAULT 'hanoi',
    base_fare       NUMERIC(10,2) NOT NULL,
    per_km_rate     NUMERIC(10,2) NOT NULL,
    per_minute_rate NUMERIC(10,2) NOT NULL DEFAULT 0,
    min_fare        NUMERIC(10,2) NOT NULL,
    surge_threshold NUMERIC(4,2) NOT NULL DEFAULT 1.5,  -- demand/supply ratio
    max_surge       NUMERIC(4,2) NOT NULL DEFAULT 3.0,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    updated_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(service_type, vehicle_type, city)
);
