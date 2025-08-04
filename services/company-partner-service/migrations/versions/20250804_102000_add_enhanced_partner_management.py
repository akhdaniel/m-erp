"""Add enhanced partner management tables

Revision ID: 20250804_102000
Revises: 20250803_130000
Create Date: 2025-08-04 10:20:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250804_102000'
down_revision = '20250803_130000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create partner_categories table
    op.create_table(
        'partner_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('parent_category_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('framework_version', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_category_id'], ['partner_categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'code', name='partner_categories_company_code_unique'),
        sa.UniqueConstraint('company_id', 'name', name='partner_categories_company_name_unique'),
        sa.CheckConstraint('LENGTH(name) >= 1', name='partner_categories_name_check'),
        sa.CheckConstraint('LENGTH(code) >= 1', name='partner_categories_code_check'),
        sa.CheckConstraint("color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'", name='partner_categories_color_check')
    )
    op.create_index(op.f('ix_partner_categories_company_id'), 'partner_categories', ['company_id'], unique=False)
    op.create_index(op.f('ix_partner_categories_parent_category_id'), 'partner_categories', ['parent_category_id'], unique=False)
    op.create_index(op.f('ix_partner_categories_is_active'), 'partner_categories', ['is_active'], unique=False)

    # Create partner_communications table
    op.create_table(
        'partner_communications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('partner_id', sa.Integer(), nullable=False),
        sa.Column('partner_contact_id', sa.Integer(), nullable=True),
        sa.Column('communication_type', sa.String(length=50), nullable=False, default='email'),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('direction', sa.String(length=20), nullable=False, default='outbound'),
        sa.Column('initiated_by', sa.String(length=255), nullable=True),
        sa.Column('participants', sa.Text(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('priority', sa.String(length=20), nullable=False, default='normal'),
        sa.Column('outcome', sa.String(length=100), nullable=True),
        sa.Column('follow_up_required', sa.Boolean(), nullable=False, default=False),
        sa.Column('follow_up_date', sa.DateTime(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('attachments_count', sa.Integer(), nullable=False, default=0),
        sa.Column('external_reference', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['partner_id'], ['partners.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['partner_contact_id'], ['partner_contacts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint(
            "communication_type IN ('email', 'phone', 'meeting', 'video_call', 'letter', 'fax', 'text', 'other')",
            name='partner_communications_type_check'
        ),
        sa.CheckConstraint(
            "direction IN ('inbound', 'outbound')",
            name='partner_communications_direction_check'
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'cancelled', 'failed')",
            name='partner_communications_status_check'
        ),
        sa.CheckConstraint(
            "priority IN ('low', 'normal', 'high', 'urgent')",
            name='partner_communications_priority_check'
        ),
        sa.CheckConstraint('LENGTH(subject) >= 1', name='partner_communications_subject_check')
    )
    op.create_index(op.f('ix_partner_communications_partner_id'), 'partner_communications', ['partner_id'], unique=False)
    op.create_index(op.f('ix_partner_communications_partner_contact_id'), 'partner_communications', ['partner_contact_id'], unique=False)
    op.create_index(op.f('ix_partner_communications_communication_type'), 'partner_communications', ['communication_type'], unique=False)
    op.create_index(op.f('ix_partner_communications_direction'), 'partner_communications', ['direction'], unique=False)
    op.create_index(op.f('ix_partner_communications_scheduled_at'), 'partner_communications', ['scheduled_at'], unique=False)
    op.create_index(op.f('ix_partner_communications_completed_at'), 'partner_communications', ['completed_at'], unique=False)
    op.create_index(op.f('ix_partner_communications_status'), 'partner_communications', ['status'], unique=False)
    op.create_index(op.f('ix_partner_communications_priority'), 'partner_communications', ['priority'], unique=False)
    op.create_index(op.f('ix_partner_communications_follow_up_date'), 'partner_communications', ['follow_up_date'], unique=False)

    # Add category_id column to partners table
    op.add_column('partners', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_partners_category_id', 'partners', 'partner_categories', ['category_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_partners_category_id'), 'partners', ['category_id'], unique=False)


def downgrade() -> None:
    # Remove category_id column from partners table
    op.drop_index(op.f('ix_partners_category_id'), table_name='partners')
    op.drop_constraint('fk_partners_category_id', 'partners', type_='foreignkey')
    op.drop_column('partners', 'category_id')
    
    # Drop partner_communications table
    op.drop_table('partner_communications')
    
    # Drop partner_categories table
    op.drop_table('partner_categories')