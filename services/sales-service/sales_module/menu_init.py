"""
Sales Service Menu Initialization
Registers sales menus and permissions with the menu-access-service
"""

import asyncio
import logging
import os
import sys

# Add parent directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.menu_registration_client import (
    MenuRegistrationClient, 
    MenuItem, 
    MenuPermission,
    register_service_menus
)

logger = logging.getLogger(__name__)

# Define sales permissions
SALES_PERMISSIONS = [
    MenuPermission(
        code="access_sales",
        name="Access Sales",
        description="Permission to access sales module",
        category="sales",
        action="access"
    ),
    MenuPermission(
        code="view_quotes",
        name="View Quotes",
        description="Permission to view sales quotes",
        category="sales",
        action="view"
    ),
    MenuPermission(
        code="manage_quotes",
        name="Manage Quotes",
        description="Permission to create, edit, delete quotes",
        category="sales",
        action="manage"
    ),
    MenuPermission(
        code="view_orders",
        name="View Orders",
        description="Permission to view sales orders",
        category="sales",
        action="view"
    ),
    MenuPermission(
        code="manage_orders",
        name="Manage Orders",
        description="Permission to create, edit, delete orders",
        category="sales",
        action="manage"
    ),
    MenuPermission(
        code="view_pricing",
        name="View Pricing",
        description="Permission to view pricing rules",
        category="sales",
        action="view"
    ),
    MenuPermission(
        code="manage_pricing",
        name="Manage Pricing",
        description="Permission to create, edit pricing rules",
        category="sales",
        action="manage"
    ),
    MenuPermission(
        code="sales_analytics",
        name="Sales Analytics",
        description="Permission to view sales analytics",
        category="sales",
        action="view"
    ),
    MenuPermission(
        code="approve_discounts",
        name="Approve Discounts",
        description="Permission to approve special discounts",
        category="sales",
        action="approve"
    ),
]

# Define sales menu structure
SALES_MENUS = [
    # Parent menu
    MenuItem(
        code="sales_management",
        title="Sales",
        description="Sales Management",
        parent_code=None,
        order_index=2,
        level=0,
        url="#",
        icon="shopping-cart",
        item_type="dropdown",
        required_permission="access_sales"
    ),
    # Child menus
    MenuItem(
        code="sales_quotes",
        title="Quotes",
        description="Quote Management",
        parent_code="sales_management",
        order_index=1,
        level=1,
        url="/sales/quotes",
        icon="file-text",
        item_type="link",
        required_permission="manage_quotes"
    ),
    MenuItem(
        code="sales_orders",
        title="Orders",
        description="Sales Order Management",
        parent_code="sales_management",
        order_index=2,
        level=1,
        url="/sales/orders",
        icon="shopping-bag",
        item_type="link",
        required_permission="manage_orders"
    ),
    MenuItem(
        code="sales_pricing",
        title="Pricing Rules",
        description="Pricing Management",
        parent_code="sales_management",
        order_index=3,
        level=1,
        url="/sales/pricing",
        icon="dollar-sign",
        item_type="link",
        required_permission="view_pricing"
    ),
    MenuItem(
        code="sales_customers",
        title="Customers",
        description="Customer Management",
        parent_code="sales_management",
        order_index=4,
        level=1,
        url="/sales/customers",
        icon="users",
        item_type="link",
        required_permission="access_sales"
    ),
    MenuItem(
        code="sales_analytics",
        title="Analytics",
        description="Sales Analytics & Reports",
        parent_code="sales_management",
        order_index=5,
        level=1,
        url="/sales/analytics",
        icon="bar-chart",
        item_type="link",
        required_permission="sales_analytics"
    ),
]


async def initialize_sales_menus():
    """Initialize sales menus on service startup"""
    try:
        menu_service_url = os.getenv("MENU_SERVICE_URL", "http://menu-access-service:8000")
        
        logger.info("Initializing sales menus...")
        
        success = await register_service_menus(
            service_name="sales-service",
            permissions=SALES_PERMISSIONS,
            menus=SALES_MENUS,
            menu_service_url=menu_service_url
        )
        
        if success:
            logger.info("✅ Sales menus initialized successfully")
        else:
            logger.error("❌ Failed to initialize sales menus")
            
        return success
        
    except Exception as e:
        logger.error(f"Error initializing sales menus: {e}")
        return False


def init_menus_on_startup():
    """Synchronous wrapper for menu initialization"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(initialize_sales_menus())
    finally:
        loop.close()


if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    success = init_menus_on_startup()
    sys.exit(0 if success else 1)