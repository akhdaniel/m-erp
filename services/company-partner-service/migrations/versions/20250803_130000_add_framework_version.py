"""Add framework_version column to companies and partners tables

Revision ID: 20250803_130000
Revises: 20250803_095110
Create Date: 2025-08-03 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250803_130000'
down_revision = '20250803_095110'
branch_labels = None
depends_on = None


def upgrade():
    """Add framework_version column to existing tables."""
    # Add framework_version to companies table
    op.add_column('companies', 
        sa.Column('framework_version', sa.String(20), 
                 nullable=False, server_default='1.0.0'))
    
    # Add framework_version to partners table  
    op.add_column('partners',
        sa.Column('framework_version', sa.String(20),
                 nullable=False, server_default='1.0.0'))


def downgrade():
    """Remove framework_version columns."""
    # Remove framework_version from partners table
    op.drop_column('partners', 'framework_version')
    
    # Remove framework_version from companies table
    op.drop_column('companies', 'framework_version')