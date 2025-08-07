#!/usr/bin/env python3
"""
Script to set up basic menu items for Companies, Partners, and Users.
This should be run after the menu-access-service is operational.
"""

import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

# Add menu-access-service to Python path
sys.path.insert(0, '/app')

from app.core.database import get_db
from app.models.menu import MenuItem
from app.models.permission import Permission

# Database configuration from menu-access-service
DATABASE_URL = "postgresql+asyncpg://postgres:password@postgres:5432/menu_access_db"

engine = create_async_engine(DATABASE_URL)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

async def create_basic_menus():
    """Create basic menu structure for Companies, Partners, and Users."""
    async with AsyncSession() as session:
        # Create permissions for basic features if they don't exist
        basic_permissions = [
            Permission(
                code="companies.view",
                name="View Companies",
                description="View company information",
                category="companies",
                action="read"
            ),
            Permission(
                code="partners.view", 
                name="View Partners",
                description="View partner information",
                category="partners",
                action="read"
            ),
            Permission(
                code="users.view",
                name="View Users",
                description="View user accounts",
                category="users",
                action="read"
            ),
            Permission(
                code="admin.access",
                name="Admin Access",
                description="Access administrative features",
                category="admin",
                action="access"
            ),
        ]

        # Check and add permissions
        for perm in basic_permissions:
            existing = await session.execute(
                select(Permission).where(Permission.code == perm.code)
            )
            if not existing.scalar_one_or_none():
                session.add(perm)
        
        await session.commit()

        # Create basic menu items
        basic_menus = [
            MenuItem(
                code="companies",
                title="Companies",
                description="Manage companies and organizations",
                url="/companies",
                icon="fas fa-building",
                order_index=10,
                level=0,
                item_type="link",
                required_permission="companies.view"
            ),
            MenuItem(
                code="partners",
                title="Partners", 
                description="Manage customers and suppliers",
                url="/partners",
                icon="fas fa-handshake",
                order_index=20,
                level=0,
                item_type="link",
                required_permission="partners.view"
            ),
            MenuItem(
                code="users",
                title="Users",
                description="Manage user accounts and permissions",
                url="/users",
                icon="fas fa-users",
                order_index=40,
                level=0,
                item_type="link",
                required_permission="admin.access"
            ),
        ]

        # Check and add menu items
        for menu in basic_menus:
            existing = await session.execute(
                select(MenuItem).where(MenuItem.code == menu.code)
            )
            if not existing.scalar_one_or_none():
                session.add(menu)
                print(f"✅ Created menu: {menu.title}")
            else:
                print(f"ℹ️  Menu already exists: {menu.title}")

        await session.commit()
        print("\n✅ Basic menus have been set up successfully!")

async def main():
    """Main setup function."""
    print("🔧 Setting up basic menu items...")
    try:
        await create_basic_menus()
        
        print("\n📘 Next steps:")
        print("1. Restart the menu-access-service: docker compose restart menu-access-service")
        print("2. Refresh the UI to see the new menu items")
        print("3. Run setup_inventory_sales_menus.py to add Inventory and Sales menus")
        
    except Exception as e:
        print(f"❌ Error setting up menus: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())