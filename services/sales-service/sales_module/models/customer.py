"""
Customer management models for sales operations.

Provides comprehensive customer relationship management including
customer information, contacts, addresses, and categorization.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from sales_module.framework.base import CompanyBusinessObject, BaseModel


class CustomerStatus(str, enum.Enum):
    """Customer status enumeration"""
    PROSPECT = "prospect"  # Potential customer
    ACTIVE = "active"  # Active customer
    INACTIVE = "inactive"  # Inactive customer
    BLOCKED = "blocked"  # Blocked from transactions
    VIP = "vip"  # VIP customer


class CustomerType(str, enum.Enum):
    """Customer type enumeration"""
    INDIVIDUAL = "individual"  # Individual consumer
    BUSINESS = "business"  # Business customer
    GOVERNMENT = "government"  # Government entity
    NON_PROFIT = "non_profit"  # Non-profit organization


class ContactType(str, enum.Enum):
    """Contact type enumeration"""
    PRIMARY = "primary"  # Primary contact
    BILLING = "billing"  # Billing contact
    SHIPPING = "shipping"  # Shipping contact
    TECHNICAL = "technical"  # Technical contact
    SALES = "sales"  # Sales contact


class AddressType(str, enum.Enum):
    """Address type enumeration"""
    BILLING = "billing"  # Billing address
    SHIPPING = "shipping"  # Shipping address
    MAILING = "mailing"  # Mailing address
    HEADQUARTERS = "headquarters"  # Company headquarters


class CustomerCategory(CompanyBusinessObject):
    """
    Customer Category model for customer segmentation and classification.
    
    Provides hierarchical categorization system for customers with
    parent-child relationships and business rules.
    """
    
    __tablename__ = "customer_categories"
    
    # Category information
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    
    # Hierarchical structure
    parent_category_id = Column(
        Integer,
        ForeignKey("customer_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Display and organization
    display_order = Column(Integer, nullable=False, default=0)
    color = Column(String(7))  # Hex color code for UI
    icon = Column(String(100))  # Icon identifier for UI
    
    # Business rules
    credit_limit_default = Column(Numeric(15, 2), nullable=True)
    payment_terms_days = Column(Integer, nullable=True, default=30)
    discount_percentage = Column(Numeric(5, 2), nullable=True, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Statistics (updated by triggers/background jobs)
    customer_count = Column(Integer, nullable=False, default=0)
    
    # Relationships
    # parent_category = relationship("CustomerCategory", remote_side=[id], back_populates="child_categories")
    # child_categories = relationship("CustomerCategory", back_populates="parent_category", cascade="all, delete-orphan")
    # customers = relationship("Customer", back_populates="category")
    
    def __str__(self):
        """String representation of customer category."""
        return f"{self.name} ({self.code})"
    
    def __repr__(self):
        """Detailed representation of customer category."""
        return (
            f"CustomerCategory(id={self.id}, name='{self.name}', code='{self.code}', "
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


class Customer(CompanyBusinessObject):
    """
    Customer model representing sales customers and prospects.
    
    Comprehensive customer information including identification,
    classification, financial settings, and relationship management.
    """
    
    __tablename__ = "customers"
    
    # Basic customer information
    name = Column(String(255), nullable=False, index=True)
    customer_number = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=True)
    
    # Customer classification
    customer_type = Column(Enum(CustomerType), nullable=False, default=CustomerType.BUSINESS, index=True)
    status = Column(Enum(CustomerStatus), nullable=False, default=CustomerStatus.PROSPECT, index=True)
    
    # Categorization
    category_id = Column(
        Integer,
        ForeignKey("customer_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Business information
    tax_id = Column(String(50), nullable=True, index=True)
    registration_number = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    
    # Financial settings
    currency_code = Column(String(3), nullable=False, default="USD")
    credit_limit = Column(Numeric(15, 2), nullable=True)
    payment_terms_days = Column(Integer, nullable=False, default=30)
    discount_percentage = Column(Numeric(5, 2), nullable=False, default=0.0)
    
    # Sales information
    sales_rep_user_id = Column(Integer, nullable=True, index=True)
    referral_source = Column(String(255), nullable=True)
    acquisition_date = Column(DateTime, nullable=True)
    first_order_date = Column(DateTime, nullable=True)
    last_order_date = Column(DateTime, nullable=True)
    
    # Preferences
    preferred_communication = Column(String(50), nullable=True, default="email")
    language_code = Column(String(5), nullable=False, default="en")
    timezone = Column(String(50), nullable=False, default="UTC")
    
    # Marketing and communication
    allow_marketing = Column(Boolean, nullable=False, default=True)
    allow_sms = Column(Boolean, nullable=False, default=False)
    newsletter_subscription = Column(Boolean, nullable=False, default=False)
    
    # Internal notes and tracking
    description = Column(Text)
    internal_notes = Column(Text)
    tags = Column(JSON)  # Array of string tags
    
    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    blocked_reason = Column(String(255), nullable=True)
    blocked_date = Column(DateTime, nullable=True)
    
    # Financial tracking (calculated fields)
    total_orders_count = Column(Integer, nullable=False, default=0)
    total_orders_value = Column(Numeric(15, 2), nullable=False, default=0.0)
    average_order_value = Column(Numeric(15, 2), nullable=False, default=0.0)
    outstanding_balance = Column(Numeric(15, 2), nullable=False, default=0.0)
    
    # Additional attributes (flexible schema)
    custom_attributes = Column(JSON)
    
    # Relationships
    # category = relationship("CustomerCategory", back_populates="customers")
    # contacts = relationship("CustomerContact", back_populates="customer", cascade="all, delete-orphan")
    # addresses = relationship("CustomerAddress", back_populates="customer", cascade="all, delete-orphan")
    # opportunities = relationship("SalesOpportunity", back_populates="customer")
    # quotes = relationship("SalesQuote", back_populates="customer")
    # orders = relationship("SalesOrder", back_populates="customer")
    
    def __str__(self):
        """String representation of customer."""
        return f"{self.name} ({self.customer_number})"
    
    def __repr__(self):
        """Detailed representation of customer."""
        return (
            f"Customer(id={self.id}, name='{self.name}', number='{self.customer_number}', "
            f"type='{self.customer_type.value}', status='{self.status.value}')"
        )
    
    @property
    def display_identifier(self) -> str:
        """Get display identifier with customer number."""
        return f"{self.display_name or self.name} ({self.customer_number})"
    
    @property
    def is_blocked(self) -> bool:
        """Check if customer is blocked."""
        return self.status == CustomerStatus.BLOCKED
    
    @property
    def is_vip(self) -> bool:
        """Check if customer has VIP status."""
        return self.status == CustomerStatus.VIP
    
    @property
    def available_credit(self) -> Optional[Decimal]:
        """Calculate available credit limit."""
        if not self.credit_limit:
            return None
        return self.credit_limit - self.outstanding_balance
    
    @property
    def is_over_credit_limit(self) -> bool:
        """Check if customer is over credit limit."""
        if not self.credit_limit:
            return False
        return self.outstanding_balance > self.credit_limit
    
    @property
    def customer_age_days(self) -> Optional[int]:
        """Calculate customer age in days since acquisition."""
        if not self.acquisition_date:
            return None
        return (datetime.utcnow() - self.acquisition_date).days
    
    @property
    def days_since_last_order(self) -> Optional[int]:
        """Calculate days since last order."""
        if not self.last_order_date:
            return None
        return (datetime.utcnow() - self.last_order_date).days
    
    def generate_customer_number(self, prefix: str = "CUST") -> str:
        """Generate customer number if not provided."""
        # In production, would use company settings and sequence numbers
        import time
        timestamp = int(time.time())
        return f"{prefix}{timestamp:08d}"
    
    def update_financial_metrics(self, order_count_change: int = 0, 
                                order_value_change: Decimal = None) -> None:
        """Update customer financial metrics."""
        self.total_orders_count += order_count_change
        
        if order_value_change:
            self.total_orders_value += order_value_change
            
            # Recalculate average order value
            if self.total_orders_count > 0:
                self.average_order_value = self.total_orders_value / self.total_orders_count
    
    def block_customer(self, reason: str, user_id: int = None) -> None:
        """Block customer from transactions."""
        self.status = CustomerStatus.BLOCKED
        self.blocked_reason = reason
        self.blocked_date = datetime.utcnow()
        
        # Log audit trail
        self.log_audit_trail("customer_blocked", user_id, {"reason": reason})
        
        # Publish event
        self.publish_event("customer.blocked", {
            "customer_id": self.id,
            "customer_number": self.customer_number,
            "reason": reason
        })
    
    def unblock_customer(self, user_id: int = None) -> None:
        """Unblock customer."""
        old_status = self.status
        self.status = CustomerStatus.ACTIVE
        self.blocked_reason = None
        self.blocked_date = None
        
        # Log audit trail
        self.log_audit_trail("customer_unblocked", user_id, {
            "previous_status": old_status.value
        })
        
        # Publish event
        self.publish_event("customer.unblocked", {
            "customer_id": self.id,
            "customer_number": self.customer_number
        })
    
    def calculate_credit_score(self) -> int:
        """Calculate basic customer credit score (simplified)."""
        score = 50  # Base score
        
        # Payment history (simplified)
        if self.outstanding_balance <= 0:
            score += 20
        elif self.is_over_credit_limit:
            score -= 30
        
        # Customer age
        age_days = self.customer_age_days
        if age_days and age_days > 365:
            score += 15
        elif age_days and age_days > 90:
            score += 5
        
        # Order frequency
        if self.days_since_last_order:
            if self.days_since_last_order <= 30:
                score += 10
            elif self.days_since_last_order <= 90:
                score += 5
        
        # Order value
        if self.average_order_value > 1000:
            score += 10
        elif self.average_order_value > 500:
            score += 5
        
        return max(0, min(100, score))


class CustomerContact(CompanyBusinessObject):
    """
    Customer Contact model for managing multiple contacts per customer.
    
    Handles contact information, communication preferences,
    and role-based contact management.
    """
    
    __tablename__ = "customer_contacts"
    
    # Customer reference
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Contact information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    title = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Contact details
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    mobile = Column(String(50), nullable=True)
    fax = Column(String(50), nullable=True)
    
    # Contact type and preferences
    contact_type = Column(Enum(ContactType), nullable=False, default=ContactType.PRIMARY, index=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    
    # Communication preferences
    preferred_communication = Column(String(50), nullable=False, default="email")
    language_code = Column(String(5), nullable=False, default="en")
    timezone = Column(String(50), nullable=False, default="UTC")
    
    # Permissions and access
    can_place_orders = Column(Boolean, nullable=False, default=False)
    can_approve_orders = Column(Boolean, nullable=False, default=False)
    can_view_pricing = Column(Boolean, nullable=False, default=True)
    can_receive_invoices = Column(Boolean, nullable=False, default=False)
    
    # Additional information
    birthday = Column(DateTime, nullable=True)
    notes = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    # customer = relationship("Customer", back_populates="contacts")
    
    def __str__(self):
        """String representation of customer contact."""
        return f"{self.full_name} ({self.contact_type.value})"
    
    def __repr__(self):
        """Detailed representation of customer contact."""
        return (
            f"CustomerContact(id={self.id}, name='{self.full_name}', "
            f"customer_id={self.customer_id}, type='{self.contact_type.value}')"
        )
    
    @property
    def full_name(self) -> str:
        """Get full name of contact."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self) -> str:
        """Get display name with title if available."""
        if self.title:
            return f"{self.full_name}, {self.title}"
        return self.full_name
    
    def get_primary_contact_method(self) -> Optional[str]:
        """Get primary contact information based on preference."""
        if self.preferred_communication == "email" and self.email:
            return self.email
        elif self.preferred_communication == "phone" and self.phone:
            return self.phone
        elif self.preferred_communication == "mobile" and self.mobile:
            return self.mobile
        
        # Fallback to any available contact method
        return self.email or self.phone or self.mobile


class CustomerAddress(CompanyBusinessObject):
    """
    Customer Address model for managing multiple addresses per customer.
    
    Handles billing, shipping, and other address types with
    validation and geocoding support.
    """
    
    __tablename__ = "customer_addresses"
    
    # Customer reference
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Address identification
    name = Column(String(255), nullable=False)  # Address nickname
    address_type = Column(Enum(AddressType), nullable=False, index=True)
    
    # Address details
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state_province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=False)
    country_code = Column(String(3), nullable=False, default="US")
    
    # Additional address information
    company_name = Column(String(255), nullable=True)
    attention_to = Column(String(255), nullable=True)
    
    # Geographic coordinates (for mapping and distance calculations)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    
    # Delivery instructions and notes
    delivery_instructions = Column(Text)
    access_code = Column(String(50), nullable=True)
    
    # Address flags
    is_default = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Validation information
    validated_date = Column(DateTime, nullable=True)
    validation_service = Column(String(100), nullable=True)
    
    # Relationships
    # customer = relationship("Customer", back_populates="addresses")
    
    def __str__(self):
        """String representation of customer address."""
        return f"{self.name} ({self.address_type.value})"
    
    def __repr__(self):
        """Detailed representation of customer address."""
        return (
            f"CustomerAddress(id={self.id}, name='{self.name}', "
            f"customer_id={self.customer_id}, type='{self.address_type.value}')"
        )
    
    @property
    def full_address(self) -> str:
        """Get formatted full address."""
        parts = []
        if self.company_name:
            parts.append(self.company_name)
        if self.attention_to:
            parts.append(f"Attn: {self.attention_to}")
        
        parts.append(self.address_line_1)
        if self.address_line_2:
            parts.append(self.address_line_2)
        
        city_line = self.city
        if self.state_province:
            city_line += f", {self.state_province}"
        if self.postal_code:
            city_line += f" {self.postal_code}"
        parts.append(city_line)
        
        parts.append(self.country_code)
        
        return "\n".join(parts)
    
    @property
    def single_line_address(self) -> str:
        """Get single line address format."""
        parts = [self.address_line_1]
        if self.address_line_2:
            parts.append(self.address_line_2)
        parts.append(self.city)
        if self.state_province:
            parts.append(self.state_province)
        parts.append(self.postal_code)
        parts.append(self.country_code)
        
        return ", ".join(parts)
    
    def validate_address(self, validation_service: str = "internal") -> bool:
        """Validate address using specified service."""
        # In production, would integrate with address validation services
        # like Google Maps API, USPS, etc.
        
        # Simple validation
        required_fields = [self.address_line_1, self.city, self.postal_code, self.country_code]
        is_valid = all(field for field in required_fields)
        
        if is_valid:
            self.is_verified = True
            self.validated_date = datetime.utcnow()
            self.validation_service = validation_service
        
        return is_valid
    
    def geocode_address(self) -> bool:
        """Geocode address to get latitude/longitude coordinates."""
        # In production, would integrate with geocoding services
        # For demo purposes, return success without actual geocoding
        
        # Simulate successful geocoding
        if self.city and self.country_code:
            # Would set actual coordinates from geocoding service
            self.latitude = Decimal('0.0')  # Would be actual latitude
            self.longitude = Decimal('0.0')  # Would be actual longitude
            return True
        
        return False