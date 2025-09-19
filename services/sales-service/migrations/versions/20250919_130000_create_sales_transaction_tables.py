"""Create consolidated sales transaction tables

Revision ID: 20250919_130000
Revises: 20250805_200000
Create Date: 2025-09-19 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250919_130000'
down_revision = '20250805_200000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create consolidated sales transaction tables with multi-company isolation."""
    
    # Create sales transaction state enum
    sales_transaction_state_enum = postgresql.ENUM(
        'draft', 'quote_pending_approval', 'quote_approved', 'quote_sent', 
        'quote_accepted', 'quote_rejected', 'quote_expired', 'order_pending',
        'order_confirmed', 'order_in_production', 'order_ready_to_ship',
        'order_partially_shipped', 'order_shipped', 'order_delivered',
        'order_completed', 'order_cancelled', 'order_on_hold',
        name='salestransactionstate',
        create_type=False
    )
    sales_transaction_state_enum.create(op.get_bind(), checkfirst=True)
    
    # Create payment status enum
    payment_status_enum = postgresql.ENUM(
        'pending', 'authorized', 'partially_paid', 'paid', 
        'overdue', 'refunded', 'cancelled',
        name='paymentstatus',
        create_type=False
    )
    payment_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create line item type enum
    line_item_type_enum = postgresql.ENUM(
        'product', 'service', 'discount', 'shipping', 'tax', 'misc',
        name='lineitemtype',
        create_type=False
    )
    line_item_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Create sales transactions table
    op.create_table('sales_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_user_id', sa.Integer(), nullable=True),
        
        # Basic transaction information
        sa.Column('transaction_number', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Customer and opportunity references
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('opportunity_id', sa.Integer(), nullable=True),
        
        # Transaction state and workflow
        sa.Column('state', sales_transaction_state_enum, nullable=False, default='draft'),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        
        # Financial information
        sa.Column('subtotal', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('discount_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('shipping_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('currency_code', sa.String(length=3), nullable=False, default='USD'),
        
        # Pricing and discounts
        sa.Column('overall_discount_percentage', sa.Numeric(precision=5, scale=2), nullable=False, default=0.0),
        sa.Column('margin_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('total_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        
        # Quotation validity and terms
        sa.Column('valid_from', sa.DateTime(), nullable=False),
        sa.Column('valid_until', sa.DateTime(), nullable=True),
        sa.Column('payment_terms_days', sa.Integer(), nullable=False, default=30),
        sa.Column('delivery_terms', sa.String(length=255), nullable=True),
        
        # Transaction preparation and sending
        sa.Column('prepared_by_user_id', sa.Integer(), nullable=False),
        sa.Column('approved_by_user_id', sa.Integer(), nullable=True),
        sa.Column('sent_date', sa.DateTime(), nullable=True),
        sa.Column('sent_by_user_id', sa.Integer(), nullable=True),
        
        # Customer response
        sa.Column('customer_response_date', sa.DateTime(), nullable=True),
        sa.Column('customer_response_notes', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.String(length=255), nullable=True),
        
        # Approval workflow
        sa.Column('requires_approval', sa.Boolean(), nullable=False, default=False),
        sa.Column('approval_threshold_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        
        # Order-specific information
        sa.Column('order_date', sa.DateTime(), nullable=True),
        sa.Column('required_date', sa.DateTime(), nullable=True),
        sa.Column('promised_date', sa.DateTime(), nullable=True),
        sa.Column('shipped_date', sa.DateTime(), nullable=True),
        sa.Column('delivered_date', sa.DateTime(), nullable=True),
        
        # Payment information
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('paid_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('outstanding_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('payment_status', payment_status_enum, nullable=False, default='pending'),
        
        # Order source and tracking
        sa.Column('source_channel', sa.String(length=50), nullable=True),
        sa.Column('sales_rep_user_id', sa.Integer(), nullable=True),
        
        # Shipping information
        sa.Column('shipping_method', sa.String(length=100), nullable=True),
        sa.Column('carrier_name', sa.String(length=100), nullable=True),
        sa.Column('tracking_number', sa.String(length=255), nullable=True),
        
        # Billing and shipping addresses (JSON for flexibility)
        sa.Column('billing_address', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('shipping_address', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Order flags and settings
        sa.Column('is_priority', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_dropship', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_backorder_allowed', sa.Boolean(), nullable=False, default=True),
        
        # Customer service information
        sa.Column('customer_po_number', sa.String(length=100), nullable=True),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        
        # Fulfillment tracking
        sa.Column('items_shipped', sa.Integer(), nullable=False, default=0),
        sa.Column('items_remaining', sa.Integer(), nullable=False, default=0),
        sa.Column('shipment_count', sa.Integer(), nullable=False, default=0),
        
        # Document generation
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('document_url', sa.String(length=500), nullable=True),
        sa.Column('pdf_generated', sa.Boolean(), nullable=False, default=False),
        
        # Communication tracking
        sa.Column('email_sent_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_email_sent', sa.DateTime(), nullable=True),
        sa.Column('viewed_by_customer', sa.Boolean(), nullable=False, default=False),
        sa.Column('first_viewed_date', sa.DateTime(), nullable=True),
        sa.Column('last_viewed_date', sa.DateTime(), nullable=True),
        
        # Additional information
        sa.Column('terms_and_conditions', sa.Text(), nullable=True),
        sa.Column('custom_fields', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Status tracking
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_number'),
        sa.Index('ix_sales_transactions_company_id', 'company_id'),
        sa.Index('ix_sales_transactions_transaction_number', 'transaction_number'),
        sa.Index('ix_sales_transactions_customer_id', 'customer_id'),
        sa.Index('ix_sales_transactions_opportunity_id', 'opportunity_id'),
        sa.Index('ix_sales_transactions_state', 'state'),
        sa.Index('ix_sales_transactions_valid_until', 'valid_until'),
        sa.Index('ix_sales_transactions_order_date', 'order_date'),
        sa.Index('ix_sales_transactions_required_date', 'required_date'),
        sa.Index('ix_sales_transactions_promised_date', 'promised_date'),
        sa.Index('ix_sales_transactions_shipped_date', 'shipped_date'),
        sa.Index('ix_sales_transactions_delivered_date', 'delivered_date'),
        sa.Index('ix_sales_transactions_due_date', 'due_date'),
        sa.Index('ix_sales_transactions_payment_status', 'payment_status'),
        sa.Index('ix_sales_transactions_tracking_number', 'tracking_number'),
        sa.Index('ix_sales_transactions_customer_po_number', 'customer_po_number'),
        sa.Index('ix_sales_transactions_prepared_by_user_id', 'prepared_by_user_id'),
        sa.Index('ix_sales_transactions_approved_by_user_id', 'approved_by_user_id'),
        sa.Index('ix_sales_transactions_sent_date', 'sent_date'),
        sa.Index('ix_sales_transactions_sent_by_user_id', 'sent_by_user_id'),
        sa.Index('ix_sales_transactions_sales_rep_user_id', 'sales_rep_user_id'),
        sa.Index('ix_sales_transactions_warehouse_id', 'warehouse_id'),
        sa.Index('ix_sales_transactions_is_active', 'is_active')
    )
    
    # Create sales transaction line items table
    op.create_table('sales_transaction_line_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_user_id', sa.Integer(), nullable=True),
        
        # Transaction reference
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        
        # Line identification
        sa.Column('line_number', sa.Integer(), nullable=False),
        
        # Product/service information
        sa.Column('line_type', line_item_type_enum, nullable=False, default='product'),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('product_variant_id', sa.Integer(), nullable=True),
        
        # Item details
        sa.Column('item_code', sa.String(length=100), nullable=True),
        sa.Column('item_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Quantities
        sa.Column('quantity_ordered', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('quantity_shipped', sa.Numeric(precision=15, scale=4), nullable=False, default=0.0),
        sa.Column('quantity_cancelled', sa.Numeric(precision=15, scale=4), nullable=False, default=0.0),
        sa.Column('quantity_backordered', sa.Numeric(precision=15, scale=4), nullable=False, default=0.0),
        sa.Column('unit_of_measure', sa.String(length=50), nullable=False, default='each'),
        
        # Pricing
        sa.Column('unit_price', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('unit_cost', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('discount_percentage', sa.Numeric(precision=5, scale=2), nullable=False, default=0.0),
        sa.Column('discount_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        
        # Calculations
        sa.Column('line_total', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('line_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        
        # Tax information
        sa.Column('tax_percentage', sa.Numeric(precision=5, scale=2), nullable=False, default=0.0),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('tax_code', sa.String(length=50), nullable=True),
        
        # Fulfillment information
        sa.Column('warehouse_id', sa.Integer(), nullable=True),
        sa.Column('reserved_quantity', sa.Numeric(precision=15, scale=4), nullable=False, default=0.0),
        sa.Column('allocated_quantity', sa.Numeric(precision=15, scale=4), nullable=False, default=0.0),
        
        # Delivery information
        sa.Column('required_date', sa.DateTime(), nullable=True),
        sa.Column('promised_date', sa.DateTime(), nullable=True),
        sa.Column('shipped_date', sa.DateTime(), nullable=True),
        
        # Product specifications
        sa.Column('specifications', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('custom_options', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Status and flags
        sa.Column('is_backordered', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_dropship', sa.Boolean(), nullable=False, default=False),
        sa.Column('requires_special_handling', sa.Boolean(), nullable=False, default=False),
        
        # Additional attributes
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('custom_attributes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Status tracking
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['transaction_id'], ['sales_transactions.id'], ondelete='CASCADE'),
        sa.Index('ix_sales_transaction_line_items_company_id', 'company_id'),
        sa.Index('ix_sales_transaction_line_items_transaction_id', 'transaction_id'),
        sa.Index('ix_sales_transaction_line_items_product_id', 'product_id'),
        sa.Index('ix_sales_transaction_line_items_product_variant_id', 'product_variant_id'),
        sa.Index('ix_sales_transaction_line_items_item_code', 'item_code'),
        sa.Index('ix_sales_transaction_line_items_line_type', 'line_type'),
        sa.Index('ix_sales_transaction_line_items_warehouse_id', 'warehouse_id'),
        sa.Index('ix_sales_transaction_line_items_required_date', 'required_date'),
        sa.Index('ix_sales_transaction_line_items_promised_date', 'promised_date'),
        sa.Index('ix_sales_transaction_line_items_shipped_date', 'shipped_date'),
        sa.Index('ix_sales_transaction_line_items_is_active', 'is_active')
    )


def downgrade() -> None:
    """Drop consolidated sales transaction tables."""
    
    # Drop tables
    op.drop_table('sales_transaction_line_items')
    op.drop_table('sales_transactions')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS salestransactionstate')
    op.execute('DROP TYPE IF EXISTS paymentstatus')
    op.execute('DROP TYPE IF EXISTS lineitemtype')
