"""
PartnerAddress model for multiple address types per partner.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class PartnerAddress(BaseModel):
    """
    PartnerAddress model for storing multiple address types.
    
    This model allows partners to have multiple addresses for different purposes
    such as billing, shipping, and general correspondence with proper type management.
    """
    
    __tablename__ = "partner_addresses"
    
    # Foreign key to partner
    partner_id = Column(
        Integer, 
        ForeignKey("partners.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Address information
    address_type = Column(String(20), nullable=False, default="default", index=True)
    street = Column(Text, nullable=False)
    street2 = Column(Text)
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    zip = Column(String(20))
    country = Column(String(100), nullable=False)
    
    # Settings
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    partner = relationship("Partner", back_populates="addresses")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "address_type IN ('default', 'billing', 'shipping', 'other')", 
            name="partner_addresses_type_check"
        ),
        {'extend_existing': True}
    )
    
    def __str__(self):
        """String representation of the partner address."""
        return f"PartnerAddress(type='{self.address_type}', {self.street}, {self.city})"
    
    def __repr__(self):
        """Detailed representation of the partner address."""
        return (
            f"PartnerAddress(id={self.id}, partner_id={self.partner_id}, "
            f"type='{self.address_type}', default={self.is_default})"
        )
    
    def get_formatted_address(self, include_type=False):
        """Get formatted address string."""
        lines = []
        
        if include_type and self.address_type != "default":
            lines.append(f"{self.address_type.title()} Address:")
        
        lines.append(self.street)
        
        if self.street2:
            lines.append(self.street2)
        
        # City, State ZIP
        city_line = self.city
        if self.state:
            city_line += f", {self.state}"
        if self.zip:
            city_line += f" {self.zip}"
        lines.append(city_line)
        
        lines.append(self.country)
        
        return "\n".join(lines)
    
    def get_single_line_address(self):
        """Get address as single line string."""
        parts = [self.street]
        
        if self.street2:
            parts.append(self.street2)
        
        parts.append(self.city)
        
        if self.state:
            parts.append(self.state)
        
        if self.zip:
            parts.append(self.zip)
        
        parts.append(self.country)
        
        return ", ".join(parts)
    
    def is_complete(self):
        """Check if address has all required fields."""
        return bool(self.street and self.city and self.country)
    
    def is_billing_address(self):
        """Check if this is a billing address."""
        return self.address_type == "billing"
    
    def is_shipping_address(self):
        """Check if this is a shipping address."""
        return self.address_type == "shipping"