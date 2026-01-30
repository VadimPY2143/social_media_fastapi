"""change picture to MEDIUMBLOB

Revision ID: 9e979599e75b
Revises: cascade_delete_comments
Create Date: 2026-01-20 16:03:32.860882

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e979599e75b'
down_revision: Union[str, Sequence[str], None] = 'cascade_delete_comments'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
