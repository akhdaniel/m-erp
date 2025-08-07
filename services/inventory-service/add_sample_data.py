#!/usr/bin/env python3
"""
Add sample inventory data to demonstrate the service-driven UI architecture.
"""

import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random

# Import models  
from inventory_module.models import (
    Product, ProductCategory, ProductVariant,
    Warehouse, WarehouseLocation,
    StockLevel, StockMovement
)
from inventory_module.models.stock import StockMovementType
from inventory_module.database import Base

# Database URL
DATABASE_URL = "postgresql://postgres:password@postgres:5432/inventory_db"

# Create engine and session
engine = create_engine(DATABASE_URL.replace("+asyncpg", ""))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_sample_data():
    """Create sample inventory data"""
    session = SessionLocal()
    
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Check if data already exists
        existing_products = session.query(Product).count()
        if existing_products > 0:
            print(f"ℹ️  Database already has {existing_products} products. Skipping sample data creation.")
            return
        
        print("📦 Creating sample inventory data...")
        
        # Create product categories with default company_id
        categories = [
            ProductCategory(
                code="ELECTRONICS",
                name="Electronics",
                description="Electronic devices and accessories",
                parent_category_id=None,
                is_active=True,
                company_id=1  # Default company
            ),
            ProductCategory(
                code="COMPUTERS",
                name="Computers",
                description="Computers and components",
                parent_category_id=None,
                is_active=True,
                company_id=1
            ),
            ProductCategory(
                code="FURNITURE",
                name="Office Furniture",
                description="Office furniture and equipment",
                parent_category_id=None,
                is_active=True,
                company_id=1
            ),
            ProductCategory(
                code="SUPPLIES",
                name="Office Supplies",
                description="General office supplies",
                parent_category_id=None,
                is_active=True,
                company_id=1
            )
        ]
        session.add_all(categories)
        session.commit()
        print(f"✅ Created {len(categories)} product categories")
        
        # Create warehouses
        warehouses = [
            Warehouse(
                code="WH-001",
                name="Main Warehouse",
                address_line_1="123 Storage Lane",
                address_line_2="Industrial District",
                city="New York",
                state_province="NY",
                postal_code="10001",
                country_code="US",
                contact_person="John Smith",
                phone="+1-555-0100",
                email="warehouse1@m-erp.com",
                total_area_sqm=10000,
                storage_area_sqm=8000,
                is_active=True,
                is_primary=True,
                company_id=1
            ),
            Warehouse(
                code="WH-002",
                name="Secondary Warehouse",
                address_line_1="456 Distribution Ave",
                city="Los Angeles",
                state_province="CA",
                postal_code="90001",
                country_code="US",
                contact_person="Jane Doe",
                phone="+1-555-0200",
                email="warehouse2@m-erp.com",
                total_area_sqm=7500,
                storage_area_sqm=6000,
                is_active=True,
                company_id=1
            ),
            Warehouse(
                code="WH-003",
                name="European Distribution Center",
                address_line_1="789 Logistics Blvd",
                city="Amsterdam",
                state_province="NH",
                postal_code="1011",
                country_code="NL",
                contact_person="Peter van Berg",
                phone="+31-555-0300",
                email="warehouse3@m-erp.com",
                total_area_sqm=8000,
                storage_area_sqm=6500,
                is_active=True,
                company_id=1
            )
        ]
        session.add_all(warehouses)
        session.commit()
        print(f"✅ Created {len(warehouses)} warehouses")
        
        # Create products
        products_data = [
            # Electronics
            {"sku": "LAPTOP-001", "name": "ProBook Laptop 15\"", "category": "ELECTRONICS", "price": 899.99, "cost": 650.00},
            {"sku": "PHONE-001", "name": "SmartPhone X12", "category": "ELECTRONICS", "price": 699.99, "cost": 450.00},
            {"sku": "TABLET-001", "name": "TabletPro 10\"", "category": "ELECTRONICS", "price": 499.99, "cost": 350.00},
            {"sku": "HEADPHONE-001", "name": "Wireless Headphones Pro", "category": "ELECTRONICS", "price": 199.99, "cost": 120.00},
            {"sku": "MONITOR-001", "name": "UltraWide Monitor 34\"", "category": "ELECTRONICS", "price": 599.99, "cost": 400.00},
            
            # Computers
            {"sku": "DESKTOP-001", "name": "WorkStation Pro", "category": "COMPUTERS", "price": 1299.99, "cost": 900.00},
            {"sku": "KEYBOARD-001", "name": "Mechanical Keyboard RGB", "category": "COMPUTERS", "price": 149.99, "cost": 80.00},
            {"sku": "MOUSE-001", "name": "Gaming Mouse Wireless", "category": "COMPUTERS", "price": 79.99, "cost": 45.00},
            {"sku": "SSD-001", "name": "SSD 1TB NVMe", "category": "COMPUTERS", "price": 129.99, "cost": 85.00},
            {"sku": "RAM-001", "name": "RAM 32GB DDR4", "category": "COMPUTERS", "price": 179.99, "cost": 120.00},
            
            # Furniture
            {"sku": "DESK-001", "name": "Executive Desk Oak", "category": "FURNITURE", "price": 799.99, "cost": 450.00},
            {"sku": "CHAIR-001", "name": "Ergonomic Office Chair", "category": "FURNITURE", "price": 399.99, "cost": 250.00},
            {"sku": "CABINET-001", "name": "Filing Cabinet 4-Drawer", "category": "FURNITURE", "price": 299.99, "cost": 180.00},
            {"sku": "BOOKSHELF-001", "name": "Bookshelf 5-Tier", "category": "FURNITURE", "price": 199.99, "cost": 120.00},
            
            # Supplies
            {"sku": "PAPER-001", "name": "A4 Paper (500 sheets)", "category": "SUPPLIES", "price": 9.99, "cost": 5.00},
            {"sku": "PEN-001", "name": "Ballpoint Pens (Box of 12)", "category": "SUPPLIES", "price": 12.99, "cost": 6.00},
            {"sku": "NOTEBOOK-001", "name": "Spiral Notebook A5", "category": "SUPPLIES", "price": 4.99, "cost": 2.50},
            {"sku": "STAPLER-001", "name": "Heavy Duty Stapler", "category": "SUPPLIES", "price": 24.99, "cost": 15.00},
            {"sku": "FOLDER-001", "name": "File Folders (Pack of 25)", "category": "SUPPLIES", "price": 14.99, "cost": 8.00},
            {"sku": "MARKER-001", "name": "Whiteboard Markers (Set of 4)", "category": "SUPPLIES", "price": 8.99, "cost": 4.00}
        ]
        
        category_map = {cat.code: cat for cat in categories}
        products = []
        
        for prod_data in products_data:
            product = Product(
                sku=prod_data["sku"],
                name=prod_data["name"],
                description=f"High-quality {prod_data['name']} for professional use",
                category_id=category_map[prod_data["category"]].id,
                barcode=f"BAR{prod_data['sku']}",
                list_price=prod_data["price"],
                cost_price=prod_data["cost"],
                weight=random.uniform(0.1, 5.0),
                unit_of_measure="EACH",
                minimum_stock_level=random.randint(5, 20),
                maximum_stock_level=random.randint(100, 500),
                reorder_point=random.randint(10, 30),
                is_active=True if random.random() > 0.1 else False,  # 90% active
                company_id=1
            )
            products.append(product)
        
        session.add_all(products)
        session.commit()
        print(f"✅ Created {len(products)} products")
        
        # Create stock levels for products in warehouses
        stock_levels = []
        movements = []
        
        for product in products:
            for warehouse in warehouses:
                # Random stock allocation
                if random.random() > 0.3:  # 70% chance of having stock
                    quantity = random.randint(10, 200)
                    stock_level = StockLevel(
                        product_id=product.id,
                        warehouse_location_id=None,  # Not assigning to specific location
                        quantity_on_hand=quantity,
                        quantity_reserved=random.randint(0, min(20, quantity)),
                        quantity_available=quantity,
                        last_count_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                        company_id=1
                    )
                    stock_levels.append(stock_level)
                    
                    # Create some historical movements
                    for _ in range(random.randint(1, 5)):
                        movement_types = [
                            StockMovementType.RECEIPT,
                            StockMovementType.SALE,
                            StockMovementType.ADJUSTMENT_IN,
                            StockMovementType.ADJUSTMENT_OUT,
                            StockMovementType.TRANSFER_IN
                        ]
                        movement = StockMovement(
                            product_id=product.id,
                            warehouse_location_id=None,
                            movement_type=random.choice(movement_types),
                            quantity=random.randint(1, 50),
                            source_document_type="manual",
                            source_document_number="SAMPLE-001",
                            movement_date=datetime.now() - timedelta(days=random.randint(1, 60)),
                            notes=f"Sample movement for {product.name}",
                            created_by_user_id=1,  # Default user
                            company_id=1
                        )
                        movements.append(movement)
        
        session.add_all(stock_levels)
        session.add_all(movements)
        session.commit()
        print(f"✅ Created {len(stock_levels)} stock levels")
        print(f"✅ Created {len(movements)} stock movements")
        
        # Create warehouse locations
        locations = []
        for warehouse in warehouses:
            zones = ["A", "B", "C"]
            for zone in zones:
                for aisle in range(1, 4):
                    for shelf in range(1, 5):
                        location = WarehouseLocation(
                            warehouse_id=warehouse.id,
                            code=f"{zone}-{aisle:02d}-{shelf:02d}",
                            name=f"Zone {zone}, Aisle {aisle}, Shelf {shelf}",
                            location_type="shelf",
                            max_items=100,
                            is_active=True,
                            company_id=1
                        )
                        locations.append(location)
        
        session.add_all(locations)
        session.commit()
        print(f"✅ Created {len(locations)} warehouse locations")
        
        # Summary statistics
        print("\n📊 Sample Data Summary:")
        print(f"   • Categories: {len(categories)}")
        print(f"   • Products: {len(products)} ({sum(1 for p in products if p.is_active)} active)")
        print(f"   • Warehouses: {len(warehouses)}")
        print(f"   • Stock Levels: {len(stock_levels)}")
        print(f"   • Stock Movements: {len(movements)}")
        print(f"   • Warehouse Locations: {len(locations)}")
        
        # Calculate some metrics for display
        total_stock_value = sum(
            float(sl.quantity_on_hand * prod.list_price) 
            for sl, prod in session.query(StockLevel, Product).join(Product).all()
        )
        low_stock_count = session.query(Product).filter(
            Product.minimum_stock_level > 0
        ).count()
        
        print(f"\n💰 Inventory Metrics:")
        print(f"   • Total Stock Value: ${total_stock_value:,.2f}")
        print(f"   • Products with Low Stock Alerts: {low_stock_count}")
        
        print("\n✨ Sample data created successfully!")
        print("   The inventory dashboard should now display real data.")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    create_sample_data()