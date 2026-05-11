"""session_device_token_oauth_indexes

Revision ID: 4173551e6754
Revises:
Create Date: 2026-05-08

Thay đổi:
  1. sessions: thêm device_token + push_provider (chuyển từ users)
  2. sessions: thêm UNIQUE constraint trên refresh_token_hash
  3. sessions: thêm partial index idx_sessions_active (WHERE revoked_at IS NULL)
  4. users: xóa device_token + device_platform (đã chuyển sang sessions)
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4173551e6754'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. sessions: thêm device_token + push_provider ────────────────────────
    op.add_column(
        'sessions',
        sa.Column('device_token', sa.Text(), nullable=True,
                  comment='FCM (Android/Web) hoặc APNS (iOS) push token'),
        schema='public',
    )
    op.add_column(
        'sessions',
        sa.Column('push_provider', sa.String(10), nullable=True,
                  comment='FCM | APNS | None'),
        schema='public',
    )

    # ── 2. sessions: unique constraint trên refresh_token_hash ─────────────────
    op.create_unique_constraint(
        'sessions_refresh_token_hash_key',
        'sessions',
        ['refresh_token_hash'],
        schema='public',
    )

    # ── 3. sessions: partial index cho active sessions (WHERE revoked_at IS NULL)
    op.create_index(
        'idx_sessions_active',
        'sessions',
        ['user_id'],
        unique=False,
        schema='public',
        postgresql_where=sa.text('revoked_at IS NULL'),
    )

    # ── 4. users: xóa device_token + device_platform ──────────────────────────
    # (đã chuyển xuống sessions để hỗ trợ multi-device push notification)
    # user_with_roles view phụ thuộc vào device_platform → drop view trước
    op.execute("DROP VIEW IF EXISTS public.user_with_roles")
    op.drop_column('users', 'device_token', schema='public')
    op.drop_column('users', 'device_platform', schema='public')
    # Tái tạo view không có device_platform
    op.execute("""
        CREATE OR REPLACE VIEW public.user_with_roles AS
        SELECT
            u.id,
            u.email,
            u.phone,
            u.full_name,
            u.status,
            u.is_verified,
            u.avatar_url,
            array_agg(r.name) FILTER (WHERE r.name IS NOT NULL) AS roles,
            u.created_at,
            u.last_login_at
        FROM public.users u
        LEFT JOIN public.user_roles ur ON ur.user_id = u.id AND ur.is_active = true
        LEFT JOIN public.roles r ON r.id = ur.role_id
        GROUP BY u.id
    """)


def downgrade() -> None:
    # ── Undo theo thứ tự ngược lại ────────────────────────────────────────────

    # 4. Khôi phục users columns
    op.add_column(
        'users',
        sa.Column('device_platform', sa.String(10), nullable=True),
        schema='public',
    )
    op.add_column(
        'users',
        sa.Column('device_token', sa.Text(), nullable=True),
        schema='public',
    )

    # 3. Xóa partial index
    op.drop_index('idx_sessions_active', table_name='sessions', schema='public')

    # 2. Xóa unique constraint
    op.drop_constraint(
        'sessions_refresh_token_hash_key',
        'sessions',
        type_='unique',
        schema='public',
    )

    # 1. Xóa sessions columns
    op.drop_column('sessions', 'push_provider', schema='public')
    op.drop_column('sessions', 'device_token', schema='public')
