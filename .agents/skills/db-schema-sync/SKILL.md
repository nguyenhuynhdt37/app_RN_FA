---
name: db-schema-sync
description: "Thiết kế DB schema production → apply lên PostgreSQL → dùng sqlacodegen reverse-engineer SQLAlchemy models → tự động fix cú pháp. Dành cho FastAPI + PostgreSQL projects."
risk: moderate
source: custom
date_added: "2026-04-30"
---

# 🗄️ DB Schema Sync Skill

Workflow tự động: **Design SQL Schema → Migrate to PostgreSQL → sqlacodegen → Fix syntax → Ready to use models**

## Use this skill when

- Thiết kế DB schema mới cho một module hoặc toàn bộ dự án
- Đồng bộ SQLAlchemy models từ PostgreSQL thực tế (reverse engineering)
- Thêm bảng mới và cần regenerate models
- Cần tái cấu trúc models sau khi schema thay đổi nhiều

## Do NOT use this skill when

- Chỉ sửa nhỏ 1-2 field → dùng Alembic migration trực tiếp
- Project không dùng PostgreSQL
- Project không dùng SQLAlchemy

---

## Workflow: 5 Bước Bắt Buộc (Theo Thứ Tự)

```
Step 1: Thiết kế SQL DDL Schema
    ↓
Step 2: Apply schema lên PostgreSQL
    ↓
Step 3: Chạy sqlacodegen (reverse engineer)
    ↓
Step 4: Chạy fix_sqlacodegen_models.py
    ↓
Step 5: Tích hợp vào project (update alembic env.py)
```

---

## Step 1: Thiết Kế SQL DDL Schema

### Nguyên tắc thiết kế

- **UUID làm Primary Key** — không dùng int/serial cho production
- **Tất cả PK** phải có `DEFAULT uuid_generate_v4()`
- **Timestamps** bắt buộc: `created_at TIMESTAMPTZ DEFAULT NOW()`, `updated_at TIMESTAMPTZ DEFAULT NOW()`
- **Enum types** khai báo bằng `CREATE TYPE ... AS ENUM` trước khi tạo table
- **Index** ngay trong DDL — đừng để sau
- **JSONB** cho dữ liệu semi-structured (operating_hours, metadata, settings)
- **PostGIS** khi cần spatial query (driver proximity search)

### File output

```
backend/app/scripts/mobility_schema.sql
```

### Template DDL chuẩn

```sql
-- ① Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- ② Enums
CREATE TYPE user_role AS ENUM ('customer', 'driver', 'admin');

-- ③ Table với UUID PK
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone       VARCHAR(20) UNIQUE NOT NULL,
    role        user_role NOT NULL DEFAULT 'customer',
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ④ Index ngay sau table
CREATE INDEX idx_users_role ON users(role);
```

---

## Step 2: Apply Schema Lên PostgreSQL

### Trường hợp A — DB chưa có gì (fresh)

```bash
# Đứng trong thư mục backend/
psql postgresql://postgres:password@127.0.0.1:5432/myapp_db \
  -f app/scripts/mobility_schema.sql
```

### Trường hợp B — DB đã có dữ liệu (incremental)

```bash
# Tạo Alembic migration từ models hiện tại
cd backend/
source venv/bin/activate
alembic revision --autogenerate -m "add_mobility_schema"
alembic upgrade head
```

### Trường hợp C — Reset hoàn toàn (dev only)

```bash
psql postgresql://postgres:password@127.0.0.1:5432/postgres \
  -c "DROP DATABASE IF EXISTS myapp_db;"
psql postgresql://postgres:password@127.0.0.1:5432/postgres \
  -c "CREATE DATABASE myapp_db;"
psql postgresql://postgres:password@127.0.0.1:5432/myapp_db \
  -f app/scripts/mobility_schema.sql
```

---

## Step 3: Chạy sqlacodegen

> [!IMPORTANT]
> Lệnh sqlacodegen PHẢI dùng `postgresql+psycopg` (sync driver), KHÔNG phải asyncpg.
> sqlacodegen là tool chạy offline để đọc schema — nó dùng sync connection.

### Cài đặt (nếu chưa có)

```bash
cd backend/
source venv/bin/activate
pip install sqlacodegen psycopg2-binary
# hoặc: pip install sqlacodegen "psycopg[binary]"
```

### Lệnh chạy (template)

```bash
python -m sqlacodegen \
  postgresql+psycopg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB} \
  --schema public \
  --outfile app/db/models/database.py
```

### Lệnh thực tế cho project này

```bash
cd backend/
source venv/bin/activate

python -m sqlacodegen \
  postgresql+psycopg://postgres:password@127.0.0.1:5432/myapp_db \
  --schema public \
  --outfile app/db/models/database.py
```

> [!NOTE]
> Thay `postgres:password` bằng thông tin từ `.env` hoặc `docker-compose.yml`.
> Xem DB credentials tại: `backend/docker-compose.yml` → `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`

---

## Step 4: Chạy fix_sqlacodegen_models.py

Script này tự động fix các vấn đề sqlacodegen sinh ra:

| Vấn đề | Fix |
|---|---|
| Class kế thừa sai parent | → đổi về `Base` |
| `ForeignKeyConstraint` bị indent sai | → fix indent |
| Thiếu `relationship()` | → inject tự động với `back_populates` |
| UUID columns bị gen là `String(32)` | → đổi về `UUID` type |
| JSONB type hint sai | → đổi về `dict` |
| Thiếu imports | → thêm tự động |

### Chạy lệnh

```bash
cd backend/
source venv/bin/activate

python app/scripts/fix_sqlacodegen_models.py app/db/models/database.py
```

### Output mong đợi

```
🔧 Processing: app/db/models/database.py
  ⚙️  Fixing imports...
  ⚙️  Fixing indented constraints...
  ⚙️  Fixing class inheritance...
  ⚙️  Fixing UUID columns...
  ⚙️  Fixing ARRAY columns...
  ⚙️  Fixing JSONB columns...
  ⚙️  Injecting relationships...
  ⚙️  Adding summary comment...
✅ Done → app/db/models/database.py
```

---

## Step 5: Tích Hợp Vào Project

### 5a. Tạo thư mục models nếu chưa có

```
backend/app/db/models/
    __init__.py
    database.py     ← file được gen
```

### 5b. Cập nhật alembic/env.py

```python
# alembic/env.py — thêm import models mới
from app.db.models.database import *  # noqa: F401, F403
# HOẶC import cụ thể từng class:
from app.db.models.database import User, DriverProfile, CustomerProfile  # noqa
```

### 5c. Cập nhật app/db/base.py nếu cần

```python
# Nếu database.py dùng Base riêng, import lại:
from app.db.models.database import Base  # noqa
```

### 5d. Kiểm tra bằng lệnh

```bash
cd backend/
source venv/bin/activate

# Kiểm tra Alembic nhận models
alembic check

# Nếu có diff → generate migration
alembic revision --autogenerate -m "sync_from_sqlacodegen"
alembic upgrade head
```

---

## One-liner Full Workflow (Copy & Run)

```bash
#!/bin/bash
# ============================================================
# Full DB Schema Sync Workflow
# ============================================================
set -e

DB_URL="postgresql+psycopg://postgres:password@127.0.0.1:5432/myapp_db"
SCHEMA_FILE="app/scripts/mobility_schema.sql"
OUTPUT_FILE="app/db/models/database.py"
FIX_SCRIPT="app/scripts/fix_sqlacodegen_models.py"

cd backend/
source venv/bin/activate

echo "📐 Step 1: Apply SQL schema..."
psql "${DB_URL/postgresql+psycopg/postgresql}" -f "$SCHEMA_FILE"

echo "🔄 Step 2: Running sqlacodegen..."
mkdir -p app/db/models
touch app/db/models/__init__.py
python -m sqlacodegen "$DB_URL" --schema public --outfile "$OUTPUT_FILE"

echo "🔧 Step 3: Fixing generated models..."
python "$FIX_SCRIPT" "$OUTPUT_FILE"

echo "✅ Done! Models at: $OUTPUT_FILE"
```

---

## Cấu Trúc File Output Sau Khi Fix

```
backend/
└── app/
    ├── db/
    │   ├── base.py           ← DeclarativeBase gốc
    │   ├── session.py        ← AsyncEngine + get_db()
    │   └── models/
    │       ├── __init__.py
    │       └── database.py   ← Generated + Fixed models
    │
    └── scripts/
        ├── mobility_schema.sql         ← DDL schema source of truth
        └── fix_sqlacodegen_models.py   ← Auto-fix script
```

---

## Troubleshooting

### ❌ `ModuleNotFoundError: No module named 'sqlacodegen'`
```bash
pip install sqlacodegen "psycopg[binary]"
```

### ❌ `connection refused` khi chạy sqlacodegen
```bash
# Kiểm tra Docker đang chạy
docker compose ps
docker compose up -d db
```

### ❌ `extension "uuid-ossp" does not exist`
```bash
psql ... -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
```

### ❌ `extension "postgis" does not exist`
```bash
# docker-compose.yml phải dùng image pgvector/pgvector hoặc postgis/postgis
# image: postgis/postgis:16-3.4
```

### ❌ sqlacodegen tạo class kế thừa sai (không phải Base)
→ Đây là lý do phải chạy `fix_sqlacodegen_models.py` ở Step 4.

### ❌ Relationships thiếu `back_populates` → Alembic error
→ Script đã xử lý tự động. Nếu vẫn lỗi, kiểm tra class name mapping trong script.

---

## Notes Quan Trọng

> [!WARNING]
> **KHÔNG commit file `database.py` vào git nếu nó chứa connection strings.**
> File này là generated artifact. Source of truth là `mobility_schema.sql`.

> [!TIP]
> Với team lớn, nên maintain cả hai:
> - `mobility_schema.sql` — DDL source of truth (commit)
> - Alembic migrations — incremental changes (commit)
> - `database.py` từ sqlacodegen — chỉ dùng để tham khảo hoặc bootstrap

> [!NOTE]
> sqlacodegen không support async. Models được gen là sync-style nhưng
> hoàn toàn tương thích khi dùng với AsyncSession của SQLAlchemy 2.0.
