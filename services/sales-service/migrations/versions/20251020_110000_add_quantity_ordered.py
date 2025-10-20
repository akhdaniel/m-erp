"""Add quantity_ordered field to sales_orders table

Revision ID: 20251020_110000
Revises: 20251014_170000
Create Date: 2025-10-14 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251020_110000'
down_revision = '20251014_170000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add quantity_ordered column to sales_orders table."""
    # Add due_date column to sales_orders table
    op.add_column('sales_orders', sa.Column('quantity_ordered', sa.DateTime(), nullable=True, index=True))

def downgrade() -> None:
    """Remove quantity_ordered column from sales_orders table."""
    op.drop_column('sales_orders', 'quantity_ordered')
