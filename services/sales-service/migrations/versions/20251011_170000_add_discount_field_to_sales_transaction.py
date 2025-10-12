"""Add discount field to sales_transactions table

Revision ID: 20251011_170000
Revises: 20251011_160000
Create Date: 2025-10-11 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251011_170000'
down_revision = '20251011_160000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add discount column to sales_transactions table."""
    # Add discount column
    op.add_column('sales_transactions', sa.Column('discount', sa.Numeric(15, 2), nullable=True, default=0.0))


def downgrade() -> None:
    """Remove discount column from sales_transactions table."""
    op.drop_column('sales_transactions', 'discount')