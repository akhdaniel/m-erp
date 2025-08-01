"""
Base classes for Business Object Framework.

Provides abstract base classes that combine mixins for different types
of business objects:
- BusinessObjectBase: For non-company-scoped objects
- CompanyBusinessObject: For company-scoped objects with multi-tenant isolation
"""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr

from app.core.database import Base
from .mixins import BusinessObjectMixin, AuditableMixin, EventPublisherMixin


class BusinessObjectBase(Base, BusinessObjectMixin, AuditableMixin, EventPublisherMixin):
    """
    Abstract base class for non-company-scoped business objects.
    
    Combines all core mixins to provide:
    - Standard fields (id, timestamps, framework version)
    - Automatic audit logging
    - Automatic event publishing
    
    Use this for objects that don't need company-level isolation,
    such as system-wide configuration or lookup tables.
    """
    
    __abstract__ = True


class CompanyBusinessObject(BusinessObjectBase):
    """
    Abstract base class for company-scoped business objects.
    
    Extends BusinessObjectBase with multi-company data isolation:
    - Includes company_id foreign key
    - Enforces company-level data separation
    - Inherits all BusinessObjectBase functionality
    
    Use this for all business entities that should be isolated
    by company (partners, invoices, products, etc.).
    """
    
    __abstract__ = True
    
    @declared_attr
    def company_id(cls):
        """Company ID for multi-tenant data isolation."""
        return Column(
            Integer, 
            ForeignKey("companies.id", ondelete="CASCADE"), 
            nullable=False, 
            index=True
        )
    
    @declared_attr
    def __table_args__(cls):
        """Table arguments for company-scoped objects."""
        return {'extend_existing': True}