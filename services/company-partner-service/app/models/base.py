"""
Base models and mixins for company-partner service.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr

from app.core.database import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class CompanyMixin(TimestampMixin):
    """
    Mixin for multi-company data isolation.
    All business objects should inherit from this to ensure proper company scoping.
    """
    
    @declared_attr
    def company_id(cls):
        return Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    @declared_attr
    def __table_args__(cls):
        # Index on company_id for efficient filtering
        return {'extend_existing': True}


class BaseModel(Base, TimestampMixin):
    """Base model for non-company-scoped tables (like companies themselves)."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)


class CompanyBaseModel(Base, CompanyMixin):
    """Base model for company-scoped business objects."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)