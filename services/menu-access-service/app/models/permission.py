"""
Permission model for managing access rights.
"""

from sqlalchemy import Column, String, Text, Boolean, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Permission(BaseModel):
    """
    Permission model for access control.
    
    Defines what actions users can perform in the system.
    Permissions are atomic operations like "users.create", "companies.read", etc.
    """
    
    __tablename__ = "permissions"
    
    # Permission identification
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Permission categorization
    category = Column(String(50), nullable=False, index=True)  # e.g., "users", "companies", "reports"
    action = Column(String(50), nullable=False, index=True)    # e.g., "create", "read", "update", "delete"
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_system = Column(Boolean, default=False, nullable=False)  # System permissions cannot be deleted
    
    # Additional metadata
    metadata_info = Column(JSON, default=dict)  # Additional permission configuration
    
    # Relationships
    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("category", "action", name="permissions_category_action_unique"),
        {'extend_existing': True}
    )
    
    def __str__(self):
        """String representation of the permission."""
        return f"Permission(code='{self.code}', name='{self.name}')"
    
    def __repr__(self):
        """Detailed representation of the permission."""
        return (
            f"Permission(id={self.id}, code='{self.code}', "
            f"category='{self.category}', action='{self.action}', active={self.is_active})"
        )