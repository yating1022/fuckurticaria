"""add system_settings and ai_insights tables

Revision ID: 6cb665509021
Revises: cd4ac8289d5d
Create Date: 2026-06-09 18:44:32.788390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cb665509021'
down_revision: Union[str, Sequence[str], None] = 'cd4ac8289d5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'system_settings',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('key', sa.String(100), unique=True, nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.String(200), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'ai_insights',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('insight_type', sa.String(30), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('analysis_range_start', sa.Date(), nullable=True),
        sa.Column('analysis_range_end', sa.Date(), nullable=True),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('ai_insights')
    op.drop_table('system_settings')
