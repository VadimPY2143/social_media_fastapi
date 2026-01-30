"""change picture to MEDIUMBLOB

Revision ID: 851fc3b98c3a
Revises: 9e979599e75b
Create Date: 2026-01-20 16:04:34.686598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '851fc3b98c3a'
down_revision: Union[str, Sequence[str], None] = '9e979599e75b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
