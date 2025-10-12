"""Properly update discount field in sales_transactions table

Revision ID: 20251011_190000
Revises: 20251011_170000
Create Date: 2025-10-11 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251011_190000'
down_revision = '20251011_170000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Ensure discount column has proper default and handle existing NULL values."""
    # Check if column exists and set default values for any NULL entries
    # First update any NULL values to 0.0
    op.execute("UPDATE sales_transactions SET discount = 0.0 WHERE discount IS NULL")
    
    # Then ensure the column has the proper default and is NOT NULL
    op.alter_column('sales_transactions', 'discount',
                    server_default='0.0')
    
    # Ensure it's NOT NULL after setting all values
    op.alter_column('sales_transactions', 'discount',
                    nullable=False)


def downgrade() -> None:
    """Revert discount column changes."""
    op.alter_column('sales_transactions', 'discount',
                    nullable=True,
                    server_default=None)