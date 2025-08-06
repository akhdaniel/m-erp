"""
Pricing Rules model for dynamic pricing management.

Provides comprehensive pricing engine with flexible rule types including
customer-specific pricing, volume discounts, promotional pricing, and product category rules.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from sales_module.framework.base import CompanyBusinessObject


class PricingRuleType(str, enum.Enum):
    """Pricing rule type enumeration"""
    CUSTOMER_SPECIFIC = "customer_specific"  # Customer-specific pricing
    VOLUME_DISCOUNT = "volume_discount"  # Volume-based discount
    PROMOTIONAL = "promotional"  # Promotional pricing
    PRODUCT_CATEGORY = "product_category"  # Product category pricing


class DiscountType(str, enum.Enum):
    """Discount type enumeration"""
    PERCENTAGE = "percentage"  # Percentage discount
    FIXED_AMOUNT = "fixed_amount"  # Fixed amount discount  
    FIXED_PRICE = "fixed_price"  # Fixed price override


class PricingRule(CompanyBusinessObject):
    """
    Pricing Rule model for flexible pricing management.
    
    Comprehensive pricing rules supporting customer-specific pricing,
    volume discounts, promotional pricing, and product category rules.
    """
    
    __tablename__ = "pricing_rules"
    
    # Basic rule information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Rule type and priority
    rule_type = Column(Enum(PricingRuleType), nullable=False, index=True)
    priority = Column(Integer, default=1, nullable=False, index=True)  # Lower = higher priority
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Customer specific rules
    customer_id = Column(Integer, nullable=True, index=True)  # References partners table
    
    # Product specific rules
    product_id = Column(Integer, nullable=True, index=True)  # References inventory module product
    product_category_id = Column(Integer, nullable=True, index=True)  # References inventory module category
    
    # Volume discount rules
    min_quantity = Column(Numeric(12, 3), nullable=True)
    max_quantity = Column(Numeric(12, 3), nullable=True)
    min_amount = Column(Numeric(12, 2), nullable=True)
    max_amount = Column(Numeric(12, 2), nullable=True)
    
    # Discount configuration
    discount_type = Column(Enum(DiscountType), nullable=False, default=DiscountType.PERCENTAGE)
    discount_value = Column(Numeric(12, 2), nullable=False)
    
    # Date range for promotional rules
    start_date = Column(Date, nullable=True, index=True)
    end_date = Column(Date, nullable=True, index=True)
    
    # Audit fields
    created_by = Column(Integer, nullable=True, index=True)  # References users table
    framework_version = Column(Integer, default=1)
    
    def __str__(self):
        """String representation of pricing rule."""
        return f"{self.name} ({self.rule_type.value})"
    
    def __repr__(self):
        """Detailed representation of pricing rule."""
        return (
            f"PricingRule(id={self.id}, name='{self.name}', "
            f"type='{self.rule_type.value}', active={self.is_active})"
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if pricing rule is currently valid."""
        if not self.is_active:
            return False
        
        today = date.today()
        
        # Check start date
        if self.start_date and today < self.start_date:
            return False
        
        # Check end date
        if self.end_date and today > self.end_date:
            return False
        
        return True
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Calculate days until rule expires."""
        if not self.end_date:
            return None
        
        delta = self.end_date - date.today()
        return max(0, delta.days)
    
    @property
    def is_customer_specific(self) -> bool:
        """Check if rule is customer-specific."""
        return self.rule_type == PricingRuleType.CUSTOMER_SPECIFIC
    
    @property
    def is_volume_discount(self) -> bool:
        """Check if rule is volume-based discount."""
        return self.rule_type == PricingRuleType.VOLUME_DISCOUNT
    
    @property
    def is_promotional(self) -> bool:
        """Check if rule is promotional."""
        return self.rule_type == PricingRuleType.PROMOTIONAL
    
    @property
    def is_product_category(self) -> bool:
        """Check if rule is product category-based."""
        return self.rule_type == PricingRuleType.PRODUCT_CATEGORY
    
    def is_applicable_to_customer(self, customer_id: int) -> bool:
        """Check if rule applies to given customer."""
        if not self.is_valid:
            return False
        
        # If no customer restriction, applies to all
        if not self.customer_id:
            return True
        
        # Check specific customer
        return self.customer_id == customer_id
    
    def is_applicable_to_product(self, product_id: int = None, product_category_id: int = None) -> bool:
        """Check if rule applies to given product or category."""
        if not self.is_valid:
            return False
        
        # Check specific product
        if self.product_id and product_id:
            return self.product_id == product_id
        
        # Check product category
        if self.product_category_id and product_category_id:
            return self.product_category_id == product_category_id
        
        # If no product restrictions, applies to all
        if not self.product_id and not self.product_category_id:
            return True
        
        return False
    
    def is_applicable_to_quantity(self, quantity: Decimal) -> bool:
        """Check if rule applies to given quantity."""
        if not self.is_valid:
            return False
        
        # Check minimum quantity
        if self.min_quantity and quantity < self.min_quantity:
            return False
        
        # Check maximum quantity
        if self.max_quantity and quantity > self.max_quantity:
            return False
        
        return True
    
    def is_applicable_to_amount(self, amount: Decimal) -> bool:
        """Check if rule applies to given amount."""
        if not self.is_valid:
            return False
        
        # Check minimum amount
        if self.min_amount and amount < self.min_amount:
            return False
        
        # Check maximum amount
        if self.max_amount and amount > self.max_amount:
            return False
        
        return True
    
    def calculate_price(self, base_price: Decimal, quantity: Decimal = Decimal('1.0')) -> Optional[Decimal]:
        """Calculate price based on rule."""
        if not base_price or base_price <= 0:
            return None
        
        # Check applicability
        if not self.is_applicable_to_quantity(quantity):
            return None
        
        total_amount = base_price * quantity
        if not self.is_applicable_to_amount(total_amount):
            return None
        
        if self.discount_type == DiscountType.FIXED_PRICE:
            # Override with fixed price per unit
            return self.discount_value
        
        elif self.discount_type == DiscountType.PERCENTAGE:
            # Apply percentage discount
            discount_multiplier = 1 - (self.discount_value / 100)
            return base_price * discount_multiplier
        
        elif self.discount_type == DiscountType.FIXED_AMOUNT:
            # Apply fixed amount discount per unit
            discounted_price = base_price - self.discount_value
            return max(Decimal('0.00'), discounted_price)
        
        return None
    
    def calculate_discount_amount(self, base_price: Decimal, quantity: Decimal = Decimal('1.0')) -> Decimal:
        """Calculate discount amount for the rule."""
        if not base_price or base_price <= 0:
            return Decimal('0.00')
        
        # Check applicability  
        if not self.is_applicable_to_quantity(quantity):
            return Decimal('0.00')
        
        total_amount = base_price * quantity
        if not self.is_applicable_to_amount(total_amount):
            return Decimal('0.00')
        
        if self.discount_type == DiscountType.FIXED_PRICE:
            # Discount is difference between base and fixed price
            if self.discount_value < base_price:
                return (base_price - self.discount_value) * quantity
            return Decimal('0.00')
        
        elif self.discount_type == DiscountType.PERCENTAGE:
            # Percentage of total amount
            return total_amount * (self.discount_value / 100)
        
        elif self.discount_type == DiscountType.FIXED_AMOUNT:
            # Fixed amount per unit
            return self.discount_value * quantity
        
        return Decimal('0.00')
    
    def extend_validity(self, additional_days: int, user_id: int = None) -> None:
        """Extend rule validity period."""
        if self.end_date:
            old_end_date = self.end_date
            self.end_date = self.end_date + timedelta(days=additional_days)
        else:
            old_end_date = None
            self.end_date = date.today() + timedelta(days=additional_days)
        
        # Log audit trail
        self.log_audit_trail("validity_extended", user_id, {
            "old_end_date": old_end_date.isoformat() if old_end_date else None,
            "new_end_date": self.end_date.isoformat(),
            "additional_days": additional_days
        })
        
        # Publish event
        self.publish_event("pricing_rule.validity_extended", {
            "rule_id": self.id,
            "rule_name": self.name,
            "new_end_date": self.end_date.isoformat()
        })
    
    def activate(self, user_id: int = None) -> None:
        """Activate pricing rule."""
        self.is_active = True
        
        # Log audit trail
        self.log_audit_trail("pricing_rule_activated", user_id)
        
        # Publish event
        self.publish_event("pricing_rule.activated", {
            "rule_id": self.id,
            "rule_name": self.name,
            "rule_type": self.rule_type.value
        })
    
    def deactivate(self, user_id: int = None) -> None:
        """Deactivate pricing rule."""
        self.is_active = False
        
        # Log audit trail
        self.log_audit_trail("pricing_rule_deactivated", user_id)
        
        # Publish event
        self.publish_event("pricing_rule.deactivated", {
            "rule_id": self.id,
            "rule_name": self.name,
            "rule_type": self.rule_type.value
        })
    
    @classmethod
    def get_applicable_rules(cls, session, customer_id: int = None, product_id: int = None,
                           product_category_id: int = None, quantity: Decimal = None,
                           amount: Decimal = None, company_id: int = None) -> List['PricingRule']:
        """Get applicable pricing rules for given criteria."""
        query = session.query(cls).filter(
            cls.is_active == True,
            cls.company_id == company_id
        )
        
        # Filter by validity date range
        today = date.today()
        query = query.filter(
            (cls.start_date.is_(None)) | (cls.start_date <= today)
        ).filter(
            (cls.end_date.is_(None)) | (cls.end_date >= today)
        )
        
        # Filter by customer if specified
        if customer_id:
            query = query.filter(
                (cls.customer_id.is_(None)) | (cls.customer_id == customer_id)
            )
        
        # Filter by product if specified
        if product_id:
            query = query.filter(
                (cls.product_id.is_(None)) | (cls.product_id == product_id)
            )
        
        # Filter by product category if specified
        if product_category_id:
            query = query.filter(
                (cls.product_category_id.is_(None)) | (cls.product_category_id == product_category_id)
            )
        
        # Order by priority (lower number = higher priority)
        query = query.order_by(cls.priority.asc(), cls.created_at.desc())
        
        rules = query.all()
        
        # Further filter by quantity and amount constraints
        applicable_rules = []
        for rule in rules:
            if quantity and not rule.is_applicable_to_quantity(quantity):
                continue
            if amount and not rule.is_applicable_to_amount(amount):
                continue
            applicable_rules.append(rule)
        
        return applicable_rules