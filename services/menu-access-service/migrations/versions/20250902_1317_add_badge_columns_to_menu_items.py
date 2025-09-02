"""add_badge_columns_to_menu_items

Revision ID: c13ab8992f1f
Revises: 0a9c71802b92
Create Date: 2025-09-02 13:17:15.222815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c13ab8992f1f'
down_revision = '0a9c71802b92'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add badge columns to menu_items table
    op.add_column('menu_items', sa.Column('badge_text', sa.String(length=50), nullable=True))
    op.add_column('menu_items', sa.Column('badge_class', sa.String(length=100), nullable=True))


def downgrade() -> None:
    # Remove badge columns from menu_items table
    op.drop_column('menu_items', 'badge_class')
    op.drop_column('menu_items', 'badge_text')