#!/usr/bin/env python3
"""
Script to set up Settings menu with Menu Configuration submenu.
This will show menus requested by all services.
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

# Add menu-access-service to Python path
sys.path.insert(0, '/app')

from app.models.menu import MenuItem
from app.models.permission import Permission

# Database configuration from menu-access-service
DATABASE_URL = "postgresql+asyncpg://postgres:password@postgres:5432/menu_access_db"

engine = create_async_engine(DATABASE_URL)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

async def create_settings_menus():
    """Create Settings menu with Menu Configuration submenu."""
    async with AsyncSession() as session:
        # Create permissions for settings features
        settings_permissions = [
            Permission(
                code="settings.access",
                name="Settings Access",
                description="Access to system settings",
                category="settings",
                action="access"
            ),
            Permission(
                code="menu.configuration",
                name="Menu Configuration",
                description="Configure and manage menu items",
                category="menu",
                action="manage"
            ),
        ]

        # Check and add permissions
        for perm in settings_permissions:
            existing = await session.execute(
                select(Permission).where(Permission.code == perm.code)
            )
            if not existing.scalar_one_or_none():
                session.add(perm)
                print(f"✅ Created permission: {perm.name}")
            else:
                print(f"ℹ️  Permission already exists: {perm.name}")
        
        await session.commit()

        # Check if Settings menu already exists
        existing_settings = await session.execute(
            select(MenuItem).where(MenuItem.code == "settings")
        )
        settings_menu = existing_settings.scalar_one_or_none()
        
        if not settings_menu:
            # Create Settings root menu
            settings_menu = MenuItem(
                code="settings",
                title="Settings",
                description="System configuration and settings",
                url="/settings",
                icon="fas fa-cog",
                order_index=100,  # Put at the end
                level=0,
                item_type="dropdown",
                required_permission="settings.access"
            )
            session.add(settings_menu)
            await session.flush()
            await session.refresh(settings_menu)
            print("✅ Created Settings menu")
        else:
            print("ℹ️  Settings menu already exists")

        # Create Menu Configuration submenu
        existing_config = await session.execute(
            select(MenuItem).where(MenuItem.code == "menu_configuration")
        )
        menu_config = existing_config.scalar_one_or_none()
        
        if not menu_config:
            menu_config = MenuItem(
                code="menu_configuration",
                title="Menu Configuration",
                description="View and configure all service menus",
                url="/settings/menus",
                icon="fas fa-bars",
                parent_id=settings_menu.id,
                order_index=10,
                level=1,
                item_type="link",
                required_permission="menu.configuration"
            )
            session.add(menu_config)
            print("✅ Created Menu Configuration submenu")
        else:
            print("ℹ️  Menu Configuration submenu already exists")

        await session.commit()
        print("\n✅ Settings menu with Menu Configuration has been set up successfully!")

async def main():
    """Main setup function."""
    print("🔧 Setting up Settings menu with Menu Configuration...")
    try:
        await create_settings_menus()
        
        print("\n📘 Next steps:")
        print("1. Restart the menu-access-service: docker compose restart menu-access-service")
        print("2. Refresh the UI to see the new menu items")
        print("3. Assign appropriate permissions to users for accessing these menus")
        
    except Exception as e:
        print(f"❌ Error setting up menus: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())