"""
Business Object Framework for XERPIUM.

This package provides base classes, mixins, and utilities for creating
standardized business objects across all XERPIUM microservices.
"""

__version__ = "1.0.0"

from .mixins import BusinessObjectMixin, AuditableMixin, EventPublisherMixin
from .base import BusinessObjectBase, CompanyBusinessObject

__all__ = [
    "BusinessObjectMixin",
    "AuditableMixin", 
    "EventPublisherMixin",
    "BusinessObjectBase",
    "CompanyBusinessObject"
]