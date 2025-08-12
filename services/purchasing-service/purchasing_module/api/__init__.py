"""
API module for the Purchasing Module.

This module provides REST API endpoints for all purchasing functionality
including purchase orders, suppliers, and approval workflows.
"""

from .purchase_order_api import router as purchase_orders_router
from .supplier_api import router as suppliers_router
from .approval_api import router as approvals_router
from .dashboard_api import router as dashboard_router

__all__ = [
    "purchase_orders_router",
    "suppliers_router",
    "approvals_router",
    "dashboard_router"
]