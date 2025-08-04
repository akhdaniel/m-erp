"""
Local Business Object Framework interfaces for the Inventory Module.

This provides the interface to the Business Object Framework that would
normally be imported from the company-partner-service.
"""

from .base import BaseModel, CompanyBusinessObject, TimestampMixin

__all__ = [
    "BaseModel",
    "CompanyBusinessObject", 
    "TimestampMixin"
]