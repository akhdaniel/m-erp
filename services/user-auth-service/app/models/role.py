from datetime import datetime
from typing import Optional, List

from sqlalchemy import DateTime, String, ForeignKey, func, JSON, UniqueConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import Base


class Role(Base):
  __tablename__ = "roles"
  
  # Primary key
  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
  # Role information
  name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
  description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
  
  # Permissions stored as JSON array
  permissions: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
  
  # Timestamps
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), 
    server_default=func.now(), 
    nullable=False
  )
  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), 
    server_default=func.now(), 
    onupdate=func.now(), 
    nullable=False
  )
  
  # Relationships
  users: Mapped[List["UserRole"]] = relationship(
    "UserRole", 
    back_populates="role",
    cascade="all, delete-orphan"
  )
  
  @validates('name')
  def validate_name(self, key, name):
    """Validate role name."""
    if not name or not name.strip():
      raise ValueError("Role name is required")
    
    return name.strip().lower()
  
  @validates('permissions')
  def validate_permissions(self, key, permissions):
    """Validate permissions list."""
    if permissions is None:
      return []
    
    if not isinstance(permissions, list):
      raise ValueError("Permissions must be a list")
    
    # Remove duplicates and empty strings
    valid_permissions = []
    for perm in permissions:
      if isinstance(perm, str) and perm.strip():
        perm_clean = perm.strip()
        if perm_clean not in valid_permissions:
          valid_permissions.append(perm_clean)
    
    return valid_permissions
  
  def has_permission(self, permission: str) -> bool:
    """Check if role has a specific permission."""
    return permission in self.permissions
  
  def add_permission(self, permission: str) -> None:
    """Add a permission to the role."""
    if permission and permission not in self.permissions:
      self.permissions = self.permissions + [permission]
  
  def remove_permission(self, permission: str) -> None:
    """Remove a permission from the role."""
    if permission in self.permissions:
      self.permissions = [p for p in self.permissions if p != permission]
  
  def __repr__(self) -> str:
    return f"<Role(id={self.id}, name='{self.name}', permissions_count={len(self.permissions)})>"


class UserRole(Base):
  __tablename__ = "user_roles"
  
  # Primary key
  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
  # Foreign keys
  user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"), 
    nullable=False,
    index=True
  )
  role_id: Mapped[int] = mapped_column(
    ForeignKey("roles.id", ondelete="CASCADE"), 
    nullable=False,
    index=True
  )
  
  # Assignment metadata
  assigned_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), 
    server_default=func.now(), 
    nullable=False
  )
  assigned_by: Mapped[Optional[int]] = mapped_column(
    ForeignKey("users.id", ondelete="SET NULL"), 
    nullable=True
  )
  
  # Relationships
  user: Mapped["User"] = relationship(
    "User", 
    back_populates="roles",
    foreign_keys=[user_id]
  )
  role: Mapped["Role"] = relationship(
    "Role", 
    back_populates="users"
  )
  assigner: Mapped[Optional["User"]] = relationship(
    "User", 
    foreign_keys=[assigned_by]
  )
  
  # Unique constraint to prevent duplicate user-role assignments
  __table_args__ = (
    UniqueConstraint('user_id', 'role_id', name='_user_role_uc'),
  )
  
  def __repr__(self) -> str:
    return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class UserSession(Base):
  __tablename__ = "user_sessions"
  
  # Primary key
  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
  # Foreign key
  user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"), 
    nullable=False,
    index=True
  )
  
  # Session information
  refresh_token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
  expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
  
  # Session metadata
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), 
    server_default=func.now(), 
    nullable=False
  )
  ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 compatible
  user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
  is_revoked: Mapped[bool] = mapped_column(default=False, nullable=False)
  
  # Relationships
  user: Mapped["User"] = relationship(
    "User", 
    back_populates="sessions"
  )
  
  @property
  def is_expired(self) -> bool:
    """Check if session is expired."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    expires_at = self.expires_at
    
    # Ensure both datetime objects have timezone info for comparison
    if expires_at.tzinfo is None:
      expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    return now > expires_at
  
  @property
  def is_valid(self) -> bool:
    """Check if session is valid (not expired and not revoked)."""
    return not self.is_expired and not self.is_revoked
  
  def revoke(self) -> None:
    """Revoke the session."""
    self.is_revoked = True
  
  def __repr__(self) -> str:
    return f"<UserSession(user_id={self.user_id}, expired={self.is_expired}, revoked={self.is_revoked})>"