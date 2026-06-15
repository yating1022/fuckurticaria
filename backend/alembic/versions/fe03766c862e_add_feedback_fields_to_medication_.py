"""add feedback fields to medication_records

Revision ID: fe03766c862e
Revises: c3cab457301a
Create Date: 2026-06-10 09:50:22.889716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'fe03766c862e'
down_revision: Union[str, Sequence[str], None] = 'c3cab457301a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('medication_records', sa.Column('effectiveness', sa.SmallInteger(), nullable=True))
    op.add_column('medication_records', sa.Column('side_effects', sa.JSON(), nullable=True))
    op.add_column('medication_records', sa.Column('feedback_note', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('medication_records', 'feedback_note')
    op.drop_column('medication_records', 'side_effects')
    op.drop_column('medication_records', 'effectiveness')
