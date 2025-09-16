"""
Purchasing Service Menu Initialization
Registers purchasing menus and permissions with the menu-access-service
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

logger = logging.getLogger('uvicorn')
UI_REGISTRY_URL= os.getenv("UI_REGISTRY_URL")
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL")

# Define purchasing permissions
PURCHASING_PERMISSIONS = [
    MenuPermission(
        code="access_purchasing",
        name="Access Purchasing",
        description="Permission to access purchasing module",
        category="purchasing",
        action="access"
    ),
    MenuPermission(
        code="view_purchase_orders",
        name="View Purchase Orders",
        description="Permission to view purchase orders",
        category="purchasing",
        action="view"
    ),
    MenuPermission(
        code="manage_purchase_orders",
        name="Manage Purchase Orders",
        description="Permission to create, edit, delete purchase orders",
        category="purchasing",
        action="manage"
    ),
    MenuPermission(
        code="approve_purchase_orders",
        name="Approve Purchase Orders",
        description="Permission to approve purchase orders",
        category="purchasing",
        action="approve"
    ),
    MenuPermission(
        code="view_suppliers",
        name="View Suppliers",
        description="Permission to view suppliers",
        category="purchasing",
        action="view"
    ),
    MenuPermission(
        code="manage_suppliers",
        name="Manage Suppliers",
        description="Permission to create, edit, delete suppliers",
        category="purchasing",
        action="manage"
    ),
    MenuPermission(
        code="evaluate_suppliers",
        name="Evaluate Suppliers",
        description="Permission to evaluate supplier performance",
        category="purchasing",
        action="manage"
    ),
    MenuPermission(
        code="view_purchasing_reports",
        name="View Purchasing Reports",
        description="Permission to view purchasing reports",
        category="purchasing",
        action="view"
    ),
    MenuPermission(
        code="manage_approvals",
        name="Manage Approvals",
        description="Permission to manage approval workflows",
        category="purchasing",
        action="manage"
    ),
]

# Define purchasing menu structure
PURCHASING_MENUS = [
    # Parent menu
    MenuItem(
        code="purchasing_management",
        title="Purchasing",
        description="Purchasing Management",
        parent_code=None,
        order_index=4,
        level=0,
        url="/purchasing/dashboard",
        icon="shopping-cart",
        item_type="dropdown",
        required_permission="access_purchasing"
    ),
    # Child menus
    MenuItem(
        code="purchasing_dashboard",
        title="Dashboard",
        description="Purchasing Dashboard",
        parent_code="purchasing_management",
        order_index=1,
        level=1,
        url="/purchasing/dashboard",
        icon="dashboard",
        item_type="link",
        required_permission="access_purchasing"
    ),
    MenuItem(
        code="purchase_orders",
        title="Purchase Orders",
        description="Purchase Order Management",
        parent_code="purchasing_management",
        order_index=2,
        level=1,
        url="/purchasing/orders",
        icon="file-text",
        item_type="link",
        required_permission="view_purchase_orders"
    ),
    MenuItem(
        code="suppliers",
        title="Suppliers",
        description="Supplier Management",
        parent_code="purchasing_management",
        order_index=3,
        level=1,
        url="/purchasing/suppliers",
        icon="truck",
        item_type="link",
        required_permission="view_suppliers"
    ),
    MenuItem(
        code="approvals",
        title="Approvals",
        description="Approval Management",
        parent_code="purchasing_management",
        order_index=4,
        level=1,
        url="/purchasing/approvals",
        icon="check-circle",
        item_type="link",
        required_permission="manage_approvals"
    ),
    MenuItem(
        code="purchasing_reports",
        title="Reports",
        description="Purchasing Reports",
        parent_code="purchasing_management",
        order_index=5,
        level=1,
        url="/purchasing/reports",
        icon="bar-chart",
        item_type="link",
        required_permission="view_purchasing_reports"
    ),
    MenuItem(
        code="purchasing_settings",
        title="Settings",
        description="Purchasing Settings",
        parent_code="purchasing_management",
        order_index=100,
        level=1,
        url="#",
        icon="cogs",
        item_type="dropdown",
        required_permission="access_purchasing"
    ),
]


async def initialize_purchasing_menus():
    """Initialize purchasing menus on service startup"""
    try:
        
        logger.info(f"Initializing purchasing menus...{MENU_SERVICE_URL}")
        
        success = await register_service_menus(
            service_name="purchasing-service",
            permissions=PURCHASING_PERMISSIONS,
            menus=PURCHASING_MENUS,
            menu_service_url=MENU_SERVICE_URL
        )
        
        if success:
            logger.info("✅ Purchasing menus initialized successfully")
        else:
            logger.error("❌ Failed to initialize purchasing menus")
            
        return success
        
    except Exception as e:
        logger.error(f"Error initializing purchasing menus: {e}")
        return False


def init_menus_on_startup():
    """Synchronous wrapper for menu initialization"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(initialize_purchasing_menus())
    finally:
        loop.close()


if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    success = init_menus_on_startup()
    sys.exit(0 if success else 1)