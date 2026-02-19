"""Expand username length

Revision ID: 3c7b1f2a9d4e
Revises: 9a3c8b2f7d1e
Create Date: 2026-02-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3c7b1f2a9d4e'
down_revision: Union[str, Sequence[str], None] = '9a3c8b2f7d1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'users',
        'username',
        existing_type=sa.String(length=15),
        type_=sa.String(length=30),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'users',
        'username',
        existing_type=sa.String(length=30),
        type_=sa.String(length=15),
        existing_nullable=False,
    )
