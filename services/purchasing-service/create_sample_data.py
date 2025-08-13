#!/usr/bin/env python3
"""
Create sample data for purchasing module.

This script creates sample purchase orders, suppliers, and related data
to demonstrate the purchasing dashboard functionality.
"""

import httpx
import asyncio
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Base URL for the purchasing service
BASE_URL = "http://localhost:8007"

# Sample supplier data
SUPPLIERS = [
    {
        "code": "SUP001",
        "name": "Tech Solutions Inc",
        "category": "technology",
        "contact_person": "John Smith",
        "email": "john@techsolutions.com",
        "phone": "+1-555-0100",
        "address": "123 Tech Street",
        "city": "San Francisco",
        "state": "CA",
        "country": "USA",
        "postal_code": "94105",
        "payment_terms": "Net 30",
        "currency_code": "USD"
    },
    {
        "code": "SUP002",
        "name": "Office Supplies Co",
        "category": "office",
        "contact_person": "Sarah Johnson",
        "email": "sarah@officesupplies.com",
        "phone": "+1-555-0200",
        "address": "456 Office Blvd",
        "city": "New York",
        "state": "NY",
        "country": "USA",
        "postal_code": "10001",
        "payment_terms": "Net 60",
        "currency_code": "USD"
    },
    {
        "code": "SUP003",
        "name": "Global Manufacturing Ltd",
        "category": "manufacturing",
        "contact_person": "Michael Chen",
        "email": "michael@globalmanufacturing.com",
        "phone": "+1-555-0300",
        "address": "789 Industrial Park",
        "city": "Chicago",
        "state": "IL",
        "country": "USA",
        "postal_code": "60601",
        "payment_terms": "Net 45",
        "currency_code": "USD"
    },
    {
        "code": "SUP004",
        "name": "Premium Services Group",
        "category": "services",
        "contact_person": "Emily Davis",
        "email": "emily@premiumservices.com",
        "phone": "+1-555-0400",
        "address": "321 Service Lane",
        "city": "Boston",
        "state": "MA",
        "country": "USA",
        "postal_code": "02101",
        "payment_terms": "Net 30",
        "currency_code": "USD"
    },
    {
        "code": "SUP005",
        "name": "Eco Supplies International",
        "category": "sustainable",
        "contact_person": "David Green",
        "email": "david@ecosupplies.com",
        "phone": "+1-555-0500",
        "address": "555 Green Way",
        "city": "Seattle",
        "state": "WA",
        "country": "USA",
        "postal_code": "98101",
        "payment_terms": "COD",
        "currency_code": "USD"
    }
]

# Sample products for line items
PRODUCTS = [
    {"name": "Laptop Pro 15", "code": "TECH-001", "unit_price": 1299.99, "category": "technology"},
    {"name": "Office Chair Ergonomic", "code": "FURN-001", "unit_price": 449.99, "category": "furniture"},
    {"name": "Printer Paper A4 (Box)", "code": "SUPP-001", "unit_price": 24.99, "category": "supplies"},
    {"name": "Standing Desk", "code": "FURN-002", "unit_price": 599.99, "category": "furniture"},
    {"name": "Wireless Mouse", "code": "TECH-002", "unit_price": 39.99, "category": "technology"},
    {"name": "Notebook Set", "code": "SUPP-002", "unit_price": 12.99, "category": "supplies"},
    {"name": "Monitor 27 inch", "code": "TECH-003", "unit_price": 349.99, "category": "technology"},
    {"name": "Desk Lamp LED", "code": "FURN-003", "unit_price": 79.99, "category": "furniture"},
    {"name": "Coffee Machine", "code": "APPL-001", "unit_price": 199.99, "category": "appliances"},
    {"name": "Whiteboard", "code": "FURN-004", "unit_price": 149.99, "category": "furniture"}
]


async def create_suppliers(client: httpx.AsyncClient):
    """Create sample suppliers."""
    created_suppliers = []
    
    for supplier in SUPPLIERS:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/suppliers/",
                json=supplier,
                headers={"x-user-id": "1", "x-company-id": "1"}
            )
            if response.status_code == 201:
                created_suppliers.append(response.json())
                print(f"✓ Created supplier: {supplier['name']}")
            else:
                print(f"✗ Failed to create supplier: {supplier['name']} - {response.status_code}")
        except Exception as e:
            print(f"✗ Error creating supplier {supplier['name']}: {e}")
    
    return created_suppliers


async def create_purchase_orders(client: httpx.AsyncClient, suppliers):
    """Create sample purchase orders with varying statuses and dates."""
    created_orders = []
    
    # Create orders with different dates and statuses
    for i in range(20):
        # Random supplier
        supplier = random.choice(suppliers)
        
        # Random date in the last 90 days
        days_ago = random.randint(0, 90)
        order_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        # Expected delivery date
        delivery_days = random.randint(7, 30)
        expected_delivery = (datetime.now() + timedelta(days=delivery_days)).isoformat()
        
        # Random products for line items (1-5 items)
        num_items = random.randint(1, 5)
        selected_products = random.sample(PRODUCTS, num_items)
        
        line_items = []
        for product in selected_products:
            quantity = random.randint(1, 20)
            line_items.append({
                "product_id": random.randint(1, 100),
                "product_name": product["name"],
                "product_code": product["code"],
                "quantity": quantity,
                "unit_price": product["unit_price"],
                "discount_percentage": random.choice([0, 5, 10, 15]),
                "tax_rate": random.choice([0, 8, 10])
            })
        
        # Determine status
        if i < 5:
            status = "draft"
        elif i < 10:
            status = "approved"
        elif i < 15:
            status = "pending"
        else:
            status = random.choice(["completed", "cancelled"])
        
        po_data = {
            "supplier_id": supplier.get("id", random.randint(1, 5)),
            "supplier_name": supplier["name"],
            "expected_delivery": expected_delivery,
            "status": status,
            "currency_code": "USD",
            "payment_terms": supplier.get("payment_terms", "Net 30"),
            "shipping_address": f"{random.randint(100, 999)} Main Street, City, State 12345",
            "billing_address": f"{random.randint(100, 999)} Billing Ave, City, State 12345",
            "notes": f"Purchase order #{i+1} - {random.choice(['Urgent', 'Standard', 'Routine'])} delivery",
            "items": line_items
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/purchase-orders/",
                json=po_data,
                headers={"x-user-id": "1", "x-company-id": "1"}
            )
            if response.status_code == 201:
                order = response.json()
                created_orders.append(order)
                print(f"✓ Created PO: {order['po_number']} - ${order['total_amount']} ({status})")
            else:
                print(f"✗ Failed to create PO: {response.status_code}")
        except Exception as e:
            print(f"✗ Error creating PO: {e}")
    
    return created_orders


async def evaluate_suppliers(client: httpx.AsyncClient, suppliers):
    """Add performance evaluations for suppliers."""
    for supplier in suppliers:
        evaluation = {
            "delivery_rating": random.uniform(3.5, 5.0),
            "quality_rating": random.uniform(3.5, 5.0),
            "price_rating": random.uniform(3.0, 5.0),
            "communication_rating": random.uniform(3.5, 5.0),
            "comments": f"Evaluation for {supplier['name']} - Generally performing well."
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/suppliers/{supplier['id']}/evaluate",
                json=evaluation,
                headers={"x-user-id": "1", "x-company-id": "1"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Evaluated supplier: {supplier['name']} - Rating: {result['new_rating']:.2f}")
            else:
                print(f"✗ Failed to evaluate supplier: {supplier['name']}")
        except Exception as e:
            print(f"✗ Error evaluating supplier {supplier['name']}: {e}")


async def main():
    """Main function to create all sample data."""
    print("\n=== Creating Sample Data for Purchasing Module ===\n")
    
    async with httpx.AsyncClient() as client:
        # Create suppliers
        print("1. Creating Suppliers...")
        suppliers = await create_suppliers(client)
        print(f"   Created {len(suppliers)} suppliers\n")
        
        # Create purchase orders
        print("2. Creating Purchase Orders...")
        orders = await create_purchase_orders(client, suppliers)
        print(f"   Created {len(orders)} purchase orders\n")
        
        # Evaluate suppliers
        print("3. Adding Supplier Evaluations...")
        await evaluate_suppliers(client, suppliers)
        print()
        
        # Test dashboard endpoints
        print("4. Testing Dashboard Endpoints...")
        
        # Test metrics
        response = await client.get(f"{BASE_URL}/api/v1/dashboard/metrics")
        if response.status_code == 200:
            metrics = response.json()
            print(f"   ✓ Dashboard Metrics:")
            print(f"     - Total Orders: {metrics['total_orders']}")
            print(f"     - Pending Approval: {metrics['pending_approval']}")
            print(f"     - Active Suppliers: {metrics['active_suppliers']}")
            print(f"     - Total Spend: ${metrics['total_spend']}")
        
        # Test recent orders
        response = await client.get(f"{BASE_URL}/api/v1/dashboard/recent/orders")
        if response.status_code == 200:
            recent = response.json()
            print(f"   ✓ Recent Orders: {len(recent['orders'])} orders")
        
        # Test top suppliers
        response = await client.get(f"{BASE_URL}/api/v1/dashboard/analytics/top-suppliers")
        if response.status_code == 200:
            top = response.json()
            print(f"   ✓ Top Suppliers: {len(top['suppliers'])} suppliers")
        
        print("\n=== Sample Data Creation Complete ===\n")


if __name__ == "__main__":
    asyncio.run(main())