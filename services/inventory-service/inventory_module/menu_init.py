"""
Inventory Service Menu Initialization
Registers inventory menus and permissions with the menu-access-service
"""

import asyncio
import logging
import os
import sys

from shared.menu_registration_client import (
    MenuRegistrationClient, 
    MenuItem, 
    MenuPermission,
    register_service_menus
)

logger = logging.getLogger(__name__)

# Define inventory permissions
INVENTORY_PERMISSIONS = [
    MenuPermission(
        code="access_inventory",
        name="Access Inventory",
        description="Permission to access inventory module",
        category="inventory",
        action="access"
    ),
    MenuPermission(
        code="view_products",
        name="View Products",
        description="Permission to view products",
        category="inventory",
        action="view"
    ),
    MenuPermission(
        code="manage_products",
        name="Manage Products",
        description="Permission to create, edit, delete products",
        category="inventory",
        action="manage"
    ),
    MenuPermission(
        code="view_stock",
        name="View Stock",
        description="Permission to view stock levels",
        category="inventory",
        action="view"
    ),
    MenuPermission(
        code="manage_stock",
        name="Manage Stock",
        description="Permission to adjust stock levels",
        category="inventory",
        action="manage"
    ),
    MenuPermission(
        code="view_warehouses",
        name="View Warehouses",
        description="Permission to view warehouse information",
        category="inventory",
        action="view"
    ),
    MenuPermission(
        code="manage_warehouses",
        name="Manage Warehouses",
        description="Permission to create, edit, delete warehouses",
        category="inventory",
        action="manage"
    ),
    MenuPermission(
        code="process_receiving",
        name="Process Receiving",
        description="Permission to process receiving operations",
        category="inventory",
        action="manage"
    ),
    MenuPermission(
        code="view_inventory_reports",
        name="View Inventory Reports",
        description="Permission to view inventory reports",
        category="inventory",
        action="view"
    ),
]

# Define inventory menu structure
INVENTORY_MENUS = [
    # Parent menu
    MenuItem(
        code="inventory_management",
        title="Inventory",
        description="Inventory Management",
        parent_code=None,
        order_index=3,
        level=0,
        url="#",
        icon="warehouse",
        item_type="dropdown",
        required_permission="access_inventory"
    ),
    # Child menus
    MenuItem(
        code="inventory_products",
        title="Products",
        description="Product Management",
        parent_code="inventory_management",
        order_index=1,
        level=1,
        url="/inventory/products",
        icon="box",
        item_type="link",
        required_permission="view_products"
    ),
    MenuItem(
        code="inventory_stock",
        title="Stock",
        description="Stock Management",
        parent_code="inventory_management",
        order_index=2,
        level=1,
        url="/inventory/stock",
        icon="layers",
        item_type="link",
        required_permission="view_stock"
    ),
    MenuItem(
        code="inventory_warehouses",
        title="Warehouses",
        description="Warehouse Management",
        parent_code="inventory_management",
        order_index=3,
        level=1,
        url="/inventory/warehouses",
        icon="building",
        item_type="link",
        required_permission="view_warehouses"
    ),
    MenuItem(
        code="inventory_receiving",
        title="Receiving",
        description="Receiving Operations",
        parent_code="inventory_management",
        order_index=4,
        level=1,
        url="/inventory/receiving",
        icon="download",
        item_type="link",
        required_permission="process_receiving"
    ),
    MenuItem(
        code="inventory_reports",
        title="Reports",
        description="Inventory Reports",
        parent_code="inventory_management",
        order_index=5,
        level=1,
        url="/inventory/reports",
        icon="file-text",
        item_type="link",
        required_permission="view_inventory_reports"
    ),
]


async def initialize_inventory_menus():
    """Initialize inventory menus on service startup"""
    try:
        menu_service_url = os.getenv("MENU_SERVICE_URL", "http://menu-access-service:8000")
        
        logger.info("Initializing inventory menus...")
        
        success = await register_service_menus(
            service_name="inventory-service",
            permissions=INVENTORY_PERMISSIONS,
            menus=INVENTORY_MENUS,
            menu_service_url=menu_service_url
        )
        
        if success:
            logger.info("✅ Inventory menus initialized successfully")
        else:
            logger.error("❌ Failed to initialize inventory menus")
            
        return success
        
    except Exception as e:
        logger.error(f"Error initializing inventory menus: {e}")
        return False


def init_menus_on_startup():
    """Synchronous wrapper for menu initialization"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(initialize_inventory_menus())
    finally:
        loop.close()


if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    success = init_menus_on_startup()
    sys.exit(0 if success else 1)