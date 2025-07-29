import re
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import Boolean, DateTime, String, Integer, func, select
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


class User(Base):
  __tablename__ = "users"
  
  # Primary key
  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  
  # Authentication fields
  email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
  password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
  
  # Profile fields
  first_name: Mapped[str] = mapped_column(String(100), nullable=False)
  last_name: Mapped[str] = mapped_column(String(100), nullable=False)
  
  # Status fields
  is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
  is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
  is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
  
  # Account lockout fields
  failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
  last_failed_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
  
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
  last_login: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), 
    nullable=True
  )
  deleted_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), 
    nullable=True
  )
  
  # Relationships
  roles: Mapped[list["UserRole"]] = relationship(
    "UserRole", 
    back_populates="user",
    foreign_keys="UserRole.user_id",
    cascade="all, delete-orphan"
  )
  sessions: Mapped[list["UserSession"]] = relationship(
    "UserSession", 
    back_populates="user",
    cascade="all, delete-orphan"
  )
  password_history: Mapped[list["PasswordHistory"]] = relationship(
    "PasswordHistory",
    back_populates="user",
    cascade="all, delete-orphan"
  )
  
  @validates('email')
  def validate_email(self, key, email):
    """Validate email format."""
    if not email:
      raise ValueError("Email is required")
    
    # Basic email validation pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
      raise ValueError("Invalid email format")
    
    return email.lower()
  
  @validates('first_name', 'last_name')
  def validate_names(self, key, value):
    """Validate name fields."""
    if not value or not value.strip():
      raise ValueError(f"{key.replace('_', ' ').title()} is required")
    
    return value.strip()
  
  @validates('password_hash')
  def validate_password_hash(self, key, password_hash):
    """Validate password hash."""
    if not password_hash:
      raise ValueError("Password hash is required")
    
    return password_hash
  
  @property
  def full_name(self) -> str:
    """Return user's full name."""
    return f"{self.first_name} {self.last_name}"
  
  @property
  def is_deleted(self) -> bool:
    """Check if user is soft deleted."""
    return self.deleted_at is not None
  
  @property
  def is_locked(self) -> bool:
    """Check if user account is currently locked."""
    if self.locked_until is None:
      return False
    return datetime.utcnow() < self.locked_until
  
  @property
  def lockout_remaining_time(self) -> Optional[timedelta]:
    """Get remaining lockout time."""
    if not self.is_locked:
      return None
    return self.locked_until - datetime.utcnow()
  
  def increment_failed_attempts(self, max_attempts: int = 5, lockout_duration_minutes: int = 15) -> bool:
    """
    Increment failed login attempts and lock account if threshold reached.
    
    Args:
      max_attempts: Maximum allowed failed attempts before lockout
      lockout_duration_minutes: Duration of lockout in minutes
      
    Returns:
      True if account was locked, False otherwise
    """
    self.failed_login_attempts += 1
    self.last_failed_login = datetime.utcnow()
    
    if self.failed_login_attempts >= max_attempts:
      self.locked_until = datetime.utcnow() + timedelta(minutes=lockout_duration_minutes)
      return True
    
    return False
  
  def reset_failed_attempts(self):
    """Reset failed login attempts after successful login."""
    self.failed_login_attempts = 0
    self.locked_until = None
    self.last_failed_login = None
  
  def unlock_account(self):
    """Manually unlock account and reset failed attempts."""
    self.failed_login_attempts = 0
    self.locked_until = None
    self.last_failed_login = None
  
  async def get_permissions(self, db: AsyncSession) -> List[str]:
    """Get all permissions from user's roles."""
    from app.models.role import Role, UserRole
    
    # Query to get all roles for this user
    stmt = (
      select(Role.permissions)
      .join(UserRole, Role.id == UserRole.role_id)
      .where(UserRole.user_id == self.id)
    )
    
    result = await db.execute(stmt)
    role_permissions = result.scalars().all()
    
    # Flatten and deduplicate permissions
    all_permissions = set()
    for permissions in role_permissions:
      if permissions:
        all_permissions.update(permissions)
    
    return list(all_permissions)
  
  async def has_permission(self, db: AsyncSession, permission: str) -> bool:
    """Check if user has a specific permission."""
    permissions = await self.get_permissions(db)
    return permission in permissions
  
  def __repr__(self) -> str:
    return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"