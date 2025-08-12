"""
UI Schema endpoints for purchasing module.

Provides UI component schemas for dynamic UI rendering.
"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(tags=["ui-schemas"])


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
        "dataSource": "/api/v1/purchase-orders",
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
        "dataSource": "/api/v1/suppliers",
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