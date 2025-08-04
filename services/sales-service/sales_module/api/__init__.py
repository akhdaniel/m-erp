"""
Sales Module API Package.

This package contains all API endpoints and routing for
the sales management module using FastAPI.
"""

from .customer_api import router as customer_router
from .opportunity_api import router as opportunity_router
from .quote_api import router as quote_router
from .order_api import router as order_router
from .pricing_api import router as pricing_router

__all__ = [
    "customer_router",
    "opportunity_router", 
    "quote_router",
    "order_router",
    "pricing_router"
]