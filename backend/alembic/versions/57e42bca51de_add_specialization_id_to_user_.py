"""add_specialization_id_to_user_specializations

Revision ID: 57e42bca51de
Revises: 71c7e1bc4b90
Create Date: 2026-05-09 21:27:06.096716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '57e42bca51de'
down_revision: Union[str, Sequence[str], None] = '71c7e1bc4b90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Clear invalid data in user_specializations first
    op.execute("DELETE FROM public.user_specializations")

    # 2. Update user_specializations table
    op.add_column('user_specializations', sa.Column('specialization_id', sa.Uuid(), nullable=False), schema='public')
    op.create_foreign_key(
        'user_specializations_spec_id_fkey',
        'user_specializations', 'specializations_reference',
        ['specialization_id'], ['id'],
        source_schema='public', referent_schema='public',
        ondelete='CASCADE'
    )
    op.drop_column('user_specializations', 'name', schema='public')

    # 3. Update users table (drop obsolete columns)
    op.drop_column('users', 'specialization', schema='public')
    op.drop_column('users', 'education_level', schema='public')
    op.drop_column('users', 'skills', schema='public')


def downgrade() -> None:
    # 1. Restore columns to users table
    op.add_column('users', sa.Column('specialization', sa.String(100), nullable=True), schema='public')
    op.add_column('users', sa.Column('education_level', sa.String(50), nullable=True), schema='public')
    op.add_column('users', sa.Column('skills', postgresql.JSONB, server_default='[]', nullable=True), schema='public')

    # 2. Restore columns to user_specializations table
    op.add_column('user_specializations', sa.Column('name', sa.String(100), nullable=False), schema='public')
    op.drop_constraint('user_specializations_spec_id_fkey', 'user_specializations', schema='public', type_='foreignkey')
    op.drop_column('user_specializations', 'specialization_id', schema='public')
