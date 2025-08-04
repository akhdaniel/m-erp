"""Create extension tables for Business Object Framework

Revision ID: 20250801_120000
Revises: 20250730_180400
Create Date: 2025-08-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250801_120000'
down_revision = '20250730_1800'
branch_labels = None
depends_on = None


def upgrade():
    """Create extension system tables."""
    
    # Create business_object_extensions table
    op.create_table(
        'business_object_extensions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False, index=True),
        sa.Column('entity_id', sa.Integer(), nullable=False, index=True),
        sa.Column('field_name', sa.String(length=100), nullable=False, index=True),
        sa.Column('field_type', sa.String(length=50), nullable=False),
        sa.Column('field_value', sa.Text(), nullable=True),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('framework_version', sa.String(length=20), nullable=True, default='1.0.0'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create unique constraint for extensions (one extension per entity/field/company combination)
    op.create_unique_constraint(
        'uq_extensions_entity_field_company',
        'business_object_extensions',
        ['entity_type', 'entity_id', 'field_name', 'company_id']
    )
    
    # Create indexes for common queries
    op.create_index(
        'idx_extensions_entity_company',
        'business_object_extensions',
        ['entity_type', 'entity_id', 'company_id']
    )
    op.create_index(
        'idx_extensions_field_type',
        'business_object_extensions',
        ['field_type']
    )
    op.create_index(
        'idx_extensions_active',
        'business_object_extensions',
        ['is_active']
    )
    
    # Create business_object_validators table
    op.create_table(
        'business_object_validators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False, index=True),
        sa.Column('field_name', sa.String(length=100), nullable=False, index=True),
        sa.Column('validator_type', sa.String(length=50), nullable=False, index=True),
        sa.Column('validator_config', sa.Text(), nullable=False, default='{}'),
        sa.Column('validation_order', sa.Integer(), nullable=False, default=0),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('framework_version', sa.String(length=20), nullable=True, default='1.0.0'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for validators
    op.create_index(
        'idx_validators_entity_field',
        'business_object_validators',
        ['entity_type', 'field_name']
    )
    op.create_index(
        'idx_validators_company',
        'business_object_validators',
        ['company_id']
    )
    op.create_index(
        'idx_validators_type_active',
        'business_object_validators',
        ['validator_type', 'is_active']
    )
    op.create_index(
        'idx_validators_order',
        'business_object_validators',
        ['validation_order']
    )
    
    # Create extension field definitions table (for field metadata)
    op.create_table(
        'business_object_field_definitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False, index=True),
        sa.Column('field_name', sa.String(length=100), nullable=False, index=True),
        sa.Column('field_type', sa.String(length=50), nullable=False),
        sa.Column('field_label', sa.String(length=200), nullable=True),
        sa.Column('field_description', sa.Text(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=False, default=False),
        sa.Column('default_value', sa.Text(), nullable=True),
        sa.Column('field_options', sa.Text(), nullable=True),  # JSON for select options, etc.
        sa.Column('display_order', sa.Integer(), nullable=False, default=0),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('framework_version', sa.String(length=20), nullable=True, default='1.0.0'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create unique constraint for field definitions
    op.create_unique_constraint(
        'uq_field_definitions_entity_field_company',
        'business_object_field_definitions',
        ['entity_type', 'field_name', 'company_id']
    )
    
    # Create indexes for field definitions
    op.create_index(
        'idx_field_definitions_entity_company',
        'business_object_field_definitions',
        ['entity_type', 'company_id']
    )
    op.create_index(
        'idx_field_definitions_active',
        'business_object_field_definitions',
        ['is_active']
    )
    op.create_index(
        'idx_field_definitions_order',
        'business_object_field_definitions',
        ['display_order']
    )


def downgrade():
    """Drop extension system tables."""
    
    # Drop indexes first
    op.drop_index('idx_field_definitions_order', table_name='business_object_field_definitions')
    op.drop_index('idx_field_definitions_active', table_name='business_object_field_definitions')
    op.drop_index('idx_field_definitions_entity_company', table_name='business_object_field_definitions')
    
    op.drop_index('idx_validators_order', table_name='business_object_validators')
    op.drop_index('idx_validators_type_active', table_name='business_object_validators')
    op.drop_index('idx_validators_company', table_name='business_object_validators')
    op.drop_index('idx_validators_entity_field', table_name='business_object_validators')
    
    op.drop_index('idx_extensions_active', table_name='business_object_extensions')
    op.drop_index('idx_extensions_field_type', table_name='business_object_extensions')
    op.drop_index('idx_extensions_entity_company', table_name='business_object_extensions')
    
    # Drop unique constraints
    op.drop_constraint('uq_field_definitions_entity_field_company', 'business_object_field_definitions', type_='unique')
    op.drop_constraint('uq_extensions_entity_field_company', 'business_object_extensions', type_='unique')
    
    # Drop tables
    op.drop_table('business_object_field_definitions')
    op.drop_table('business_object_validators')
    op.drop_table('business_object_extensions')