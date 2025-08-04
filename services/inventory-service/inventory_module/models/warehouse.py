"""
Warehouse and location management models for organizing inventory
across multiple storage facilities and locations.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from inventory_module.framework.base import CompanyBusinessObject, BaseModel


class WarehouseType(str, enum.Enum):
    """Warehouse type enumeration"""
    MAIN = "main"
    DISTRIBUTION = "distribution"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    TRANSIT = "transit"
    THIRD_PARTY = "third_party"
    VIRTUAL = "virtual"


class LocationType(str, enum.Enum):
    """Location type enumeration"""
    ZONE = "zone"  # Large area within warehouse
    AISLE = "aisle"  # Row of storage locations
    RACK = "rack"  # Storage rack structure
    SHELF = "shelf"  # Individual shelf
    BIN = "bin"  # Storage bin/container
    FLOOR = "floor"  # Floor storage area
    DOCK = "dock"  # Loading/unloading dock
    STAGING = "staging"  # Temporary staging area
    QUALITY = "quality"  # Quality control area
    DAMAGED = "damaged"  # Damaged goods area


class Warehouse(CompanyBusinessObject):
    """
    Warehouse model representing physical storage facilities.
    
    Manages warehouse information, configuration, and
    hierarchical organization of storage locations.
    """
    
    __tablename__ = "warehouses"
    
    # Basic warehouse information
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # Warehouse type and configuration
    warehouse_type = Column(Enum(WarehouseType), nullable=False, default=WarehouseType.MAIN, index=True)
    
    # Address information
    address_line_1 = Column(String(255))
    address_line_2 = Column(String(255))
    city = Column(String(100))
    state_province = Column(String(100))
    postal_code = Column(String(20))
    country_code = Column(String(3), default="US")
    
    # Contact information
    phone = Column(String(50))
    email = Column(String(255))
    contact_person = Column(String(255))
    
    # Geographic coordinates
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    
    # Operational information
    timezone = Column(String(50), default="UTC")
    operating_hours = Column(JSON)  # {"monday": {"open": "08:00", "close": "17:00"}, ...}
    currency_code = Column(String(3), default="USD")
    
    # Warehouse capabilities
    capabilities = Column(JSON)  # ["refrigerated", "hazmat", "bulk", "automated"]
    
    # Physical properties
    total_area_sqm = Column(Numeric(12, 2))
    storage_area_sqm = Column(Numeric(12, 2))
    ceiling_height_m = Column(Numeric(6, 2))
    dock_doors_count = Column(Integer)
    
    # Cost centers
    default_cost_center = Column(String(50))
    labor_cost_per_hour = Column(Numeric(8, 2))
    storage_cost_per_sqm = Column(Numeric(8, 4))
    
    # Configuration settings
    allow_negative_stock = Column(Boolean, default=False, nullable=False)
    require_location_tracking = Column(Boolean, default=True, nullable=False)
    enable_cycle_counting = Column(Boolean, default=True, nullable=False)
    default_receiving_location_id = Column(Integer, ForeignKey("warehouse_locations.id"), nullable=True)
    default_shipping_location_id = Column(Integer, ForeignKey("warehouse_locations.id"), nullable=True)
    
    # Status and flags
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_primary = Column(Boolean, default=False, nullable=False)  # Primary warehouse for company
    
    # Manager assignment
    warehouse_manager_user_id = Column(Integer, nullable=True, index=True)
    
    # System timestamps
    last_cycle_count_date = Column(DateTime, nullable=True)
    
    # Relationships
    # locations = relationship("WarehouseLocation", back_populates="warehouse", cascade="all, delete-orphan")
    # stock_levels = relationship("StockLevel", back_populates="warehouse")
    # stock_movements = relationship("StockMovement", back_populates="warehouse")
    
    def __str__(self):
        """String representation of warehouse."""
        return f"{self.name} ({self.code})"
    
    def __repr__(self):
        """Detailed representation of warehouse."""
        return (
            f"Warehouse(id={self.id}, name='{self.name}', code='{self.code}', "
            f"type='{self.warehouse_type.value}', active={self.is_active})"
        )
    
    @property
    def full_address(self) -> str:
        """Get formatted full address."""
        parts = []
        if self.address_line_1:
            parts.append(self.address_line_1)
        if self.address_line_2:
            parts.append(self.address_line_2)
        if self.city:
            parts.append(self.city)
        if self.state_province:
            parts.append(self.state_province)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country_code:
            parts.append(self.country_code)
        
        return ", ".join(parts)
    
    @property
    def storage_utilization_percentage(self) -> Optional[float]:
        """Calculate storage area utilization percentage."""
        if not self.storage_area_sqm:
            return None
        
        # In production, would calculate used area from locations
        used_area = Decimal('0.00')  # Would be calculated
        return float((used_area / self.storage_area_sqm) * 100)
    
    @property
    def location_count(self) -> int:
        """Get total number of locations in warehouse."""
        # In production, would count related locations
        return 0  # Simplified for demo
    
    @property
    def active_location_count(self) -> int:
        """Get number of active locations in warehouse."""
        # In production, would count active locations only
        return 0  # Simplified for demo
    
    @property
    def total_stock_value(self) -> Decimal:
        """Calculate total value of stock in warehouse."""
        # In production, would sum stock values from all locations
        return Decimal('0.00')  # Simplified for demo
    
    def has_capability(self, capability: str) -> bool:
        """Check if warehouse has specific capability."""
        if not self.capabilities:
            return False
        return capability in self.capabilities
    
    def add_capability(self, capability: str) -> None:
        """Add capability to warehouse."""
        if not self.capabilities:
            self.capabilities = []
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def remove_capability(self, capability: str) -> None:
        """Remove capability from warehouse."""
        if self.capabilities and capability in self.capabilities:
            self.capabilities.remove(capability)
    
    def is_open_at_time(self, check_time: datetime) -> bool:
        """Check if warehouse is open at specified time."""
        if not self.operating_hours:
            return True  # Assume 24/7 if no hours specified
        
        day_name = check_time.strftime('%A').lower()
        day_hours = self.operating_hours.get(day_name)
        
        if not day_hours:
            return False
        
        # Simplified time check (would need proper timezone handling in production)
        time_str = check_time.strftime('%H:%M')
        return day_hours.get('open', '00:00') <= time_str <= day_hours.get('close', '23:59')
    
    def get_default_locations(self) -> Dict[str, Optional[int]]:
        """Get default location IDs for various operations."""
        return {
            'receiving': self.default_receiving_location_id,
            'shipping': self.default_shipping_location_id
        }


class WarehouseLocation(CompanyBusinessObject):
    """
    Warehouse Location model for specific storage locations within warehouses.
    
    Provides hierarchical organization of storage areas with detailed
    location tracking and capacity management.
    """
    
    __tablename__ = "warehouse_locations"
    
    # Warehouse reference
    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Location identification
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=False, index=True)  # e.g., "A-01-001"
    barcode = Column(String(100), nullable=True, unique=True, index=True)
    
    # Hierarchical structure
    parent_location_id = Column(
        Integer,
        ForeignKey("warehouse_locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Location type and properties
    location_type = Column(Enum(LocationType), nullable=False, index=True)
    level = Column(Integer, nullable=False, default=0)  # Hierarchy level (0 = top level)
    
    # Physical properties
    position_x = Column(Numeric(8, 2))  # X coordinate in warehouse
    position_y = Column(Numeric(8, 2))  # Y coordinate in warehouse
    position_z = Column(Numeric(6, 2))  # Z coordinate (height/level)
    
    # Capacity information
    max_weight_kg = Column(Numeric(10, 2))
    max_volume_cbm = Column(Numeric(10, 4))
    max_items = Column(Integer)
    
    # Current utilization
    current_weight_kg = Column(Numeric(10, 2), default=0.0)
    current_volume_cbm = Column(Numeric(10, 4), default=0.0)
    current_items = Column(Integer, default=0)
    
    # Location configuration
    allow_mixed_products = Column(Boolean, default=True, nullable=False)
    allow_mixed_batches = Column(Boolean, default=True, nullable=False)
    require_picking_confirmation = Column(Boolean, default=False, nullable=False)
    climate_controlled = Column(Boolean, default=False, nullable=False)
    
    # Temperature and humidity (for climate-controlled locations)
    temperature_min = Column(Numeric(5, 2))  # Celsius
    temperature_max = Column(Numeric(5, 2))  # Celsius
    humidity_min = Column(Numeric(5, 2))  # Percentage
    humidity_max = Column(Numeric(5, 2))  # Percentage
    
    # Picking and putaway
    pick_sequence = Column(Integer, default=0)  # Order for picking optimization
    putaway_sequence = Column(Integer, default=0)  # Order for putaway optimization
    abc_classification = Column(String(1))  # A, B, C classification for fast/slow movers
    
    # Access and restrictions
    restricted_access = Column(Boolean, default=False, nullable=False)
    access_permissions = Column(JSON)  # User/role permissions for location access
    hazmat_approved = Column(Boolean, default=False, nullable=False)
    
    # Maintenance and inspection
    last_inspected_date = Column(DateTime, nullable=True)
    next_inspection_date = Column(DateTime, nullable=True)
    inspection_frequency_days = Column(Integer, default=90)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_blocked = Column(Boolean, default=False, nullable=False, index=True)
    blocked_reason = Column(String(255))
    blocked_until = Column(DateTime, nullable=True)
    
    # Additional metadata
    notes = Column(Text)
    custom_attributes = Column(JSON)
    
    # Relationships
    # warehouse = relationship("Warehouse", back_populates="locations")
    # parent_location = relationship("WarehouseLocation", remote_side=[id], back_populates="child_locations")
    # child_locations = relationship("WarehouseLocation", back_populates="parent_location", cascade="all, delete-orphan")
    # stock_levels = relationship("StockLevel", back_populates="warehouse_location")
    # stock_movements = relationship("StockMovement", back_populates="warehouse_location")
    
    def __str__(self):
        """String representation of warehouse location."""
        return f"{self.code} - {self.name}"
    
    def __repr__(self):
        """Detailed representation of warehouse location."""
        return (
            f"WarehouseLocation(id={self.id}, code='{self.code}', "
            f"warehouse_id={self.warehouse_id}, type='{self.location_type.value}')"
        )
    
    @property
    def full_path(self) -> str:
        """Get full location path from warehouse root."""
        # In production, would traverse parent relationships
        path_parts = [self.code]
        if self.parent_location_id:
            path_parts.insert(0, "Parent")  # Would load actual parent codes
        return " > ".join(path_parts)
    
    @property
    def is_leaf_location(self) -> bool:
        """Check if this is a leaf location (no children)."""
        # In production, would check for child locations
        return True  # Simplified for demo
    
    @property
    def weight_utilization_percentage(self) -> Optional[float]:
        """Calculate weight capacity utilization percentage."""
        if not self.max_weight_kg:
            return None
        return float((self.current_weight_kg / self.max_weight_kg) * 100)
    
    @property
    def volume_utilization_percentage(self) -> Optional[float]:
        """Calculate volume capacity utilization percentage."""
        if not self.max_volume_cbm:
            return None
        return float((self.current_volume_cbm / self.max_volume_cbm) * 100)
    
    @property
    def item_utilization_percentage(self) -> Optional[float]:
        """Calculate item capacity utilization percentage."""
        if not self.max_items:
            return None
        return float((self.current_items / self.max_items) * 100)
    
    @property
    def is_at_capacity(self) -> bool:
        """Check if location is at or near capacity."""
        utilization_threshold = 95.0  # 95% capacity threshold
        
        weight_util = self.weight_utilization_percentage
        volume_util = self.volume_utilization_percentage
        item_util = self.item_utilization_percentage
        
        return any(util and util >= utilization_threshold for util in [weight_util, volume_util, item_util])
    
    @property
    def available_capacity(self) -> Dict[str, Optional[Decimal]]:
        """Get available capacity in various units."""
        return {
            'weight_kg': (self.max_weight_kg - self.current_weight_kg) if self.max_weight_kg else None,
            'volume_cbm': (self.max_volume_cbm - self.current_volume_cbm) if self.max_volume_cbm else None,
            'items': (self.max_items - self.current_items) if self.max_items else None
        }
    
    def can_accommodate(self, weight_kg: Decimal = None, volume_cbm: Decimal = None, items: int = None) -> bool:
        """Check if location can accommodate specified requirements."""
        if weight_kg and self.max_weight_kg:
            if (self.current_weight_kg + weight_kg) > self.max_weight_kg:
                return False
        
        if volume_cbm and self.max_volume_cbm:
            if (self.current_volume_cbm + volume_cbm) > self.max_volume_cbm:
                return False
        
        if items and self.max_items:
            if (self.current_items + items) > self.max_items:
                return False
        
        return True
    
    def is_accessible_by_user(self, user_id: int) -> bool:
        """Check if user has access to this location."""
        if not self.restricted_access:
            return True
        
        if not self.access_permissions:
            return False
        
        # Simplified access check (would integrate with user roles in production)
        allowed_users = self.access_permissions.get('users', [])
        return user_id in allowed_users
    
    def block_location(self, reason: str, blocked_until: datetime = None) -> None:
        """Block location for specified reason and duration."""
        self.is_blocked = True
        self.blocked_reason = reason
        self.blocked_until = blocked_until
    
    def unblock_location(self) -> None:
        """Unblock location."""
        self.is_blocked = False
        self.blocked_reason = None
        self.blocked_until = None
    
    def update_utilization(self, weight_change: Decimal = None, volume_change: Decimal = None, items_change: int = None) -> None:
        """Update current utilization values."""
        if weight_change:
            self.current_weight_kg = (self.current_weight_kg or Decimal('0.00')) + weight_change
        
        if volume_change:
            self.current_volume_cbm = (self.current_volume_cbm or Decimal('0.0000')) + volume_change
        
        if items_change:
            self.current_items = (self.current_items or 0) + items_change
        
        # Ensure values don't go negative
        self.current_weight_kg = max(self.current_weight_kg or Decimal('0.00'), Decimal('0.00'))
        self.current_volume_cbm = max(self.current_volume_cbm or Decimal('0.0000'), Decimal('0.0000'))
        self.current_items = max(self.current_items or 0, 0)
    
    def get_child_location_ids(self) -> List[int]:
        """Get all child location IDs recursively."""
        # In production, would recursively get all descendant location IDs
        return []  # Simplified for demo