"""Create order tables

Revision ID: 20250106_150000
Revises: 20250805_200000
Create Date: 2025-01-06 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250106_150000'
down_revision = '20250805_200000'
branch_labels = None
depends_on = None


def upgrade():
    """Create order-related tables"""
    
    # Create sales_orders table
    op.create_table('sales_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False, index=True),
        sa.Column('order_number', sa.String(length=100), nullable=False, index=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Customer and references
        sa.Column('customer_id', sa.Integer(), nullable=False, index=True),
        sa.Column('opportunity_id', sa.Integer(), nullable=True, index=True),
        sa.Column('quote_id', sa.Integer(), nullable=True, index=True),
        
        # Status and workflow
        sa.Column('status', sa.Enum('DRAFT', 'PENDING', 'CONFIRMED', 'IN_PRODUCTION', 'READY_TO_SHIP', 
                                  'PARTIALLY_SHIPPED', 'SHIPPED', 'DELIVERED', 'COMPLETED', 'CANCELLED', 'ON_HOLD',
                                  name='orderstatus'), nullable=False, index=True),
        sa.Column('payment_status', sa.Enum('PENDING', 'PARTIALLY_PAID', 'PAID', 'OVERDUE', 'REFUNDED',
                                          name='paymentstatus'), nullable=False, index=True),
        
        # Dates
        sa.Column('order_date', sa.DateTime(), nullable=False, index=True),
        sa.Column('required_date', sa.DateTime(), nullable=True, index=True),
        sa.Column('confirmed_date', sa.DateTime(), nullable=True),
        sa.Column('shipped_date', sa.DateTime(), nullable=True),
        sa.Column('delivered_date', sa.DateTime(), nullable=True),
        sa.Column('completed_date', sa.DateTime(), nullable=True),
        
        # Financial information
        sa.Column('subtotal', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('discount_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('shipping_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('currency_code', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('payment_terms_days', sa.Integer(), nullable=False, default=30),
        
        # Paid amounts
        sa.Column('paid_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('outstanding_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        
        # Fulfillment tracking
        sa.Column('items_shipped', sa.Integer(), nullable=False, default=0),
        sa.Column('items_remaining', sa.Integer(), nullable=False, default=0),
        sa.Column('shipment_count', sa.Integer(), nullable=False, default=0),
        sa.Column('invoice_count', sa.Integer(), nullable=False, default=0),
        
        # Addresses (stored as JSON)
        sa.Column('billing_address', sa.JSON(), nullable=True),
        sa.Column('shipping_address', sa.JSON(), nullable=True),
        
        # Priority and preferences
        sa.Column('priority', sa.String(length=20), nullable=False, default='normal'),
        sa.Column('shipping_method', sa.String(length=100), nullable=True),
        sa.Column('delivery_instructions', sa.Text(), nullable=True),
        
        # People
        sa.Column('sales_rep_user_id', sa.Integer(), nullable=True, index=True),
        sa.Column('confirmed_by_user_id', sa.Integer(), nullable=True, index=True),
        
        # Additional information
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('customer_po_number', sa.String(length=100), nullable=True, index=True),
        sa.Column('terms_and_conditions', sa.Text(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        
        # Hold management
        sa.Column('hold_status', sa.Boolean(), nullable=False, default=False),
        sa.Column('hold_reason', sa.String(length=255), nullable=True),
        sa.Column('hold_date', sa.DateTime(), nullable=True),
        sa.Column('hold_by_user_id', sa.Integer(), nullable=True),
        
        # Inventory reservations (stored as JSON)
        sa.Column('inventory_reservations', sa.JSON(), nullable=True),
        
        # System fields
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_user_id', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number', name='uk_sales_orders_order_number')
    )
    
    # Create index for multi-company isolation
    op.create_index('ix_sales_orders_company_status', 'sales_orders', ['company_id', 'status'])
    op.create_index('ix_sales_orders_company_date', 'sales_orders', ['company_id', 'order_date'])
    
    # Create sales_order_line_items table
    op.create_table('sales_order_line_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False, index=True),
        sa.Column('order_id', sa.Integer(), nullable=False, index=True),
        sa.Column('line_number', sa.Integer(), nullable=False),
        
        # Item type and product information
        sa.Column('line_type', sa.Enum('PRODUCT', 'SERVICE', 'DISCOUNT', 'SHIPPING', 'TAX', 'MISC',
                                     name='lineitemtype'), nullable=False, default='PRODUCT', index=True),
        sa.Column('product_id', sa.Integer(), nullable=True, index=True),
        sa.Column('product_variant_id', sa.Integer(), nullable=True, index=True),
        
        # Item details
        sa.Column('item_code', sa.String(length=100), nullable=True, index=True),
        sa.Column('item_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Quantity and units
        sa.Column('quantity', sa.Numeric(precision=15, scale=4), nullable=False, default=1.0),
        sa.Column('unit_of_measure', sa.String(length=50), nullable=False, default='each'),
        
        # Pricing
        sa.Column('unit_price', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('list_price', sa.Numeric(precision=15, scale=4), nullable=True),
        sa.Column('unit_cost', sa.Numeric(precision=15, scale=4), nullable=True),
        
        # Discounts
        sa.Column('discount_percentage', sa.Numeric(precision=5, scale=2), nullable=False, default=0.0),
        sa.Column('discount_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        
        # Calculations
        sa.Column('line_total', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('line_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        
        # Tax information
        sa.Column('tax_percentage', sa.Numeric(precision=5, scale=2), nullable=False, default=0.0),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('tax_code', sa.String(length=50), nullable=True),
        
        # Fulfillment tracking
        sa.Column('quantity_shipped', sa.Numeric(precision=15, scale=4), nullable=True, default=0.0),
        sa.Column('quantity_invoiced', sa.Numeric(precision=15, scale=4), nullable=True, default=0.0),
        
        # Product specifications
        sa.Column('specifications', sa.JSON(), nullable=True),
        sa.Column('custom_options', sa.JSON(), nullable=True),
        
        # Delivery information
        sa.Column('lead_time_days', sa.Integer(), nullable=True),
        sa.Column('delivery_date', sa.DateTime(), nullable=True),
        
        # Additional attributes
        sa.Column('notes', sa.Text(), nullable=True),
        
        # System fields
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_user_id', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['sales_orders.id'], ondelete='CASCADE')
    )
    
    # Create order_shipments table
    op.create_table('order_shipments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False, index=True),
        sa.Column('order_id', sa.Integer(), nullable=False, index=True),
        sa.Column('shipment_number', sa.String(length=100), nullable=False, index=True),
        
        # Shipment status
        sa.Column('status', sa.Enum('PENDING', 'IN_TRANSIT', 'DELIVERED', 'EXCEPTION', 'CANCELLED',
                                  name='shipmentstatus'), nullable=False, index=True),
        
        # Tracking information
        sa.Column('tracking_number', sa.String(length=100), nullable=True, index=True),
        sa.Column('carrier', sa.String(length=100), nullable=True),
        sa.Column('shipping_method', sa.String(length=100), nullable=True),
        
        # Dates
        sa.Column('shipped_date', sa.DateTime(), nullable=True, index=True),
        sa.Column('estimated_delivery_date', sa.DateTime(), nullable=True),
        sa.Column('actual_delivery_date', sa.DateTime(), nullable=True),
        sa.Column('delivered_to', sa.String(length=255), nullable=True),
        
        # Address and package details
        sa.Column('shipping_address', sa.JSON(), nullable=True),
        sa.Column('weight_kg', sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column('dimensions', sa.JSON(), nullable=True),
        sa.Column('package_count', sa.Integer(), nullable=True, default=1),
        
        # Cost information
        sa.Column('shipping_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('insurance_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        
        # Additional information
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        
        # System fields
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_user_id', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['sales_orders.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('shipment_number', name='uk_order_shipments_shipment_number')
    )
    
    # Create order_invoices table
    op.create_table('order_invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False, index=True),
        sa.Column('order_id', sa.Integer(), nullable=False, index=True),
        sa.Column('invoice_number', sa.String(length=100), nullable=False, index=True),
        
        # Invoice status
        sa.Column('status', sa.Enum('DRAFT', 'SENT', 'PAID', 'PARTIALLY_PAID', 'OVERDUE', 'CANCELLED',
                                  name='invoicestatus'), nullable=False, index=True),
        
        # Dates
        sa.Column('invoice_date', sa.DateTime(), nullable=False, index=True),
        sa.Column('due_date', sa.DateTime(), nullable=False, index=True),
        sa.Column('sent_date', sa.DateTime(), nullable=True),
        sa.Column('payment_terms_days', sa.Integer(), nullable=False, default=30),
        
        # Financial information
        sa.Column('subtotal', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('discount_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('paid_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('outstanding_amount', sa.Numeric(precision=15, scale=2), nullable=False, default=0.0),
        sa.Column('currency_code', sa.String(length=3), nullable=False, default='USD'),
        
        # Invoice details
        sa.Column('billing_address', sa.JSON(), nullable=True),
        sa.Column('line_items_data', sa.JSON(), nullable=True),  # Snapshot of line items at invoice time
        
        # Communication tracking
        sa.Column('email_sent_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_email_sent', sa.DateTime(), nullable=True),
        
        # Additional information
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        
        # System fields
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('updated_by_user_id', sa.Integer(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['sales_orders.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('invoice_number', name='uk_order_invoices_invoice_number')
    )
    
    # Create indexes for efficient queries
    op.create_index('ix_order_line_items_order_line', 'sales_order_line_items', ['order_id', 'line_number'])
    op.create_index('ix_order_shipments_company_status', 'order_shipments', ['company_id', 'status'])
    op.create_index('ix_order_invoices_company_status', 'order_invoices', ['company_id', 'status'])
    op.create_index('ix_order_invoices_due_date', 'order_invoices', ['due_date'])


def downgrade():
    """Drop order-related tables"""
    
    # Drop indexes first
    op.drop_index('ix_order_invoices_due_date', table_name='order_invoices')
    op.drop_index('ix_order_invoices_company_status', table_name='order_invoices')
    op.drop_index('ix_order_shipments_company_status', table_name='order_shipments')
    op.drop_index('ix_order_line_items_order_line', table_name='sales_order_line_items')
    op.drop_index('ix_sales_orders_company_date', table_name='sales_orders')
    op.drop_index('ix_sales_orders_company_status', table_name='sales_orders')
    
    # Drop tables in reverse order (due to foreign keys)
    op.drop_table('order_invoices')
    op.drop_table('order_shipments')
    op.drop_table('sales_order_line_items')
    op.drop_table('sales_orders')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS invoicestatus")
    op.execute("DROP TYPE IF EXISTS shipmentstatus")
    op.execute("DROP TYPE IF EXISTS lineitemtype")
    op.execute("DROP TYPE IF EXISTS paymentstatus")
    op.execute("DROP TYPE IF EXISTS orderstatus")