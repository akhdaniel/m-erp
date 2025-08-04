"""
Product models for inventory management including product catalog,
variants, categories, and related product information.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from inventory_module.framework.base import CompanyBusinessObject, BaseModel


class ProductType(str, enum.Enum):
    """Product type enumeration"""
    PHYSICAL = "physical"
    DIGITAL = "digital"
    SERVICE = "service"
    KIT = "kit"  # Bundle of other products


class ProductStatus(str, enum.Enum):
    """Product status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    DRAFT = "draft"


class UnitOfMeasure(str, enum.Enum):
    """Unit of measure enumeration"""
    EACH = "each"
    DOZEN = "dozen"
    CASE = "case"
    KILOGRAM = "kg"
    GRAM = "g"
    POUND = "lb"
    OUNCE = "oz"
    LITER = "l"
    MILLILITER = "ml"
    METER = "m"
    CENTIMETER = "cm"
    INCH = "in"
    FOOT = "ft"
    SQUARE_METER = "sqm"
    SQUARE_FOOT = "sqft"
    CUBIC_METER = "cbm"
    CUBIC_FOOT = "cbft"


class ProductCategory(CompanyBusinessObject):
    """
    Product Category model for organizing products hierarchically.
    
    Provides categorization system for products with parent-child
    relationships and metadata management.
    """
    
    __tablename__ = "product_categories"
    
    # Category information
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    
    # Hierarchical structure
    parent_category_id = Column(
        Integer,
        ForeignKey("product_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Display and organization
    display_order = Column(Integer, nullable=False, default=0)
    color = Column(String(7))  # Hex color code for UI
    icon = Column(String(100))  # Icon identifier for UI
    
    # SEO and web presence
    slug = Column(String(255), nullable=True, index=True)
    meta_title = Column(String(255))
    meta_description = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Statistics (updated by triggers/background jobs)
    product_count = Column(Integer, nullable=False, default=0)
    
    # Relationships
    # parent_category = relationship("ProductCategory", remote_side=[id], back_populates="child_categories")
    # child_categories = relationship("ProductCategory", back_populates="parent_category", cascade="all, delete-orphan")
    # products = relationship("Product", back_populates="category")
    
    def __str__(self):
        """String representation of product category."""
        return f"{self.name} ({self.code})"
    
    def __repr__(self):
        """Detailed representation of product category."""
        return (
            f"ProductCategory(id={self.id}, name='{self.name}', code='{self.code}', "
            f"parent_id={self.parent_category_id}, active={self.is_active})"
        )
    
    @property
    def full_path(self) -> str:
        """Get full category path from root to current category."""
        # In production, would traverse parent relationships
        if self.parent_category_id:
            return f"Parent Category > {self.name}"
        return self.name
    
    @property
    def is_leaf_category(self) -> bool:
        """Check if this is a leaf category (no children)."""
        # In production, would check for child categories
        return True  # Simplified for demo
    
    def get_all_child_ids(self) -> List[int]:
        """Get all descendant category IDs."""
        # In production, would recursively get all child category IDs
        return []  # Simplified for demo


class Product(CompanyBusinessObject):
    """
    Product model representing items in the inventory catalog.
    
    Comprehensive product information including identification,
    categorization, pricing, and inventory management settings.
    """
    
    __tablename__ = "products"
    
    # Basic product information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    short_description = Column(String(500))
    
    # Product identification
    sku = Column(String(100), nullable=False, unique=True, index=True)
    barcode = Column(String(100), nullable=True, index=True)
    manufacturer_part_number = Column(String(100), nullable=True, index=True)
    
    # Categorization
    category_id = Column(
        Integer,
        ForeignKey("product_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Product type and status
    product_type = Column(Enum(ProductType), nullable=False, default=ProductType.PHYSICAL, index=True)
    status = Column(Enum(ProductStatus), nullable=False, default=ProductStatus.ACTIVE, index=True)
    
    # Pricing information
    list_price = Column(Numeric(15, 2), nullable=True)
    cost_price = Column(Numeric(15, 2), nullable=True)
    currency_code = Column(String(3), nullable=False, default="USD")
    
    # Units and measurements
    unit_of_measure = Column(Enum(UnitOfMeasure), nullable=False, default=UnitOfMeasure.EACH)
    weight = Column(Numeric(10, 4), nullable=True)  # Weight in base unit (kg)
    weight_unit = Column(String(10), nullable=True, default="kg")
    dimensions = Column(JSON)  # {"length": 10, "width": 5, "height": 2, "unit": "cm"}
    
    # Inventory management
    track_inventory = Column(Boolean, nullable=False, default=True)
    minimum_stock_level = Column(Numeric(10, 2), nullable=True)
    maximum_stock_level = Column(Numeric(10, 2), nullable=True)
    reorder_point = Column(Numeric(10, 2), nullable=True)
    reorder_quantity = Column(Numeric(10, 2), nullable=True)
    lead_time_days = Column(Integer, nullable=True)
    
    # Supplier information
    primary_supplier_id = Column(Integer, nullable=True, index=True)  # Foreign key to Partner
    supplier_product_code = Column(String(100), nullable=True)
    
    # Quality and compliance
    quality_control_required = Column(Boolean, nullable=False, default=False)
    hazardous_material = Column(Boolean, nullable=False, default=False)
    expiration_tracking = Column(Boolean, nullable=False, default=False)
    batch_tracking = Column(Boolean, nullable=False, default=False)
    serial_tracking = Column(Boolean, nullable=False, default=False)
    
    # Web and marketing
    web_enabled = Column(Boolean, nullable=False, default=False)
    meta_title = Column(String(255))
    meta_description = Column(Text)
    tags = Column(JSON)  # Array of string tags
    
    # Images and media
    images = Column(JSON)  # Array of image URLs/paths
    primary_image = Column(String(500))
    documents = Column(JSON)  # Array of document references
    
    # Additional attributes (flexible schema)
    custom_attributes = Column(JSON)
    
    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    discontinued_date = Column(DateTime, nullable=True)
    
    # Relationships
    # category = relationship("ProductCategory", back_populates="products")
    # variants = relationship("ProductVariant", back_populates="parent_product", cascade="all, delete-orphan")
    # stock_levels = relationship("StockLevel", back_populates="product")
    # stock_movements = relationship("StockMovement", back_populates="product")
    
    def __str__(self):
        """String representation of product."""
        return f"{self.name} ({self.sku})"
    
    def __repr__(self):
        """Detailed representation of product."""
        return (
            f"Product(id={self.id}, name='{self.name}', sku='{self.sku}', "
            f"type='{self.product_type.value}', status='{self.status.value}')"
        )
    
    @property
    def display_name(self) -> str:
        """Get display name with SKU."""
        return f"{self.name} ({self.sku})"
    
    @property
    def is_stockable(self) -> bool:
        """Check if product requires stock tracking."""
        return self.track_inventory and self.product_type in [ProductType.PHYSICAL, ProductType.KIT]
    
    @property
    def has_variants(self) -> bool:
        """Check if product has variants."""
        # In production, would check for existence of variants
        return False  # Simplified for demo
    
    @property
    def current_stock_level(self) -> Decimal:
        """Get current total stock level across all locations."""
        # In production, would sum stock levels from all locations
        return Decimal('0.00')  # Simplified for demo
    
    @property 
    def stock_status(self) -> str:
        """Get stock status based on current levels and thresholds."""
        current_stock = self.current_stock_level
        
        if not self.is_stockable:
            return "not_tracked"
        
        if current_stock <= 0:
            return "out_of_stock"
        elif self.minimum_stock_level and current_stock <= self.minimum_stock_level:
            return "low_stock"
        elif self.reorder_point and current_stock <= self.reorder_point:
            return "reorder_needed"
        else:
            return "in_stock"
    
    @property
    def gross_margin_percentage(self) -> Optional[float]:
        """Calculate gross margin percentage."""
        if not self.list_price or not self.cost_price or self.cost_price <= 0:
            return None
        
        margin = (self.list_price - self.cost_price) / self.list_price * 100
        return float(margin)
    
    def generate_sku(self, prefix: str = "SKU") -> str:
        """Generate SKU if not provided."""
        # In production, would use company settings and sequence numbers
        import time
        timestamp = int(time.time())
        return f"{prefix}{timestamp:06d}"
    
    def update_reorder_point(self, lead_time_days: int = None, safety_stock: Decimal = None) -> None:
        """Update reorder point based on lead time and safety stock."""
        if lead_time_days is None:
            lead_time_days = self.lead_time_days or 14
        
        if safety_stock is None:
            safety_stock = self.minimum_stock_level or Decimal('0')
        
        # Simple calculation: (average daily usage * lead time) + safety stock
        # In production, would calculate based on historical usage data
        average_daily_usage = Decimal('1.0')  # Simplified
        self.reorder_point = (average_daily_usage * lead_time_days) + safety_stock
    
    def validate_pricing(self) -> List[str]:
        """Validate product pricing."""
        errors = []
        
        if self.list_price and self.list_price <= 0:
            errors.append("List price must be positive")
        
        if self.cost_price and self.cost_price <= 0:
            errors.append("Cost price must be positive")
        
        if (self.list_price and self.cost_price and 
            self.list_price < self.cost_price):
            errors.append("List price should not be less than cost price")
        
        return errors


class ProductVariant(CompanyBusinessObject):
    """
    Product Variant model for products with variations.
    
    Handles product variants such as different sizes, colors,
    or other attribute combinations while maintaining separate
    inventory tracking for each variant.
    """
    
    __tablename__ = "product_variants"
    
    # Parent product reference
    parent_product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Variant identification
    variant_name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=False, unique=True, index=True)
    barcode = Column(String(100), nullable=True, index=True)
    
    # Variant attributes
    attributes = Column(JSON)  # {"size": "Large", "color": "Red", "material": "Cotton"}
    
    # Variant-specific pricing
    list_price = Column(Numeric(15, 2), nullable=True)
    cost_price = Column(Numeric(15, 2), nullable=True)
    price_adjustment = Column(Numeric(15, 2), nullable=True, default=0)  # Adjustment from parent
    
    # Variant-specific inventory settings
    minimum_stock_level = Column(Numeric(10, 2), nullable=True)
    maximum_stock_level = Column(Numeric(10, 2), nullable=True)
    reorder_point = Column(Numeric(10, 2), nullable=True)
    reorder_quantity = Column(Numeric(10, 2), nullable=True)
    
    # Physical properties (if different from parent)
    weight = Column(Numeric(10, 4), nullable=True)
    dimensions = Column(JSON)
    
    # Images and media specific to variant
    images = Column(JSON)
    primary_image = Column(String(500))
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    # parent_product = relationship("Product", back_populates="variants")
    # stock_levels = relationship("StockLevel", back_populates="product_variant")
    # stock_movements = relationship("StockMovement", back_populates="product_variant")
    
    def __str__(self):
        """String representation of product variant."""
        return f"{self.variant_name} ({self.sku})"
    
    def __repr__(self):
        """Detailed representation of product variant."""
        return (
            f"ProductVariant(id={self.id}, name='{self.variant_name}', "
            f"sku='{self.sku}', parent_id={self.parent_product_id})"
        )
    
    @property
    def display_name(self) -> str:
        """Get display name with parent product context."""
        # In production, would load parent product name
        return f"Parent Product - {self.variant_name} ({self.sku})"
    
    @property
    def effective_list_price(self) -> Optional[Decimal]:
        """Get effective list price (variant price or parent + adjustment)."""
        if self.list_price:
            return self.list_price
        
        # In production, would get parent product price and add adjustment
        parent_price = Decimal('0.00')  # Would load from parent
        return parent_price + (self.price_adjustment or Decimal('0.00'))
    
    @property
    def effective_cost_price(self) -> Optional[Decimal]:
        """Get effective cost price (variant cost or parent cost)."""
        if self.cost_price:
            return self.cost_price
        
        # In production, would get parent product cost price
        return None  # Would load from parent
    
    @property
    def current_stock_level(self) -> Decimal:
        """Get current stock level for this variant."""
        # In production, would sum stock levels for this variant
        return Decimal('0.00')
    
    def get_attribute_value(self, attribute_name: str) -> Optional[str]:
        """Get value for a specific attribute."""
        if not self.attributes:
            return None
        return self.attributes.get(attribute_name)
    
    def set_attribute_value(self, attribute_name: str, value: str) -> None:
        """Set value for a specific attribute."""
        if not self.attributes:
            self.attributes = {}
        self.attributes[attribute_name] = value