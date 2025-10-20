"""Add quantity_ordered field to sales_order_line_items table

Revision ID: 20251020_150000
Revises: 20251020_140000
Create Date: 2025-10-14 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251020_150000'
down_revision = '20251020_140000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add quantity_ordered column to sales_order_line_items table."""
    # Add due_date column to sales_order_line_items table
    op.add_column('sales_order_line_items', sa.Column('warehouse_id', sa.Integer(), nullable=True, index=True))
    op.add_column('sales_order_line_items', sa.Column('reserved_quantity', sa.Numeric(), nullable=True, ))
    op.add_column('sales_order_line_items', sa.Column('reserved_quantity', sa.Numeric(), nullable=True, ))
    op.add_column('sales_order_line_items', sa.Column('allocated_quantity', sa.Numeric(), nullable=True, ))
    op.add_column('sales_order_line_items', sa.Column('required_date', sa.DateTime(), nullable=True, ))
    op.add_column('sales_order_line_items', sa.Column('promised_date', sa.DateTime(), nullable=True, ))
    op.add_column('sales_order_line_items', sa.Column('shipped_date', sa.DateTime(), nullable=True, ))
    op.add_column('sales_order_line_items', sa.Column('is_backordered', sa.Boolean(), nullable=True, index=True))
    op.add_column('sales_order_line_items', sa.Column('is_dropship', sa.Boolean(), nullable=True, index=True))
    op.add_column('sales_order_line_items', sa.Column('requires_special_handling', sa.Boolean(), nullable=True, index=True))
    op.add_column('sales_order_line_items', sa.Column('custom_options', sa.JSON(), nullable=True, index=True))

def downgrade() -> None:
    """Remove quantity_ordered column from sales_order_line_items table."""
    op.drop_column('sales_order_line_items', 'warehouse_id')
    op.drop_column('sales_order_line_items', 'reserved_quantity')
    op.drop_column('sales_order_line_items', 'allocated_quantity')
    op.drop_column('sales_order_line_items', 'required_date')
    op.drop_column('sales_order_line_items', 'promised_date')
    op.drop_column('sales_order_line_items', 'shipped_date')
    op.drop_column('sales_order_line_items', 'is_backordered')
    op.drop_column('sales_order_line_items', 'is_dropship')
    op.drop_column('sales_order_line_items', 'requires_special_handling')
    op.drop_column('sales_order_line_items', 'custom_options')
