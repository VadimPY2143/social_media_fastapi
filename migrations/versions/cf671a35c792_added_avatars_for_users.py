"""added avatars for users

Revision ID: cf671a35c792
Revises: fa0837a1ed09
Create Date: 2026-01-21 22:23:27.036712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf671a35c792'
down_revision: Union[str, Sequence[str], None] = 'fa0837a1ed09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
