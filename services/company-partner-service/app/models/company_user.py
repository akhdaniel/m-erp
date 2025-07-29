"""
CompanyUser association model for user-company relationships.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class CompanyUser(BaseModel):
    """
    CompanyUser association model for linking users to companies.
    
    This model creates the many-to-many relationship between users (from the auth service)
    and companies, allowing users to have access to multiple companies with different
    roles in each company.
    """
    
    __tablename__ = "company_users"
    
    # Foreign keys
    company_id = Column(
        Integer, 
        ForeignKey("companies.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    user_id = Column(Integer, nullable=False, index=True)  # References users.id from auth service
    
    # Role within the company
    role = Column(String(50), nullable=False, default="user")
    
    # Whether this is the user's default company
    is_default_company = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    # company = relationship("Company", back_populates="users")
    
    # Constraints
    __table_args__ = (
        # Each user can only be associated with a company once
        UniqueConstraint("company_id", "user_id", name="company_users_unique"),
        # Role must be valid
        CheckConstraint(
            "role IN ('admin', 'manager', 'user', 'viewer')", 
            name="company_users_role_check"
        ),
        {'extend_existing': True}
    )
    
    def __str__(self):
        """String representation of the company user association."""
        return f"CompanyUser(company_id={self.company_id}, user_id={self.user_id}, role='{self.role}')"
    
    def __repr__(self):
        """Detailed representation of the company user association."""
        return (
            f"CompanyUser(id={self.id}, company_id={self.company_id}, user_id={self.user_id}, "
            f"role='{self.role}', default={self.is_default_company})"
        )
    
    def has_admin_access(self):
        """Check if user has admin access in this company."""
        return self.role == "admin"
    
    def has_manager_access(self):
        """Check if user has manager or admin access in this company."""
        return self.role in ("admin", "manager")
    
    def can_manage_users(self):
        """Check if user can manage other users in this company."""
        return self.role in ("admin", "manager")
    
    def can_edit_data(self):
        """Check if user can edit data in this company."""
        return self.role in ("admin", "manager", "user")
    
    def is_read_only(self):
        """Check if user has read-only access in this company."""
        return self.role == "viewer"