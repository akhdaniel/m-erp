"""
Purchase Order models using Business Object Framework
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

# Import Business Object Framework base classes
# These would be imported from the company-partner-service framework
# For now, we'll define the interface they would provide
from purchasing_module.framework.base import CompanyBusinessObject, BaseModel


class PurchaseOrderStatus(str, enum.Enum):
    """Purchase order status enumeration"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT_TO_SUPPLIER = "sent_to_supplier"
    ACKNOWLEDGED = "acknowledged"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    INVOICED = "invoiced"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PurchaseOrderPriority(str, enum.Enum):
    """Purchase order priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class PurchaseOrder(CompanyBusinessObject):
    """
    Purchase Order model for procurement management.
    
    Represents a purchase order with line items, approval workflow,
    and supplier integration using the Business Object Framework.
    """
    
    __tablename__ = "purchase_orders"
    
    # Basic Information
    po_number = Column(String(50), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Supplier Information (Partner integration)
    supplier_id = Column(
        Integer,
        ForeignKey("partners.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    supplier_contact_id = Column(
        Integer,
        ForeignKey("partner_contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Financial Information
    currency_code = Column(String(3), nullable=False, default="USD")
    exchange_rate = Column(Numeric(12, 6), nullable=False, default=1.0)
    subtotal = Column(Numeric(15, 2), nullable=False, default=0.0)
    tax_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    shipping_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    discount_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    total_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    
    # Status and Workflow
    status = Column(Enum(PurchaseOrderStatus), nullable=False, default=PurchaseOrderStatus.DRAFT, index=True)
    priority = Column(Enum(PurchaseOrderPriority), nullable=False, default=PurchaseOrderPriority.NORMAL, index=True)
    
    # Dates
    order_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    required_date = Column(DateTime, nullable=True, index=True)
    promised_date = Column(DateTime, nullable=True)
    approved_date = Column(DateTime, nullable=True)
    sent_date = Column(DateTime, nullable=True)
    
    # Approval Information
    approved_by_user_id = Column(Integer, nullable=True, index=True)
    approval_notes = Column(Text)
    
    # Additional Information
    terms_and_conditions = Column(Text)
    notes = Column(Text)
    internal_notes = Column(Text)
    reference_number = Column(String(100))
    
    # Delivery Information
    delivery_address = Column(Text)
    delivery_contact = Column(String(255))
    delivery_phone = Column(String(50))
    delivery_instructions = Column(Text)
    
    # Tracking
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    line_items = relationship("PurchaseOrderLineItem", back_populates="purchase_order", cascade="all, delete-orphan")
    approval_workflow = relationship("ApprovalWorkflow", back_populates="purchase_order", uselist=False)
    
    # Business Object Framework will automatically add:
    # - company relationship
    # - audit trail
    # - event publishing
    # - created_at, updated_at timestamps
    
    def __str__(self):
        """String representation of the purchase order."""
        return f"PO {self.po_number}: {self.title} - {self.status.value} - {self.currency_code} {self.total_amount}"
    
    def __repr__(self):
        """Detailed representation of the purchase order."""
        return (
            f"PurchaseOrder(id={self.id}, po_number='{self.po_number}', "
            f"supplier_id={self.supplier_id}, status='{self.status.value}', "
            f"total={self.currency_code} {self.total_amount})"
        )
    
    @property
    def is_approved(self) -> bool:
        """Check if purchase order is approved."""
        return self.status in [
            PurchaseOrderStatus.APPROVED,
            PurchaseOrderStatus.SENT_TO_SUPPLIER,
            PurchaseOrderStatus.ACKNOWLEDGED,
            PurchaseOrderStatus.PARTIALLY_RECEIVED,
            PurchaseOrderStatus.RECEIVED,
            PurchaseOrderStatus.INVOICED,
            PurchaseOrderStatus.COMPLETED
        ]
    
    @property
    def is_editable(self) -> bool:
        """Check if purchase order can be edited."""
        return self.status in [
            PurchaseOrderStatus.DRAFT,
            PurchaseOrderStatus.REJECTED
        ]
    
    @property
    def requires_approval(self) -> bool:
        """Check if purchase order requires approval."""
        return self.status == PurchaseOrderStatus.PENDING_APPROVAL
    
    @property
    def can_be_cancelled(self) -> bool:
        """Check if purchase order can be cancelled."""
        return self.status not in [
            PurchaseOrderStatus.RECEIVED,
            PurchaseOrderStatus.INVOICED,
            PurchaseOrderStatus.COMPLETED,
            PurchaseOrderStatus.CANCELLED
        ]
    
    def calculate_totals(self) -> None:
        """Calculate and update totals based on line items."""
        if not self.line_items:
            self.subtotal = Decimal('0.00')
        else:
            self.subtotal = sum(item.line_total for item in self.line_items)
        
        # Calculate total amount
        self.total_amount = (
            self.subtotal + 
            self.tax_amount + 
            self.shipping_amount - 
            self.discount_amount
        )
    
    def generate_po_number(self, company_prefix: str = "PO") -> str:
        """Generate unique PO number."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d")
        # This would typically use a sequence or counter from the database
        # For now, using a simple format
        return f"{company_prefix}-{timestamp}-{self.id or 'NEW'}"
    
    def can_approve(self, user_permissions: List[str], amount_limit: Optional[Decimal] = None) -> bool:
        """
        Check if user can approve this purchase order.
        
        Args:
            user_permissions: List of user permissions
            amount_limit: Maximum amount user can approve (optional)
        
        Returns:
            bool: True if user can approve
        """
        if "purchasing.approve" not in user_permissions:
            return False
        
        if amount_limit and self.total_amount > amount_limit:
            return False
        
        return self.status == PurchaseOrderStatus.PENDING_APPROVAL
    
    def submit_for_approval(self) -> bool:
        """Submit purchase order for approval."""
        if self.status != PurchaseOrderStatus.DRAFT:
            return False
        
        if not self.line_items:
            return False
        
        self.calculate_totals()
        self.status = PurchaseOrderStatus.PENDING_APPROVAL
        return True
    
    def approve(self, approved_by_user_id: int, notes: Optional[str] = None) -> bool:
        """Approve the purchase order."""
        if self.status != PurchaseOrderStatus.PENDING_APPROVAL:
            return False
        
        self.status = PurchaseOrderStatus.APPROVED
        self.approved_by_user_id = approved_by_user_id
        self.approved_date = datetime.utcnow()
        if notes:
            self.approval_notes = notes
        
        return True
    
    def reject(self, notes: Optional[str] = None) -> bool:
        """Reject the purchase order."""
        if self.status != PurchaseOrderStatus.PENDING_APPROVAL:
            return False
        
        self.status = PurchaseOrderStatus.REJECTED
        if notes:
            self.approval_notes = notes
        
        return True


class PurchaseOrderLineItem(BaseModel):
    """
    Purchase Order Line Item model.
    
    Represents individual items within a purchase order.
    """
    
    __tablename__ = "purchase_order_line_items"
    
    # Foreign key to purchase order
    purchase_order_id = Column(
        Integer,
        ForeignKey("purchase_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Line item details
    line_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    
    # Product information (could link to product catalog in future)
    product_code = Column(String(100))
    unit_of_measure = Column(String(20), nullable=False, default="each")
    
    # Quantities
    quantity_ordered = Column(Numeric(12, 3), nullable=False)
    quantity_received = Column(Numeric(12, 3), nullable=False, default=0.0)
    
    # Pricing
    unit_price = Column(Numeric(15, 4), nullable=False)
    line_total = Column(Numeric(15, 2), nullable=False)
    
    # Dates
    required_date = Column(DateTime, nullable=True)
    promised_date = Column(DateTime, nullable=True)
    
    # Notes
    notes = Column(Text)
    supplier_part_number = Column(String(100))
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="line_items")
    
    def __str__(self):
        """String representation of the line item."""
        return f"Line {self.line_number}: {self.description} - Qty: {self.quantity_ordered} @ {self.unit_price}"
    
    def __repr__(self):
        """Detailed representation of the line item."""
        return (
            f"PurchaseOrderLineItem(id={self.id}, po_id={self.purchase_order_id}, "
            f"line={self.line_number}, qty={self.quantity_ordered}, price={self.unit_price})"
        )
    
    def calculate_line_total(self) -> None:
        """Calculate and update the line total."""
        self.line_total = self.quantity_ordered * self.unit_price
    
    @property
    def is_fully_received(self) -> bool:
        """Check if line item is fully received."""
        return self.quantity_received >= self.quantity_ordered
    
    @property
    def quantity_outstanding(self) -> Decimal:
        """Get outstanding quantity to be received."""
        return max(Decimal('0'), self.quantity_ordered - self.quantity_received)
    
    @property 
    def received_percentage(self) -> float:
        """Get percentage of quantity received."""
        if self.quantity_ordered == 0:
            return 0.0
        return float((self.quantity_received / self.quantity_ordered) * 100)
    
    def receive_quantity(self, quantity: Decimal) -> bool:
        """
        Receive a quantity for this line item.
        
        Args:
            quantity: Quantity being received
            
        Returns:
            bool: True if successful, False if invalid quantity
        """
        if quantity <= 0:
            return False
        
        if self.quantity_received + quantity > self.quantity_ordered:
            return False
        
        self.quantity_received += quantity
        return True