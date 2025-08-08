"""
UI Definitions for Inventory Service.

Defines all UI components that the inventory service wants to register
with the UI Registry Service.
"""

INVENTORY_UI_PACKAGE = {
    "components": [
        {
            "id": "inventory-dashboard",
            "type": "dashboard",
            "title": "Inventory Dashboard",
            "description": "Overview of inventory metrics and status",
            "path": "/inventory",
            "icon": "warehouse",
            "permissions": ["access_inventory"],
            "order": 1
        }
    ],
    
    "widgets": [
        {
            "id": "total-products",
            "title": "Total Products",
            "type": "metric",
            "size": "small",
            "data_endpoint": "http://inventory-service:8005/api/v1/products/stats",
            "config": {
                "field": "total",
                "format": "number",
                "icon": "package",
                "color": "blue"
            },
            "permissions": ["view_products"]
        },
        {
            "id": "stock-value",
            "title": "Stock Value",
            "type": "metric",
            "size": "small",
            "data_endpoint": "http://inventory-service:8005/api/v1/stock/stats",
            "config": {
                "field": "total_value",
                "format": "currency",
                "icon": "dollar-sign",
                "color": "green"
            },
            "permissions": ["view_stock"]
        },
        {
            "id": "low-stock-alerts",
            "title": "Low Stock Items",
            "type": "metric",
            "size": "small",
            "data_endpoint": "http://inventory-service:8005/api/v1/stock/stats",
            "config": {
                "field": "low_stock_count",
                "format": "number",
                "icon": "alert-triangle",
                "color": "yellow",
                "link": "/inventory/low-stock"
            },
            "permissions": ["view_stock"]
        },
        {
            "id": "warehouse-count",
            "title": "Warehouses",
            "type": "metric",
            "size": "small",
            "data_endpoint": "http://inventory-service:8005/api/v1/warehouses/stats",
            "config": {
                "field": "total",
                "format": "number",
                "icon": "building",
                "color": "purple"
            },
            "permissions": ["view_warehouses"]
        },
        {
            "id": "recent-movements",
            "title": "Recent Stock Movements",
            "type": "list",
            "size": "large",
            "data_endpoint": "http://inventory-service:8005/api/v1/stock/movements/recent",
            "config": {
                "limit": 10,
                "columns": ["product", "type", "quantity", "warehouse", "time"],
                "refresh": 60
            },
            "permissions": ["view_stock_movements"]
        },
        {
            "id": "low-stock-list",
            "title": "Low Stock Alerts",
            "type": "list",
            "size": "medium",
            "data_endpoint": "http://inventory-service:8005/api/v1/stock/low",
            "config": {
                "limit": 5,
                "columns": ["product", "current_stock", "reorder_point", "warehouse"],
                "highlight": "critical"
            },
            "permissions": ["view_stock"]
        }
    ],
    
    "lists": [
        {
            "id": "products-list",
            "title": "Products",
            "entity": "products",
            "data_endpoint": "http://inventory-service:8005/api/v1/products",
            "columns": [
                {"key": "sku", "label": "SKU", "sortable": True},
                {"key": "name", "label": "Product Name", "sortable": True},
                {"key": "category", "label": "Category", "sortable": True},
                {"key": "list_price", "label": "Price", "format": "currency", "sortable": True},
                {"key": "quantity_on_hand", "label": "Stock", "format": "number", "sortable": True},
                {"key": "status", "label": "Status", "format": "badge"}
            ],
            "actions": [
                {"id": "view", "label": "View", "icon": "eye", "type": "link"},
                {"id": "edit", "label": "Edit", "icon": "edit", "type": "modal"},
                {"id": "delete", "label": "Delete", "icon": "trash", "type": "confirm"}
            ],
            "filters": [
                {"key": "category_id", "label": "Category", "type": "select"},
                {"key": "status", "label": "Status", "type": "select"},
                {"key": "search", "label": "Search", "type": "text"}
            ],
            "permissions": ["view_products"]
        },
        {
            "id": "stock-levels",
            "title": "Stock Levels",
            "entity": "stock",
            "data_endpoint": "http://inventory-service:8005/api/v1/stock",
            "columns": [
                {"key": "product_code", "label": "Product Code", "sortable": True},
                {"key": "product_name", "label": "Product", "sortable": True},
                {"key": "warehouse", "label": "Warehouse", "sortable": True},
                {"key": "on_hand", "label": "On Hand", "format": "number"},
                {"key": "available", "label": "Available", "format": "number"},
                {"key": "reserved", "label": "Reserved", "format": "number"}
            ],
            "filters": [
                {"key": "warehouse_id", "label": "Warehouse", "type": "select"},
                {"key": "low_stock", "label": "Low Stock Only", "type": "checkbox"}
            ],
            "permissions": ["view_stock"]
        },
        {
            "id": "warehouses-list",
            "title": "Warehouses",
            "entity": "warehouses",
            "data_endpoint": "http://inventory-service:8005/api/v1/warehouses",
            "columns": [
                {"key": "code", "label": "Code", "sortable": True},
                {"key": "name", "label": "Name", "sortable": True},
                {"key": "city", "label": "City", "sortable": True},
                {"key": "capacity", "label": "Capacity", "format": "number"},
                {"key": "utilization", "label": "Utilization", "format": "percentage"},
                {"key": "is_active", "label": "Active", "format": "boolean"}
            ],
            "actions": [
                {"id": "view", "label": "View Details", "icon": "eye"},
                {"id": "edit", "label": "Edit", "icon": "edit"},
                {"id": "locations", "label": "Manage Locations", "icon": "map-pin"}
            ],
            "permissions": ["view_warehouses"]
        }
    ],
    
    "forms": [
        {
            "id": "product-form",
            "title": "Product",
            "entity": "product",
            "submit_endpoint": "/api/v1/products",
            "data_endpoint": "http://inventory-service:8005/api/v1/products/{id}",
            "fields": [
                {
                    "key": "sku",
                    "label": "SKU",
                    "type": "text",
                    "required": True,
                    "validation": {"pattern": "^[A-Z0-9-]+$"}
                },
                {
                    "key": "name",
                    "label": "Product Name",
                    "type": "text",
                    "required": True
                },
                {
                    "key": "description",
                    "label": "Description",
                    "type": "textarea",
                    "rows": 3
                },
                {
                    "key": "category_id",
                    "label": "Category",
                    "type": "select",
                    "data_source": "/api/v1/products/categories",
                    "required": True
                },
                {
                    "key": "list_price",
                    "label": "List Price",
                    "type": "number",
                    "format": "currency",
                    "required": True
                },
                {
                    "key": "cost_price",
                    "label": "Cost Price",
                    "type": "number",
                    "format": "currency"
                },
                {
                    "key": "track_inventory",
                    "label": "Track Inventory",
                    "type": "checkbox",
                    "default": True
                },
                {
                    "key": "reorder_point",
                    "label": "Reorder Point",
                    "type": "number",
                    "conditional": {"field": "track_inventory", "value": True}
                },
                {
                    "key": "reorder_quantity",
                    "label": "Reorder Quantity",
                    "type": "number",
                    "conditional": {"field": "track_inventory", "value": True}
                },
                {
                    "key": "is_active",
                    "label": "Active",
                    "type": "checkbox",
                    "default": True
                }
            ],
            "layout": "single",
            "permissions": ["manage_products"]
        },
        {
            "id": "stock-adjustment-form",
            "title": "Stock Adjustment",
            "entity": "stock_adjustment",
            "submit_endpoint": "/api/v1/stock/adjustments",
            "fields": [
                {
                    "key": "product_id",
                    "label": "Product",
                    "type": "select",
                    "data_source": "/api/v1/products",
                    "required": True
                },
                {
                    "key": "warehouse_id",
                    "label": "Warehouse",
                    "type": "select",
                    "data_source": "/api/v1/warehouses",
                    "required": True
                },
                {
                    "key": "adjustment_type",
                    "label": "Adjustment Type",
                    "type": "select",
                    "options": [
                        {"value": "increase", "label": "Increase"},
                        {"value": "decrease", "label": "Decrease"},
                        {"value": "set", "label": "Set To"}
                    ],
                    "required": True
                },
                {
                    "key": "quantity",
                    "label": "Quantity",
                    "type": "number",
                    "required": True,
                    "min": 0
                },
                {
                    "key": "reason",
                    "label": "Reason",
                    "type": "select",
                    "options": [
                        {"value": "count", "label": "Physical Count"},
                        {"value": "damaged", "label": "Damaged Goods"},
                        {"value": "lost", "label": "Lost/Stolen"},
                        {"value": "found", "label": "Found"},
                        {"value": "other", "label": "Other"}
                    ],
                    "required": True
                },
                {
                    "key": "notes",
                    "label": "Notes",
                    "type": "textarea",
                    "rows": 2
                }
            ],
            "permissions": ["manage_stock"]
        },
        {
            "id": "warehouse-form",
            "title": "Warehouse",
            "entity": "warehouse",
            "submit_endpoint": "/api/v1/warehouses",
            "data_endpoint": "http://inventory-service:8005/api/v1/warehouses/{id}",
            "fields": [
                {
                    "key": "code",
                    "label": "Warehouse Code",
                    "type": "text",
                    "required": True,
                    "validation": {"pattern": "^[A-Z0-9-]+$"}
                },
                {
                    "key": "name",
                    "label": "Warehouse Name",
                    "type": "text",
                    "required": True
                },
                {
                    "key": "description",
                    "label": "Description",
                    "type": "textarea",
                    "rows": 2
                },
                {
                    "key": "address",
                    "label": "Address",
                    "type": "text"
                },
                {
                    "key": "city",
                    "label": "City",
                    "type": "text"
                },
                {
                    "key": "state",
                    "label": "State/Province",
                    "type": "text"
                },
                {
                    "key": "country",
                    "label": "Country",
                    "type": "select",
                    "data_source": "/api/v1/countries"
                },
                {
                    "key": "postal_code",
                    "label": "Postal Code",
                    "type": "text"
                },
                {
                    "key": "capacity_units",
                    "label": "Capacity (Units)",
                    "type": "number",
                    "min": 0
                },
                {
                    "key": "is_active",
                    "label": "Active",
                    "type": "checkbox",
                    "default": True
                }
            ],
            "layout": "single",
            "permissions": ["manage_warehouses"]
        }
    ]
}