"""Add source_channel field to sales_orders table

Revision ID: 20251014_170000
Revises: 20251014_160000
Create Date: 2025-10-14 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251014_170000'
down_revision = '20251014_160000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add source_channel column to sales_orders table."""
    # Add due_date column to sales_orders table
    op.add_column('sales_orders', sa.Column('source_channel', sa.DateTime(), nullable=True, index=True))
    op.add_column('sales_orders', sa.Column('carrier_name', sa.Text(), nullable=True, index=True))
    op.add_column('sales_orders', sa.Column('tracking_number', sa.Text(), nullable=True, index=True))
    op.add_column('sales_orders', sa.Column('custom_attributes', sa.JSON(), nullable=True))
    op.add_column('sales_orders', sa.Column('is_priority', sa.Boolean(), nullable=False, default=False))
    op.add_column('sales_orders', sa.Column('requires_approval', sa.Boolean(), nullable=False, default=False))
    op.add_column('sales_orders', sa.Column('is_dropship', sa.Boolean(), nullable=False, default=False))
    op.add_column('sales_orders', sa.Column('special_instructions', sa.Text(), nullable=False, default=False))
    op.add_column('sales_orders', sa.Column('framework_version', sa.String(length=50), nullable=True))

def downgrade() -> None:
    """Remove source_channel column from sales_orders table."""
    op.drop_column('sales_orders', 'source_channel')
    op.drop_column('sales_orders', 'carrier_name')
    op.drop_column('sales_orders', 'tracking_number')
    op.drop_column('sales_orders', 'custom_attributes')
    op.drop_column('sales_orders', 'is_priority')
    op.drop_column('sales_orders', 'requires_approval')
    op.drop_column('sales_orders', 'is_dropship')
    op.drop_column('sales_orders', 'special_instructions')