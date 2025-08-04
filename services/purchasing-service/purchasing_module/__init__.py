"""
Purchasing Module for M-ERP Extension System

This module provides comprehensive procurement functionality including:
- Purchase Order Management
- Supplier Performance Tracking  
- Approval Workflows
- Multi-Currency Support
- Integration with Partner Management

Version: 1.0.0
Author: M-ERP Development Team
"""

__version__ = "1.0.0"
__author__ = "M-ERP Development Team"
__email__ = "dev@m-erp.com"

# Module metadata for framework integration
MODULE_INFO = {
    "name": "purchasing-module",
    "version": __version__,
    "display_name": "Purchasing Management Module",
    "description": "Complete procurement workflow management",
    "author": __author__,
    "author_email": __email__,
    "license": "MIT",
    "type": "full_module",
    "category": "procurement",
    "tags": ["purchasing", "procurement", "suppliers", "approval", "workflow"],
    "minimum_m_erp_version": "2.0.0"
}

# Export key classes and functions
from .main import initialize_module, shutdown_module
from .models import PurchaseOrder, PurchaseOrderLineItem, SupplierPerformance, ApprovalWorkflow
from .services import PurchaseOrderService, SupplierService, ApprovalService

__all__ = [
    "MODULE_INFO",
    "initialize_module", 
    "shutdown_module",
    "PurchaseOrder",
    "PurchaseOrderLineItem", 
    "SupplierPerformance",
    "ApprovalWorkflow",
    "PurchaseOrderService",
    "SupplierService", 
    "ApprovalService"
]