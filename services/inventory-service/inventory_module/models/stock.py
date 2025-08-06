"""
Stock management models for tracking inventory levels, movements,
and stock-related operations across multiple locations.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
import enum

from inventory_module.framework.base import CompanyBusinessObject, BaseModel


class StockMovementType(str, enum.Enum):
    """Stock movement type enumeration"""
    # Inbound movements
    RECEIPT = "receipt"  # Goods received from purchase order
    ADJUSTMENT_IN = "adjustment_in"  # Manual stock increase
    TRANSFER_IN = "transfer_in"  # Stock transferred from another location
    RETURN_IN = "return_in"  # Customer return
    PRODUCTION_IN = "production_in"  # Manufactured/assembled goods
    
    # Outbound movements
    SALE = "sale"  # Stock sold to customer
    ADJUSTMENT_OUT = "adjustment_out"  # Manual stock decrease
    TRANSFER_OUT = "transfer_out"  # Stock transferred to another location
    RETURN_OUT = "return_out"  # Return to supplier
    WASTE = "waste"  # Stock written off as waste/damaged
    PRODUCTION_OUT = "production_out"  # Raw materials consumed in production
    
    # Special movements
    CYCLE_COUNT = "cycle_count"  # Physical count adjustment
    RESERVATION = "reservation"  # Stock reserved for order
    RELEASE_RESERVATION = "release_reservation"  # Reserved stock released


class StockLevel(CompanyBusinessObject):
    """
    Stock Level model tracking current inventory quantities by location.
    
    Maintains real-time stock levels for products across different
    warehouse locations with support for reserved quantities.
    """
    
    __tablename__ = "stock_levels"
    
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
    
    # Location reference
    warehouse_location_id = Column(
        Integer,
        ForeignKey("warehouse_locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Stock quantities
    quantity_on_hand = Column(Numeric(15, 4), nullable=False, default=0.0)
    quantity_reserved = Column(Numeric(15, 4), nullable=False, default=0.0)
    quantity_available = Column(Numeric(15, 4), nullable=False, default=0.0)  # on_hand - reserved
    quantity_incoming = Column(Numeric(15, 4), nullable=False, default=0.0)  # Expected from POs
    
    # Batch and serial tracking
    batch_number = Column(String(100), nullable=True, index=True)
    serial_numbers = Column(JSON)  # Array of serial numbers for serialized items
    expiration_date = Column(DateTime, nullable=True, index=True)
    
    # Cost tracking
    unit_cost = Column(Numeric(15, 4), nullable=True)
    total_cost = Column(Numeric(15, 2), nullable=True)
    cost_method = Column(String(20), nullable=True)  # FIFO, LIFO, AVERAGE, STANDARD
    
    # Last movement tracking
    last_movement_date = Column(DateTime, nullable=True)
    last_movement_type = Column(Enum(StockMovementType), nullable=True)
    last_count_date = Column(DateTime, nullable=True)
    
    # Status and flags
    is_active = Column(Boolean, default=True, nullable=False)
    negative_stock_allowed = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    # product = relationship("Product", back_populates="stock_levels")
    # product_variant = relationship("ProductVariant", back_populates="stock_levels")
    # warehouse_location = relationship("WarehouseLocation", back_populates="stock_levels")
    
    def __str__(self):
        """String representation of stock level."""
        return f"Stock: Product {self.product_id} at Location {self.warehouse_location_id}: {self.quantity_on_hand}"
    
    def __repr__(self):
        """Detailed representation of stock level."""
        return (
            f"StockLevel(id={self.id}, product_id={self.product_id}, "
            f"location_id={self.warehouse_location_id}, qty={self.quantity_on_hand})"
        )
    
    @property
    def is_out_of_stock(self) -> bool:
        """Check if stock is out of stock."""
        return self.quantity_available <= 0
    
    @property
    def has_reserved_stock(self) -> bool:
        """Check if there is reserved stock."""
        return self.quantity_reserved > 0
    
    @property
    def is_overstocked(self) -> bool:
        """Check if stock exceeds maximum level (requires product info)."""
        # In production, would check against product's maximum stock level
        return False  # Simplified for demo
    
    @property
    def is_low_stock(self) -> bool:
        """Check if stock is below minimum level (requires product info)."""
        # In production, would check against product's minimum stock level
        return False  # Simplified for demo
    
    @property
    def stock_value(self) -> Decimal:
        """Calculate total stock value."""
        if not self.unit_cost:
            return Decimal('0.00')
        return self.quantity_on_hand * self.unit_cost
    
    def update_available_quantity(self) -> None:
        """Update available quantity based on on-hand and reserved."""
        self.quantity_available = self.quantity_on_hand - self.quantity_reserved
    
    def can_reserve(self, quantity: Decimal) -> bool:
        """Check if specified quantity can be reserved."""
        return (self.quantity_on_hand - self.quantity_reserved) >= quantity
    
    def reserve_stock(self, quantity: Decimal, reason: str = None) -> bool:
        """Reserve specified quantity of stock."""
        if not self.can_reserve(quantity):
            return False
        
        self.quantity_reserved += quantity
        self.update_available_quantity()
        return True
    
    def release_reservation(self, quantity: Decimal) -> bool:
        """Release reserved stock."""
        if quantity > self.quantity_reserved:
            return False
        
        self.quantity_reserved -= quantity
        self.update_available_quantity()
        return True
    
    def adjust_stock(self, quantity_change: Decimal, movement_type: StockMovementType) -> None:
        """Adjust stock level and update movement metadata."""
        self.quantity_on_hand += quantity_change
        self.update_available_quantity()
        self.last_movement_date = datetime.utcnow()
        self.last_movement_type = movement_type
        
        # Update cost if this is an inbound movement with cost information
        if quantity_change > 0 and self.unit_cost:
            self.total_cost = self.quantity_on_hand * self.unit_cost


class StockMovement(CompanyBusinessObject):
    """
    Stock Movement model for tracking all inventory transactions.
    
    Provides complete audit trail of stock changes with references
    to source documents and detailed movement information.
    """
    
    __tablename__ = "stock_movements"
    
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
    
    # Location information
    warehouse_location_id = Column(
        Integer,
        ForeignKey("warehouse_locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    from_location_id = Column(
        Integer,
        ForeignKey("warehouse_locations.id"),
        nullable=True,
        index=True
    )
    to_location_id = Column(
        Integer,
        ForeignKey("warehouse_locations.id"),
        nullable=True,
        index=True
    )
    
    # Movement details
    movement_type = Column(Enum(StockMovementType), nullable=False, index=True)
    movement_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    quantity = Column(Numeric(15, 4), nullable=False)
    unit_cost = Column(Numeric(15, 4), nullable=True)
    total_cost = Column(Numeric(15, 2), nullable=True)
    
    # Batch and serial tracking
    batch_number = Column(String(100), nullable=True, index=True)
    serial_numbers = Column(JSON)  # Array of serial numbers affected
    expiration_date = Column(DateTime, nullable=True)
    
    # Source document references
    source_document_type = Column(String(50), nullable=True, index=True)  # 'purchase_order', 'sales_order', etc.
    source_document_id = Column(Integer, nullable=True, index=True)
    source_document_number = Column(String(100), nullable=True, index=True)
    
    # User and approval information
    created_by_user_id = Column(Integer, nullable=False, index=True)
    approved_by_user_id = Column(Integer, nullable=True, index=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Movement notes and references
    reference_number = Column(String(100), nullable=True, index=True)
    notes = Column(Text)
    reason_code = Column(String(50), nullable=True, index=True)
    
    # Quality and inspection
    quality_check_required = Column(Boolean, default=False, nullable=False)
    quality_check_passed = Column(Boolean, nullable=True)
    quality_notes = Column(Text)
    inspected_by_user_id = Column(Integer, nullable=True)
    inspected_at = Column(DateTime, nullable=True)
    
    # Stock level snapshots (for audit)
    quantity_before = Column(Numeric(15, 4), nullable=True)
    quantity_after = Column(Numeric(15, 4), nullable=True)
    
    # System fields
    is_reversed = Column(Boolean, default=False, nullable=False)
    reversed_by_movement_id = Column(Integer, ForeignKey("stock_movements.id"), nullable=True)
    reversed_at = Column(DateTime, nullable=True)
    
    # Additional metadata
    movement_metadata = Column(JSON)  # Additional movement-specific data
    
    # Relationships
    # product = relationship("Product", back_populates="stock_movements")
    # product_variant = relationship("ProductVariant", back_populates="stock_movements")
    # warehouse_location = relationship("WarehouseLocation", back_populates="stock_movements")
    # from_location = relationship("WarehouseLocation", foreign_keys=[from_location_id])
    # to_location = relationship("WarehouseLocation", foreign_keys=[to_location_id])
    # reversed_by_movement = relationship("StockMovement", remote_side=[id])
    
    def __str__(self):
        """String representation of stock movement."""
        direction = "+" if self.quantity >= 0 else ""
        return f"{self.movement_type.value}: {direction}{self.quantity} units on {self.movement_date.strftime('%Y-%m-%d')}"
    
    def __repr__(self):
        """Detailed representation of stock movement."""
        return (
            f"StockMovement(id={self.id}, type='{self.movement_type.value}', "
            f"product_id={self.product_id}, qty={self.quantity}, date='{self.movement_date}')"
        )
    
    @property
    def is_inbound(self) -> bool:
        """Check if this is an inbound movement (increases stock)."""
        inbound_types = [
            StockMovementType.RECEIPT,
            StockMovementType.ADJUSTMENT_IN,
            StockMovementType.TRANSFER_IN,
            StockMovementType.RETURN_IN,
            StockMovementType.PRODUCTION_IN,
            StockMovementType.RELEASE_RESERVATION
        ]
        return self.movement_type in inbound_types
    
    @property
    def is_outbound(self) -> bool:
        """Check if this is an outbound movement (decreases stock)."""
        return not self.is_inbound
    
    @property
    def is_transfer(self) -> bool:
        """Check if this is a transfer movement between locations."""
        return self.movement_type in [StockMovementType.TRANSFER_IN, StockMovementType.TRANSFER_OUT]
    
    @property
    def requires_approval(self) -> bool:
        """Check if movement requires approval based on type and amount."""
        # In production, would check business rules
        high_value_threshold = Decimal('1000.00')
        
        if self.total_cost and self.total_cost > high_value_threshold:
            return True
        
        # Adjustments typically require approval
        if self.movement_type in [StockMovementType.ADJUSTMENT_IN, StockMovementType.ADJUSTMENT_OUT]:
            return True
        
        return False
    
    @property
    def is_approved(self) -> bool:
        """Check if movement has been approved."""
        return self.approved_by_user_id is not None and self.approved_at is not None
    
    @property
    def movement_value(self) -> Decimal:
        """Calculate movement value."""
        if not self.unit_cost:
            return Decimal('0.00')
        return abs(self.quantity) * self.unit_cost
    
    def can_be_reversed(self) -> bool:
        """Check if movement can be reversed."""
        if self.is_reversed:
            return False
        
        # Check if enough time has passed (business rule)
        hours_since_movement = (datetime.utcnow() - self.movement_date).total_seconds() / 3600
        max_reversal_hours = 72  # 3 days
        
        return hours_since_movement <= max_reversal_hours
    
    def create_reversal_movement(self, user_id: int, reason: str) -> 'StockMovement':
        """Create a reversal movement for this movement."""
        if not self.can_be_reversed():
            raise ValueError("Movement cannot be reversed")
        
        # Create opposite movement
        reversal = StockMovement(
            company_id=self.company_id,
            product_id=self.product_id,
            product_variant_id=self.product_variant_id,
            warehouse_location_id=self.warehouse_location_id,
            movement_type=self._get_reversal_movement_type(),
            quantity=-self.quantity,  # Opposite quantity
            unit_cost=self.unit_cost,
            total_cost=-self.total_cost if self.total_cost else None,
            batch_number=self.batch_number,
            serial_numbers=self.serial_numbers,
            created_by_user_id=user_id,
            reference_number=f"REV-{self.id}",
            notes=f"Reversal of movement {self.id}: {reason}",
            source_document_type="reversal",
            source_document_id=self.id
        )
        
        # Mark this movement as reversed
        self.is_reversed = True
        self.reversed_at = datetime.utcnow()
        
        return reversal
    
    def _get_reversal_movement_type(self) -> StockMovementType:
        """Get the appropriate movement type for reversal."""
        reversal_map = {
            StockMovementType.RECEIPT: StockMovementType.ADJUSTMENT_OUT,
            StockMovementType.ADJUSTMENT_IN: StockMovementType.ADJUSTMENT_OUT,
            StockMovementType.ADJUSTMENT_OUT: StockMovementType.ADJUSTMENT_IN,
            StockMovementType.SALE: StockMovementType.RETURN_IN,
            StockMovementType.TRANSFER_IN: StockMovementType.TRANSFER_OUT,
            StockMovementType.TRANSFER_OUT: StockMovementType.TRANSFER_IN,
        }
        
        return reversal_map.get(self.movement_type, StockMovementType.ADJUSTMENT_IN)
    
    def calculate_stock_impact(self) -> Decimal:
        """Calculate the impact on stock levels (positive for increase, negative for decrease)."""
        if self.is_inbound:
            return abs(self.quantity)
        else:
            return -abs(self.quantity)
    
    def validate_movement(self) -> list:
        """Validate the stock movement."""
        errors = []
        
        if self.quantity == 0:
            errors.append("Movement quantity cannot be zero")
        
        if self.movement_type == StockMovementType.TRANSFER_IN and not self.from_location_id:
            errors.append("Transfer in movements require from_location_id")
        
        if self.movement_type == StockMovementType.TRANSFER_OUT and not self.to_location_id:
            errors.append("Transfer out movements require to_location_id")
        
        if self.unit_cost and self.unit_cost < 0:
            errors.append("Unit cost cannot be negative")
        
        return errors