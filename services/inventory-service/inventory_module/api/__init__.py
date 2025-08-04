"""
Inventory Module API Package.

This package contains FastAPI routers and endpoints for inventory management,
providing REST API access to inventory operations and data.
"""

from .products import router as products_router
from .stock import router as stock_router
from .warehouses import router as warehouses_router
from .receiving import router as receiving_router

__all__ = [
    "products_router",
    "stock_router", 
    "warehouses_router",
    "receiving_router"
]