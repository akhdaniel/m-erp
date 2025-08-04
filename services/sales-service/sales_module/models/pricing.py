"""
Pricing and discount models for dynamic pricing management.

Provides comprehensive pricing engine including price lists,
rules, discounts, promotions, and dynamic pricing calculations.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from sales_module.framework.base import CompanyBusinessObject, BaseModel


class PriceListType(str, enum.Enum):
    """Price list type enumeration"""
    STANDARD = "standard"  # Standard pricing
    CUSTOMER_SPECIFIC = "customer_specific"  # Customer-specific pricing
    VOLUME = "volume"  # Volume pricing
    PROMOTIONAL = "promotional"  # Promotional pricing
    CONTRACT = "contract"  # Contract pricing


class RuleType(str, enum.Enum):
    """Price rule type enumeration"""
    FIXED_PRICE = "fixed_price"  # Fixed price override
    PERCENTAGE_DISCOUNT = "percentage_discount"  # Percentage discount
    FIXED_DISCOUNT = "fixed_discount"  # Fixed amount discount
    VOLUME_DISCOUNT = "volume_discount"  # Volume-based discount
    MARKUP = "markup"  # Markup from cost
    MARGIN = "margin"  # Target margin percentage


class DiscountType(str, enum.Enum):
    """Discount type enumeration"""
    PERCENTAGE = "percentage"  # Percentage discount
    FIXED_AMOUNT = "fixed_amount"  # Fixed amount discount
    BUY_X_GET_Y = "buy_x_get_y"  # Buy X get Y free
    VOLUME_TIER = "volume_tier"  # Volume tier discount


class PromotionType(str, enum.Enum):
    """Promotion type enumeration"""
    PRODUCT_DISCOUNT = "product_discount"  # Product-specific discount
    ORDER_DISCOUNT = "order_discount"  # Order-level discount
    FREE_SHIPPING = "free_shipping"  # Free shipping promotion
    BUNDLE_DEAL = "bundle_deal"  # Bundle pricing
    LOYALTY_DISCOUNT = "loyalty_discount"  # Loyalty program discount


class PriceList(CompanyBusinessObject):
    """
    Price List model for managing product pricing.
    
    Comprehensive price list management including customer-specific,
    volume-based, and promotional pricing structures.
    """
    
    __tablename__ = "price_lists"
    
    # Basic price list information
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    
    # Price list type and configuration
    price_list_type = Column(Enum(PriceListType), nullable=False, index=True)
    currency_code = Column(String(3), nullable=False, default="USD")
    
    # Validity period
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    valid_until = Column(DateTime, nullable=True, index=True)
    
    # Customer and category filters
    customer_categories = Column(JSON)  # Array of customer category IDs
    specific_customers = Column(JSON)  # Array of specific customer IDs
    product_categories = Column(JSON)  # Array of product category IDs
    
    # Geographic and channel restrictions
    allowed_countries = Column(JSON)  # Array of country codes
    allowed_channels = Column(JSON)  # Array of sales channels
    
    # Pricing configuration
    base_price_list_id = Column(
        Integer,
        ForeignKey("price_lists.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    markup_percentage = Column(Numeric(5, 2), nullable=True)
    margin_percentage = Column(Numeric(5, 2), nullable=True)
    
    # Volume pricing settings
    minimum_quantity = Column(Numeric(15, 4), nullable=True)
    quantity_breaks = Column(JSON)  # Array of quantity break rules
    
    # Priority and rules
    priority = Column(Integer, nullable=False, default=100)  # Lower number = higher priority
    allow_manual_override = Column(Boolean, nullable=False, default=True)
    requires_approval = Column(Boolean, nullable=False, default=False)
    
    # Usage tracking
    usage_count = Column(Integer, nullable=False, default=0)
    last_used_date = Column(DateTime, nullable=True)
    
    # Status and activation
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    auto_activate = Column(Boolean, nullable=False, default=True)
    
    # Additional settings
    notes = Column(Text)
    tags = Column(JSON)  # Array of string tags
    
    # Relationships
    # base_price_list = relationship("PriceList", remote_side=[id], back_populates="derived_lists")
    # derived_lists = relationship("PriceList", back_populates="base_price_list", cascade="all, delete-orphan")
    # price_rules = relationship("PriceRule", back_populates="price_list", cascade="all, delete-orphan")
    
    def __str__(self):
        """String representation of price list."""
        return f"{self.name} ({self.code})"
    
    def __repr__(self):
        """Detailed representation of price list."""
        return (
            f"PriceList(id={self.id}, name='{self.name}', code='{self.code}', "
            f"type='{self.price_list_type.value}', active={self.is_active})"
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if price list is currently valid."""
        now = datetime.utcnow()
        
        # Check validity period
        if now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        return self.is_active
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Calculate days until price list expires."""
        if not self.valid_until:
            return None
        
        delta = self.valid_until - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def is_customer_specific(self) -> bool:
        """Check if price list is customer-specific."""
        return self.price_list_type == PriceListType.CUSTOMER_SPECIFIC
    
    def is_applicable_to_customer(self, customer_id: int, customer_category_id: int = None) -> bool:
        """Check if price list applies to given customer."""
        if not self.is_valid:
            return False
        
        # Check specific customers
        if self.specific_customers and customer_id in self.specific_customers:
            return True
        
        # Check customer categories
        if (self.customer_categories and customer_category_id and 
            customer_category_id in self.customer_categories):
            return True
        
        # If no restrictions, applies to all
        if not self.specific_customers and not self.customer_categories:
            return True
        
        return False
    
    def is_applicable_to_product(self, product_id: int, product_category_id: int = None) -> bool:
        """Check if price list applies to given product."""
        if not self.is_valid:
            return False
        
        # Check product categories
        if (self.product_categories and product_category_id and 
            product_category_id in self.product_categories):
            return True
        
        # If no product restrictions, applies to all products
        if not self.product_categories:
            return True
        
        return False
    
    def calculate_price(self, base_price: Decimal, quantity: Decimal = 1) -> Decimal:
        """Calculate price based on price list rules."""
        if not base_price or base_price <= 0:
            return Decimal('0.00')
        
        calculated_price = base_price
        
        # Apply markup if configured
        if self.markup_percentage:
            calculated_price = base_price * (1 + self.markup_percentage / 100)
        
        # Apply volume pricing if configured
        if self.quantity_breaks and quantity:
            applicable_break = self.get_applicable_quantity_break(quantity)
            if applicable_break:
                discount_percentage = applicable_break.get('discount_percentage', 0)
                calculated_price = calculated_price * (1 - discount_percentage / 100)
        
        return calculated_price
    
    def get_applicable_quantity_break(self, quantity: Decimal) -> Optional[Dict]:
        """Get applicable quantity break for given quantity."""
        if not self.quantity_breaks:
            return None
        
        # Find the highest quantity break that applies
        applicable_break = None
        for break_rule in self.quantity_breaks:
            min_quantity = break_rule.get('min_quantity', 0)
            if quantity >= min_quantity:
                if not applicable_break or min_quantity > applicable_break.get('min_quantity', 0):
                    applicable_break = break_rule
        
        return applicable_break
    
    def activate(self, user_id: int = None) -> None:
        """Activate price list."""
        self.is_active = True
        
        # Log audit trail
        self.log_audit_trail("price_list_activated", user_id)
        
        # Publish event
        self.publish_event("price_list.activated", {
            "price_list_id": self.id,
            "price_list_code": self.code
        })
    
    def deactivate(self, user_id: int = None) -> None:
        """Deactivate price list."""
        self.is_active = False
        
        # Log audit trail
        self.log_audit_trail("price_list_deactivated", user_id)
        
        # Publish event
        self.publish_event("price_list.deactivated", {
            "price_list_id": self.id,
            "price_list_code": self.code
        })


class PriceRule(CompanyBusinessObject):
    """
    Price Rule model for specific pricing rules and overrides.
    
    Individual pricing rules that can override or supplement
    price list pricing for specific products or conditions.
    """
    
    __tablename__ = "price_rules"
    
    # Price list reference
    price_list_id = Column(
        Integer,
        ForeignKey("price_lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Rule identification
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True, index=True)
    description = Column(Text)
    
    # Rule type and configuration
    rule_type = Column(Enum(RuleType), nullable=False, index=True)
    
    # Product targeting
    product_id = Column(Integer, nullable=True, index=True)
    product_code = Column(String(100), nullable=True, index=True)
    product_category_id = Column(Integer, nullable=True, index=True)
    
    # Pricing values
    fixed_price = Column(Numeric(15, 4), nullable=True)
    percentage_value = Column(Numeric(5, 2), nullable=True)  # For discounts/markups
    fixed_amount = Column(Numeric(15, 2), nullable=True)  # For fixed discounts
    
    # Quantity-based rules
    minimum_quantity = Column(Numeric(15, 4), nullable=True)
    maximum_quantity = Column(Numeric(15, 4), nullable=True)
    
    # Conditions and filters
    conditions = Column(JSON)  # Complex condition rules
    customer_restrictions = Column(JSON)  # Customer-specific restrictions
    
    # Validity period
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    valid_until = Column(DateTime, nullable=True, index=True)
    
    # Priority and stacking
    priority = Column(Integer, nullable=False, default=100)
    can_stack = Column(Boolean, nullable=False, default=False)  # Can combine with other rules
    
    # Usage limits
    usage_limit = Column(Integer, nullable=True)  # Maximum number of uses
    usage_count = Column(Integer, nullable=False, default=0)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Additional information
    notes = Column(Text)
    
    # Relationships
    # price_list = relationship("PriceList", back_populates="price_rules")
    
    def __str__(self):
        """String representation of price rule."""
        return f"{self.name} ({self.rule_type.value})"
    
    def __repr__(self):
        """Detailed representation of price rule."""
        return (
            f"PriceRule(id={self.id}, name='{self.name}', "
            f"type='{self.rule_type.value}', active={self.is_active})"
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if price rule is currently valid."""
        now = datetime.utcnow()
        
        # Check active status
        if not self.is_active:
            return False
        
        # Check validity period
        if now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        # Check usage limit
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        
        return True
    
    @property
    def has_usage_remaining(self) -> bool:
        """Check if rule has usage remaining."""
        if not self.usage_limit:
            return True
        return self.usage_count < self.usage_limit
    
    def is_applicable_to_product(self, product_id: int = None, product_code: str = None,
                                product_category_id: int = None) -> bool:
        """Check if rule applies to given product."""
        if not self.is_valid:
            return False
        
        # Check specific product ID
        if self.product_id and product_id != self.product_id:
            return False
        
        # Check specific product code
        if self.product_code and product_code != self.product_code:
            return False
        
        # Check product category
        if self.product_category_id and product_category_id != self.product_category_id:
            return False
        
        return True
    
    def is_applicable_to_quantity(self, quantity: Decimal) -> bool:
        """Check if rule applies to given quantity."""
        if not self.is_valid:
            return False
        
        # Check minimum quantity
        if self.minimum_quantity and quantity < self.minimum_quantity:
            return False
        
        # Check maximum quantity
        if self.maximum_quantity and quantity > self.maximum_quantity:
            return False
        
        return True
    
    def calculate_price(self, base_price: Decimal, quantity: Decimal = 1) -> Optional[Decimal]:
        """Calculate price based on rule."""
        if not self.is_applicable_to_quantity(quantity):
            return None
        
        if self.rule_type == RuleType.FIXED_PRICE:
            return self.fixed_price
        
        elif self.rule_type == RuleType.PERCENTAGE_DISCOUNT:
            if self.percentage_value:
                discount = base_price * (self.percentage_value / 100)
                return base_price - discount
        
        elif self.rule_type == RuleType.FIXED_DISCOUNT:
            if self.fixed_amount:
                return max(Decimal('0.00'), base_price - self.fixed_amount)
        
        elif self.rule_type == RuleType.MARKUP:
            if self.percentage_value:
                return base_price * (1 + self.percentage_value / 100)
        
        elif self.rule_type == RuleType.MARGIN:
            # Calculate price to achieve target margin
            if self.percentage_value:
                # Price = Cost / (1 - Margin%)
                margin_multiplier = 1 - (self.percentage_value / 100)
                if margin_multiplier > 0:
                    return base_price / margin_multiplier
        
        return None
    
    def use_rule(self, user_id: int = None) -> None:
        """Record usage of the rule."""
        self.usage_count += 1
        
        # Log audit trail
        self.log_audit_trail("price_rule_used", user_id, {
            "usage_count": self.usage_count
        })


class Discount(CompanyBusinessObject):
    """
    Discount model for managing promotional discounts.
    
    Flexible discount system supporting various discount types,
    conditions, and customer targeting.
    """
    
    __tablename__ = "discounts"
    
    # Basic discount information
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # Discount type and configuration
    discount_type = Column(Enum(DiscountType), nullable=False, index=True)
    
    # Discount values
    percentage_value = Column(Numeric(5, 2), nullable=True)
    fixed_amount = Column(Numeric(15, 2), nullable=True)
    currency_code = Column(String(3), nullable=False, default="USD")
    
    # Buy X Get Y configuration
    buy_quantity = Column(Integer, nullable=True)  # Buy X
    get_quantity = Column(Integer, nullable=True)  # Get Y free
    
    # Volume tier configuration
    tier_rules = Column(JSON)  # Array of tier rules
    
    # Applicability rules
    minimum_order_amount = Column(Numeric(15, 2), nullable=True)
    minimum_quantity = Column(Numeric(15, 4), nullable=True)
    
    # Product targeting
    applies_to_all_products = Column(Boolean, nullable=False, default=True)
    specific_products = Column(JSON)  # Array of product IDs
    product_categories = Column(JSON)  # Array of product category IDs
    excluded_products = Column(JSON)  # Array of excluded product IDs
    
    # Customer targeting
    applies_to_all_customers = Column(Boolean, nullable=False, default=True)
    specific_customers = Column(JSON)  # Array of customer IDs
    customer_categories = Column(JSON)  # Array of customer category IDs
    
    # Validity period
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    valid_until = Column(DateTime, nullable=True, index=True)
    
    # Usage limits
    usage_limit = Column(Integer, nullable=True)  # Total usage limit
    usage_limit_per_customer = Column(Integer, nullable=True)  # Per customer limit
    usage_count = Column(Integer, nullable=False, default=0)
    
    # Discount combination rules
    can_combine_with_other_discounts = Column(Boolean, nullable=False, default=False)
    priority = Column(Integer, nullable=False, default=100)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    auto_apply = Column(Boolean, nullable=False, default=False)  # Auto-apply if conditions met
    
    # Additional settings
    notes = Column(Text)
    tags = Column(JSON)  # Array of string tags
    
    def __str__(self):
        """String representation of discount."""
        return f"{self.name} ({self.code})"
    
    def __repr__(self):
        """Detailed representation of discount."""
        return (
            f"Discount(id={self.id}, name='{self.name}', code='{self.code}', "
            f"type='{self.discount_type.value}', active={self.is_active})"
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if discount is currently valid."""
        now = datetime.utcnow()
        
        # Check active status
        if not self.is_active:
            return False
        
        # Check validity period
        if now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        # Check usage limit
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        
        return True
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Calculate days until discount expires."""
        if not self.valid_until:
            return None
        
        delta = self.valid_until - datetime.utcnow()
        return max(0, delta.days)
    
    def is_applicable_to_customer(self, customer_id: int, customer_category_id: int = None) -> bool:
        """Check if discount applies to given customer."""
        if not self.is_valid:
            return False
        
        # If applies to all customers
        if self.applies_to_all_customers:
            return True
        
        # Check specific customers
        if self.specific_customers and customer_id in self.specific_customers:
            return True
        
        # Check customer categories
        if (self.customer_categories and customer_category_id and
            customer_category_id in self.customer_categories):
            return True
        
        return False
    
    def is_applicable_to_product(self, product_id: int, product_category_id: int = None) -> bool:
        """Check if discount applies to given product."""
        if not self.is_valid:
            return False
        
        # Check excluded products first
        if self.excluded_products and product_id in self.excluded_products:
            return False
        
        # If applies to all products
        if self.applies_to_all_products:
            return True
        
        # Check specific products
        if self.specific_products and product_id in self.specific_products:
            return True
        
        # Check product categories
        if (self.product_categories and product_category_id and
            product_category_id in self.product_categories):
            return True
        
        return False
    
    def calculate_discount(self, price: Decimal, quantity: Decimal = 1,
                          order_total: Decimal = None) -> Decimal:
        """Calculate discount amount."""
        if not self.is_valid:
            return Decimal('0.00')
        
        # Check minimum order amount
        if self.minimum_order_amount and (order_total or price) < self.minimum_order_amount:
            return Decimal('0.00')
        
        # Check minimum quantity
        if self.minimum_quantity and quantity < self.minimum_quantity:
            return Decimal('0.00')
        
        if self.discount_type == DiscountType.PERCENTAGE:
            if self.percentage_value:
                return price * (self.percentage_value / 100)
        
        elif self.discount_type == DiscountType.FIXED_AMOUNT:
            if self.fixed_amount:
                return min(self.fixed_amount, price)  # Don't exceed item price
        
        elif self.discount_type == DiscountType.VOLUME_TIER:
            return self.calculate_volume_tier_discount(price, quantity)
        
        return Decimal('0.00')
    
    def calculate_volume_tier_discount(self, price: Decimal, quantity: Decimal) -> Decimal:
        """Calculate volume tier discount."""
        if not self.tier_rules:
            return Decimal('0.00')
        
        # Find applicable tier
        applicable_tier = None
        for tier in self.tier_rules:
            min_quantity = tier.get('min_quantity', 0)
            if quantity >= min_quantity:
                if not applicable_tier or min_quantity > applicable_tier.get('min_quantity', 0):
                    applicable_tier = tier
        
        if not applicable_tier:
            return Decimal('0.00')
        
        # Apply tier discount
        discount_percentage = applicable_tier.get('discount_percentage', 0)
        return price * (Decimal(str(discount_percentage)) / 100)
    
    def use_discount(self, user_id: int = None) -> None:
        """Record usage of the discount."""
        self.usage_count += 1
        
        # Log audit trail
        self.log_audit_trail("discount_used", user_id, {
            "discount_code": self.code,
            "usage_count": self.usage_count
        })


class Promotion(CompanyBusinessObject):
    """
    Promotion model for managing marketing promotions.
    
    Complex promotional campaigns with multiple conditions,
    rewards, and marketing integration.
    """
    
    __tablename__ = "promotions"
    
    # Basic promotion information
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # Promotion type and configuration
    promotion_type = Column(Enum(PromotionType), nullable=False, index=True)
    
    # Promotion mechanics
    reward_type = Column(String(50), nullable=False)  # discount, free_item, free_shipping, etc.
    reward_value = Column(Numeric(15, 4), nullable=True)
    reward_configuration = Column(JSON)  # Complex reward rules
    
    # Conditions and requirements
    conditions = Column(JSON, nullable=False)  # Array of condition rules
    minimum_purchase_amount = Column(Numeric(15, 2), nullable=True)
    minimum_item_count = Column(Integer, nullable=True)
    
    # Product targeting
    qualifying_products = Column(JSON)  # Products that qualify for promotion
    reward_products = Column(JSON)  # Products that receive the reward
    excluded_products = Column(JSON)  # Excluded products
    
    # Customer targeting
    target_customers = Column(JSON)  # Specific customers
    target_customer_segments = Column(JSON)  # Customer segments/categories
    new_customers_only = Column(Boolean, nullable=False, default=False)
    
    # Validity period
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    valid_until = Column(DateTime, nullable=True, index=True)
    
    # Usage limits and tracking
    usage_limit = Column(Integer, nullable=True)
    usage_limit_per_customer = Column(Integer, nullable=True)
    usage_count = Column(Integer, nullable=False, default=0)
    
    # Marketing settings
    is_public = Column(Boolean, nullable=False, default=True)  # Publicly advertised
    requires_coupon_code = Column(Boolean, nullable=False, default=False)
    auto_apply = Column(Boolean, nullable=False, default=False)
    
    # Priority and stacking
    priority = Column(Integer, nullable=False, default=100)
    stackable = Column(Boolean, nullable=False, default=False)
    
    # Budget and cost tracking
    budget_amount = Column(Numeric(15, 2), nullable=True)
    spent_amount = Column(Numeric(15, 2), nullable=False, default=0.0)
    
    # Performance tracking
    click_count = Column(Integer, nullable=False, default=0)
    conversion_count = Column(Integer, nullable=False, default=0)
    revenue_generated = Column(Numeric(15, 2), nullable=False, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Additional settings
    notes = Column(Text)
    tags = Column(JSON)  # Array of string tags
    
    def __str__(self):
        """String representation of promotion."""
        return f"{self.name} ({self.code})"
    
    def __repr__(self):
        """Detailed representation of promotion."""
        return (
            f"Promotion(id={self.id}, name='{self.name}', code='{self.code}', "
            f"type='{self.promotion_type.value}', active={self.is_active})"
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if promotion is currently valid."""
        now = datetime.utcnow()
        
        # Check active status
        if not self.is_active:
            return False
        
        # Check validity period
        if now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        # Check usage limit
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        
        # Check budget limit
        if self.budget_amount and self.spent_amount >= self.budget_amount:
            return False
        
        return True
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Calculate days until promotion expires."""
        if not self.valid_until:
            return None
        
        delta = self.valid_until - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def budget_utilization_percentage(self) -> Optional[float]:
        """Calculate budget utilization percentage."""
        if not self.budget_amount or self.budget_amount <= 0:
            return None
        
        return (self.spent_amount / self.budget_amount) * 100
    
    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate."""
        if self.click_count <= 0:
            return 0.0
        
        return (self.conversion_count / self.click_count) * 100
    
    def is_applicable_to_customer(self, customer_id: int, is_new_customer: bool = False) -> bool:
        """Check if promotion applies to given customer."""
        if not self.is_valid:
            return False
        
        # Check new customer requirement
        if self.new_customers_only and not is_new_customer:
            return False
        
        # Check specific customers
        if self.target_customers and customer_id not in self.target_customers:
            return False
        
        return True
    
    def evaluate_conditions(self, order_data: Dict[str, Any]) -> bool:
        """Evaluate if order meets promotion conditions."""
        if not self.conditions:
            return True
        
        # This would implement complex condition evaluation
        # For demo purposes, simplified logic
        order_total = order_data.get('total_amount', 0)
        item_count = order_data.get('item_count', 0)
        
        if self.minimum_purchase_amount and order_total < self.minimum_purchase_amount:
            return False
        
        if self.minimum_item_count and item_count < self.minimum_item_count:
            return False
        
        return True
    
    def apply_promotion(self, order_data: Dict[str, Any], user_id: int = None) -> Dict[str, Any]:
        """Apply promotion and return reward details."""
        if not self.evaluate_conditions(order_data):
            return {"applied": False, "reason": "Conditions not met"}
        
        # Record usage
        self.usage_count += 1
        
        # Calculate reward
        reward_amount = self.calculate_reward(order_data)
        self.spent_amount += reward_amount
        
        # Track conversion
        self.conversion_count += 1
        
        # Log audit trail
        self.log_audit_trail("promotion_applied", user_id, {
            "promotion_code": self.code,
            "reward_amount": float(reward_amount),
            "order_total": order_data.get('total_amount', 0)
        })
        
        # Publish event
        self.publish_event("promotion.applied", {
            "promotion_id": self.id,
            "promotion_code": self.code,
            "customer_id": order_data.get('customer_id'),
            "reward_amount": float(reward_amount)
        })
        
        return {
            "applied": True,
            "reward_amount": float(reward_amount),
            "reward_type": self.reward_type,
            "promotion_name": self.name
        }
    
    def calculate_reward(self, order_data: Dict[str, Any]) -> Decimal:
        """Calculate reward amount based on promotion type."""
        if self.reward_type == "percentage_discount":
            order_total = Decimal(str(order_data.get('total_amount', 0)))
            return order_total * (self.reward_value / 100)
        
        elif self.reward_type == "fixed_discount":
            return self.reward_value or Decimal('0.00')
        
        elif self.reward_type == "free_shipping":
            return Decimal(str(order_data.get('shipping_amount', 0)))
        
        return Decimal('0.00')
    
    def track_click(self) -> None:
        """Track promotion click/view."""
        self.click_count += 1