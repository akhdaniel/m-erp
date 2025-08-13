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
            "title": "Purchasing Metrics",
            "description": "Key purchasing KPIs",
            "type": "metrics",
            "size": "large",
            "data_endpoint": "/api/v1/dashboard/metrics",
            "refresh_interval": 60
        },
        {
            "id": "pending-approvals",
            "title": "Pending Approvals",
            "description": "Purchase orders awaiting approval",
            "type": "list",
            "size": "medium",
            "data_endpoint": "/api/v1/approvals/pending",
            "refresh_interval": 30
        },
        {
            "id": "spending-trend",
            "title": "Spending Trend",
            "description": "Monthly spending trend chart",
            "type": "chart",
            "size": "large",
            "data_endpoint": "/api/v1/dashboard/charts/spending-trend",
            "refresh_interval": 300
        },
        {
            "id": "top-suppliers",
            "title": "Top Suppliers",
            "description": "Suppliers by spend volume",
            "type": "list",
            "size": "medium",
            "data_endpoint": "/api/v1/dashboard/analytics/top-suppliers",
            "refresh_interval": 300
        },
        {
            "id": "recent-orders",
            "title": "Recent Orders",
            "description": "Latest purchase orders",
            "type": "list",
            "size": "medium",
            "data_endpoint": "/api/v1/dashboard/recent/orders",
            "refresh_interval": 60
        },
        {
            "id": "supplier-performance",
            "title": "Supplier Performance",
            "description": "Supplier rating distribution",
            "type": "chart",
            "size": "small",
            "data_endpoint": "/api/v1/dashboard/charts/supplier-distribution",
            "refresh_interval": 300
        }
    ],
    "lists": [
        {
            "id": "purchase-orders-list",
            "title": "Purchase Orders",
            "entity": "purchase-orders",
            "description": "Manage purchase orders",
            "icon": "file-text",
            "path": "/purchasing/orders",
            "data_endpoint": "/api/v1/purchase-orders/",
            "columns": [
                {"key": "po_number", "label": "PO Number", "sortable": True},
                {"key": "supplier_name", "label": "Supplier", "sortable": True},
                {"key": "total_amount", "label": "Amount", "format": "currency"},
                {"key": "status", "label": "Status", "badge": True}
            ],
            "actions": [
                {"type": "view", "label": "View"},
                {"type": "edit", "label": "Edit"},
                {"type": "approve", "label": "Approve"},
                {"type": "delete", "label": "Delete"}
            ],
            "filters": [
                {"key": "status", "type": "select", "label": "Status"},
                {"key": "supplier", "type": "select", "label": "Supplier"},
                {"key": "date_range", "type": "daterange", "label": "Date Range"}
            ],
            "pagination": True
        },
        {
            "id": "suppliers-list",
            "title": "Suppliers",
            "entity": "suppliers",
            "description": "Manage suppliers",
            "icon": "truck",
            "path": "/purchasing/suppliers",
            "data_endpoint": "/api/v1/suppliers/",
            "columns": [
                {"key": "name", "label": "Name", "sortable": True},
                {"key": "category", "label": "Category"},
                {"key": "performance_rating", "label": "Rating", "format": "rating"},
                {"key": "status", "label": "Status", "badge": True}
            ],
            "actions": [
                {"type": "view", "label": "View"},
                {"type": "edit", "label": "Edit"},
                {"type": "evaluate", "label": "Evaluate"}
            ],
            "filters": [
                {"key": "status", "type": "select", "label": "Status"},
                {"key": "category", "type": "select", "label": "Category"},
                {"key": "rating", "type": "range", "label": "Rating"}
            ],
            "pagination": True
        },
        {
            "id": "approvals-list",
            "title": "Approvals",
            "entity": "approvals",
            "description": "Pending approval requests",
            "icon": "check-circle",
            "path": "/purchasing/approvals",
            "data_endpoint": "/api/v1/approvals/pending/",
            "columns": [
                {"key": "po_number", "label": "PO Number"},
                {"key": "supplier_name", "label": "Supplier"},
                {"key": "total_amount", "label": "Amount", "format": "currency"},
                {"key": "urgency", "label": "Urgency", "badge": True}
            ],
            "actions": [
                {"type": "approve", "label": "Approve"},
                {"type": "reject", "label": "Reject"},
                {"type": "view", "label": "View"}
            ],
            "pagination": True
        }
    ],
    "forms": [
        {
            "id": "purchase-order-form",
            "title": "Purchase Order Form",
            "entity": "purchase-orders",
            "description": "Create or edit purchase orders",
            "icon": "file-plus",
            "path": "/purchasing/orders/new",
            "submit_endpoint": "/api/v1/purchase-orders",
            "mode": "create",
            "layout": "single",
            "fields": [
                {"key": "supplier_id", "label": "Supplier", "type": "select", "required": True},
                {"key": "order_date", "label": "Order Date", "type": "date", "required": True},
                {"key": "expected_delivery", "label": "Expected Delivery", "type": "date"},
                {"key": "payment_terms", "label": "Payment Terms", "type": "select"},
                {"key": "line_items", "label": "Line Items", "type": "array", "required": True}
            ]
        },
        {
            "id": "supplier-form",
            "title": "Supplier Form",
            "entity": "suppliers",
            "description": "Create or edit suppliers",
            "icon": "truck",
            "path": "/purchasing/suppliers/new",
            "submit_endpoint": "/api/v1/suppliers",
            "mode": "create",
            "layout": "single",
            "fields": [
                {"key": "name", "label": "Supplier Name", "type": "text", "required": True},
                {"key": "code", "label": "Supplier Code", "type": "text"},
                {"key": "category", "label": "Category", "type": "select"},
                {"key": "tax_id", "label": "Tax ID", "type": "text"},
                {"key": "contact_person", "label": "Contact Person", "type": "text"},
                {"key": "email", "label": "Email", "type": "email"},
                {"key": "phone", "label": "Phone", "type": "tel"},
                {"key": "website", "label": "Website", "type": "url"},
                {"key": "address", "label": "Street Address", "type": "text"},
                {"key": "city", "label": "City", "type": "text"},
                {"key": "state", "label": "State/Province", "type": "text"},
                {"key": "country", "label": "Country", "type": "select"},
                {"key": "postal_code", "label": "Postal Code", "type": "text"}
            ]
        },
        {
            "id": "supplier-evaluation-form",
            "title": "Supplier Evaluation",
            "entity": "supplier-evaluation",
            "description": "Evaluate supplier performance",
            "icon": "star",
            "path": "/purchasing/suppliers/evaluate",
            "submit_endpoint": "/api/v1/suppliers/{id}/evaluate",
            "mode": "create",
            "layout": "single",
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