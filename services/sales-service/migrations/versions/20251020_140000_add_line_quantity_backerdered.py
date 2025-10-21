"""Add quantity_ordered field to sales_order_line_items table

Revision ID: 20251020_140000
Revises: 20251020_130000
Create Date: 2025-10-14 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251020_140000'
down_revision = '20251020_130000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add quantity_ordered column to sales_order_line_items table."""
    # Add due_date column to sales_order_line_items table
    op.add_column('sales_order_line_items', sa.Column('quantity_backordered', sa.Numeric(), nullable=True, index=True))

def downgrade() -> None:
    """Remove quantity_ordered column from sales_order_line_items table."""
    op.drop_column('sales_order_line_items', 'quantity_ordered')
