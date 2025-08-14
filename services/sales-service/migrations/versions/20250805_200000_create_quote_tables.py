"""Create quote management tables

Revision ID: 20250805_200000
Revises: 
Create Date: 2025-08-05 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250805_200000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create quote management tables with multi-company isolation."""
    
    # Create quote status enum
    quote_status_enum = postgresql.ENUM(
        'draft', 'pending_approval', 'approved', 'sent', 'accepted', 
        'rejected', 'expired', 'converted', 'cancelled',
        name='quotestatus',
        create_type=False
    )
    quote_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create approval status enum
    approval_status_enum = postgresql.ENUM(
        'pending', 'approved', 'rejected', 'escalated',
        name='approvalstatus',
        create_type=False
    )
    approval_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create line item type enum
    line_item_type_enum = postgresql.ENUM(
        'product', 'service', 'discount', 'shipping', 'tax', 'misc',
        name='lineitemtype',
        create_type=False
    )
    line_item_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Create sales_quotes table
    op.create_table('sales_quotes',
        # Primary key and timestamps
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Multi-company isolation
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('framework_version', sa.String(length=50), nullable=True),
        
        # Basic quote information
        sa.Column('quote_number', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Customer and opportunity references
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('opportunity_id', sa.Integer(), nullable=True),
        
        # Quote status and workflow
        sa.Column('status', quote_status_enum, nullable=False, server_default='draft'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        
        # Financial information
        sa.Column('subtotal', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),
        sa.Column('discount_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),
        sa.Column('shipping_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),
        sa.Column('currency_code', sa.String(length=3), nullable=False, server_default='USD'),
        
        # Pricing and discounts
        sa.Column('overall_discount_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.00'),
        sa.Column('margin_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('total_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        
        # Quote validity and terms
        sa.Column('valid_from', sa.DateTime(), nullable=False),
        sa.Column('valid_until', sa.DateTime(), nullable=False),
        sa.Column('payment_terms_days', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('delivery_terms', sa.String(length=255), nullable=True),
        
        # Quote preparation and sending
        sa.Column('prepared_by_user_id', sa.Integer(), nullable=False),
        sa.Column('approved_by_user_id', sa.Integer(), nullable=True),
        sa.Column('sent_date', sa.DateTime(), nullable=True),
        sa.Column('sent_by_user_id', sa.Integer(), nullable=True),
        
        # Customer response
        sa.Column('customer_response_date', sa.DateTime(), nullable=True),
        sa.Column('customer_response_notes', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.String(length=255), nullable=True),
        
        # Approval workflow
        sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('approval_threshold_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        
        # Conversion information
        sa.Column('converted_to_order_id', sa.Integer(), nullable=True),
        sa.Column('converted_date', sa.DateTime(), nullable=True),
        sa.Column('converted_by_user_id', sa.Integer(), nullable=True),
        
        # Document generation
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('document_url', sa.String(length=500), nullable=True),
        sa.Column('pdf_generated', sa.Boolean(), nullable=False, server_default='false'),
        
        # Communication tracking
        sa.Column('email_sent_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_email_sent', sa.DateTime(), nullable=True),
        sa.Column('viewed_by_customer', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('first_viewed_date', sa.DateTime(), nullable=True),
        sa.Column('last_viewed_date', sa.DateTime(), nullable=True),
        
        # Additional information
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('terms_and_conditions', sa.Text(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        
        # Status tracking
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for sales_quotes
    op.create_index('ix_sales_quotes_id', 'sales_quotes', ['id'])
    op.create_index('ix_sales_quotes_company_id', 'sales_quotes', ['company_id'])
    op.create_index('ix_sales_quotes_quote_number', 'sales_quotes', ['quote_number'], unique=True)
    op.create_index('ix_sales_quotes_customer_id', 'sales_quotes', ['customer_id'])
    op.create_index('ix_sales_quotes_opportunity_id', 'sales_quotes', ['opportunity_id'])
    op.create_index('ix_sales_quotes_status', 'sales_quotes', ['status'])
    op.create_index('ix_sales_quotes_valid_until', 'sales_quotes', ['valid_until'])
    op.create_index('ix_sales_quotes_prepared_by_user_id', 'sales_quotes', ['prepared_by_user_id'])
    op.create_index('ix_sales_quotes_approved_by_user_id', 'sales_quotes', ['approved_by_user_id'])
    op.create_index('ix_sales_quotes_sent_date', 'sales_quotes', ['sent_date'])
    op.create_index('ix_sales_quotes_sent_by_user_id', 'sales_quotes', ['sent_by_user_id'])
    op.create_index('ix_sales_quotes_converted_to_order_id', 'sales_quotes', ['converted_to_order_id'])
    op.create_index('ix_sales_quotes_is_active', 'sales_quotes', ['is_active'])

    # Create sales_quote_line_items table
    op.create_table('sales_quote_line_items',
        # Primary key and timestamps
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Multi-company isolation
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('framework_version', sa.String(length=50), nullable=True),
        
        # Quote reference
        sa.Column('quote_id', sa.Integer(), nullable=False),
        
        # Line identification
        sa.Column('line_number', sa.Integer(), nullable=False),
        
        # Product/service information
        sa.Column('line_type', line_item_type_enum, nullable=False, server_default='product'),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('product_variant_id', sa.Integer(), nullable=True),
        
        # Item details
        sa.Column('item_code', sa.String(length=100), nullable=True),
        sa.Column('item_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Quantity and units
        sa.Column('quantity', sa.Numeric(precision=15, scale=4), nullable=False, server_default='1.0000'),
        sa.Column('unit_of_measure', sa.String(length=50), nullable=False, server_default='each'),
        
        # Pricing
        sa.Column('unit_price', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('list_price', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('unit_cost', sa.Numeric(precision=15, scale=4), nullable=True),
        
        # Discounts
        sa.Column('discount_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.00'),
        sa.Column('discount_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),
        
        # Calculations
        sa.Column('line_total', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('line_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        
        # Tax information
        sa.Column('tax_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.00'),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),
        sa.Column('tax_code', sa.String(length=50), nullable=True),
        
        # Product specifications
        sa.Column('specifications', sa.JSON(), nullable=True),
        sa.Column('custom_options', sa.JSON(), nullable=True),
        
        # Delivery information
        sa.Column('lead_time_days', sa.Integer(), nullable=True),
        sa.Column('delivery_date', sa.DateTime(), nullable=True),
        
        # Pricing rules and promotions
        sa.Column('price_rule_id', sa.Integer(), nullable=True),
        sa.Column('promotion_id', sa.Integer(), nullable=True),
        
        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        
        # Additional attributes
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('custom_attributes', sa.JSON(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['quote_id'], ['sales_quotes.id'], ondelete='CASCADE')
    )
    
    # Create indexes for sales_quote_line_items
    op.create_index('ix_sales_quote_line_items_id', 'sales_quote_line_items', ['id'])
    op.create_index('ix_sales_quote_line_items_company_id', 'sales_quote_line_items', ['company_id'])
    op.create_index('ix_sales_quote_line_items_quote_id', 'sales_quote_line_items', ['quote_id'])
    op.create_index('ix_sales_quote_line_items_line_type', 'sales_quote_line_items', ['line_type'])
    op.create_index('ix_sales_quote_line_items_product_id', 'sales_quote_line_items', ['product_id'])
    op.create_index('ix_sales_quote_line_items_product_variant_id', 'sales_quote_line_items', ['product_variant_id'])
    op.create_index('ix_sales_quote_line_items_item_code', 'sales_quote_line_items', ['item_code'])
    op.create_index('ix_sales_quote_line_items_price_rule_id', 'sales_quote_line_items', ['price_rule_id'])
    op.create_index('ix_sales_quote_line_items_promotion_id', 'sales_quote_line_items', ['promotion_id'])
    op.create_index('ix_sales_quote_line_items_is_active', 'sales_quote_line_items', ['is_active'])

    # Create quote_versions table
    op.create_table('quote_versions',
        # Primary key and timestamps
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Multi-company isolation
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('framework_version', sa.String(length=50), nullable=True),
        
        # Quote reference
        sa.Column('quote_id', sa.Integer(), nullable=False),
        
        # Version information
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('change_reason', sa.String(length=255), nullable=True),
        sa.Column('change_summary', sa.Text(), nullable=True),
        
        # Snapshot data
        sa.Column('quote_data', sa.JSON(), nullable=False),
        sa.Column('line_items_data', sa.JSON(), nullable=True),
        
        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['quote_id'], ['sales_quotes.id'], ondelete='CASCADE')
    )
    
    # Create indexes for quote_versions
    op.create_index('ix_quote_versions_id', 'quote_versions', ['id'])
    op.create_index('ix_quote_versions_company_id', 'quote_versions', ['company_id'])
    op.create_index('ix_quote_versions_quote_id', 'quote_versions', ['quote_id'])
    op.create_index('ix_quote_versions_version_number', 'quote_versions', ['version_number'])
    op.create_index('ix_quote_versions_created_by_user_id', 'quote_versions', ['created_by_user_id'])
    op.create_index('ix_quote_versions_is_active', 'quote_versions', ['is_active'])

    # Create quote_approvals table
    op.create_table('quote_approvals',
        # Primary key and timestamps
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Multi-company isolation
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('framework_version', sa.String(length=50), nullable=True),
        
        # Quote reference
        sa.Column('quote_id', sa.Integer(), nullable=False),
        
        # Approval workflow
        sa.Column('approval_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('requested_by_user_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to_user_id', sa.Integer(), nullable=False),
        
        # Approval request information
        sa.Column('request_date', sa.DateTime(), nullable=False),
        sa.Column('request_reason', sa.Text(), nullable=True),
        sa.Column('urgency_level', sa.String(length=20), nullable=False, server_default='normal'),
        
        # Approval response
        sa.Column('status', approval_status_enum, nullable=False, server_default='pending'),
        sa.Column('response_date', sa.DateTime(), nullable=True),
        sa.Column('response_by_user_id', sa.Integer(), nullable=True),
        sa.Column('response_notes', sa.Text(), nullable=True),
        
        # Escalation information
        sa.Column('escalated_date', sa.DateTime(), nullable=True),
        sa.Column('escalated_to_user_id', sa.Integer(), nullable=True),
        sa.Column('escalation_reason', sa.String(length=255), nullable=True),
        
        # Due dates and SLA
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('sla_hours', sa.Integer(), nullable=False, server_default='24'),
        
        # Approval criteria
        sa.Column('discount_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('quote_total', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('margin_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        
        # Additional information
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        
        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['quote_id'], ['sales_quotes.id'], ondelete='CASCADE')
    )
    
    # Create indexes for quote_approvals
    op.create_index('ix_quote_approvals_id', 'quote_approvals', ['id'])
    op.create_index('ix_quote_approvals_company_id', 'quote_approvals', ['company_id'])
    op.create_index('ix_quote_approvals_quote_id', 'quote_approvals', ['quote_id'])
    op.create_index('ix_quote_approvals_requested_by_user_id', 'quote_approvals', ['requested_by_user_id'])
    op.create_index('ix_quote_approvals_assigned_to_user_id', 'quote_approvals', ['assigned_to_user_id'])
    op.create_index('ix_quote_approvals_request_date', 'quote_approvals', ['request_date'])
    op.create_index('ix_quote_approvals_status', 'quote_approvals', ['status'])
    op.create_index('ix_quote_approvals_response_date', 'quote_approvals', ['response_date'])
    op.create_index('ix_quote_approvals_response_by_user_id', 'quote_approvals', ['response_by_user_id'])
    op.create_index('ix_quote_approvals_escalated_to_user_id', 'quote_approvals', ['escalated_to_user_id'])
    op.create_index('ix_quote_approvals_due_date', 'quote_approvals', ['due_date'])
    op.create_index('ix_quote_approvals_is_active', 'quote_approvals', ['is_active'])


def downgrade() -> None:
    """Drop quote management tables."""
    
    # Drop tables in reverse order (due to foreign key constraints)
    op.drop_table('quote_approvals')
    op.drop_table('quote_versions')
    op.drop_table('sales_quote_line_items')
    op.drop_table('sales_quotes')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS lineitemtype')
    op.execute('DROP TYPE IF EXISTS approvalstatus')
    op.execute('DROP TYPE IF EXISTS quotestatus')