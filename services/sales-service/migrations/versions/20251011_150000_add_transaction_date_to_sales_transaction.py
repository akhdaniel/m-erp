"""Add transaction_date column to sales_transactions table

Revision ID: 20251011_150000
Revises: 20250919_130000
Create Date: 2025-10-11 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251011_150000'
down_revision = '20250919_130000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add transaction_date column to sales_transactions table."""
    op.add_column('sales_transactions', sa.Column('transaction_date', sa.DateTime(), nullable=True))
    
    # Create index for the new column
    op.create_index('ix_sales_transactions_transaction_date', 'sales_transactions', ['transaction_date'])


def downgrade() -> None:
    """Remove transaction_date column from sales_transactions table."""
    op.drop_index('ix_sales_transactions_transaction_date', table_name='sales_transactions')
    op.drop_column('sales_transactions', 'transaction_date')