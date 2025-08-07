#!/usr/bin/env python3
"""
Script to register inventory service UI components with the UI Registry.
This demonstrates the service-driven UI architecture.
"""

import requests
import json
import sys

# UI Registry endpoint
UI_REGISTRY_URL = "http://localhost:8010"

# Inventory UI Package Definition
INVENTORY_UI_PACKAGE = {
    "widgets": [
        {
            "id": "total-products",
            "title": "Total Products",
            "type": "metric",
            "size": "small",
            "data_endpoint": "/api/v1/products/stats",
            "refresh_interval": 300,
            "config": {
                "field": "total",
                "format": "number",
                "color": "blue",
                "icon": "package"
            }
        },
        {
            "id": "active-products",
            "title": "Active Products",
            "type": "metric",
            "size": "small",
            "data_endpoint": "/api/v1/products/stats",
            "refresh_interval": 300,
            "config": {
                "field": "active",
                "format": "number",
                "color": "green",
                "icon": "check-circle"
            }
        },
        {
            "id": "low-stock-alerts",
            "title": "Low Stock Alerts",
            "type": "metric",
            "size": "small",
            "data_endpoint": "/api/v1/stock/low-stock",
            "refresh_interval": 60,
            "config": {
                "field": "count",
                "format": "number",
                "color": "red",
                "icon": "alert-triangle",
                "link": "/inventory/stock/low"
            }
        },
        {
            "id": "warehouse-count",
            "title": "Warehouses",
            "type": "metric",
            "size": "small",
            "data_endpoint": "/api/v1/warehouses/stats",
            "refresh_interval": 600,
            "config": {
                "field": "total",
                "format": "number",
                "color": "purple",
                "icon": "building"
            }
        },
        {
            "id": "recent-movements",
            "title": "Recent Stock Movements",
            "type": "list",
            "size": "large",
            "data_endpoint": "/api/v1/stock/movements/recent",
            "refresh_interval": 60,
            "config": {
                "limit": 10,
                "columns": ["product_name", "quantity", "movement_type", "timestamp"]
            }
        },
        {
            "id": "top-products",
            "title": "Top Products by Movement",
            "type": "chart",
            "size": "medium",
            "data_endpoint": "/api/v1/products/top-movers",
            "refresh_interval": 300,
            "config": {
                "chart_type": "bar",
                "x_field": "product_name",
                "y_field": "movement_count"
            }
        }
    ],
    "lists": [
        {
            "id": "products-list",
            "title": "Products",
            "entity": "products",
            "data_endpoint": "/api/v1/products",
            "columns": [
                {"key": "sku", "label": "SKU", "sortable": True},
                {"key": "name", "label": "Product Name", "sortable": True},
                {"key": "category", "label": "Category", "sortable": True},
                {"key": "list_price", "label": "Price", "format": "currency"},
                {"key": "stock_on_hand", "label": "Stock", "format": "number"},
                {"key": "status", "label": "Status", "format": "badge"}
            ],
            "actions": [
                {"id": "view", "label": "View", "icon": "eye"},
                {"id": "edit", "label": "Edit", "icon": "edit"},
                {"id": "delete", "label": "Delete", "icon": "trash", "confirm": True}
            ],
            "filters": [
                {"field": "category", "type": "select", "label": "Category"},
                {"field": "status", "type": "select", "label": "Status", "options": ["active", "inactive"]}
            ]
        },
        {
            "id": "warehouses-list",
            "title": "Warehouses",
            "entity": "warehouses",
            "data_endpoint": "/api/v1/warehouses",
            "columns": [
                {"key": "code", "label": "Code", "sortable": True},
                {"key": "name", "label": "Warehouse Name", "sortable": True},
                {"key": "location", "label": "Location"},
                {"key": "capacity", "label": "Capacity", "format": "percentage"},
                {"key": "status", "label": "Status", "format": "badge"}
            ]
        },
        {
            "id": "stock-movements-list",
            "title": "Stock Movements",
            "entity": "movements",
            "data_endpoint": "/api/v1/stock/movements",
            "columns": [
                {"key": "timestamp", "label": "Date/Time", "format": "datetime", "sortable": True},
                {"key": "product_name", "label": "Product"},
                {"key": "warehouse", "label": "Warehouse"},
                {"key": "movement_type", "label": "Type", "format": "badge"},
                {"key": "quantity", "label": "Quantity", "format": "number"},
                {"key": "user", "label": "User"}
            ]
        }
    ],
    "forms": [
        {
            "id": "product-form",
            "title": "Product Details",
            "entity": "product",
            "mode": "create",
            "submit_endpoint": "/api/v1/products",
            "data_endpoint": "/api/v1/products/{id}",
            "fields": [
                {"name": "sku", "label": "SKU", "type": "text", "required": True},
                {"name": "name", "label": "Product Name", "type": "text", "required": True},
                {"name": "description", "label": "Description", "type": "textarea"},
                {"name": "category_id", "label": "Category", "type": "select", "data_source": "/api/v1/categories"},
                {"name": "list_price", "label": "List Price", "type": "number", "min": 0},
                {"name": "cost_price", "label": "Cost Price", "type": "number", "min": 0},
                {"name": "min_stock_level", "label": "Minimum Stock", "type": "number", "min": 0},
                {"name": "max_stock_level", "label": "Maximum Stock", "type": "number", "min": 0}
            ],
            "layout": "single"
        },
        {
            "id": "warehouse-form",
            "title": "Warehouse Details",
            "entity": "warehouse",
            "submit_endpoint": "/api/v1/warehouses",
            "data_endpoint": "/api/v1/warehouses/{id}",
            "fields": [
                {"name": "code", "label": "Warehouse Code", "type": "text", "required": True},
                {"name": "name", "label": "Warehouse Name", "type": "text", "required": True},
                {"name": "address", "label": "Address", "type": "textarea"},
                {"name": "manager", "label": "Manager", "type": "text"},
                {"name": "phone", "label": "Phone", "type": "tel"},
                {"name": "email", "label": "Email", "type": "email"}
            ]
        },
        {
            "id": "stock-adjustment-form",
            "title": "Stock Adjustment",
            "entity": "adjustment",
            "submit_endpoint": "/api/v1/stock/adjustments",
            "fields": [
                {"name": "product_id", "label": "Product", "type": "select", "data_source": "/api/v1/products", "required": True},
                {"name": "warehouse_id", "label": "Warehouse", "type": "select", "data_source": "/api/v1/warehouses", "required": True},
                {"name": "adjustment_type", "label": "Type", "type": "select", "options": ["add", "remove", "correct"], "required": True},
                {"name": "quantity", "label": "Quantity", "type": "number", "min": 1, "required": True},
                {"name": "reason", "label": "Reason", "type": "textarea", "required": True}
            ]
        }
    ],
    "components": [
        {
            "id": "inventory-dashboard",
            "type": "dashboard",
            "title": "Inventory Dashboard",
            "path": "/inventory/dashboard",
            "icon": "package",
            "config": {
                "layout": [
                    {"widget": "total-products", "row": 0, "col": 0},
                    {"widget": "active-products", "row": 0, "col": 1},
                    {"widget": "low-stock-alerts", "row": 0, "col": 2},
                    {"widget": "warehouse-count", "row": 0, "col": 3},
                    {"widget": "recent-movements", "row": 1, "col": 0, "colspan": 2},
                    {"widget": "top-products", "row": 1, "col": 2, "colspan": 2}
                ]
            }
        }
    ]
}

def register_ui_package():
    """Register the inventory UI package with the UI Registry"""
    try:
        # Register the complete UI package
        response = requests.post(
            f"{UI_REGISTRY_URL}/api/v1/services/inventory-service/ui-package",
            json=INVENTORY_UI_PACKAGE,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Successfully registered inventory UI package")
            result = response.json()
            print(f"   Status: {result.get('status')}")
            print(f"   Service: {result.get('service')}")
            
            # Verify registration
            print("\n📊 Registered components:")
            
            # Check widgets
            widgets_response = requests.get(f"{UI_REGISTRY_URL}/api/v1/dashboard/widgets")
            if widgets_response.status_code == 200:
                widgets = widgets_response.json()
                inventory_widgets = [w for w in widgets if w.get('service') == 'inventory-service']
                print(f"   - {len(inventory_widgets)} dashboard widgets")
                for widget in inventory_widgets:
                    print(f"     • {widget['id']}: {widget['title']}")
            
            # Check lists
            lists_response = requests.get(f"{UI_REGISTRY_URL}/api/v1/lists")
            if lists_response.status_code == 200:
                lists = lists_response.json()
                inventory_lists = [l for l in lists if l.get('service') == 'inventory-service']
                print(f"   - {len(inventory_lists)} list views")
                for lst in inventory_lists:
                    print(f"     • {lst['id']}: {lst['title']}")
            
            # Check forms
            forms_response = requests.get(f"{UI_REGISTRY_URL}/api/v1/forms")
            if forms_response.status_code == 200:
                forms = forms_response.json()
                inventory_forms = [f for f in forms if f.get('service') == 'inventory-service']
                print(f"   - {len(inventory_forms)} form views")
                for form in inventory_forms:
                    print(f"     • {form['id']}: {form['title']}")
            
            return True
        else:
            print(f"❌ Failed to register UI package: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to UI Registry Service")
        print("   Make sure the service is running on http://localhost:8010")
        return False
    except Exception as e:
        print(f"❌ Error registering UI package: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Registering Inventory Service UI Components")
    print("=" * 50)
    
    success = register_ui_package()
    
    if success:
        print("\n✨ Inventory UI components are now available in the UI Registry!")
        print("   The UI service can now fetch and render these components dynamically.")
    else:
        print("\n⚠️  Failed to register UI components. Please check the errors above.")
        sys.exit(1)