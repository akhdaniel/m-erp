"""
Service model for inter-service authentication and authorization.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from datetime import datetime, timezone
from typing import List, Optional

from app.core.database import Base


class Service(Base):
    """
    Service model for registering microservices that can authenticate
    with the auth service and access protected endpoints.
    """
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(100), unique=True, nullable=False, index=True)
    service_description = Column(String(500), nullable=False)
    service_secret_hash = Column(String(255), nullable=False)  # Hashed service secret
    allowed_scopes = Column(JSON, nullable=False, default=list)  # List of allowed scopes
    callback_urls = Column(JSON, nullable=True, default=list)  # Optional callback URLs
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_used = Column(DateTime(timezone=True), nullable=True)  # Last token request time

    def __repr__(self):
        return f"<Service(id={self.id}, name='{self.service_name}', active={self.is_active})>"

    def has_scope(self, scope: str) -> bool:
        """Check if service is allowed to request a specific scope."""
        return scope in self.allowed_scopes

    def has_scopes(self, scopes: List[str]) -> bool:
        """Check if service is allowed to request all specified scopes."""
        return all(scope in self.allowed_scopes for scope in scopes)

    def update_last_used(self):
        """Update the last_used timestamp to current time."""
        self.last_used = datetime.now(timezone.utc)


class ServiceToken(Base):
    """
    Service token model for tracking active service authentication tokens.
    This helps with token revocation and monitoring.
    """
    __tablename__ = "service_tokens"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, nullable=False, index=True)  # References Service.id
    token_hash = Column(String(255), unique=True, nullable=False, index=True)  # Hashed token
    scopes = Column(JSON, nullable=False, default=list)  # Granted scopes
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<ServiceToken(id={self.id}, service_id={self.service_id}, revoked={self.is_revoked})>"

    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now(timezone.utc) > self.expires_at.replace(tzinfo=timezone.utc)

    def is_valid(self) -> bool:
        """Check if token is valid (not revoked and not expired)."""
        return not self.is_revoked and not self.is_expired()

    def revoke(self):
        """Revoke the token."""
        self.is_revoked = True
        self.revoked_at = datetime.now(timezone.utc)