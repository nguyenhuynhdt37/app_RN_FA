"""add_user_specializations_and_references

Revision ID: 71c7e1bc4b90
Revises: 2ea159bca29b
Create Date: 2026-05-09 18:46:09.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '71c7e1bc4b90'
down_revision: Union[str, Sequence[str], None] = '2ea159bca29b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Specializations Reference
    op.create_table(
        'specializations_reference',
        sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=False),
        sa.Column('name_vi', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='specializations_reference_pkey'),
        sa.UniqueConstraint('code', name='specializations_reference_code_key'),
        schema='public'
    )

    # 2. Skills Reference
    op.create_table(
        'skills_reference',
        sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('specialization_id', sa.Uuid(), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=False),
        sa.Column('name_vi', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.ForeignKeyConstraint(['specialization_id'], ['public.specializations_reference.id'], name='skills_reference_specialization_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='skills_reference_pkey'),
        schema='public'
    )
    op.create_index('idx_skills_ref_specialization', 'skills_reference', ['specialization_id'], schema='public')

    # 3. Interests Reference
    op.create_table(
        'interests_reference',
        sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name_en', sa.String(length=100), nullable=False),
        sa.Column('name_vi', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='interests_reference_pkey'),
        schema='public'
    )

    # 4. User Specializations (Already defined in models but table missing)
    op.create_table(
        'user_specializations',
        sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('level', sa.String(length=50), nullable=False),
        sa.Column('skills', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['public.users.id'], name='user_specializations_user_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='user_specializations_pkey'),
        schema='public'
    )
    op.create_index('idx_user_specializations_user_id', 'user_specializations', ['user_id'], schema='public')


def downgrade() -> None:
    op.drop_table('user_specializations', schema='public')
    op.drop_table('interests_reference', schema='public')
    op.drop_table('skills_reference', schema='public')
    op.drop_table('specializations_reference', schema='public')
