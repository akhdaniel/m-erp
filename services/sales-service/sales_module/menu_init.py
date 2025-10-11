"""
Sales Service Menu Initialization
Registers sales menus and permissions with the menu-access-service
"""

import asyncio
import logging
import os
import sys
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL")

# Add parent directory to path to import shared modules
# When running from /app/sales_module/menu_init.py, we need to add /app to the path
current_file = os.path.abspath(__file__)
if '/app/sales_module' in current_file:
    # Running in Docker container
    sys.path.insert(0, '/app')
else:
    # Running locally
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(current_file))))

from shared.menu_registration_client import (
    MenuRegistrationClient, 
    MenuItem, 
    MenuPermission,
    register_service_menus
)

logger = logging.getLogger('uvicorn')

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
        code="view_transactions",
        name="View Transactions",
        description="Permission to view sales transactions",
        category="sales",
        action="view"
    ),
    MenuPermission(
        code="manage_transactions",
        name="Manage Transactions",
        description="Permission to create, edit, delete sales transactions",
        category="sales",
        action="manage"
    ),
    MenuPermission(
        code="view_quotes",
        name="View Quotations",
        description="Permission to view sales quotations",
        category="sales",
        action="view"
    ),
    MenuPermission(
        code="manage_quotes",
        name="Manage Quotations",
        description="Permission to create, edit, delete quotations",
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
        description="Permission to create, edit, delete sales orders",
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
    # Child menus - Dashboard first (order_index=0 to ensure it's first)
    MenuItem(
        code="sales_dashboard",
        title="Dashboard",
        description="Sales Dashboard Overview",
        parent_code="sales_management",
        order_index=0,  # Explicitly set to 0 to be first
        level=1,
        url="/sales/dashboard",
        icon="grid-3x3",
        item_type="link",
        required_permission="access_sales"
    ),
    MenuItem(
        code="sales_transactions",
        title="Transactions",
        description="All Sales Transactions",
        parent_code="sales_management",
        order_index=1,  # Second item after Dashboard
        level=1,
        url="/sales/transactions",
        icon="file-text",
        item_type="link",
        required_permission="access_sales"
    ),
    MenuItem(
        code="sales_quotes",
        title="Quotations",
        description="Quotation Management",
        parent_code="sales_management",
        order_index=2,  # Third item
        level=1,
        url="/sales/transactions?state=draft,quote_pending_approval,quote_approved,quote_sent,quote_accepted,quote_rejected,quote_expired",
        icon="file-text",
        item_type="link",
        required_permission="manage_quotes"
    ),
    MenuItem(
        code="sales_orders",
        title="Orders",
        description="Sales Order Management",
        parent_code="sales_management",
        order_index=3,  # Fourth item
        level=1,
        url="/sales/transactions?state=order_pending,order_confirmed,order_in_production,order_ready_to_ship,order_partially_shipped,order_shipped,order_delivered,order_completed,order_cancelled,order_on_hold",
        icon="shopping-bag",
        item_type="link",
        required_permission="manage_orders"
    ),
    MenuItem(
        code="sales_customers",
        title="Customers",
        description="Customer Management",
        parent_code="sales_management",
        order_index=4,  # Fifth item
        level=1,
        url="/sales/customers",
        icon="users",
        item_type="link",
        required_permission="access_sales"
    ),
    MenuItem(
        code="sales_products",
        title="Products",
        description="Product catalog and inventory for sales",
        url="/inventory/products",
        icon="fas fa-tags",
        parent_code="sales_management",
        order_index=5,
        level=1,
        required_permission="access_sales"
    ),    
    MenuItem(
        code="sales_analytics",
        title="Analytics",
        description="Sales Analytics & Reports",
        parent_code="sales_management",
        order_index=5,  # Sixth item
        level=1,
        url="/sales/analytics",
        icon="bar-chart",
        item_type="link",
        required_permission="sales_analytics"
    ),
    MenuItem(
        code="sales_settings",
        title="Settings",
        description="Sales Settings and Configurations",
        parent_code="sales_management",
        order_index=100,  # Last item
        level=1,
        url="/sales/settings",
        icon="cogs",
        item_type="dropdown",
        required_permission="access_sales"
    ),
    MenuItem(
        code="sales_pricing",
        title="Pricing Rules",
        description="Pricing Management",
        parent_code="sales_settings",
        order_index=3,  # Fourth item
        level=1,
        url="/sales/pricing",
        icon="dollar-sign",
        item_type="link",
        required_permission="view_pricing"
    ),    
]

async def initialize_sales_menus():
    """Initialize sales menus on service startup"""
    try:
        
        logger.info(f"Initializing sales menus..")
        
        success = await register_service_menus(
            service_name="sales-service",
            permissions=SALES_PERMISSIONS,
            menus=SALES_MENUS,
            menu_service_url=MENU_SERVICE_URL
        )
        
        if success:
            logger.info("✅ Sales menus initialized successfully")
        else:
            logger.error("❌ Failed to initialize Sales menus")
            
        return success
        
    except Exception as e:
        logger.error(f"Error initializing Sales menus: {e}")
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