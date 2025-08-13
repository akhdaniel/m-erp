"""
UI Schema endpoints for purchasing module.

Provides UI component schemas for dynamic UI rendering.
"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(tags=["ui-schemas"])


# New endpoint patterns that match what the frontend expects
@router.get("/ui-schemas/lists/purchase-orders")
async def get_purchase_orders_list_schema_v2():
    """Get list view schema for purchase orders (frontend compatible)."""
    return await get_purchase_orders_list_schema()


@router.get("/ui-schemas/forms/purchase-order")
async def get_purchase_order_form_schema_v2():
    """Get form schema for purchase order (frontend compatible)."""
    return await get_purchase_order_form_schema()


@router.get("/ui-schemas/lists/suppliers")
async def get_suppliers_list_schema_v2():
    """Get list view schema for suppliers (frontend compatible)."""
    return await get_suppliers_list_schema()


@router.get("/ui-schemas/forms/supplier")
async def get_supplier_form_schema():
    """Get form schema for supplier creation/editing."""
    return {
        "id": "supplier-form",
        "title": "Supplier",
        "sections": [
            {
                "title": "Basic Information",
                "fields": [
                    {"key": "code", "label": "Supplier Code", "type": "text", "required": True},
                    {"key": "name", "label": "Supplier Name", "type": "text", "required": True},
                    {"key": "category", "label": "Category", "type": "select", "options": ["general", "preferred", "strategic"], "default": "general"},
                    {"key": "status", "label": "Status", "type": "select", "options": ["active", "inactive", "suspended"], "default": "active"}
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
                    {"key": "address_line1", "label": "Address Line 1", "type": "text"},
                    {"key": "address_line2", "label": "Address Line 2", "type": "text"},
                    {"key": "city", "label": "City", "type": "text"},
                    {"key": "state", "label": "State/Province", "type": "text"},
                    {"key": "postal_code", "label": "Postal Code", "type": "text"},
                    {"key": "country", "label": "Country", "type": "text"}
                ]
            },
            {
                "title": "Business Terms",
                "fields": [
                    {"key": "payment_terms", "label": "Payment Terms", "type": "select", "options": ["Net 30", "Net 60", "Net 90", "COD", "Prepaid"], "default": "Net 30"},
                    {"key": "currency_code", "label": "Currency", "type": "select", "options": ["USD", "EUR", "GBP"], "default": "USD"},
                    {"key": "tax_id", "label": "Tax ID", "type": "text"},
                    {"key": "bank_account", "label": "Bank Account", "type": "text"}
                ]
            }
        ],
        "actions": [
            {"label": "Save", "action": "save", "type": "primary"},
            {"label": "Cancel", "action": "cancel", "type": "secondary"}
        ]
    }


@router.get("/ui-schemas/lists/approvals")
async def get_approvals_list_schema():
    """Get list view schema for purchase approvals."""
    return {
        "id": "approvals-list",
        "title": "Purchase Approvals",
        "endpoint": "/api/v1/approvals/pending",
        "dataSource": "/api/v1/approvals/pending",
        "columns": [
            {"key": "po_number", "label": "PO Number", "sortable": True},
            {"key": "supplier_name", "label": "Supplier"},
            {"key": "amount", "label": "Amount", "format": "currency"},
            {"key": "requested_by", "label": "Requested By"},
            {"key": "request_date", "label": "Request Date", "format": "date"},
            {"key": "status", "label": "Status", "badge": True}
        ],
        "filters": [
            {"key": "status", "label": "Status", "type": "select", "options": ["pending", "approved", "rejected"]},
            {"key": "amount_min", "label": "Min Amount", "type": "number"},
            {"key": "amount_max", "label": "Max Amount", "type": "number"}
        ],
        "actions": [
            {"label": "View", "action": "view", "icon": "eye"},
            {"label": "Approve", "action": "approve", "icon": "check", "color": "success", "condition": {"status": ["pending"]}},
            {"label": "Reject", "action": "reject", "icon": "x", "color": "danger", "condition": {"status": ["pending"]}}
        ],
        "pagination": True,
        "pageSize": 20
    }


@router.get("/ui-schemas/views/reports")
async def get_reports_view_schema():
    """Get view schema for purchasing reports."""
    return {
        "id": "purchasing-reports",
        "title": "Purchasing Reports",
        "type": "reports-dashboard",
        "sections": [
            {
                "title": "Standard Reports",
                "reports": [
                    {"id": "spend-analysis", "title": "Spend Analysis", "description": "Analyze spending patterns by category, supplier, and time period", "icon": "bar-chart"},
                    {"id": "supplier-performance", "title": "Supplier Performance", "description": "Evaluate supplier delivery, quality, and pricing performance", "icon": "star"},
                    {"id": "po-status", "title": "PO Status Report", "description": "Track purchase order status and approval workflows", "icon": "file-text"},
                    {"id": "budget-variance", "title": "Budget Variance", "description": "Compare actual spending against budgeted amounts", "icon": "dollar-sign"}
                ]
            },
            {
                "title": "Analytics",
                "reports": [
                    {"id": "trend-analysis", "title": "Trend Analysis", "description": "Identify spending trends over time", "icon": "trending-up"},
                    {"id": "category-breakdown", "title": "Category Breakdown", "description": "Detailed breakdown by purchase category", "icon": "pie-chart"},
                    {"id": "savings-opportunities", "title": "Savings Opportunities", "description": "Identify potential cost reduction areas", "icon": "target"}
                ]
            }
        ]
    }


@router.get("/ui-schemas/views/settings")
async def get_settings_view_schema():
    """Get view schema for purchasing settings."""
    return {
        "id": "purchasing-settings",
        "title": "Purchasing Settings",
        "type": "settings",
        "sections": [
            {
                "title": "General Settings",
                "fields": [
                    {"key": "default_payment_terms", "label": "Default Payment Terms", "type": "select", "options": ["Net 30", "Net 60", "COD"]},
                    {"key": "default_currency", "label": "Default Currency", "type": "select", "options": ["USD", "EUR", "GBP"]},
                    {"key": "po_number_prefix", "label": "PO Number Prefix", "type": "text", "placeholder": "PO-"},
                    {"key": "auto_approve_limit", "label": "Auto-Approve Limit", "type": "currency", "help": "Orders below this amount are auto-approved"}
                ]
            },
            {
                "title": "Approval Workflow",
                "fields": [
                    {"key": "enable_approvals", "label": "Enable Approval Workflow", "type": "toggle"},
                    {"key": "approval_levels", "label": "Approval Levels", "type": "array", "fields": [
                        {"key": "level", "label": "Level", "type": "number"},
                        {"key": "max_amount", "label": "Max Amount", "type": "currency"},
                        {"key": "approver_role", "label": "Approver Role", "type": "select", "dataSource": "/api/v1/roles"}
                    ]}
                ]
            },
            {
                "title": "Notifications",
                "fields": [
                    {"key": "notify_on_approval", "label": "Notify on Approval Required", "type": "toggle"},
                    {"key": "notify_on_delivery", "label": "Notify on Expected Delivery", "type": "toggle"},
                    {"key": "notify_on_budget_exceed", "label": "Notify on Budget Exceeded", "type": "toggle"}
                ]
            }
        ],
        "actions": [
            {"label": "Save Settings", "action": "save", "type": "primary"},
            {"label": "Reset to Defaults", "action": "reset", "type": "secondary"}
        ]
    }


@router.get("/ui-schemas/dashboard")
async def get_dashboard_schema():
    """Get dashboard configuration for purchasing module."""
    return {
        "id": "purchasing-dashboard",
        "title": "Purchasing Dashboard",
        "description": "Overview of purchasing operations",
        "layout": "grid",
        "refreshInterval": 30000,
        "widgets": [
            {
                "id": "purchasing-metrics",
                "type": "metrics",
                "title": "Key Metrics",
                "position": {"x": 0, "y": 0, "w": 12, "h": 2},
                "dataSource": "/api/v1/dashboard/metrics",
                "metrics": [
                    {"key": "total_orders", "label": "Total Orders", "format": "number", "icon": "file-text"},
                    {"key": "pending_approval", "label": "Pending Approval", "format": "number", "icon": "clock", "color": "warning"},
                    {"key": "active_suppliers", "label": "Active Suppliers", "format": "number", "icon": "truck"},
                    {"key": "month_spend", "label": "Month Spend", "format": "currency", "icon": "dollar-sign", "color": "success"}
                ]
            },
            {
                "id": "spending-trend",
                "type": "chart",
                "title": "Spending Trend",
                "position": {"x": 0, "y": 2, "w": 8, "h": 4},
                "dataSource": "/api/v1/dashboard/charts/spending-trend",
                "chartType": "line",
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False
                }
            },
            {
                "id": "supplier-distribution",
                "type": "chart",
                "title": "Supplier Distribution",
                "position": {"x": 8, "y": 2, "w": 4, "h": 4},
                "dataSource": "/api/v1/dashboard/charts/supplier-distribution",
                "chartType": "doughnut",
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False
                }
            },
            {
                "id": "recent-orders",
                "type": "list",
                "title": "Recent Purchase Orders",
                "position": {"x": 0, "y": 6, "w": 6, "h": 4},
                "dataSource": "/api/v1/dashboard/recent/orders",
                "columns": [
                    {"key": "po_number", "label": "PO Number", "sortable": True},
                    {"key": "supplier", "label": "Supplier"},
                    {"key": "amount", "label": "Amount", "format": "currency"},
                    {"key": "status", "label": "Status", "badge": True}
                ],
                "actions": [
                    {"label": "View", "action": "view", "icon": "eye"}
                ]
            },
            {
                "id": "top-suppliers",
                "type": "list",
                "title": "Top Suppliers",
                "position": {"x": 6, "y": 6, "w": 6, "h": 4},
                "dataSource": "/api/v1/dashboard/analytics/top-suppliers",
                "dataPath": "suppliers",
                "columns": [
                    {"key": "name", "label": "Supplier"},
                    {"key": "spend", "label": "Total Spend", "format": "currency"},
                    {"key": "orders", "label": "Orders", "format": "number"},
                    {"key": "rating", "label": "Rating", "format": "rating"}
                ]
            },
            {
                "id": "pending-approvals",
                "type": "metric-card",
                "title": "Pending Approvals",
                "position": {"x": 0, "y": 10, "w": 4, "h": 2},
                "dataSource": "/api/v1/dashboard/pending-approvals/summary",
                "display": {
                    "primaryMetric": "total_pending",
                    "primaryLabel": "Awaiting Approval",
                    "secondaryMetrics": [
                        {"key": "urgent", "label": "Urgent", "color": "danger"},
                        {"key": "total_value", "label": "Total Value", "format": "currency"}
                    ],
                    "icon": "alert-circle",
                    "color": "warning"
                }
            }
        ]
    }


@router.get("/ui-schemas/purchase-orders-list")
async def get_purchase_orders_list_schema():
    """Get list view schema for purchase orders."""
    return {
        "id": "purchase-orders-list",
        "title": "Purchase Orders",
        "endpoint": "/api/v1/purchase-orders/",
        "dataSource": "/api/v1/purchase-orders/",
        "columns": [
            {"key": "po_number", "label": "PO Number", "sortable": True, "searchable": True},
            {"key": "supplier_name", "label": "Supplier", "sortable": True, "searchable": True},
            {"key": "order_date", "label": "Order Date", "sortable": True, "format": "date"},
            {"key": "total_amount", "label": "Amount", "sortable": True, "format": "currency"},
            {"key": "status", "label": "Status", "badge": True},
            {"key": "approval_status", "label": "Approval", "badge": True}
        ],
        "filters": [
            {"key": "status", "label": "Status", "type": "select", "options": ["draft", "approved", "pending", "completed", "cancelled"]},
            {"key": "supplier_id", "label": "Supplier", "type": "select", "dataSource": "/api/v1/suppliers"},
            {"key": "from_date", "label": "From Date", "type": "date"},
            {"key": "to_date", "label": "To Date", "type": "date"}
        ],
        "actions": [
            {"label": "View", "action": "view", "icon": "eye"},
            {"label": "Edit", "action": "edit", "icon": "edit", "condition": {"status": ["draft"]}},
            {"label": "Approve", "action": "approve", "icon": "check", "condition": {"approval_status": ["requires_approval"]}},
            {"label": "Delete", "action": "delete", "icon": "trash", "condition": {"status": ["draft"]}}
        ],
        "bulkActions": [
            {"label": "Export", "action": "export", "icon": "download"}
        ],
        "pagination": True,
        "pageSize": 20
    }


@router.get("/ui-schemas/purchase-order-form")
async def get_purchase_order_form_schema():
    """Get form schema for purchase order creation/editing."""
    return {
        "id": "purchase-order-form",
        "title": "Purchase Order",
        "sections": [
            {
                "title": "Basic Information",
                "fields": [
                    {"key": "supplier_id", "label": "Supplier", "type": "select", "required": True, "dataSource": "/api/v1/suppliers"},
                    {"key": "order_date", "label": "Order Date", "type": "date", "required": True, "default": "today"},
                    {"key": "expected_delivery", "label": "Expected Delivery", "type": "date"},
                    {"key": "currency_code", "label": "Currency", "type": "select", "options": ["USD", "EUR", "GBP"], "default": "USD"},
                    {"key": "payment_terms", "label": "Payment Terms", "type": "select", "options": ["Net 30", "Net 60", "COD", "Prepaid"], "default": "Net 30"}
                ]
            },
            {
                "title": "Line Items",
                "type": "array",
                "key": "line_items",
                "fields": [
                    {"key": "product_id", "label": "Product", "type": "select", "dataSource": "/api/v1/products"},
                    {"key": "product_name", "label": "Product Name", "type": "text", "required": True},
                    {"key": "quantity", "label": "Quantity", "type": "number", "required": True, "min": 1},
                    {"key": "unit_price", "label": "Unit Price", "type": "currency", "required": True},
                    {"key": "discount_percentage", "label": "Discount %", "type": "number", "min": 0, "max": 100, "default": 0},
                    {"key": "tax_rate", "label": "Tax %", "type": "number", "min": 0, "default": 0}
                ]
            },
            {
                "title": "Addresses",
                "fields": [
                    {"key": "shipping_address", "label": "Shipping Address", "type": "textarea", "rows": 3},
                    {"key": "billing_address", "label": "Billing Address", "type": "textarea", "rows": 3}
                ]
            },
            {
                "title": "Additional Information",
                "fields": [
                    {"key": "notes", "label": "Notes", "type": "textarea", "rows": 4}
                ]
            }
        ],
        "actions": [
            {"label": "Save as Draft", "action": "save_draft", "type": "secondary"},
            {"label": "Submit for Approval", "action": "submit", "type": "primary"}
        ]
    }


@router.get("/ui-schemas/suppliers-list")
async def get_suppliers_list_schema():
    """Get list view schema for suppliers."""
    return {
        "id": "suppliers-list",
        "title": "Suppliers",
        "endpoint": "/api/v1/suppliers/",
        "dataSource": "/api/v1/suppliers/",
        "columns": [
            {"key": "code", "label": "Code", "sortable": True, "searchable": True},
            {"key": "name", "label": "Name", "sortable": True, "searchable": True},
            {"key": "category", "label": "Category", "sortable": True},
            {"key": "performance_rating", "label": "Rating", "format": "rating"},
            {"key": "total_orders", "label": "Orders", "format": "number"},
            {"key": "total_spend", "label": "Total Spend", "format": "currency"},
            {"key": "status", "label": "Status", "badge": True}
        ],
        "filters": [
            {"key": "status", "label": "Status", "type": "select", "options": ["active", "inactive", "suspended"]},
            {"key": "category", "label": "Category", "type": "select", "options": ["general", "preferred", "strategic"]},
            {"key": "min_rating", "label": "Min Rating", "type": "number", "min": 1, "max": 5}
        ],
        "actions": [
            {"label": "View", "action": "view", "icon": "eye"},
            {"label": "Edit", "action": "edit", "icon": "edit"},
            {"label": "Evaluate", "action": "evaluate", "icon": "star"},
            {"label": "Deactivate", "action": "deactivate", "icon": "x-circle", "condition": {"status": ["active"]}}
        ],
        "pagination": True,
        "pageSize": 20
    }