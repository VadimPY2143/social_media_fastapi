"""Add CASCADE delete to comments post_id foreign key

Revision ID: cascade_delete_comments
Revises: 6bb335988390
Create Date: 2025-01-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cascade_delete_comments'
down_revision = '6bb335988390'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the old foreign key constraint
    op.drop_constraint('comments_ibfk_1', 'comments', type_='foreignkey')
    
    # Add the new one with CASCADE delete
    op.create_foreign_key(
        'comments_ibfk_1',
        'comments',
        'posts',
        ['post_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Drop the CASCADE foreign key
    op.drop_constraint('comments_ibfk_1', 'comments', type_='foreignkey')
    
    # Restore the old one without CASCADE
    op.create_foreign_key(
        'comments_ibfk_1',
        'comments',
        'posts',
        ['post_id'],
        ['id']
    )
