"""
Inventory Management Module for XERPIUM.

This module provides comprehensive inventory and warehouse management capabilities
including product catalog, stock tracking, location management, and integration
with purchasing workflows.

Key Features:
- Product catalog with SKU management
- Multi-location stock tracking
- Warehouse and storage location management
- Stock movement tracking and history
- Integration with purchasing module for receiving
- Real-time stock level monitoring and alerts
- Inventory valuation with multiple methods (FIFO, LIFO, Average Cost)
- Batch and serial number tracking
"""

# Module metadata
MODULE_INFO = {
    "name": "inventory-module",
    "display_name": "Inventory Management Module",
    "version": "1.0.0",
    "description": "Comprehensive inventory and warehouse management with product catalog, stock tracking, and location management",
    "author": "XERPIUM Development Team",
    "category": "inventory",
    "tags": ["inventory", "warehouse", "stock", "products", "receiving", "catalog"]
}

# Import main models for easy access
try:
    from .models import (
        Product,
        ProductVariant,
        StockLevel,
        StockMovement,
        Warehouse,
        WarehouseLocation,
        ReceivingRecord
    )
    
    # Import main services
    from .services import (
        ProductService,
        StockService,
        WarehouseService,
        ReceivingService
    )
    
    # Import API routers
    from .api import (
        products_router,
        stock_router,
        warehouses_router,
        receiving_router
    )
    
    # Import module management functions
    from .main import (
        initialize_module,
        shutdown_module,
        check_health,
        get_module_info
    )
    
except ImportError as e:
    # Handle cases where dependencies aren't available
    # This allows the module to be imported for configuration/manifest purposes
    pass

# Version compatibility
__version__ = MODULE_INFO["version"]
__author__ = MODULE_INFO["author"]

# Export public API
__all__ = [
    # Module info
    "MODULE_INFO",
    "__version__",
    "__author__",
    
    # Models
    "Product",
    "ProductVariant", 
    "StockLevel",
    "StockMovement",
    "Warehouse",
    "WarehouseLocation",
    "ReceivingRecord",
    
    # Services
    "ProductService",
    "StockService", 
    "WarehouseService",
    "ReceivingService",
    
    # API routers
    "products_router",
    "stock_router",
    "warehouses_router", 
    "receiving_router",
    
    # Module management
    "initialize_module",
    "shutdown_module",
    "check_health",
    "get_module_info"
]