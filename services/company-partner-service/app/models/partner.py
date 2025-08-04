"""
Partner model for business partner management (customers, suppliers, vendors).
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.framework.base import CompanyBusinessObject


class Partner(CompanyBusinessObject):
    """
    Partner model for business partner management.
    
    This model stores information about business partners including customers,
    suppliers, and vendors. Partners are scoped to companies for multi-company
    data isolation and support hierarchical relationships.
    """
    
    __tablename__ = "partners"
    
    # Basic information
    name = Column(String(255), nullable=False)
    code = Column(String(50))
    partner_type = Column(String(20), nullable=False, default="customer", index=True)
    
    # Contact information
    email = Column(String(255))
    phone = Column(String(50))
    mobile = Column(String(50))
    website = Column(String(255))
    
    # Business information
    tax_id = Column(String(100))
    industry = Column(String(100))
    
    # Relationship management
    parent_partner_id = Column(
        Integer, 
        ForeignKey("partners.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Category assignment
    category_id = Column(
        Integer,
        ForeignKey("partner_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Settings - what type of partner this is
    is_company = Column(Boolean, default=False, nullable=False)
    is_customer = Column(Boolean, default=True, nullable=False)
    is_supplier = Column(Boolean, default=False, nullable=False)
    is_vendor = Column(Boolean, default=False, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    parent_partner = relationship("Partner", remote_side="Partner.id", back_populates="child_partners")
    child_partners = relationship("Partner", back_populates="parent_partner")
    company = relationship("Company", back_populates="partners")
    category = relationship("PartnerCategory", back_populates="partners")
    contacts = relationship("PartnerContact", back_populates="partner", cascade="all, delete-orphan")
    addresses = relationship("PartnerAddress", back_populates="partner", cascade="all, delete-orphan")
    communications = relationship("PartnerCommunication", back_populates="partner", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        # Partner code must be unique within each company
        UniqueConstraint("company_id", "code", name="partners_company_code_unique"),
        # Partner type must be valid
        CheckConstraint(
            "partner_type IN ('customer', 'supplier', 'vendor', 'both')", 
            name="partners_type_check"
        ),
        # Partner name cannot be empty
        CheckConstraint("LENGTH(name) >= 1", name="partners_name_check"),
        {'extend_existing': True}
    )
    
    def __str__(self):
        """String representation of the partner."""
        return f"Partner(name='{self.name}', code='{self.code}', type='{self.partner_type}', active={self.is_active})"
    
    def __repr__(self):
        """Detailed representation of the partner."""
        return (
            f"Partner(id={self.id}, company_id={self.company_id}, name='{self.name}', "
            f"code='{self.code}', type='{self.partner_type}', active={self.is_active})"
        )
    
    @property
    def is_parent(self):
        """Check if this partner has child partners."""
        return len(self.child_partners) > 0
    
    @property
    def has_parent(self):
        """Check if this partner has a parent partner."""
        return self.parent_partner_id is not None
    
    def get_partner_types(self):
        """Get list of partner types this partner represents."""
        types = []
        if self.is_customer:
            types.append("customer")
        if self.is_supplier:
            types.append("supplier")
        if self.is_vendor:
            types.append("vendor")
        return types