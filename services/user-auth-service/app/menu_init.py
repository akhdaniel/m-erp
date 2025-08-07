"""
User Auth Service Menu Initialization
Registers user management menus and permissions with the menu-access-service
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

# Define user management permissions
USER_PERMISSIONS = [
    MenuPermission(
        code="access_admin",
        name="Access Admin",
        description="Permission to access admin module",
        category="admin",
        action="access"
    ),
    MenuPermission(
        code="view_users",
        name="View Users",
        description="Permission to view users",
        category="admin",
        action="view"
    ),
    MenuPermission(
        code="manage_users",
        name="Manage Users",
        description="Permission to create, edit, delete users",
        category="admin",
        action="manage"
    ),
    MenuPermission(
        code="view_roles",
        name="View Roles",
        description="Permission to view roles",
        category="admin",
        action="view"
    ),
    MenuPermission(
        code="manage_roles",
        name="Manage Roles",
        description="Permission to create, edit, delete roles",
        category="admin",
        action="manage"
    ),
    MenuPermission(
        code="view_permissions",
        name="View Permissions",
        description="Permission to view permissions",
        category="admin",
        action="view"
    ),
    MenuPermission(
        code="manage_permissions",
        name="Manage Permissions",
        description="Permission to manage permissions",
        category="admin",
        action="manage"
    ),
    MenuPermission(
        code="view_audit_logs",
        name="View Audit Logs",
        description="Permission to view audit logs",
        category="admin",
        action="view"
    ),
    MenuPermission(
        code="system_settings",
        name="System Settings",
        description="Permission to manage system settings",
        category="admin",
        action="manage"
    ),
]

# Define user management menu structure
USER_MENUS = [
    # Parent menu for Administration
    MenuItem(
        code="admin_management",
        title="Administration",
        description="System Administration",
        parent_code=None,
        order_index=10,  # Last in menu order
        level=0,
        url="#",
        icon="settings",
        item_type="dropdown",
        required_permission="access_admin"
    ),
    # Child menus
    MenuItem(
        code="admin_users",
        title="Users",
        description="User Management",
        parent_code="admin_management",
        order_index=1,
        level=1,
        url="/admin/users",
        icon="users",
        item_type="link",
        required_permission="view_users"
    ),
    MenuItem(
        code="admin_roles",
        title="Roles",
        description="Role Management",
        parent_code="admin_management",
        order_index=2,
        level=1,
        url="/admin/roles",
        icon="shield",
        item_type="link",
        required_permission="view_roles"
    ),
    MenuItem(
        code="admin_permissions",
        title="Permissions",
        description="Permission Management",
        parent_code="admin_management",
        order_index=3,
        level=1,
        url="/admin/permissions",
        icon="key",
        item_type="link",
        required_permission="view_permissions"
    ),
    MenuItem(
        code="admin_audit_logs",
        title="Audit Logs",
        description="System Audit Logs",
        parent_code="admin_management",
        order_index=4,
        level=1,
        url="/admin/audit-logs",
        icon="file-text",
        item_type="link",
        required_permission="view_audit_logs"
    ),
    MenuItem(
        code="admin_settings",
        title="Settings",
        description="System Settings",
        parent_code="admin_management",
        order_index=5,
        level=1,
        url="/admin/settings",
        icon="sliders",
        item_type="link",
        required_permission="system_settings"
    ),
    
    # Dashboard menu (top-level, no parent)
    MenuItem(
        code="dashboard",
        title="Dashboard",
        description="Main Dashboard",
        parent_code=None,
        order_index=1,  # First in menu
        level=0,
        url="/dashboard",
        icon="home",
        item_type="link",
        required_permission=None  # Public menu, no permission required
    ),
    
    # Profile menu (accessible to all authenticated users)
    MenuItem(
        code="profile",
        title="Profile",
        description="User Profile",
        parent_code=None,
        order_index=9,  # Near the end
        level=0,
        url="/profile",
        icon="user",
        item_type="link",
        required_permission="view_profile"  # Basic permission all users have
    ),
]


async def initialize_user_menus():
    """Initialize user management menus on service startup"""
    try:
        menu_service_url = os.getenv("MENU_SERVICE_URL", "http://menu-access-service:8000")
        
        logger.info("Initializing user management menus...")
        
        success = await register_service_menus(
            service_name="user-auth-service",
            permissions=USER_PERMISSIONS,
            menus=USER_MENUS,
            menu_service_url=menu_service_url
        )
        
        if success:
            logger.info("✅ User management menus initialized successfully")
        else:
            logger.error("❌ Failed to initialize user management menus")
            
        return success
        
    except Exception as e:
        logger.error(f"Error initializing user management menus: {e}")
        return False


def init_menus_on_startup():
    """Synchronous wrapper for menu initialization"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(initialize_user_menus())
    finally:
        loop.close()


if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    success = init_menus_on_startup()
    sys.exit(0 if success else 1)