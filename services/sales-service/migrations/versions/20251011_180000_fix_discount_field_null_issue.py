"""Fix discount field in sales_transactions table - handle existing data

Revision ID: 20251011_180000
Revises: 20251011_170000
Create Date: 2025-10-11 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = '20251011_180000'
down_revision = '20251011_170000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Fix discount column in sales_transactions table to handle existing data properly."""
    # First, try to add the column if it doesn't exist (in case previous migration failed)
    # But make it nullable initially to avoid NOT NULL constraint issues
    try:
        # Check if column exists by trying to add it with a default and make it nullable
        op.add_column('sales_transactions', sa.Column('discount', sa.Numeric(15, 2), nullable=True, default=0.0))
    except:
        # If column already exists, continue
        pass
    
    # Update existing records to set discount to 0.0 where it's NULL
    # Define the table for bulk update
    sales_transactions_table = sa.table('sales_transactions',
        sa.column('discount', sa.Numeric(15, 2))
    )
    
    # Update any NULL values to 0.0
    op.execute(
        sales_transactions_table.update()
        .where(sales_transactions_table.c.discount.is_(None))
        .values(discount=0.0)
    )
    
    # Now alter the column to have a default of 0.0 and be NOT NULL
    op.alter_column('sales_transactions', 'discount',
                    nullable=False,
                    server_default='0.0')


def downgrade() -> None:
    """Remove discount column from sales_transactions table."""
    op.drop_column('sales_transactions', 'discount')