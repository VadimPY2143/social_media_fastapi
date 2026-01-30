"""added reply comment table

Revision ID: fa0837a1ed09
Revises: 851fc3b98c3a
Create Date: 2026-01-20 16:29:22.868899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa0837a1ed09'
down_revision: Union[str, Sequence[str], None] = '851fc3b98c3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
