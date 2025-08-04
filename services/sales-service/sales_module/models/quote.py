"""
Quote management models for sales proposals and pricing.

Provides comprehensive quote generation and management including
versioning, approval workflows, and conversion to orders.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from sales_module.framework.base import CompanyBusinessObject, BaseModel


class QuoteStatus(str, enum.Enum):
    """Quote status enumeration"""
    DRAFT = "draft"  # Draft quote
    PENDING_APPROVAL = "pending_approval"  # Waiting for approval
    APPROVED = "approved"  # Approved quote
    SENT = "sent"  # Sent to customer
    ACCEPTED = "accepted"  # Accepted by customer
    REJECTED = "rejected"  # Rejected by customer
    EXPIRED = "expired"  # Quote expired
    CONVERTED = "converted"  # Converted to order
    CANCELLED = "cancelled"  # Cancelled quote


class ApprovalStatus(str, enum.Enum):
    """Approval status enumeration"""
    PENDING = "pending"  # Pending approval
    APPROVED = "approved"  # Approved
    REJECTED = "rejected"  # Rejected
    ESCALATED = "escalated"  # Escalated to higher authority


class LineItemType(str, enum.Enum):
    """Line item type enumeration"""
    PRODUCT = "product"  # Physical product
    SERVICE = "service"  # Service item
    DISCOUNT = "discount"  # Discount line
    SHIPPING = "shipping"  # Shipping charge
    TAX = "tax"  # Tax line
    MISC = "misc"  # Miscellaneous item


class SalesQuote(CompanyBusinessObject):
    """
    Sales Quote model for managing customer quotes and proposals.
    
    Comprehensive quote management including versioning, approval workflows,
    pricing calculations, and conversion to sales orders.
    """
    
    __tablename__ = "sales_quotes"
    
    # Basic quote information
    quote_number = Column(String(100), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Customer and opportunity references
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
    
    # Quote status and workflow
    status = Column(Enum(QuoteStatus), nullable=False, default=QuoteStatus.DRAFT, index=True)
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
    
    # Quote validity and terms
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=False, index=True)
    payment_terms_days = Column(Integer, nullable=False, default=30)
    delivery_terms = Column(String(255), nullable=True)
    
    # Quote preparation and sending
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
    
    # Conversion information
    converted_to_order_id = Column(Integer, nullable=True, index=True)
    converted_date = Column(DateTime, nullable=True)
    converted_by_user_id = Column(Integer, nullable=True)
    
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
    internal_notes = Column(Text)
    terms_and_conditions = Column(Text)
    custom_fields = Column(JSON)
    tags = Column(JSON)  # Array of string tags
    
    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    # customer = relationship("Customer", back_populates="quotes")
    # opportunity = relationship("SalesOpportunity", back_populates="quotes")
    # line_items = relationship("SalesQuoteLineItem", back_populates="quote", cascade="all, delete-orphan")
    # versions = relationship("QuoteVersion", back_populates="quote", cascade="all, delete-orphan")
    # approvals = relationship("QuoteApproval", back_populates="quote", cascade="all, delete-orphan")
    
    def __str__(self):
        """String representation of sales quote."""
        return f"Quote {self.quote_number} v{self.version}"
    
    def __repr__(self):
        """Detailed representation of sales quote."""
        return (
            f"SalesQuote(id={self.id}, number='{self.quote_number}', "
            f"version={self.version}, status='{self.status.value}', total={self.total_amount})"
        )
    
    @property
    def display_identifier(self) -> str:
        """Get display identifier with quote number and version."""
        return f"{self.quote_number} v{self.version} - {self.title}"
    
    @property
    def is_expired(self) -> bool:
        """Check if quote is expired."""
        return datetime.utcnow() > self.valid_until
    
    @property
    def days_until_expiry(self) -> int:
        """Calculate days until quote expires."""
        delta = self.valid_until - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def is_open(self) -> bool:
        """Check if quote is in open status."""
        open_statuses = [QuoteStatus.DRAFT, QuoteStatus.PENDING_APPROVAL, 
                        QuoteStatus.APPROVED, QuoteStatus.SENT]
        return self.status in open_statuses
    
    @property
    def is_closed(self) -> bool:
        """Check if quote is closed."""
        return not self.is_open
    
    @property
    def gross_margin(self) -> Optional[Decimal]:
        """Calculate gross margin amount."""
        if not self.total_cost:
            return None
        return self.total_amount - self.total_cost
    
    @property
    def gross_margin_percentage(self) -> Optional[float]:
        """Calculate gross margin percentage."""
        if not self.total_cost or self.total_amount <= 0:
            return None
        margin = (self.total_amount - self.total_cost) / self.total_amount * 100
        return float(margin)
    
    def generate_quote_number(self, prefix: str = "QUO") -> str:
        """Generate quote number if not provided."""
        # In production, would use company settings and sequence numbers
        import time
        timestamp = int(time.time())
        return f"{prefix}{timestamp:08d}"
    
    def calculate_totals(self) -> None:
        """Calculate quote totals from line items."""
        # In production, would calculate from actual line items
        # This would sum up all line item amounts, discounts, taxes, etc.
        
        # Update margin percentage if cost is available
        if self.total_cost and self.total_amount > 0:
            self.margin_percentage = self.gross_margin_percentage
    
    def apply_overall_discount(self, discount_percentage: Decimal) -> None:
        """Apply overall discount to quote."""
        self.overall_discount_percentage = discount_percentage
        self.discount_amount = (self.subtotal * discount_percentage) / 100
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount + self.shipping_amount
        
        # Recalculate margin
        if self.total_cost:
            self.margin_percentage = self.gross_margin_percentage
    
    def extend_validity(self, additional_days: int, user_id: int = None) -> None:
        """Extend quote validity period."""
        old_valid_until = self.valid_until
        self.valid_until = self.valid_until + timedelta(days=additional_days)
        
        # Log audit trail
        self.log_audit_trail("validity_extended", user_id, {
            "old_valid_until": old_valid_until.isoformat(),
            "new_valid_until": self.valid_until.isoformat(),
            "additional_days": additional_days
        })
        
        # Publish event
        self.publish_event("quote.validity_extended", {
            "quote_id": self.id,
            "quote_number": self.quote_number,
            "new_valid_until": self.valid_until.isoformat()
        })
    
    def send_to_customer(self, user_id: int, email_template: str = None) -> None:
        """Send quote to customer."""
        self.status = QuoteStatus.SENT
        self.sent_date = datetime.utcnow()
        self.sent_by_user_id = user_id
        self.email_sent_count += 1
        self.last_email_sent = datetime.utcnow()
        
        # Log audit trail
        self.log_audit_trail("quote_sent", user_id, {
            "email_template": email_template,
            "customer_id": self.customer_id
        })
        
        # Publish event
        self.publish_event("quote.sent", {
            "quote_id": self.id,
            "quote_number": self.quote_number,
            "customer_id": self.customer_id,
            "total_amount": float(self.total_amount)
        })
    
    def mark_accepted(self, user_id: int = None, notes: str = None) -> None:
        """Mark quote as accepted by customer."""
        self.status = QuoteStatus.ACCEPTED
        self.customer_response_date = datetime.utcnow()
        if notes:
            self.customer_response_notes = notes
        
        # Log audit trail
        self.log_audit_trail("quote_accepted", user_id, {
            "response_notes": notes
        })
        
        # Publish event
        self.publish_event("quote.accepted", {
            "quote_id": self.id,
            "quote_number": self.quote_number,
            "customer_id": self.customer_id,
            "total_amount": float(self.total_amount)
        })
    
    def mark_rejected(self, reason: str, user_id: int = None, notes: str = None) -> None:
        """Mark quote as rejected by customer."""
        self.status = QuoteStatus.REJECTED
        self.customer_response_date = datetime.utcnow()
        self.rejection_reason = reason
        if notes:
            self.customer_response_notes = notes
        
        # Log audit trail
        self.log_audit_trail("quote_rejected", user_id, {
            "rejection_reason": reason,
            "response_notes": notes
        })
        
        # Publish event
        self.publish_event("quote.rejected", {
            "quote_id": self.id,
            "quote_number": self.quote_number,
            "customer_id": self.customer_id,
            "rejection_reason": reason
        })
    
    def convert_to_order(self, user_id: int, order_id: int = None) -> None:
        """Convert quote to sales order."""
        self.status = QuoteStatus.CONVERTED
        self.converted_date = datetime.utcnow()
        self.converted_by_user_id = user_id
        if order_id:
            self.converted_to_order_id = order_id
        
        # Log audit trail
        self.log_audit_trail("quote_converted", user_id, {
            "order_id": order_id
        })
        
        # Publish event
        self.publish_event("quote.converted", {
            "quote_id": self.id,
            "quote_number": self.quote_number,
            "order_id": order_id,
            "customer_id": self.customer_id,
            "total_amount": float(self.total_amount)
        })
    
    def create_new_version(self, user_id: int, reason: str = None) -> 'SalesQuote':
        """Create a new version of the quote."""
        # Archive current version
        current_version = QuoteVersion(
            company_id=self.company_id,
            quote_id=self.id,
            version_number=self.version,
            created_by_user_id=user_id,
            change_reason=reason or "New version created",
            quote_data=self.to_dict()
        )
        
        # Increment version
        self.version += 1
        self.status = QuoteStatus.DRAFT  # Reset to draft for editing
        
        # Log audit trail
        self.log_audit_trail("new_version_created", user_id, {
            "new_version": self.version,
            "reason": reason
        })
        
        return current_version


class SalesQuoteLineItem(CompanyBusinessObject):
    """
    Sales Quote Line Item model for individual quoted products/services.
    
    Detailed line item information including product details,
    pricing, discounts, and calculations.
    """
    
    __tablename__ = "sales_quote_line_items"
    
    # Quote reference
    quote_id = Column(
        Integer,
        ForeignKey("sales_quotes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Line identification
    line_number = Column(Integer, nullable=False)
    
    # Product/service information
    line_type = Column(Enum(LineItemType), nullable=False, default=LineItemType.PRODUCT, index=True)
    product_id = Column(Integer, nullable=True, index=True)  # Reference to inventory product
    product_variant_id = Column(Integer, nullable=True, index=True)
    
    # Item details
    item_code = Column(String(100), nullable=True, index=True)
    item_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Quantity and units
    quantity = Column(Numeric(15, 4), nullable=False, default=1.0)
    unit_of_measure = Column(String(50), nullable=False, default="each")
    
    # Pricing
    unit_price = Column(Numeric(15, 4), nullable=False)
    list_price = Column(Numeric(15, 4), nullable=True)  # Original list price
    unit_cost = Column(Numeric(15, 4), nullable=True)  # Cost for margin calculation
    
    # Discounts
    discount_percentage = Column(Numeric(5, 2), nullable=False, default=0.0)
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    
    # Calculations
    line_total = Column(Numeric(15, 2), nullable=False)  # (quantity * unit_price) - discount
    line_cost = Column(Numeric(15, 2), nullable=True)  # quantity * unit_cost
    
    # Tax information
    tax_percentage = Column(Numeric(5, 2), nullable=False, default=0.0)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    tax_code = Column(String(50), nullable=True)
    
    # Product specifications
    specifications = Column(JSON)  # Product-specific specifications
    custom_options = Column(JSON)  # Customization options
    
    # Delivery information
    lead_time_days = Column(Integer, nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    
    # Pricing rules and promotions
    price_rule_id = Column(Integer, nullable=True, index=True)
    promotion_id = Column(Integer, nullable=True, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Additional attributes
    notes = Column(Text)
    custom_attributes = Column(JSON)
    
    # Relationships
    # quote = relationship("SalesQuote", back_populates="line_items")
    
    def __str__(self):
        """String representation of quote line item."""
        return f"Line {self.line_number}: {self.item_name} (Qty: {self.quantity})"
    
    def __repr__(self):
        """Detailed representation of quote line item."""
        return (
            f"SalesQuoteLineItem(id={self.id}, line_number={self.line_number}, "
            f"item_name='{self.item_name}', quantity={self.quantity}, total={self.line_total})"
        )
    
    @property
    def unit_margin(self) -> Optional[Decimal]:
        """Calculate unit margin."""
        if not self.unit_cost:
            return None
        return self.unit_price - self.unit_cost
    
    @property
    def margin_percentage(self) -> Optional[float]:
        """Calculate margin percentage."""
        if not self.unit_cost or self.unit_price <= 0:
            return None
        margin = ((self.unit_price - self.unit_cost) / self.unit_price) * 100
        return float(margin)
    
    @property
    def line_margin(self) -> Optional[Decimal]:
        """Calculate total line margin."""
        if not self.line_cost:
            return None
        return self.line_total - self.line_cost
    
    @property
    def effective_unit_price(self) -> Decimal:
        """Calculate effective unit price after discounts."""
        if self.discount_percentage > 0:
            return self.unit_price * (1 - self.discount_percentage / 100)
        return self.unit_price - (self.discount_amount / self.quantity if self.quantity > 0 else 0)
    
    def calculate_line_total(self) -> None:
        """Calculate line total with discounts."""
        gross_total = self.quantity * self.unit_price
        
        # Apply discount
        if self.discount_percentage > 0:
            self.discount_amount = gross_total * (self.discount_percentage / 100)
        
        self.line_total = gross_total - self.discount_amount
        
        # Calculate line cost if unit cost is available
        if self.unit_cost:
            self.line_cost = self.quantity * self.unit_cost
        
        # Calculate tax
        if self.tax_percentage > 0:
            self.tax_amount = self.line_total * (self.tax_percentage / 100)
    
    def apply_discount(self, discount_percentage: Decimal = None, 
                      discount_amount: Decimal = None) -> None:
        """Apply discount to line item."""
        if discount_percentage is not None:
            self.discount_percentage = discount_percentage
            self.discount_amount = (self.quantity * self.unit_price) * (discount_percentage / 100)
        elif discount_amount is not None:
            self.discount_amount = discount_amount
            if self.quantity > 0 and self.unit_price > 0:
                self.discount_percentage = (discount_amount / (self.quantity * self.unit_price)) * 100
        
        self.calculate_line_total()
    
    def update_pricing(self, new_unit_price: Decimal, recalculate: bool = True) -> None:
        """Update unit price and recalculate totals."""
        self.unit_price = new_unit_price
        if recalculate:
            self.calculate_line_total()


class QuoteVersion(CompanyBusinessObject):
    """
    Quote Version model for tracking quote revision history.
    
    Maintains complete history of quote changes with
    version control and change tracking.
    """
    
    __tablename__ = "quote_versions"
    
    # Quote reference
    quote_id = Column(
        Integer,
        ForeignKey("sales_quotes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Version information
    version_number = Column(Integer, nullable=False, index=True)
    created_by_user_id = Column(Integer, nullable=False, index=True)
    change_reason = Column(String(255), nullable=True)
    change_summary = Column(Text)
    
    # Snapshot data
    quote_data = Column(JSON, nullable=False)  # Complete quote snapshot
    line_items_data = Column(JSON, nullable=True)  # Line items snapshot
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    # quote = relationship("SalesQuote", back_populates="versions")
    
    def __str__(self):
        """String representation of quote version."""
        return f"Version {self.version_number} - {self.change_reason}"
    
    def __repr__(self):
        """Detailed representation of quote version."""
        return (
            f"QuoteVersion(id={self.id}, quote_id={self.quote_id}, "
            f"version={self.version_number}, reason='{self.change_reason}')"
        )


class QuoteApproval(CompanyBusinessObject):
    """
    Quote Approval model for approval workflow management.
    
    Tracks approval requests, responses, and escalation
    for quotes requiring management approval.
    """
    
    __tablename__ = "quote_approvals"
    
    # Quote reference
    quote_id = Column(
        Integer,
        ForeignKey("sales_quotes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Approval workflow
    approval_level = Column(Integer, nullable=False, default=1)  # 1=Manager, 2=Director, etc.
    requested_by_user_id = Column(Integer, nullable=False, index=True)
    assigned_to_user_id = Column(Integer, nullable=False, index=True)
    
    # Approval request information
    request_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    request_reason = Column(Text)
    urgency_level = Column(String(20), nullable=False, default="normal")  # low, normal, high, urgent
    
    # Approval response
    status = Column(Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING, index=True)
    response_date = Column(DateTime, nullable=True, index=True)
    response_by_user_id = Column(Integer, nullable=True, index=True)
    response_notes = Column(Text)
    
    # Escalation information
    escalated_date = Column(DateTime, nullable=True)
    escalated_to_user_id = Column(Integer, nullable=True, index=True)
    escalation_reason = Column(String(255), nullable=True)
    
    # Due dates and SLA
    due_date = Column(DateTime, nullable=True, index=True)
    sla_hours = Column(Integer, nullable=False, default=24)  # SLA in hours
    
    # Approval criteria
    discount_percentage = Column(Numeric(5, 2), nullable=True)
    quote_total = Column(Numeric(15, 2), nullable=True)
    margin_percentage = Column(Numeric(5, 2), nullable=True)
    
    # Additional information
    attachments = Column(JSON)  # Supporting documents
    approval_notes = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    # quote = relationship("SalesQuote", back_populates="approvals")
    
    def __str__(self):
        """String representation of quote approval."""
        return f"Approval Level {self.approval_level} - {self.status.value}"
    
    def __repr__(self):
        """Detailed representation of quote approval."""
        return (
            f"QuoteApproval(id={self.id}, quote_id={self.quote_id}, "
            f"level={self.approval_level}, status='{self.status.value}')"
        )
    
    @property
    def is_overdue(self) -> bool:
        """Check if approval is overdue."""
        if not self.due_date or self.status != ApprovalStatus.PENDING:
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def hours_remaining(self) -> Optional[float]:
        """Calculate hours remaining until due date."""
        if not self.due_date or self.status != ApprovalStatus.PENDING:
            return None
        delta = self.due_date - datetime.utcnow()
        return delta.total_seconds() / 3600
    
    @property
    def response_time_hours(self) -> Optional[float]:
        """Calculate response time in hours."""
        if not self.response_date:
            return None
        delta = self.response_date - self.request_date
        return delta.total_seconds() / 3600
    
    def approve(self, approver_user_id: int, notes: str = None) -> None:
        """Approve the quote."""
        self.status = ApprovalStatus.APPROVED
        self.response_date = datetime.utcnow()
        self.response_by_user_id = approver_user_id
        if notes:
            self.response_notes = notes
        
        # Log audit trail
        self.log_audit_trail("approval_granted", approver_user_id, {
            "approval_level": self.approval_level,
            "response_notes": notes
        })
        
        # Publish event
        self.publish_event("quote_approval.approved", {
            "approval_id": self.id,
            "quote_id": self.quote_id,
            "approval_level": self.approval_level,
            "approver_id": approver_user_id
        })
    
    def reject(self, rejector_user_id: int, reason: str) -> None:
        """Reject the quote approval."""
        self.status = ApprovalStatus.REJECTED
        self.response_date = datetime.utcnow()
        self.response_by_user_id = rejector_user_id
        self.response_notes = reason
        
        # Log audit trail
        self.log_audit_trail("approval_rejected", rejector_user_id, {
            "approval_level": self.approval_level,
            "rejection_reason": reason
        })
        
        # Publish event
        self.publish_event("quote_approval.rejected", {
            "approval_id": self.id,
            "quote_id": self.quote_id,
            "approval_level": self.approval_level,
            "rejector_id": rejector_user_id,
            "rejection_reason": reason
        })
    
    def escalate(self, escalated_to_user_id: int, reason: str, escalated_by_user_id: int = None) -> None:
        """Escalate approval to higher authority."""
        self.status = ApprovalStatus.ESCALATED
        self.escalated_date = datetime.utcnow()
        self.escalated_to_user_id = escalated_to_user_id
        self.escalation_reason = reason
        
        # Extend due date for escalation
        self.due_date = datetime.utcnow() + timedelta(hours=self.sla_hours)
        
        # Log audit trail
        self.log_audit_trail("approval_escalated", escalated_by_user_id, {
            "escalated_to": escalated_to_user_id,
            "escalation_reason": reason
        })
        
        # Publish event
        self.publish_event("quote_approval.escalated", {
            "approval_id": self.id,
            "quote_id": self.quote_id,
            "escalated_to": escalated_to_user_id,
            "escalation_reason": reason
        })