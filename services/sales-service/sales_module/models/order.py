"""
Sales order models for order processing and fulfillment.

Provides comprehensive order management including order lifecycle,
line items, shipments, invoicing, and payment tracking.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from sales_module.framework.base import CompanyBusinessObject, BaseModel


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    DRAFT = "draft"  # Draft order
    PENDING = "pending"  # Pending confirmation
    CONFIRMED = "confirmed"  # Confirmed order
    IN_PRODUCTION = "in_production"  # In production/preparation
    READY_TO_SHIP = "ready_to_ship"  # Ready for shipment
    PARTIALLY_SHIPPED = "partially_shipped"  # Partially shipped
    SHIPPED = "shipped"  # Fully shipped
    DELIVERED = "delivered"  # Delivered to customer
    COMPLETED = "completed"  # Order completed
    CANCELLED = "cancelled"  # Cancelled order
    ON_HOLD = "on_hold"  # Order on hold


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"  # Payment pending
    AUTHORIZED = "authorized"  # Payment authorized
    PARTIALLY_PAID = "partially_paid"  # Partially paid
    PAID = "paid"  # Fully paid
    OVERDUE = "overdue"  # Payment overdue
    REFUNDED = "refunded"  # Payment refunded
    CANCELLED = "cancelled"  # Payment cancelled


class ShipmentStatus(str, enum.Enum):
    """Shipment status enumeration"""
    PREPARING = "preparing"  # Preparing for shipment
    READY = "ready"  # Ready to ship
    SHIPPED = "shipped"  # Shipped
    IN_TRANSIT = "in_transit"  # In transit
    OUT_FOR_DELIVERY = "out_for_delivery"  # Out for delivery
    DELIVERED = "delivered"  # Delivered
    FAILED_DELIVERY = "failed_delivery"  # Failed delivery attempt
    RETURNED = "returned"  # Returned to sender


class InvoiceStatus(str, enum.Enum):
    """Invoice status enumeration"""
    DRAFT = "draft"  # Draft invoice
    SENT = "sent"  # Sent to customer
    VIEWED = "viewed"  # Viewed by customer
    PAID = "paid"  # Paid
    OVERDUE = "overdue"  # Overdue
    CANCELLED = "cancelled"  # Cancelled
    REFUNDED = "refunded"  # Refunded


class SalesOrder(CompanyBusinessObject):
    """
    Sales Order model for managing customer orders.
    
    Comprehensive order management including order processing,
    fulfillment tracking, payments, and customer communication.
    """
    
    __tablename__ = "sales_orders"
    
    # Basic order information
    order_number = Column(String(100), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Customer and source references
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    opportunity_id = Column(
        Integer,
        ForeignKey("sales_opportunities.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    quote_id = Column(
        Integer,
        ForeignKey("sales_quotes.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Order status and workflow
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.DRAFT, index=True)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, index=True)
    
    # Financial information
    subtotal = Column(Numeric(15, 2), nullable=False, default=0.0)
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    shipping_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    currency_code = Column(String(3), nullable=False, default="USD")
    
    # Payment information
    payment_terms_days = Column(Integer, nullable=False, default=30)
    due_date = Column(DateTime, nullable=True, index=True)
    paid_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    outstanding_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    
    # Order dates and timeline
    order_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    required_date = Column(DateTime, nullable=True, index=True)
    promised_date = Column(DateTime, nullable=True, index=True)
    shipped_date = Column(DateTime, nullable=True, index=True)
    delivered_date = Column(DateTime, nullable=True, index=True)
    
    # Order source and tracking
    source_channel = Column(String(50), nullable=True)  # web, phone, email, etc.
    sales_rep_user_id = Column(Integer, nullable=False, index=True)
    
    # Shipping information
    shipping_method = Column(String(100), nullable=True)
    carrier_name = Column(String(100), nullable=True)
    tracking_number = Column(String(255), nullable=True, index=True)
    
    # Billing and shipping addresses (JSON for flexibility)
    billing_address = Column(JSON)
    shipping_address = Column(JSON)
    
    # Order flags and settings
    is_priority = Column(Boolean, nullable=False, default=False)
    requires_approval = Column(Boolean, nullable=False, default=False)
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
    
    # Additional attributes
    tags = Column(JSON)  # Array of string tags
    custom_attributes = Column(JSON)
    
    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    # customer = relationship("Customer", back_populates="orders")
    # opportunity = relationship("SalesOpportunity", back_populates="orders")
    # quote = relationship("SalesQuote", back_populates="order")
    # line_items = relationship("SalesOrderLineItem", back_populates="order", cascade="all, delete-orphan")
    # shipments = relationship("OrderShipment", back_populates="order", cascade="all, delete-orphan")
    # invoices = relationship("OrderInvoice", back_populates="order", cascade="all, delete-orphan")
    
    def __str__(self):
        """String representation of sales order."""
        return f"Order {self.order_number}"
    
    def __repr__(self):
        """Detailed representation of sales order."""
        return (
            f"SalesOrder(id={self.id}, number='{self.order_number}', "
            f"status='{self.status.value}', total={self.total_amount})"
        )
    
    @property
    def display_identifier(self) -> str:
        """Get display identifier with order number."""
        return f"{self.order_number} - {self.title}"
    
    @property
    def is_overdue(self) -> bool:
        """Check if order is overdue."""
        if not self.required_date or self.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            return False
        return datetime.utcnow() > self.required_date
    
    @property
    def days_until_required(self) -> Optional[int]:
        """Calculate days until required date."""
        if not self.required_date or self.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            return None
        delta = self.required_date - datetime.utcnow()
        return delta.days
    
    @property
    def is_paid(self) -> bool:
        """Check if order is fully paid."""
        return self.payment_status == PaymentStatus.PAID
    
    @property
    def is_shipped(self) -> bool:
        """Check if order is fully shipped."""
        return self.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.COMPLETED]
    
    @property
    def is_completed(self) -> bool:
        """Check if order is completed."""
        return self.status == OrderStatus.COMPLETED
    
    @property
    def fulfillment_percentage(self) -> float:
        """Calculate fulfillment percentage."""
        total_items = self.items_shipped + self.items_remaining
        if total_items == 0:
            return 0.0
        return (self.items_shipped / total_items) * 100
    
    @property
    def payment_percentage(self) -> float:
        """Calculate payment percentage."""
        if self.total_amount <= 0:
            return 0.0
        return (self.paid_amount / self.total_amount) * 100
    
    def generate_order_number(self, prefix: str = "SO") -> str:
        """Generate order number if not provided."""
        # In production, would use company settings and sequence numbers
        import time
        timestamp = int(time.time())
        return f"{prefix}{timestamp:08d}"
    
    @classmethod
    def from_quote(cls, quote, user_id: int = None, **kwargs):
        """
        Create a sales order from an accepted quote.
        
        Args:
            quote: SalesQuote instance to convert
            user_id: ID of user creating the order
            **kwargs: Additional order-specific data
            
        Returns:
            SalesOrder: New order instance created from quote
        """
        # Generate order number if not provided
        order_number = kwargs.get('order_number')
        if not order_number:
            temp_order = cls(company_id=quote.company_id)
            order_number = temp_order.generate_order_number()
        
        # Create order from quote data
        order_data = {
            'company_id': quote.company_id,
            'order_number': order_number,
            'title': quote.title,
            'description': quote.description or f"Order converted from quote {quote.quote_number}",
            'customer_id': quote.customer_id,
            'quote_id': quote.id,
            'sales_rep_user_id': user_id or quote.prepared_by_user_id,
            
            # Financial information from quote
            'subtotal': quote.subtotal,
            'discount_amount': quote.discount_amount,
            'tax_amount': quote.tax_amount,
            'total_amount': quote.total_amount,
            'currency_code': quote.currency_code,
            'payment_terms_days': quote.payment_terms_days,
            
            # Order dates
            'order_date': datetime.utcnow(),
            'required_date': kwargs.get('required_date', quote.valid_until),
            
            # Order settings
            'status': OrderStatus.CONFIRMED,  # Start as confirmed since quote was accepted
            'payment_status': PaymentStatus.PENDING,
            'outstanding_amount': quote.total_amount,
            
            # Additional order attributes
            'source_channel': 'quote_conversion',
            'special_instructions': quote.notes,
            'customer_po_number': kwargs.get('customer_po_number'),
        }
        
        # Override with any additional kwargs
        order_data.update(kwargs)
        
        # Create the order
        order = cls(**order_data)
        
        # Calculate totals and set due date
        order.calculate_totals()
        
        return order
    
    def calculate_totals(self) -> None:
        """Calculate order totals from line items."""
        # In production, would calculate from actual line items
        # This would sum up all line item amounts, discounts, taxes, etc.
        
        # Calculate outstanding amount
        self.outstanding_amount = self.total_amount - self.paid_amount
        
        # Set due date based on payment terms
        if not self.due_date and self.payment_terms_days:
            self.due_date = self.order_date + timedelta(days=self.payment_terms_days)
    
    def confirm_order(self, user_id: int = None) -> None:
        """Confirm the order and start fulfillment process."""
        self.status = OrderStatus.CONFIRMED
        
        # Calculate totals and set due date
        self.calculate_totals()
        
        # Log audit trail
        self.log_audit_trail("order_confirmed", user_id)
        
        # Publish event
        self.publish_event("order.confirmed", {
            "order_id": self.id,
            "order_number": self.order_number,
            "customer_id": self.customer_id,
            "total_amount": float(self.total_amount)
        })
    
    def cancel_order(self, reason: str, user_id: int = None) -> None:
        """Cancel the order."""
        old_status = self.status
        self.status = OrderStatus.CANCELLED
        
        # Log audit trail
        self.log_audit_trail("order_cancelled", user_id, {
            "previous_status": old_status.value,
            "cancellation_reason": reason
        })
        
        # Publish event
        self.publish_event("order.cancelled", {
            "order_id": self.id,
            "order_number": self.order_number,
            "customer_id": self.customer_id,
            "cancellation_reason": reason
        })
    
    def put_on_hold(self, reason: str, user_id: int = None) -> None:
        """Put order on hold."""
        old_status = self.status
        self.status = OrderStatus.ON_HOLD
        
        # Log audit trail
        self.log_audit_trail("order_on_hold", user_id, {
            "previous_status": old_status.value,
            "hold_reason": reason
        })
        
        # Publish event
        self.publish_event("order.on_hold", {
            "order_id": self.id,
            "order_number": self.order_number,
            "hold_reason": reason
        })
    
    def release_hold(self, user_id: int = None) -> None:
        """Release order from hold."""
        self.status = OrderStatus.CONFIRMED  # Return to confirmed status
        
        # Log audit trail
        self.log_audit_trail("order_hold_released", user_id)
        
        # Publish event
        self.publish_event("order.hold_released", {
            "order_id": self.id,
            "order_number": self.order_number
        })
    
    def record_payment(self, payment_amount: Decimal, payment_method: str = None, 
                      user_id: int = None) -> None:
        """Record a payment against the order."""
        self.paid_amount += payment_amount
        self.outstanding_amount = self.total_amount - self.paid_amount
        
        # Update payment status
        if self.outstanding_amount <= 0:
            self.payment_status = PaymentStatus.PAID
        elif self.paid_amount > 0:
            self.payment_status = PaymentStatus.PARTIALLY_PAID
        
        # Log audit trail
        self.log_audit_trail("payment_recorded", user_id, {
            "payment_amount": float(payment_amount),
            "payment_method": payment_method,
            "total_paid": float(self.paid_amount)
        })
        
        # Publish event
        self.publish_event("order.payment_recorded", {
            "order_id": self.id,
            "order_number": self.order_number,
            "payment_amount": float(payment_amount),
            "total_paid": float(self.paid_amount),
            "outstanding_amount": float(self.outstanding_amount)
        })


class SalesOrderLineItem(CompanyBusinessObject):
    """
    Sales Order Line Item model for individual ordered products/services.
    
    Detailed line item information including product details,
    quantities, pricing, and fulfillment tracking.
    """
    
    __tablename__ = "sales_order_line_items"
    
    # Order reference
    order_id = Column(
        Integer,
        ForeignKey("sales_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Line identification
    line_number = Column(Integer, nullable=False)
    
    # Product/service information
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
    # order = relationship("SalesOrder", back_populates="line_items")
    
    def __str__(self):
        """String representation of order line item."""
        return f"Line {self.line_number}: {self.item_name} (Qty: {self.quantity_ordered})"
    
    def __repr__(self):
        """Detailed representation of order line item."""
        return (
            f"SalesOrderLineItem(id={self.id}, line_number={self.line_number}, "
            f"item_name='{self.item_name}', quantity={self.quantity_ordered})"
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
    
    @classmethod
    def from_quote_line_item(cls, quote_line_item, order_id: int, **kwargs):
        """
        Create an order line item from a quote line item.
        
        Args:
            quote_line_item: SalesQuoteLineItem instance to convert
            order_id: ID of the order this line item belongs to
            **kwargs: Additional line item-specific data
            
        Returns:
            SalesOrderLineItem: New order line item created from quote line item
        """
        # Create line item from quote line item data
        line_item_data = {
            'company_id': quote_line_item.company_id,
            'order_id': order_id,
            'line_number': quote_line_item.line_number,
            
            # Product/service information
            'product_id': quote_line_item.product_id,
            'product_variant_id': quote_line_item.product_variant_id,
            'item_code': quote_line_item.item_code,
            'item_name': quote_line_item.item_name,
            'description': quote_line_item.description,
            
            # Quantities - start with all quantity as ordered
            'quantity_ordered': quote_line_item.quantity,
            'unit_of_measure': quote_line_item.unit_of_measure,
            
            # Pricing from quote line item
            'unit_price': quote_line_item.unit_price,
            'discount_percentage': quote_line_item.discount_percentage,
            'discount_amount': quote_line_item.discount_amount,
            'line_total': quote_line_item.line_total,
            
            # Tax information
            'tax_percentage': quote_line_item.tax_percentage,
            'tax_amount': quote_line_item.tax_amount,
            'tax_code': quote_line_item.tax_code,
            
            # Product specifications and options
            'specifications': quote_line_item.specifications,
            'custom_options': quote_line_item.custom_options,
            
            # Delivery information (convert from quote)
            'required_date': kwargs.get('required_date', quote_line_item.delivery_date),
            
            # Additional attributes
            'notes': quote_line_item.notes,
            'custom_attributes': quote_line_item.custom_attributes,
        }
        
        # Override with any additional kwargs
        line_item_data.update(kwargs)
        
        # Create the line item
        line_item = cls(**line_item_data)
        
        # Calculate totals to ensure consistency
        line_item.calculate_line_total()
        
        return line_item
    
    def ship_quantity(self, quantity_to_ship: Decimal, user_id: int = None) -> None:
        """Ship specified quantity."""
        if quantity_to_ship > self.quantity_remaining:
            raise ValueError("Cannot ship more than remaining quantity")
        
        self.quantity_shipped += quantity_to_ship
        
        # Update shipped date if first shipment
        if not self.shipped_date:
            self.shipped_date = datetime.utcnow()
        
        # Log audit trail
        self.log_audit_trail("quantity_shipped", user_id, {
            "quantity_shipped": float(quantity_to_ship),
            "total_shipped": float(self.quantity_shipped),
            "remaining": float(self.quantity_remaining)
        })
        
        # Publish event
        self.publish_event("order_line.shipped", {
            "line_item_id": self.id,
            "order_id": self.order_id,
            "quantity_shipped": float(quantity_to_ship),
            "fully_shipped": self.is_fully_shipped
        })


class OrderShipment(CompanyBusinessObject):
    """
    Order Shipment model for tracking shipments.
    
    Manages shipment information including carrier details,
    tracking, and delivery status.
    """
    
    __tablename__ = "order_shipments"
    
    # Order reference
    order_id = Column(
        Integer,
        ForeignKey("sales_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Shipment identification
    shipment_number = Column(String(100), nullable=False, unique=True, index=True)
    
    # Carrier and shipping information
    carrier_name = Column(String(100), nullable=False)
    service_type = Column(String(100), nullable=True)  # Standard, Express, Overnight, etc.
    tracking_number = Column(String(255), nullable=True, index=True)
    
    # Status and dates
    status = Column(Enum(ShipmentStatus), nullable=False, default=ShipmentStatus.PREPARING, index=True)
    ship_date = Column(DateTime, nullable=True, index=True)
    estimated_delivery_date = Column(DateTime, nullable=True, index=True)
    actual_delivery_date = Column(DateTime, nullable=True, index=True)
    
    # Shipment details
    weight = Column(Numeric(10, 2), nullable=True)  # in pounds or kg
    weight_unit = Column(String(10), nullable=False, default="lbs")
    package_count = Column(Integer, nullable=False, default=1)
    
    # Costs
    shipping_cost = Column(Numeric(15, 2), nullable=True)
    insurance_cost = Column(Numeric(15, 2), nullable=True)
    
    # Addresses (JSON for flexibility)
    shipping_address = Column(JSON, nullable=False)
    return_address = Column(JSON, nullable=False)
    
    # Delivery information
    signature_required = Column(Boolean, nullable=False, default=False)
    delivery_instructions = Column(Text)
    delivered_to = Column(String(255), nullable=True)
    
    # Additional information
    notes = Column(Text)
    special_instructions = Column(Text)
    
    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    # order = relationship("SalesOrder", back_populates="shipments")
    
    def __str__(self):
        """String representation of shipment."""
        return f"Shipment {self.shipment_number}"
    
    def __repr__(self):
        """Detailed representation of shipment."""
        return (
            f"OrderShipment(id={self.id}, number='{self.shipment_number}', "
            f"status='{self.status.value}', carrier='{self.carrier_name}')"
        )
    
    @property
    def is_shipped(self) -> bool:
        """Check if shipment has been shipped."""
        return self.status not in [ShipmentStatus.PREPARING, ShipmentStatus.READY]
    
    @property
    def is_delivered(self) -> bool:
        """Check if shipment has been delivered."""
        return self.status == ShipmentStatus.DELIVERED
    
    @property
    def days_in_transit(self) -> Optional[int]:
        """Calculate days in transit."""
        if not self.ship_date:
            return None
        
        end_date = self.actual_delivery_date or datetime.utcnow()
        return (end_date - self.ship_date).days
    
    @property
    def is_overdue(self) -> bool:
        """Check if shipment is overdue for delivery."""
        if not self.estimated_delivery_date or self.is_delivered:
            return False
        return datetime.utcnow() > self.estimated_delivery_date
    
    def generate_shipment_number(self, prefix: str = "SHIP") -> str:
        """Generate shipment number if not provided."""
        import time
        timestamp = int(time.time())
        return f"{prefix}{timestamp:08d}"
    
    def ship(self, tracking_number: str = None, user_id: int = None) -> None:
        """Mark shipment as shipped."""
        self.status = ShipmentStatus.SHIPPED
        self.ship_date = datetime.utcnow()
        if tracking_number:
            self.tracking_number = tracking_number
        
        # Log audit trail
        self.log_audit_trail("shipment_shipped", user_id, {
            "tracking_number": tracking_number
        })
        
        # Publish event
        self.publish_event("shipment.shipped", {
            "shipment_id": self.id,
            "shipment_number": self.shipment_number,
            "order_id": self.order_id,
            "tracking_number": tracking_number
        })
    
    def mark_delivered(self, delivered_to: str = None, user_id: int = None) -> None:
        """Mark shipment as delivered."""
        self.status = ShipmentStatus.DELIVERED
        self.actual_delivery_date = datetime.utcnow()
        if delivered_to:
            self.delivered_to = delivered_to
        
        # Log audit trail
        self.log_audit_trail("shipment_delivered", user_id, {
            "delivered_to": delivered_to
        })
        
        # Publish event
        self.publish_event("shipment.delivered", {
            "shipment_id": self.id,
            "shipment_number": self.shipment_number,
            "order_id": self.order_id,
            "delivered_to": delivered_to
        })


class OrderInvoice(CompanyBusinessObject):
    """
    Order Invoice model for billing and payment tracking.
    
    Manages invoice generation, payment tracking,
    and accounts receivable functionality.
    """
    
    __tablename__ = "order_invoices"
    
    # Order reference
    order_id = Column(
        Integer,
        ForeignKey("sales_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Invoice identification
    invoice_number = Column(String(100), nullable=False, unique=True, index=True)
    invoice_type = Column(String(50), nullable=False, default="standard")  # standard, pro_forma, credit_note
    
    # Invoice status and dates
    status = Column(Enum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT, index=True)
    invoice_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    due_date = Column(DateTime, nullable=False, index=True)
    sent_date = Column(DateTime, nullable=True, index=True)
    
    # Financial information
    subtotal = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    outstanding_amount = Column(Numeric(15, 2), nullable=False)
    currency_code = Column(String(3), nullable=False, default="USD")
    
    # Payment terms
    payment_terms_days = Column(Integer, nullable=False, default=30)
    payment_terms_text = Column(String(255), nullable=True)
    
    # Invoice content
    line_items_data = Column(JSON, nullable=False)  # Snapshot of line items at time of invoicing
    billing_address = Column(JSON, nullable=False)
    
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
    notes = Column(Text)
    internal_notes = Column(Text)
    terms_and_conditions = Column(Text)
    
    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    # order = relationship("SalesOrder", back_populates="invoices")
    
    def __str__(self):
        """String representation of invoice."""
        return f"Invoice {self.invoice_number}"
    
    def __repr__(self):
        """Detailed representation of invoice."""
        return (
            f"OrderInvoice(id={self.id}, number='{self.invoice_number}', "
            f"status='{self.status.value}', total={self.total_amount})"
        )
    
    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue."""
        if self.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]:
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def days_overdue(self) -> int:
        """Calculate days overdue."""
        if not self.is_overdue:
            return 0
        return (datetime.utcnow() - self.due_date).days
    
    @property
    def is_paid(self) -> bool:
        """Check if invoice is fully paid."""
        return self.status == InvoiceStatus.PAID
    
    @property
    def payment_percentage(self) -> float:
        """Calculate payment percentage."""
        if self.total_amount <= 0:
            return 0.0
        return (self.paid_amount / self.total_amount) * 100
    
    def generate_invoice_number(self, prefix: str = "INV") -> str:
        """Generate invoice number if not provided."""
        import time
        timestamp = int(time.time())
        return f"{prefix}{timestamp:08d}"
    
    def send_to_customer(self, user_id: int = None, email_template: str = None) -> None:
        """Send invoice to customer."""
        self.status = InvoiceStatus.SENT
        self.sent_date = datetime.utcnow()
        self.email_sent_count += 1
        self.last_email_sent = datetime.utcnow()
        
        # Log audit trail
        self.log_audit_trail("invoice_sent", user_id, {
            "email_template": email_template
        })
        
        # Publish event
        self.publish_event("invoice.sent", {
            "invoice_id": self.id,
            "invoice_number": self.invoice_number,
            "order_id": self.order_id,
            "total_amount": float(self.total_amount)
        })
    
    def record_payment(self, payment_amount: Decimal, payment_method: str = None,
                      user_id: int = None) -> None:
        """Record payment against invoice."""
        self.paid_amount += payment_amount
        self.outstanding_amount = self.total_amount - self.paid_amount
        
        # Update status
        if self.outstanding_amount <= 0:
            self.status = InvoiceStatus.PAID
        
        # Log audit trail
        self.log_audit_trail("payment_recorded", user_id, {
            "payment_amount": float(payment_amount),
            "payment_method": payment_method,
            "total_paid": float(self.paid_amount)
        })
        
        # Publish event
        self.publish_event("invoice.payment_recorded", {
            "invoice_id": self.id,
            "invoice_number": self.invoice_number,
            "payment_amount": float(payment_amount),
            "total_paid": float(self.paid_amount),
            "is_fully_paid": self.is_paid
        })
    
    def mark_overdue(self, user_id: int = None) -> None:
        """Mark invoice as overdue."""
        if self.status not in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]:
            self.status = InvoiceStatus.OVERDUE
            
            # Log audit trail
            self.log_audit_trail("invoice_overdue", user_id, {
                "days_overdue": self.days_overdue
            })
            
            # Publish event
            self.publish_event("invoice.overdue", {
                "invoice_id": self.id,
                "invoice_number": self.invoice_number,
                "days_overdue": self.days_overdue,
                "outstanding_amount": float(self.outstanding_amount)
            })