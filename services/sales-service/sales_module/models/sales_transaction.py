"""
Consolidated Sales Transaction model for quotations and orders.

This model combines the functionality of both quotations and sales orders
with a state field to differentiate between different stages.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from sales_module.framework.base import CompanyBusinessObject, BaseModel


class SalesTransactionState(str, enum.Enum):
    """Sales transaction state enumeration"""
    DRAFT = "draft"  # Draft quotation
    QUOTE_PENDING_APPROVAL = "quote_pending_approval"  # Quotation waiting for approval
    QUOTE_APPROVED = "quote_approved"  # Approved quotation
    QUOTE_SENT = "quote_sent"  # Sent to customer
    QUOTE_ACCEPTED = "quote_accepted"  # Accepted by customer
    QUOTE_REJECTED = "quote_rejected"  # Rejected by customer
    QUOTE_EXPIRED = "quote_expired"  # Quotation expired
    ORDER_PENDING = "order_pending"  # Pending confirmation
    ORDER_CONFIRMED = "order_confirmed"  # Confirmed order
    ORDER_IN_PRODUCTION = "order_in_production"  # In production/preparation
    ORDER_READY_TO_SHIP = "order_ready_to_ship"  # Ready for shipment
    ORDER_PARTIALLY_SHIPPED = "order_partially_shipped"  # Partially shipped
    ORDER_SHIPPED = "order_shipped"  # Fully shipped
    ORDER_DELIVERED = "order_delivered"  # Delivered to customer
    ORDER_COMPLETED = "order_completed"  # Order completed
    ORDER_CANCELLED = "order_cancelled"  # Cancelled order
    ORDER_ON_HOLD = "order_on_hold"  # Order on hold


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"  # Payment pending
    AUTHORIZED = "authorized"  # Payment authorized
    PARTIALLY_PAID = "partially_paid"  # Partially paid
    PAID = "paid"  # Fully paid
    OVERDUE = "overdue"  # Payment overdue
    REFUNDED = "refunded"  # Payment refunded
    CANCELLED = "cancelled"  # Payment cancelled


class LineItemType(str, enum.Enum):
    """Line item type enumeration"""
    PRODUCT = "product"  # Physical product
    SERVICE = "service"  # Service item
    DISCOUNT = "discount"  # Discount line
    SHIPPING = "shipping"  # Shipping charge
    TAX = "tax"  # Tax line
    MISC = "misc"  # Miscellaneous item


class SalesTransaction(CompanyBusinessObject):
    """
    Consolidated Sales Transaction model for managing both quotations and orders.
    
    This model combines quotation and order functionality with a state field
    to differentiate between different stages of the sales process.
    """
    
    __tablename__ = "sales_transactions"
    
    # Basic transaction information
    transaction_number = Column(String(100), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Customer and opportunity references
    customer_id = Column(
        Integer,
        nullable=False,
        index=True
    )
    opportunity_id = Column(
        Integer,
        nullable=True,
        index=True
    )
    
    # Transaction state and workflow
    state = Column(Enum(SalesTransactionState, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=False, default=SalesTransactionState.DRAFT.value, index=True)
    version = Column(Integer, nullable=False, default=1)
    
    # Financial information
    subtotal = Column(Numeric(15, 2), nullable=False, default=0.0)
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    shipping_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    currency_code = Column(String(3), nullable=False, default="USD")
    
    # Pricing and discounts
    overall_discount_percentage = Column(Numeric(5, 2), nullable=False, default=0.0)
    margin_percentage = Column(Numeric(5, 2), nullable=True)
    total_cost = Column(Numeric(15, 2), nullable=True)
    
    # Quotation validity and terms
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True, index=True)
    payment_terms_days = Column(Integer, nullable=False, default=30)
    delivery_terms = Column(String(255), nullable=True)
    
    # Transaction preparation and sending
    prepared_by_user_id = Column(Integer, nullable=False, index=True)
    approved_by_user_id = Column(Integer, nullable=True, index=True)
    sent_date = Column(DateTime, nullable=True, index=True)
    sent_by_user_id = Column(Integer, nullable=True, index=True)
    
    # Customer response
    customer_response_date = Column(DateTime, nullable=True)
    customer_response_notes = Column(Text)
    rejection_reason = Column(String(255), nullable=True)
    
    # Approval workflow
    requires_approval = Column(Boolean, nullable=False, default=False)
    approval_threshold_amount = Column(Numeric(15, 2), nullable=True)
    approval_notes = Column(Text)
    
    # Order-specific information
    transaction_date = Column(DateTime, nullable=True, default=None, index=True)
    order_date = Column(DateTime, nullable=True, default=None, index=True)
    required_date = Column(DateTime, nullable=True, index=True)
    promised_date = Column(DateTime, nullable=True, index=True)
    shipped_date = Column(DateTime, nullable=True, index=True)
    delivered_date = Column(DateTime, nullable=True, index=True)
    
    # Payment information
    due_date = Column(DateTime, nullable=True, index=True)
    paid_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    outstanding_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    payment_status = Column(Enum(PaymentStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, default=PaymentStatus.PENDING.value, index=True)
    
    # Order source and tracking
    source_channel = Column(String(50), nullable=True)  # web, phone, email, etc.
    sales_rep_user_id = Column(Integer, nullable=True, index=True)
    
    # Shipping information
    shipping_method = Column(String(100), nullable=True)
    carrier_name = Column(String(100), nullable=True)
    tracking_number = Column(String(255), nullable=True, index=True)
    
    # Billing and shipping addresses (JSON for flexibility)
    billing_address = Column(JSON)
    shipping_address = Column(JSON)
    
    # Order flags and settings
    is_priority = Column(Boolean, nullable=False, default=False)
    is_dropship = Column(Boolean, nullable=False, default=False)
    is_backorder_allowed = Column(Boolean, nullable=False, default=True)
    
    # Customer service information
    customer_po_number = Column(String(100), nullable=True, index=True)
    special_instructions = Column(Text)
    internal_notes = Column(Text)
    
    # Fulfillment tracking
    items_shipped = Column(Integer, nullable=False, default=0)
    items_remaining = Column(Integer, nullable=False, default=0)
    shipment_count = Column(Integer, nullable=False, default=0)
    
    # Document generation
    template_id = Column(Integer, nullable=True)
    document_url = Column(String(500), nullable=True)
    pdf_generated = Column(Boolean, nullable=False, default=False)
    
    # Communication tracking
    email_sent_count = Column(Integer, nullable=False, default=0)
    last_email_sent = Column(DateTime, nullable=True)
    viewed_by_customer = Column(Boolean, nullable=False, default=False)
    first_viewed_date = Column(DateTime, nullable=True)
    last_viewed_date = Column(DateTime, nullable=True)
    
    # Additional information
    terms_and_conditions = Column(Text)
    custom_fields = Column(JSON)
    tags = Column(JSON)  # Array of string tags
    
    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    line_items = relationship("SalesTransactionLineItem", back_populates="transaction", cascade="all, delete-orphan")
    
    def __str__(self):
        """String representation of sales transaction."""
        return f"Transaction {self.transaction_number} v{self.version}"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary including line items."""
        result = super().to_dict()
        # Try to include line items if they exist and are loaded
        try:
            if hasattr(self, 'line_items'):
                # Check if line_items is loaded (not a query object)
                if self.line_items is not None and not callable(self.line_items):
                    # Ensure we're working with a list-like object
                    if hasattr(self.line_items, '__iter__') and not isinstance(self.line_items, str):
                        result['line_items'] = [item.to_dict() for item in self.line_items]
                    else:
                        # If line_items is not a list-like object, ensure we have an empty array
                        result['line_items'] = []
                else:
                    # If line_items is None, ensure we have an empty array
                    result['line_items'] = []
            else:
                # If line_items attribute doesn't exist, ensure we have an empty array
                result['line_items'] = []
        except Exception as e:
            # If there's an error accessing line_items, ensure we have an empty array
            result['line_items'] = []
        return result
    
    def __repr__(self):
        """Detailed representation of sales transaction."""
        return (
            f"SalesTransaction(id={self.id}, number=\"{self.transaction_number}\", "
            f"version={self.version}, state=\"{self.state.value}\", total={self.total_amount})"
        )
    
    @property
    def display_identifier(self) -> str:
        """Get display identifier with transaction number and version."""
        return f"{self.transaction_number} v{self.version} - {self.title}"
    
    @property
    def is_expired(self) -> bool:
        """Check if transaction is expired (for quotations)."""
        if self.valid_until:
            return datetime.utcnow() > self.valid_until
        return False
    
    @property
    def days_until_expiry(self) -> int:
        """Calculate days until transaction expires."""
        if self.valid_until:
            delta = self.valid_until - datetime.utcnow()
            return max(0, delta.days)
        return 0
    
    @property
    def is_quote_state(self) -> bool:
        """Check if transaction is in a quotation state."""
        quote_states = [
            SalesTransactionState.DRAFT.value,
            SalesTransactionState.QUOTE_PENDING_APPROVAL.value,
            SalesTransactionState.QUOTE_APPROVED.value,
            SalesTransactionState.QUOTE_SENT.value,
            SalesTransactionState.QUOTE_ACCEPTED.value,
            SalesTransactionState.QUOTE_REJECTED.value,
            SalesTransactionState.QUOTE_EXPIRED.value
        ]
        return self.state in quote_states
    
    @property
    def is_order_state(self) -> bool:
        """Check if transaction is in an order state."""
        order_states = [
            SalesTransactionState.ORDER_PENDING.value,
            SalesTransactionState.ORDER_CONFIRMED.value,
            SalesTransactionState.ORDER_IN_PRODUCTION.value,
            SalesTransactionState.ORDER_READY_TO_SHIP.value,
            SalesTransactionState.ORDER_PARTIALLY_SHIPPED.value,
            SalesTransactionState.ORDER_SHIPPED.value,
            SalesTransactionState.ORDER_DELIVERED.value,
            SalesTransactionState.ORDER_COMPLETED.value,
            SalesTransactionState.ORDER_CANCELLED.value,
            SalesTransactionState.ORDER_ON_HOLD.value
        ]
        return self.state in order_states
    
    @property
    def is_overdue(self) -> bool:
        """Check if transaction is overdue."""
        if self.required_date and self.is_order_state:
            if self.state in [SalesTransactionState.ORDER_COMPLETED.value, SalesTransactionState.ORDER_CANCELLED.value]:
                return False
            return datetime.utcnow() > self.required_date
        return False
    
    @property
    def is_paid(self) -> bool:
        """Check if transaction is fully paid."""
        return self.payment_status == PaymentStatus.PAID
    
    @property
    def is_shipped(self) -> bool:
        """Check if transaction is fully shipped."""
        shipped_states = [
            SalesTransactionState.ORDER_SHIPPED.value,
            SalesTransactionState.ORDER_DELIVERED.value,
            SalesTransactionState.ORDER_COMPLETED.value
        ]
        return self.state in shipped_states
    
    @property
    def is_completed(self) -> bool:
        """Check if transaction is completed."""
        return self.state == SalesTransactionState.ORDER_COMPLETED.value
    
    def generate_transaction_number(self, prefix: str = "TXN") -> str:
        """Generate transaction number if not provided."""
        import time
        timestamp = int(time.time())
        return f"{prefix}{timestamp:08d}"


class SalesTransactionLineItem(CompanyBusinessObject):
    """
    Sales Transaction Line Item model for individual transaction products/services.
    
    Detailed line item information including product details,
    quantities, pricing, and fulfillment tracking.
    """
    
    __tablename__ = "sales_transaction_line_items"
    
    # Transaction reference
    transaction_id = Column(
        Integer,
        ForeignKey("sales_transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Line identification
    line_number = Column(Integer, nullable=False)
    
    # Product/service information
    line_type = Column(Enum(LineItemType, values_callable=lambda x: [e.value for e in x]), nullable=False, default=LineItemType.PRODUCT.value, index=True)
    product_id = Column(Integer, nullable=True, index=True)  # Reference to inventory product
    product_variant_id = Column(Integer, nullable=True, index=True)
    
    # Item details
    item_code = Column(String(100), nullable=True, index=True)
    item_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Quantities
    quantity_ordered = Column(Numeric(15, 4), nullable=False)
    quantity_shipped = Column(Numeric(15, 4), nullable=False, default=0.0)
    quantity_cancelled = Column(Numeric(15, 4), nullable=False, default=0.0)
    quantity_backordered = Column(Numeric(15, 4), nullable=False, default=0.0)
    unit_of_measure = Column(String(50), nullable=False, default="each")
    
    # Pricing
    unit_price = Column(Numeric(15, 4), nullable=False)
    unit_cost = Column(Numeric(15, 4), nullable=True)  # For margin calculation
    discount_percentage = Column(Numeric(5, 2), nullable=False, default=0.0)
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    
    # Calculations
    line_total = Column(Numeric(15, 2), nullable=False)
    line_cost = Column(Numeric(15, 2), nullable=True)
    
    # Tax information
    tax_percentage = Column(Numeric(5, 2), nullable=False, default=0.0)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    tax_code = Column(String(50), nullable=True)
    
    # Fulfillment information
    warehouse_id = Column(Integer, nullable=True, index=True)
    reserved_quantity = Column(Numeric(15, 4), nullable=False, default=0.0)
    allocated_quantity = Column(Numeric(15, 4), nullable=False, default=0.0)
    
    # Delivery information
    required_date = Column(DateTime, nullable=True, index=True)
    promised_date = Column(DateTime, nullable=True, index=True)
    shipped_date = Column(DateTime, nullable=True, index=True)
    
    # Product specifications
    specifications = Column(JSON)
    custom_options = Column(JSON)
    
    # Status and flags
    is_backordered = Column(Boolean, nullable=False, default=False)
    is_dropship = Column(Boolean, nullable=False, default=False)
    requires_special_handling = Column(Boolean, nullable=False, default=False)
    
    # Additional attributes
    notes = Column(Text)
    custom_attributes = Column(JSON)
    
    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    transaction = relationship("SalesTransaction", back_populates="line_items")
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        result = super().to_dict()
        # Handle any relationship issues gracefully
        try:
            # Remove any circular references or unloaded relationships
            if 'transaction' in result:
                del result['transaction']
        except:
            pass
        return result
    
    def __str__(self):
        """String representation of transaction line item."""
        return f"Line {self.line_number}: {self.item_name} (Qty: {self.quantity_ordered})"
    
    def __repr__(self):
        """Detailed representation of transaction line item."""
        return (
            f"SalesTransactionLineItem(id={self.id}, line_number={self.line_number}, "
            f"item_name=\"{self.item_name}\", quantity={self.quantity_ordered})"
        )
    
    @property
    def quantity_remaining(self) -> Decimal:
        """Calculate remaining quantity to ship."""
        return self.quantity_ordered - self.quantity_shipped - self.quantity_cancelled
    
    @property
    def is_fully_shipped(self) -> bool:
        """Check if line item is fully shipped."""
        return self.quantity_remaining <= 0
    
    @property
    def fulfillment_percentage(self) -> float:
        """Calculate fulfillment percentage."""
        if self.quantity_ordered <= 0:
            return 0.0
        return (self.quantity_shipped / self.quantity_ordered) * 100
    
    @property
    def line_margin(self) -> Optional[Decimal]:
        """Calculate line margin."""
        if not self.line_cost:
            return None
        return self.line_total - self.line_cost
    
    @property
    def margin_percentage(self) -> Optional[float]:
        """Calculate margin percentage."""
        if not self.line_cost or self.line_total <= 0:
            return None
        margin = ((self.line_total - self.line_cost) / self.line_total) * 100
        return float(margin)
    
    def calculate_line_total(self) -> None:
        """Calculate line total with discounts."""
        gross_total = self.quantity_ordered * self.unit_price
        self.line_total = gross_total - self.discount_amount
        
        # Calculate line cost if unit cost is available
        if self.unit_cost:
            self.line_cost = self.quantity_ordered * self.unit_cost
        
        # Calculate tax
        if self.tax_percentage > 0:
            self.tax_amount = self.line_total * (self.tax_percentage / 100)
