"""
Role model for grouping permissions.
"""

from sqlalchemy import Column, String, Text, Boolean, JSON, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


# Association table for role-permission many-to-many relationship
role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)


class Role(BaseModel):
    """
    Role model for managing groups of permissions.
    
    Roles are collections of permissions that can be assigned to users.
    Examples: "Admin", "Manager", "Employee", "Viewer"
    """
    
    __tablename__ = "roles"
    
    # Role identification
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Role configuration
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_system = Column(Boolean, default=False, nullable=False)  # System roles cannot be deleted
    is_default = Column(Boolean, default=False, nullable=False)  # Default role for new users
    
    # Hierarchy support
    level = Column(Integer, default=0, nullable=False)  # Role hierarchy level (0 = highest)
    
    # Additional metadata
    metadata_info = Column(JSON, default=dict)  # Additional role configuration
    
    # Relationships
    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin"
    )
    
    def __str__(self):
        """String representation of the role."""
        return f"Role(code='{self.code}', name='{self.name}')"
    
    def __repr__(self):
        """Detailed representation of the role."""
        return (
            f"Role(id={self.id}, code='{self.code}', name='{self.name}', "
            f"level={self.level}, active={self.is_active})"
        )
    
    def has_permission(self, permission_code: str) -> bool:
        """Check if this role has a specific permission."""
        return any(perm.code == permission_code for perm in self.permissions)
    
    def get_permission_codes(self) -> list[str]:
        """Get list of all permission codes for this role."""
        return [perm.code for perm in self.permissions if perm.is_active]