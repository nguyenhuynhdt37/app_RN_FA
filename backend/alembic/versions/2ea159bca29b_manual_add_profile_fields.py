"""manual_add_profile_fields

Revision ID: 2ea159bca29b
Revises: 24ff1e653e5c
Create Date: 2026-05-09 16:42:59.551900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2ea159bca29b'
down_revision: Union[str, Sequence[str], None] = '4173551e6754'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add new columns to users table"""
    op.add_column('users', sa.Column('username', sa.String(length=50), nullable=True), schema='public')
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True), schema='public')
    op.add_column('users', sa.Column('is_profile_completed', sa.Boolean(), server_default=sa.text('false'), nullable=False), schema='public')
    op.add_column('users', sa.Column('specialization', sa.String(length=100), nullable=True), schema='public')
    op.add_column('users', sa.Column('education_level', sa.String(length=50), nullable=True), schema='public')
    op.add_column('users', sa.Column('learning_goals', sa.Text(), nullable=True), schema='public')
    op.add_column('users', sa.Column('skills', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=True), schema='public')
    op.add_column('users', sa.Column('interests', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=True), schema='public')
    op.add_column('users', sa.Column('daily_goal_minutes', sa.Integer(), server_default=sa.text('30'), nullable=False), schema='public')
    op.add_column('users', sa.Column('preferred_learning_style', sa.String(length=20), nullable=True), schema='public')
    op.add_column('users', sa.Column('social_links', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=True), schema='public')
    
    # Add unique constraint for username
    op.create_unique_constraint('users_username_key', 'users', ['username'], schema='public')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('users_username_key', 'users', schema='public', type_='unique')
    op.drop_column('users', 'social_links', schema='public')
    op.drop_column('users', 'preferred_learning_style', schema='public')
    op.drop_column('users', 'daily_goal_minutes', schema='public')
    op.drop_column('users', 'interests', schema='public')
    op.drop_column('users', 'skills', schema='public')
    op.drop_column('users', 'learning_goals', schema='public')
    op.drop_column('users', 'education_level', schema='public')
    op.drop_column('users', 'specialization', schema='public')
    op.drop_column('users', 'is_profile_completed', schema='public')
    op.drop_column('users', 'bio', schema='public')
    op.drop_column('users', 'username', schema='public')
