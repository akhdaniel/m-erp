"""
UI definitions for purchasing module.

Defines UI components for service-driven UI registration.
"""

PURCHASING_UI_PACKAGE = {
    "service": "purchasing-service",
    "version": "1.0.0",
    "dashboard": {
        "id": "purchasing-dashboard",
        "title": "Purchasing Dashboard",
        "description": "Overview of purchasing operations and metrics",
        "icon": "shopping-cart",
        "path": "/purchasing/dashboard"
    },
    "widgets": [
        {
            "id": "purchasing-metrics",
            "name": "Purchasing Metrics",
            "description": "Key purchasing KPIs",
            "type": "metrics",
            "size": "large",
            "dataSource": "/api/v1/dashboard/metrics"
        },
        {
            "id": "pending-approvals",
            "name": "Pending Approvals",
            "description": "Purchase orders awaiting approval",
            "type": "list",
            "size": "medium",
            "dataSource": "/api/v1/approvals/pending"
        },
        {
            "id": "spending-trend",
            "name": "Spending Trend",
            "description": "Monthly spending trend chart",
            "type": "chart",
            "size": "large",
            "dataSource": "/api/v1/dashboard/charts/spending-trend"
        },
        {
            "id": "top-suppliers",
            "name": "Top Suppliers",
            "description": "Suppliers by spend volume",
            "type": "list",
            "size": "medium",
            "dataSource": "/api/v1/dashboard/analytics/top-suppliers"
        },
        {
            "id": "recent-orders",
            "name": "Recent Orders",
            "description": "Latest purchase orders",
            "type": "list",
            "size": "medium",
            "dataSource": "/api/v1/dashboard/recent/orders"
        },
        {
            "id": "supplier-performance",
            "name": "Supplier Performance",
            "description": "Supplier rating distribution",
            "type": "chart",
            "size": "small",
            "dataSource": "/api/v1/dashboard/charts/supplier-distribution"
        }
    ],
    "lists": [
        {
            "id": "purchase-orders-list",
            "name": "Purchase Orders",
            "description": "Manage purchase orders",
            "icon": "file-text",
            "path": "/purchasing/orders",
            "dataSource": "/api/v1/purchase-orders",
            "columns": [
                {"key": "po_number", "label": "PO Number", "sortable": True},
                {"key": "supplier_name", "label": "Supplier", "sortable": True},
                {"key": "total_amount", "label": "Amount", "format": "currency"},
                {"key": "status", "label": "Status", "badge": True}
            ],
            "actions": ["view", "edit", "approve", "delete"],
            "filters": ["status", "supplier", "date_range"]
        },
        {
            "id": "suppliers-list",
            "name": "Suppliers",
            "description": "Manage suppliers",
            "icon": "truck",
            "path": "/purchasing/suppliers",
            "dataSource": "/api/v1/suppliers",
            "columns": [
                {"key": "name", "label": "Name", "sortable": True},
                {"key": "category", "label": "Category"},
                {"key": "performance_rating", "label": "Rating", "format": "rating"},
                {"key": "status", "label": "Status", "badge": True}
            ],
            "actions": ["view", "edit", "evaluate"],
            "filters": ["status", "category", "rating"]
        },
        {
            "id": "approvals-list",
            "name": "Approvals",
            "description": "Pending approval requests",
            "icon": "check-circle",
            "path": "/purchasing/approvals",
            "dataSource": "/api/v1/approvals/pending",
            "columns": [
                {"key": "po_number", "label": "PO Number"},
                {"key": "supplier_name", "label": "Supplier"},
                {"key": "total_amount", "label": "Amount", "format": "currency"},
                {"key": "urgency", "label": "Urgency", "badge": True}
            ],
            "actions": ["approve", "reject", "view"]
        }
    ],
    "forms": [
        {
            "id": "purchase-order-form",
            "name": "Purchase Order Form",
            "description": "Create or edit purchase orders",
            "icon": "file-plus",
            "path": "/purchasing/orders/new",
            "submitEndpoint": "/api/v1/purchase-orders",
            "sections": [
                {
                    "title": "Basic Information",
                    "fields": [
                        {"key": "supplier_id", "label": "Supplier", "type": "select", "required": True},
                        {"key": "order_date", "label": "Order Date", "type": "date", "required": True},
                        {"key": "expected_delivery", "label": "Expected Delivery", "type": "date"},
                        {"key": "payment_terms", "label": "Payment Terms", "type": "select"}
                    ]
                },
                {
                    "title": "Line Items",
                    "type": "array",
                    "key": "line_items",
                    "fields": [
                        {"key": "product_name", "label": "Product", "type": "text", "required": True},
                        {"key": "quantity", "label": "Quantity", "type": "number", "required": True},
                        {"key": "unit_price", "label": "Unit Price", "type": "currency", "required": True}
                    ]
                }
            ]
        },
        {
            "id": "supplier-form",
            "name": "Supplier Form",
            "description": "Create or edit suppliers",
            "icon": "truck",
            "path": "/purchasing/suppliers/new",
            "submitEndpoint": "/api/v1/suppliers",
            "sections": [
                {
                    "title": "Basic Information",
                    "fields": [
                        {"key": "name", "label": "Supplier Name", "type": "text", "required": True},
                        {"key": "code", "label": "Supplier Code", "type": "text"},
                        {"key": "category", "label": "Category", "type": "select"},
                        {"key": "tax_id", "label": "Tax ID", "type": "text"}
                    ]
                },
                {
                    "title": "Contact Information",
                    "fields": [
                        {"key": "contact_person", "label": "Contact Person", "type": "text"},
                        {"key": "email", "label": "Email", "type": "email"},
                        {"key": "phone", "label": "Phone", "type": "tel"},
                        {"key": "website", "label": "Website", "type": "url"}
                    ]
                },
                {
                    "title": "Address",
                    "fields": [
                        {"key": "address", "label": "Street Address", "type": "text"},
                        {"key": "city", "label": "City", "type": "text"},
                        {"key": "state", "label": "State/Province", "type": "text"},
                        {"key": "country", "label": "Country", "type": "select"},
                        {"key": "postal_code", "label": "Postal Code", "type": "text"}
                    ]
                }
            ]
        },
        {
            "id": "supplier-evaluation-form",
            "name": "Supplier Evaluation",
            "description": "Evaluate supplier performance",
            "icon": "star",
            "path": "/purchasing/suppliers/evaluate",
            "submitEndpoint": "/api/v1/suppliers/{id}/evaluate",
            "fields": [
                {"key": "delivery_rating", "label": "Delivery Performance", "type": "rating", "max": 5},
                {"key": "quality_rating", "label": "Product Quality", "type": "rating", "max": 5},
                {"key": "price_rating", "label": "Price Competitiveness", "type": "rating", "max": 5},
                {"key": "communication_rating", "label": "Communication", "type": "rating", "max": 5},
                {"key": "comments", "label": "Comments", "type": "textarea", "rows": 4}
            ]
        }
    ],
    "menus": [
        {
            "id": "purchasing",
            "label": "Purchasing",
            "icon": "shopping-cart",
            "path": "/purchasing",
            "children": [
                {
                    "id": "purchasing-dashboard",
                    "label": "Dashboard",
                    "icon": "dashboard",
                    "path": "/purchasing/dashboard"
                },
                {
                    "id": "purchase-orders",
                    "label": "Purchase Orders",
                    "icon": "file-text",
                    "path": "/purchasing/orders"
                },
                {
                    "id": "suppliers",
                    "label": "Suppliers",
                    "icon": "truck",
                    "path": "/purchasing/suppliers"
                },
                {
                    "id": "approvals",
                    "label": "Approvals",
                    "icon": "check-circle",
                    "path": "/purchasing/approvals"
                },
                {
                    "id": "reports",
                    "label": "Reports",
                    "icon": "bar-chart",
                    "path": "/purchasing/reports"
                }
            ]
        }
    ]
}