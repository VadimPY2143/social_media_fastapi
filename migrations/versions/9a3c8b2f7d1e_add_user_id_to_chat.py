"""Add user_id to chat table

Revision ID: 9a3c8b2f7d1e
Revises: 6f2c3e0b5c2a
Create Date: 2026-02-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9a3c8b2f7d1e'
down_revision: Union[str, Sequence[str], None] = '6f2c3e0b5c2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chat', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(
        'fk_chat_user_id',
        'chat',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('fk_chat_user_id', 'chat', type_='foreignkey')
    op.drop_column('chat', 'user_id')
