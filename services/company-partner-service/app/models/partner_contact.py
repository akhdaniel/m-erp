"""
PartnerContact model for extended contact management.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class PartnerContact(BaseModel):
    """
    PartnerContact model for storing extended contact information.
    
    This model allows partners to have multiple contacts with detailed
    information including job titles, departments, and communication preferences.
    """
    
    __tablename__ = "partner_contacts"
    
    # Foreign key to partner
    partner_id = Column(
        Integer, 
        ForeignKey("partners.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Contact information
    name = Column(String(255), nullable=False)
    title = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    mobile = Column(String(50))
    
    # Contact preferences
    is_primary = Column(Boolean, default=False, nullable=False, index=True)
    department = Column(String(100))
    notes = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    # partner = relationship("Partner", back_populates="contacts")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("LENGTH(name) >= 1", name="partner_contacts_name_check"),
        {'extend_existing': True}
    )
    
    def __str__(self):
        """String representation of the partner contact."""
        title_part = f", {self.title}" if self.title else ""
        return f"PartnerContact(name='{self.name}{title_part}', primary={self.is_primary})"
    
    def __repr__(self):
        """Detailed representation of the partner contact."""
        return (
            f"PartnerContact(id={self.id}, partner_id={self.partner_id}, name='{self.name}', "
            f"title='{self.title}', primary={self.is_primary}, active={self.is_active})"
        )
    
    def get_display_name(self):
        """Get formatted display name with title."""
        if self.title:
            return f"{self.name}, {self.title}"
        return self.name
    
    def get_primary_phone(self):
        """Get the primary phone number (mobile preferred)."""
        return self.mobile or self.phone
    
    def has_email(self):
        """Check if contact has email address."""
        return bool(self.email)
    
    def has_phone(self):
        """Check if contact has any phone number."""
        return bool(self.phone or self.mobile)