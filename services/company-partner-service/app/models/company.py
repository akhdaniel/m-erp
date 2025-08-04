"""
Company model for multi-company support.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, CheckConstraint
from sqlalchemy.orm import relationship

from app.framework.base import BusinessObjectBase


class Company(BusinessObjectBase):
    """
    Company model for multi-company operations.
    
    This model stores company/legal entity information and serves as the foundation
    for multi-company data isolation throughout the system. All business objects
    reference a company_id to ensure proper data scoping.
    """
    
    __tablename__ = "companies"
    
    # Basic company information
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Contact information
    email = Column(String(255))
    phone = Column(String(50))
    website = Column(String(255))
    tax_id = Column(String(100))
    
    # Address information
    street = Column(Text)
    street2 = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    zip = Column(String(20))
    country = Column(String(100))
    
    # Configuration
    currency = Column(String(3), default="USD")
    timezone = Column(String(50), default="UTC")
    logo_url = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    # Note: These will be added when the related models are created
    # users = relationship("CompanyUser", back_populates="company")
    partners = relationship("Partner", back_populates="company")
    partner_categories = relationship("PartnerCategory", back_populates="company")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("LENGTH(code) >= 2", name="companies_code_check"),
        CheckConstraint("LENGTH(name) >= 1", name="companies_name_check"),
        {'extend_existing': True}
    )
    
    def __str__(self):
        """String representation of the company."""
        return f"Company(name='{self.name}', code='{self.code}', active={self.is_active})"
    
    def __repr__(self):
        """Detailed representation of the company."""
        return (
            f"Company(id={self.id}, name='{self.name}', code='{self.code}', "
            f"legal_name='{self.legal_name}', active={self.is_active})"
        )