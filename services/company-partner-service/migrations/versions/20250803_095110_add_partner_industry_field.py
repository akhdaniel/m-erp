"""Add industry field to partners table

Revision ID: 20250803_095110
Revises: 20250801_120000
Create Date: 2025-08-03 09:51:10

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250803_095110'
down_revision = '20250801_120000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add industry column to partners table (if it doesn't already exist)
    # Note: The industry column may already exist from the initial Partner model definition
    # This migration adds it explicitly and ensures the index exists
    
    # Check if column exists before adding
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name='partners' AND column_name='industry'"))
    if not result.fetchone():
        # Add industry column to partners table
        op.add_column('partners', sa.Column('industry', sa.String(100), nullable=True))
    
    # Add index for industry filtering with company_id (if it doesn't already exist)
    try:
        op.create_index('idx_partners_industry', 'partners', ['industry', 'company_id'])
    except sa.exc.OperationalError:
        # Index may already exist, ignore
        pass


def downgrade() -> None:
    # Remove index and column
    try:
        op.drop_index('idx_partners_industry', 'partners')
    except sa.exc.OperationalError:
        # Index may not exist, ignore
        pass
    
    # Check if column exists before dropping
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT column_name FROM information_schema.columns WHERE table_name='partners' AND column_name='industry'"))
    if result.fetchone():
        op.drop_column('partners', 'industry')