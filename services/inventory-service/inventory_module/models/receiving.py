"""
Receiving models for tracking inbound inventory from purchase orders
and other sources with detailed line item tracking and quality control.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from inventory_module.framework.base import CompanyBusinessObject, BaseModel


class ReceivingStatus(str, enum.Enum):
    """Receiving record status enumeration"""
    PENDING = "pending"  # Awaiting delivery
    PARTIAL = "partial"  # Partially received
    COMPLETE = "complete"  # Fully received
    CANCELLED = "cancelled"  # Cancelled receipt
    ON_HOLD = "on_hold"  # Receipt on hold


class ReceivingLineStatus(str, enum.Enum):
    """Receiving line item status enumeration"""
    PENDING = "pending"  # Not yet received
    PARTIAL = "partial"  # Partially received
    COMPLETE = "complete"  # Fully received
    OVER_RECEIVED = "over_received"  # Received more than expected
    DAMAGED = "damaged"  # Received damaged
    REJECTED = "rejected"  # Quality rejected


class ReceivingRecord(CompanyBusinessObject):
    """
    Receiving Record model for tracking inbound inventory receipts.
    
    Manages receiving process for purchase orders and other
    inbound inventory with approval workflow and quality control.
    """
    
    __tablename__ = "receiving_records"
    
    # Receipt identification
    receipt_number = Column(String(100), nullable=False, unique=True, index=True)
    
    # Source document references
    source_document_type = Column(String(50), nullable=False, index=True)  # 'purchase_order', 'transfer', etc.
    source_document_id = Column(Integer, nullable=False, index=True)
    source_document_number = Column(String(100), nullable=True, index=True)
    
    # Supplier information
    supplier_id = Column(Integer, nullable=False, index=True)  # Foreign key to Partner
    supplier_invoice_number = Column(String(100), nullable=True, index=True)
    supplier_delivery_note = Column(String(100), nullable=True)
    
    # Warehouse and location
    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    receiving_location_id = Column(
        Integer,
        ForeignKey("warehouse_locations.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )
    
    # Receipt dates and scheduling
    expected_date = Column(DateTime, nullable=True, index=True)
    received_date = Column(DateTime, nullable=True, index=True)
    scheduled_date = Column(DateTime, nullable=True)
    
    # Status and workflow
    status = Column(Enum(ReceivingStatus), nullable=False, default=ReceivingStatus.PENDING, index=True)
    
    # Totals and financial
    total_quantity_expected = Column(Numeric(15, 4), nullable=False, default=0.0)
    total_quantity_received = Column(Numeric(15, 4), nullable=False, default=0.0)
    total_value_expected = Column(Numeric(15, 2), nullable=True)
    total_value_received = Column(Numeric(15, 2), nullable=True)
    
    # Quality control
    quality_inspection_required = Column(Boolean, default=False, nullable=False)
    quality_inspection_passed = Column(Boolean, nullable=True)
    quality_notes = Column(Text)
    
    # User tracking
    received_by_user_id = Column(Integer, nullable=True, index=True)
    approved_by_user_id = Column(Integer, nullable=True, index=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Carrier and shipping information
    carrier_name = Column(String(255))
    tracking_number = Column(String(100), index=True)
    freight_cost = Column(Numeric(10, 2))
    
    # Documentation
    notes = Column(Text)
    attachments = Column(JSON)  # Array of document references
    
    # System fields
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    # warehouse = relationship("Warehouse", back_populates="receiving_records")
    # receiving_location = relationship("WarehouseLocation", back_populates="receiving_records")
    # line_items = relationship("ReceivingLineItem", back_populates="receiving_record", cascade="all, delete-orphan")
    
    def __str__(self):
        """String representation of receiving record."""
        return f"Receipt {self.receipt_number} - {self.status.value}"
    
    def __repr__(self):
        """Detailed representation of receiving record."""
        return (
            f"ReceivingRecord(id={self.id}, receipt_number='{self.receipt_number}', "
            f"status='{self.status.value}', supplier_id={self.supplier_id})"
        )
    
    @property
    def is_complete(self) -> bool:
        """Check if receiving is complete."""
        return self.status == ReceivingStatus.COMPLETE
    
    @property
    def is_overdue(self) -> bool:
        """Check if receipt is overdue."""
        if not self.expected_date or self.is_complete:
            return False
        return datetime.utcnow() > self.expected_date
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_quantity_expected <= 0:
            return 0.0
        return float((self.total_quantity_received / self.total_quantity_expected) * 100)
    
    @property
    def line_item_count(self) -> int:
        """Get number of line items."""
        # In production, would count related line items
        return 0  # Simplified for demo
    
    @property
    def pending_line_items(self) -> int:
        """Get number of pending line items."""
        # In production, would count pending line items
        return 0  # Simplified for demo
    
    def generate_receipt_number(self, prefix: str = "REC") -> str:
        """Generate receipt number if not provided."""
        # In production, would use company settings and sequence numbers
        import time
        timestamp = int(time.time())
        return f"{prefix}{timestamp:08d}"
    
    def can_be_received(self) -> bool:
        """Check if receipt can be processed."""
        return self.status in [ReceivingStatus.PENDING, ReceivingStatus.PARTIAL]
    
    def calculate_totals(self) -> None:
        """Calculate total quantities and values from line items."""
        # In production, would calculate from actual line items
        # For now, these would be set when line items are added
        pass
    
    def start_receiving(self, user_id: int) -> None:
        """Start the receiving process."""
        if not self.can_be_received():
            raise ValueError("Receipt cannot be started in current status")
        
        self.received_by_user_id = user_id
        self.received_date = datetime.utcnow()
        
        # Log audit trail
        self.log_audit_trail("receiving_started", user_id)
        
        # Publish event
        self.publish_event("receiving_record.started", {
            "receipt_number": self.receipt_number,
            "user_id": user_id
        })
    
    def complete_receiving(self, user_id: int) -> None:
        """Complete the receiving process."""
        self.status = ReceivingStatus.COMPLETE
        self.received_date = datetime.utcnow()
        
        # Log audit trail
        self.log_audit_trail("receiving_completed", user_id)
        
        # Publish event
        self.publish_event("receiving_record.completed", {
            "receipt_number": self.receipt_number,
            "total_received": float(self.total_quantity_received)
        })
    
    def cancel_receiving(self, user_id: int, reason: str) -> None:
        """Cancel the receiving process."""
        self.status = ReceivingStatus.CANCELLED
        self.notes = f"{self.notes or ''}\nCancelled: {reason}"
        
        # Log audit trail
        self.log_audit_trail("receiving_cancelled", user_id, {"reason": reason})
        
        # Publish event
        self.publish_event("receiving_record.cancelled", {
            "receipt_number": self.receipt_number,
            "reason": reason
        })


class ReceivingLineItem(CompanyBusinessObject):
    """
    Receiving Line Item model for individual product lines in receipts.
    
    Tracks expected vs received quantities, quality control,
    and provides detailed receiving information per product.
    """
    
    __tablename__ = "receiving_line_items"
    
    # Parent receiving record
    receiving_record_id = Column(
        Integer,
        ForeignKey("receiving_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Product references
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    product_variant_id = Column(
        Integer,
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Line identification
    line_number = Column(Integer, nullable=False)  # Line sequence within receipt
    
    # Quantities
    quantity_expected = Column(Numeric(15, 4), nullable=False)
    quantity_received = Column(Numeric(15, 4), nullable=False, default=0.0)
    quantity_accepted = Column(Numeric(15, 4), nullable=False, default=0.0)
    quantity_rejected = Column(Numeric(15, 4), nullable=False, default=0.0)
    quantity_damaged = Column(Numeric(15, 4), nullable=False, default=0.0)
    
    # Pricing and costs
    unit_cost = Column(Numeric(15, 4), nullable=True)
    total_cost = Column(Numeric(15, 2), nullable=True)
    
    # Batch and serial tracking
    batch_number = Column(String(100), nullable=True, index=True)
    serial_numbers = Column(JSON)  # Array of serial numbers received
    expiration_date = Column(DateTime, nullable=True)
    
    # Location assignment
    put_away_location_id = Column(
        Integer,
        ForeignKey("warehouse_locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Status and dates
    status = Column(Enum(ReceivingLineStatus), nullable=False, default=ReceivingLineStatus.PENDING, index=True)
    received_date = Column(DateTime, nullable=True)
    
    # Quality control
    quality_check_required = Column(Boolean, default=False, nullable=False)
    quality_check_passed = Column(Boolean, nullable=True)
    quality_notes = Column(Text)
    inspected_by_user_id = Column(Integer, nullable=True)
    inspected_at = Column(DateTime, nullable=True)
    
    # Rejection and damage tracking
    rejection_reason = Column(Text)
    damage_description = Column(Text)
    
    # Notes and additional information
    notes = Column(Text)
    
    # Relationships
    # receiving_record = relationship("ReceivingRecord", back_populates="line_items")
    # product = relationship("Product", back_populates="receiving_line_items")
    # product_variant = relationship("ProductVariant", back_populates="receiving_line_items")
    # put_away_location = relationship("WarehouseLocation", back_populates="receiving_line_items")
    
    def __str__(self):
        """String representation of receiving line item."""
        return f"Line {self.line_number}: {self.quantity_received}/{self.quantity_expected} received"
    
    def __repr__(self):
        """Detailed representation of receiving line item."""
        return (
            f"ReceivingLineItem(id={self.id}, line_number={self.line_number}, "
            f"product_id={self.product_id}, qty_received={self.quantity_received})"
        )
    
    @property
    def is_complete(self) -> bool:
        """Check if line item is fully received."""
        return self.status == ReceivingLineStatus.COMPLETE
    
    @property
    def is_over_received(self) -> bool:
        """Check if more was received than expected."""
        return self.quantity_received > self.quantity_expected
    
    @property
    def quantity_remaining(self) -> Decimal:
        """Calculate remaining quantity to receive."""
        return max(Decimal('0'), self.quantity_expected - self.quantity_received)
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.quantity_expected <= 0:
            return 0.0
        return float((self.quantity_received / self.quantity_expected) * 100)
    
    @property
    def acceptance_rate(self) -> float:
        """Calculate acceptance rate (accepted/received)."""
        if self.quantity_received <= 0:
            return 0.0
        return float((self.quantity_accepted / self.quantity_received) * 100)
    
    @property
    def total_value_received(self) -> Decimal:
        """Calculate total value of received items."""
        if not self.unit_cost:
            return Decimal('0.00')
        return self.quantity_received * self.unit_cost
    
    def can_receive_quantity(self, quantity: Decimal) -> bool:
        """Check if specified quantity can be received."""
        # Allow over-receiving up to a certain percentage (business rule)
        max_over_receive_percentage = Decimal('0.10')  # 10%
        max_allowed = self.quantity_expected * (1 + max_over_receive_percentage)
        
        return (self.quantity_received + quantity) <= max_allowed
    
    def receive_quantity(self, quantity: Decimal, user_id: int, location_id: int = None) -> None:
        """Receive specified quantity."""
        if not self.can_receive_quantity(quantity):
            raise ValueError("Cannot receive more than allowed over-receive limit")
        
        # Update quantities
        old_received = self.quantity_received
        self.quantity_received += quantity
        self.quantity_accepted += quantity  # Assume accepted unless quality check fails
        
        # Update status
        if self.quantity_received >= self.quantity_expected:
            self.status = ReceivingLineStatus.COMPLETE
        elif self.quantity_received > 0:
            self.status = ReceivingLineStatus.PARTIAL
        
        # Check for over-receiving
        if self.is_over_received:
            self.status = ReceivingLineStatus.OVER_RECEIVED
        
        # Set location if provided
        if location_id:
            self.put_away_location_id = location_id
        
        # Update timestamps
        self.received_date = datetime.utcnow()
        
        # Log audit trail
        self.log_audit_trail("quantity_received", user_id, {
            "quantity": float(quantity),
            "previous_received": float(old_received),
            "new_received": float(self.quantity_received)
        })
        
        # Publish event
        self.publish_event("receiving_line_item.quantity_received", {
            "line_id": self.id,
            "product_id": self.product_id,
            "quantity": float(quantity),
            "total_received": float(self.quantity_received)
        })
    
    def reject_quantity(self, quantity: Decimal, reason: str, user_id: int) -> None:
        """Reject specified quantity."""
        if quantity > self.quantity_received:
            raise ValueError("Cannot reject more than received")
        
        # Update quantities
        self.quantity_rejected += quantity
        self.quantity_accepted -= quantity
        
        # Update rejection reason
        if self.rejection_reason:
            self.rejection_reason += f"\n{reason}"
        else:
            self.rejection_reason = reason
        
        # Update status if needed
        if self.quantity_accepted <= 0:
            self.status = ReceivingLineStatus.REJECTED
        
        # Log audit trail
        self.log_audit_trail("quantity_rejected", user_id, {
            "quantity": float(quantity),
            "reason": reason
        })
        
        # Publish event
        self.publish_event("receiving_line_item.quantity_rejected", {
            "line_id": self.id,
            "product_id": self.product_id,
            "quantity": float(quantity),
            "reason": reason
        })
    
    def mark_damaged(self, quantity: Decimal, description: str, user_id: int) -> None:
        """Mark specified quantity as damaged."""
        if quantity > self.quantity_received:
            raise ValueError("Cannot mark more as damaged than received")
        
        # Update quantities
        self.quantity_damaged += quantity
        self.quantity_accepted -= quantity
        
        # Update damage description
        if self.damage_description:
            self.damage_description += f"\n{description}"
        else:
            self.damage_description = description
        
        # Update status
        self.status = ReceivingLineStatus.DAMAGED
        
        # Log audit trail
        self.log_audit_trail("quantity_damaged", user_id, {
            "quantity": float(quantity),
            "description": description
        })
        
        # Publish event
        self.publish_event("receiving_line_item.quantity_damaged", {
            "line_id": self.id,
            "product_id": self.product_id,
            "quantity": float(quantity),
            "description": description
        })
    
    def pass_quality_inspection(self, user_id: int, notes: str = None) -> None:
        """Pass quality inspection."""
        self.quality_check_passed = True
        self.inspected_by_user_id = user_id
        self.inspected_at = datetime.utcnow()
        if notes:
            self.quality_notes = notes
        
        # Log audit trail
        self.log_audit_trail("quality_inspection_passed", user_id)
    
    def fail_quality_inspection(self, user_id: int, notes: str) -> None:
        """Fail quality inspection."""
        self.quality_check_passed = False
        self.inspected_by_user_id = user_id
        self.inspected_at = datetime.utcnow()
        self.quality_notes = notes
        
        # Reject all received quantity
        self.reject_quantity(self.quantity_received, f"Quality inspection failed: {notes}", user_id)
        
        # Log audit trail
        self.log_audit_trail("quality_inspection_failed", user_id, {"notes": notes})