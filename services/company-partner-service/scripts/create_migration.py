#!/usr/bin/env python3
"""
Script to create the initial database migration.
This script creates the migration file with all tables defined in our models.
"""

import os
from datetime import datetime

# Get current timestamp for migration filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
migration_filename = f"{timestamp}_create_initial_tables.py"
migration_path = f"migrations/versions/{migration_filename}"

# Migration content based on our database schema specification
migration_content = f'''"""Create initial tables

Revision ID: {timestamp[:10]}001
Revises: 
Create Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '{timestamp[:10]}001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('legal_name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('tax_id', sa.String(length=100), nullable=True),
        sa.Column('street', sa.Text(), nullable=True),
        sa.Column('street2', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('zip', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True, default='USD'),
        sa.Column('timezone', sa.String(length=50), nullable=True, default='UTC'),
        sa.Column('logo_url', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.CheckConstraint('LENGTH(code) >= 2', name='companies_code_check'),
        sa.CheckConstraint('LENGTH(name) >= 1', name='companies_name_check')
    )
    op.create_index(op.f('ix_companies_code'), 'companies', ['code'], unique=False)
    op.create_index(op.f('ix_companies_is_active'), 'companies', ['is_active'], unique=False)

    # Create company_users table
    op.create_table(
        'company_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, default='user'),
        sa.Column('is_default_company', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'user_id', name='company_users_unique'),
        sa.CheckConstraint("role IN ('admin', 'manager', 'user', 'viewer')", name='company_users_role_check')
    )
    op.create_index(op.f('ix_company_users_company_id'), 'company_users', ['company_id'], unique=False)
    op.create_index(op.f('ix_company_users_user_id'), 'company_users', ['user_id'], unique=False)

    # Create partners table
    op.create_table(
        'partners',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=True),
        sa.Column('partner_type', sa.String(length=20), nullable=False, default='customer'),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('mobile', sa.String(length=50), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('tax_id', sa.String(length=100), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('parent_partner_id', sa.Integer(), nullable=True),
        sa.Column('is_company', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_customer', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_supplier', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_vendor', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_partner_id'], ['partners.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'code', name='partners_company_code_unique'),
        sa.CheckConstraint("partner_type IN ('customer', 'supplier', 'vendor', 'both')", name='partners_type_check'),
        sa.CheckConstraint('LENGTH(name) >= 1', name='partners_name_check')
    )
    op.create_index(op.f('ix_partners_company_id'), 'partners', ['company_id'], unique=False)
    op.create_index(op.f('ix_partners_partner_type'), 'partners', ['partner_type'], unique=False)
    op.create_index(op.f('ix_partners_is_active'), 'partners', ['is_active'], unique=False)
    op.create_index(op.f('ix_partners_parent_partner_id'), 'partners', ['parent_partner_id'], unique=False)

    # Create partner_contacts table
    op.create_table(
        'partner_contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('partner_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('mobile', sa.String(length=50), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, default=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['partner_id'], ['partners.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('LENGTH(name) >= 1', name='partner_contacts_name_check')
    )
    op.create_index(op.f('ix_partner_contacts_partner_id'), 'partner_contacts', ['partner_id'], unique=False)
    op.create_index(op.f('ix_partner_contacts_is_primary'), 'partner_contacts', ['is_primary'], unique=False)

    # Create partner_addresses table
    op.create_table(
        'partner_addresses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('partner_id', sa.Integer(), nullable=False),
        sa.Column('address_type', sa.String(length=20), nullable=False, default='default'),
        sa.Column('street', sa.Text(), nullable=False),
        sa.Column('street2', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('zip', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['partner_id'], ['partners.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("address_type IN ('default', 'billing', 'shipping', 'other')", name='partner_addresses_type_check')
    )
    op.create_index(op.f('ix_partner_addresses_partner_id'), 'partner_addresses', ['partner_id'], unique=False)
    op.create_index(op.f('ix_partner_addresses_address_type'), 'partner_addresses', ['address_type'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('partner_addresses')
    op.drop_table('partner_contacts')
    op.drop_table('partners')
    op.drop_table('company_users')
    op.drop_table('companies')
'''

# Create the migration file
os.makedirs("migrations/versions", exist_ok=True)
with open(migration_path, 'w') as f:
    f.write(migration_content)

print(f"✅ Created migration file: {migration_path}")
print(f"Migration revision: {timestamp[:10]}001")
print()
print("To apply the migration:")
print("  docker exec -it company-partner-service alembic upgrade head")
print()
print("To verify the migration:")
print("  docker exec -it company-partner-service python verify_setup.py")