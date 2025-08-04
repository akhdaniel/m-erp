"""
Partner Category model for flexible partner organization.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from app.framework.base import CompanyBusinessObject


class PartnerCategory(CompanyBusinessObject):
    """
    Partner Category model for organizing partners into flexible groups.
    
    This model allows businesses to create custom categorization systems
    for partners with hierarchical organization capabilities and company-specific
    categories for multi-company data isolation.
    """
    
    __tablename__ = "partner_categories"
    
    # Basic information
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text)
    color = Column(String(7))  # Hex color code for UI display
    
    # Hierarchical relationships
    parent_category_id = Column(
        Integer,
        ForeignKey("partner_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Settings
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    parent_category = relationship("PartnerCategory", remote_side="PartnerCategory.id", back_populates="child_categories")    
    child_categories = relationship("PartnerCategory", back_populates="parent_category")
    company = relationship("Company", back_populates="partner_categories")
    partners = relationship("Partner", back_populates="category", foreign_keys="Partner.category_id")
    
    # Constraints
    __table_args__ = (
        # Category code must be unique within each company
        UniqueConstraint("company_id", "code", name="partner_categories_company_code_unique"),
        # Category name must be unique within each company
        UniqueConstraint("company_id", "name", name="partner_categories_company_name_unique"),
        # Category name cannot be empty
        CheckConstraint("LENGTH(name) >= 1", name="partner_categories_name_check"),
        # Category code cannot be empty
        CheckConstraint("LENGTH(code) >= 1", name="partner_categories_code_check"),
        # Color must be valid hex code if provided
        CheckConstraint("color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'", name="partner_categories_color_check"),
        {'extend_existing': True}
    )
    
    def __str__(self):
        """String representation of the partner category."""
        return f"PartnerCategory(name='{self.name}', code='{self.code}', active={self.is_active})"
    
    def __repr__(self):
        """Detailed representation of the partner category."""
        return (
            f"PartnerCategory(id={self.id}, company_id={self.company_id}, name='{self.name}', "
            f"code='{self.code}', active={self.is_active})"
        )
    
    @property
    def is_parent(self):
        """Check if this category has child categories."""
        return len(self.child_categories) > 0
    
    @property
    def has_parent(self):
        """Check if this category has a parent category."""
        return self.parent_category_id is not None
    
    @property
    def full_path(self):
        """Get full hierarchical path of the category."""
        if self.parent_category:
            return f"{self.parent_category.full_path} > {self.name}"
        return self.name
    
    def get_all_children(self):
        """Get all child categories recursively."""
        children = []
        for child in self.child_categories:
            children.append(child)
            children.extend(child.get_all_children())
        return children
    
    def get_partner_count(self):
        """Get the number of partners in this category."""
        return len([p for p in self.partners if p.is_active])
    
    def can_be_deleted(self):
        """Check if category can be safely deleted."""
        # Cannot delete if has active partners or child categories
        return not self.is_parent and self.get_partner_count() == 0