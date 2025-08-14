#!/usr/bin/env python3
"""
Script to set up Inventory Management and Sales Module menu items.
This should be run after the inventory and sales services are operational.
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

async def create_inventory_menus():
    """Create Inventory Management menu structure."""
    async with AsyncSession() as session:
        # Create permissions for inventory if they don't exist
        inventory_permissions = [
            Permission(
                code="inventory.access",
                name="Inventory Management",
                description="Access to inventory management system",
                category="inventory",
                action="access"
            ),
            Permission(
                code="products.view",
                name="View Products",
                description="View product catalog and details",
                category="products",
                action="read"
            ),
            Permission(
                code="products.manage",
                name="Manage Products",
                description="Create, update, and delete products",
                category="products",
                action="write"
            ),
            Permission(
                code="stock.view",
                name="View Stock",
                description="View stock levels and movements",
                category="stock",
                action="read"
            ),
            Permission(
                code="warehouses.view",
                name="View Warehouses",
                description="View warehouse and location information",
                category="warehouses",
                action="read"
            ),
            Permission(
                code="receiving.view",
                name="View Receiving",
                description="View inbound receiving operations",
                category="receiving",
                action="read"
            ),
        ]

        # Check existing permissions
        for perm in inventory_permissions:
            existing = await session.execute(
                select(Permission).where(Permission.code == perm.code)
            )
            if not existing.scalar_one_or_none():
                session.add(perm)
        
        await session.commit()

        # Create Inventory Management root menu
        inventory_menu = MenuItem(
            code="inventory_management",
            title="Inventory Management",
            description="Complete inventory and warehouse management system",
            url="/inventory",
            icon="fas fa-boxes-stacked",
            order_index=30,
            level=0,
            item_type="dropdown",
            required_permission="inventory.access"
        )

        # Check if inventory menu exists
        existing = await session.execute(
            select(MenuItem).where(MenuItem.code == "inventory_management")
        )
        if existing.scalar_one_or_none():
            print("Inventory management menu already exists")
            return

        session.add(inventory_menu)
        await session.flush()
        await session.refresh(inventory_menu)

        # Sub-menu items for Inventory Management
        inventory_sub_items = [
            MenuItem(
                code="products_catalog",
                title="Products",
                description="Product catalog and management",
                url="/inventory/products",
                icon="fas fa-box",
                parent_id=inventory_menu.id,
                order_index=10,
                level=1,
                required_permission="products.view"
            ),
            MenuItem(
                code="product_categories",
                title="Product Categories",
                description="Manage product categories and classification",
                url="/inventory/categories",
                icon="fas fa-sitemap",
                parent_id=inventory_menu.id,
                order_index=20,
                level=1,
                required_permission="products.view"
            ),
            MenuItem(
                code="stock_movements",
                title="Stock Movements",
                description="View stock movements and adjustments",
                url="/inventory/stock-movements",
                icon="fas fa-arrows-alt-h",
                parent_id=inventory_menu.id,
                order_index=30,
                level=1,
                required_permission="stock.view"
            ),
            MenuItem(
                code="stock_levels",
                title="Stock Levels",
                description="Current stock levels and alerts",
                url="/inventory/stock-levels",
                icon="fas fa-chart-line",
                parent_id=inventory_menu.id,
                order_index=40,
                level=1,
                required_permission="stock.view"
            ),
            MenuItem(
                code="warehouses_management",
                title="Warehouses",
                description="Warehouse and location management",
                url="/inventory/warehouses",
                icon="fas fa-warehouse",
                parent_id=inventory_menu.id,
                order_index=50,
                level=1,
                required_permission="warehouses.view"
            ),
            MenuItem(
                code="inventory_receiving",
                title="Receiving",
                description="Inbound inventory receiving operations",
                url="/inventory/receiving",
                icon="fas fa-truck-loading",
                parent_id=inventory_menu.id,
                order_index=60,
                level=1,
                required_permission="receiving.view"
            ),
            MenuItem(
                code="suppliers_management",
                title="Suppliers",
                description="Supplier and vendor management",
                url="/inventory/suppliers",
                icon="fas fa-truck",
                parent_id=inventory_menu.id,
                order_index=70,
                level=1,
                required_permission="partners.view"
            ),
        ]

        for item in inventory_sub_items:
            session.add(item)

        await session.commit()
        print("✅ Inventory Management menu created successfully")

async def create_sales_menus():
    """Create Sales Management menu structure."""
    async with AsyncSession() as session:
        # Create permissions for sales
        sales_permissions = [
            Permission(
                code="sales.access",
                name="Sales Management",
                description="Access to sales management system",
                category="sales",
                action="access"
            ),
            Permission(
                code="quotes.view",
                name="View Quotes",
                description="View sales quotes and proposals",
                category="quotes",
                action="read"
            ),
            Permission(
                code="orders.view",
                name="View Orders",
                description="View sales orders and processing",
                category="orders",
                action="read"
            ),
            Permission(
                code="customers.view",
                name="View Customers",
                description="View customer accounts and details",
                category="customers",
                action="read"
            ),
            Permission(
                code="invoices.view",
                name="View Invoices",
                description="View customer invoices",
                category="invoices",
                action="read"
            ),
        ]

        for perm in sales_permissions:
            existing = await session.execute(
                select(Permission).where(Permission.code == perm.code)
            )
            if not existing.scalar_one_or_none():
                session.add(perm)
        
        await session.commit()

        # Create Sales Management root menu
        sales_menu = MenuItem(
            code="sales_management",
            title="Sales Management",
            description="Complete sales and revenue management system",
            url="/sales",
            icon="fas fa-shopping-cart",
            order_index=20,
            level=0,
            item_type="dropdown",
            required_permission="sales.access"
        )

        # Check if sales menu exists
        existing = await session.execute(
            select(MenuItem).where(MenuItem.code == "sales_management")
        )
        if existing.scalar_one_or_none():
            print("Sales management menu already exists")
            return

        session.add(sales_menu)
        await session.flush()
        await session.refresh(sales_menu)

        # Sub-menu items for Sales Management
        sales_sub_items = [
            MenuItem(
                code="quotes_management",
                title="Sales Quotes",
                description="Create and manage sales quotes and proposals",
                url="/sales/quotes",
                icon="fas fa-file-invoice-dollar",
                parent_id=sales_menu.id,
                order_index=10,
                level=1,
                required_permission="quotes.view"
            ),
            MenuItem(
                code="sales_orders",
                title="Sales Orders",
                description="Process and manage sales orders",
                url="/sales/orders",
                icon="fas fa-receipt",
                parent_id=sales_menu.id,
                order_index=20,
                level=1,
                required_permission="orders.view"
            ),
            MenuItem(
                code="customers_management",
                title="Customers",
                description="Manage customer accounts and relationships",
                url="/sales/customers",
                icon="fas fa-users",
                parent_id=sales_menu.id,
                order_index=30,
                level=1,
                required_permission="customers.view"
            ),
            MenuItem(
                code="sales_products",
                title="Products",
                description="Product catalog and inventory for sales",
                url="/sales/products",
                icon="fas fa-tags",
                parent_id=sales_menu.id,
                order_index=40,
                level=1,
                required_permission="products.view"
            ),
            MenuItem(
                code="sales_invoices",
                title="Invoices",
                description="Sales invoices and billing management",
                url="/sales/invoices",
                icon="fas fa-file-invoice",
                parent_id=sales_menu.id,
                order_index=50,
                level=1,
                required_permission="invoices.view"
            ),
            MenuItem(
                code="sales_analytics",
                title="Sales Analytics",
                description="Sales reports and performance analytics",
                url="/sales/analytics",
                icon="fas fa-chart-bar",
                parent_id=sales_menu.id,
                order_index=60,
                level=1
            ),
        ]

        for item in sales_sub_items:
            session.add(item)

        await session.commit()
        print("✅ Sales Management menu created successfully")

async def main():
    """Main setup function."""
    print("🔧 Setting up Inventory and Sales Management menus...")
    try:
        await create_inventory_menus()
        print("🏗️  Inventory menus created successfully")
        
        await create_sales_menus()
        print("🛒 Sales menus created successfully")
        
        print("\n✅ All menus have been set up successfully!")
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