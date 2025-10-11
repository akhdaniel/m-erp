"""Add discount_code and discount_reason columns to sales_transactions table

Revision ID: 20251011_160000
Revises: 20251011_150000
Create Date: 2025-10-11 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251011_160000'
down_revision = '20251011_150000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add discount_code and discount_reason columns to sales_transactions table."""
    # Add discount_code column
    op.add_column('sales_transactions', sa.Column('discount_code', sa.String(50), nullable=True))
    
    # Create index for discount_code column
    op.create_index('ix_sales_transactions_discount_code', 'sales_transactions', ['discount_code'])
    
    # Add discount_reason column
    op.add_column('sales_transactions', sa.Column('discount_reason', sa.String(255), nullable=True))


def downgrade() -> None:
    """Remove discount_code and discount_reason columns from sales_transactions table."""
    op.drop_index('ix_sales_transactions_discount_code', table_name='sales_transactions')
    op.drop_column('sales_transactions', 'discount_reason')
    op.drop_column('sales_transactions', 'discount_code')