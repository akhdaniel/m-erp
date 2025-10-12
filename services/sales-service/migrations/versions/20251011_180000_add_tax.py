"""Add tax,total field to sales_transactions table

Revision ID: 20251011_180000
Revises: 20251011_170000
Create Date: 2025-10-11 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251011_180000'
down_revision = '20251011_170000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add tax,total column to sales_transactions table."""
    # Add tax,total column
    op.add_column('sales_transactions', sa.Column('tax', sa.Numeric(15, 2), nullable=True, default=0.0))
    op.add_column('sales_transactions', sa.Column('total', sa.Numeric(15, 2), nullable=True, default=0.0))
    op.add_column('sales_transactions', sa.Column('shipping', sa.Numeric(15, 2), nullable=True, default=0.0))


def downgrade() -> None:
    """Remove tax,total column from sales_transactions table."""
    op.drop_column('sales_transactions', 'tax')
    op.drop_column('sales_transactions', 'total')
    op.drop_column('sales_transactions', 'shipping')