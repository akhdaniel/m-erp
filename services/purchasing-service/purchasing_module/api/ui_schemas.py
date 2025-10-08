"""
UI Schema endpoints for purchasing module.

Provides UI component schemas for dynamic UI rendering.
"""

from fastapi import APIRouter
from typing import Dict, Any
from purchasing_module.ui_definitions import PURCHASING_UI_PACKAGE

router = APIRouter(tags=["ui-schemas"])


# New endpoint patterns that match what the frontend expects
@router.get("/ui-schemas/lists/purchase-orders")
async def get_purchase_orders_list_schema_v2():
    """Get list view schema for purchase orders (frontend compatible)."""
    # Find the purchase orders list in the UI definitions
    for list_def in PURCHASING_UI_PACKAGE.get("lists", []):
        if list_def["id"] == "purchase-orders-list":
            # Convert from UI definition format to schema format
            return {
                "id": list_def["id"],
                "title": list_def["title"],
                "endpoint": list_def["data_endpoint"],  # Frontend expects 'endpoint'
                "columns": list_def["columns"],
                "filters": list_def.get("filters", []),
                "actions": list_def.get("actions", []),
                "pagination": list_def.get("pagination", True),
                "pageSize": list_def.get("pageSize", 20),
                "createRoute": "/purchasing/orders/new",  # Enable New button
                "editRoute": "/purchasing/orders/{id}/edit",  # Enable row click edit
                "viewType": "table",
                "createLabel": "New Purchase Order"
            }
    # Fallback to the existing static schema if not found
    return await get_purchase_orders_list_schema()


@router.get("/ui-schemas/forms/purchase-order")
async def get_purchase_order_form_schema_v2():
    """Get form schema for purchase order (frontend compatible)."""
    # Always return the proper form structure with LineItemsManager
    return {
        "id": "purchase-order-form",
        "title": "New Purchase Order",
        "endpoint": "/api/v1/purchase-orders/",
        "method": "POST",
        "successRoute": "/purchasing/orders",
        "cancelRoute": "/purchasing/orders",
        "sections": [
            {
                "title": "Basic Information",
                "fields": [
                    {"key": "supplier_id", "label": "Supplier", "type": "select", "required": True, "dataSource": "/api/v1/suppliers"},
                    {"key": "supplier_name", "label": "Supplier Name", "type": "text", "required": True},
                    {"key": "order_date", "label": "Order Date", "type": "date", "required": True, "default": "today"},
                    {"key": "expected_delivery", "label": "Expected Delivery", "type": "date"},
                    {"key": "currency_code", "label": "Currency", "type": "select", "options": ["USD", "EUR", "GBP"], "default": "USD"},
                    {"key": "payment_terms", "label": "Payment Terms", "type": "select", "options": ["Net 30", "Net 60", "COD", "Prepaid"], "default": "Net 30"}
                ]
            },
            {
                "title": "Line Items",
                "type": "line_items",
                "key": "items",
                "component": "LineItemsManager",
                "config": {
                    "title": "Purchase Order Items",
                    "entityType": "purchase order",
                    "productApiUrl": "http://localhost:9080/api/v1/products",
                    "taxRate": 10
                }
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


@router.get("/ui-schemas/lists/suppliers")
async def get_suppliers_list_schema_v2():
    """Get list view schema for suppliers (frontend compatible)."""
    # Find the suppliers list in the UI definitions
    for list_def in PURCHASING_UI_PACKAGE.get("lists", []):
        if list_def["id"] == "suppliers-list":
            # Convert from UI definition format to schema format
            return {
                "id": list_def["id"],
                "title": list_def["title"],
                "endpoint": list_def["data_endpoint"],  # Frontend expects 'endpoint'
                "columns": list_def["columns"],
                "filters": list_def.get("filters", []),
                "actions": list_def.get("actions", []),
                "pagination": list_def.get("pagination", True),
                "pageSize": list_def.get("pageSize", 20),
                "createRoute": "/purchasing/suppliers/new",  # Enable New button
                "editRoute": "/purchasing/suppliers/{id}/edit",  # Enable row click edit
                "viewType": "table",
                "createLabel": "New Supplier"
            }
    # Fallback to the existing static schema if not found
    return await get_suppliers_list_schema()


@router.get("/ui-schemas/forms/supplier")
async def get_supplier_form_schema():
    """Get form schema for supplier creation/editing."""
    # Always return the properly structured form schema
    return {
        "id": "supplier-form",
        "title": "New Supplier",
        "endpoint": "/api/v1/suppliers/",
        "method": "POST",
        "successRoute": "/purchasing/suppliers",
        "cancelRoute": "/purchasing/suppliers",
        "sections": [
            {
                "title": "Basic Information",
                "fields": [
                    {"name": "code", "label": "Supplier Code", "type": "text", "required": True, "placeholder": "e.g., SUP001"},
                    {"name": "name", "label": "Supplier Name", "type": "text", "required": True, "placeholder": "Enter supplier company name"},
                    {"name": "category", "label": "Category", "type": "select", "options": [
                        {"value": "general", "label": "General"},
                        {"value": "preferred", "label": "Preferred"},
                        {"value": "strategic", "label": "Strategic"}
                    ], "defaultValue": "general"},
                    {"name": "is_active", "label": "Active", "type": "checkbox", "defaultValue": True}
                ]
            },
            {
                "title": "Contact Information",
                "fields": [
                    {"name": "contact_person", "label": "Contact Person", "type": "text", "placeholder": "Primary contact name"},
                    {"name": "email", "label": "Email", "type": "email", "placeholder": "supplier@example.com"},
                    {"name": "phone", "label": "Phone", "type": "tel", "placeholder": "+1-555-0100"},
                    {"name": "website", "label": "Website", "type": "url", "placeholder": "https://www.supplier.com"}
                ]
            },
            {
                "title": "Address",
                "fields": [
                    {"name": "address", "label": "Street Address", "type": "text", "placeholder": "123 Main Street"},
                    {"name": "city", "label": "City", "type": "text", "placeholder": "New York"},
                    {"name": "state", "label": "State/Province", "type": "text", "placeholder": "NY"},
                    {"name": "postal_code", "label": "Postal Code", "type": "text", "placeholder": "10001"},
                    {"name": "country", "label": "Country", "type": "text", "placeholder": "USA", "defaultValue": "USA"}
                ]
            },
            {
                "title": "Business Terms",
                "fields": [
                    {"name": "payment_terms_days", "label": "Payment Terms (Days)", "type": "number", "min": 0, "max": 365, "defaultValue": 30, "placeholder": "30"},
                    {"name": "currency_code", "label": "Currency", "type": "select", "options": [
                        {"value": "USD", "label": "USD"},
                        {"value": "EUR", "label": "EUR"},
                        {"value": "GBP", "label": "GBP"}
                    ], "defaultValue": "USD"},
                    {"name": "tax_id", "label": "Tax ID", "type": "text", "placeholder": "Tax identification number"},
                    {"name": "rating", "label": "Initial Rating", "type": "number", "min": 1, "max": 5, "step": 0.5, "defaultValue": 3.0}
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
    # Find the approvals list in the UI definitions
    for list_def in PURCHASING_UI_PACKAGE.get("lists", []):
        if list_def["id"] == "approvals-list":
            # Convert from UI definition format to schema format
            return {
                "id": list_def["id"],
                "title": list_def["title"],
                "endpoint": list_def["data_endpoint"],  # Frontend expects 'endpoint'
                "columns": list_def["columns"],
                "filters": list_def.get("filters", []),
                "actions": list_def.get("actions", []),
                "pagination": list_def.get("pagination", True),
                "pageSize": list_def.get("pageSize", 20)
            }
    # Fallback to static schema if not found
    return {
        "id": "approvals-list",
        "title": "Purchase Approvals",
        "endpoint": "/api/v1/approvals/pending",
        "dataSource": "/api/v1/approvals/pending",
        "columns": [
            {"field": "po_number", "label": "PO Number", "sortable": True},
            {"field": "supplier_name", "label": "Supplier"},
            {"field": "amount", "label": "Amount", "formatter": "currency"},
            {"field": "requested_by", "label": "Requested By"},
            {"field": "request_date", "label": "Request Date", "formatter": "date"},
            {"field": "status", "label": "Status", "badge": True}
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
    # Use the dashboard definition from UI definitions
    dashboard = PURCHASING_UI_PACKAGE.get("dashboard", {})
    widgets = PURCHASING_UI_PACKAGE.get("widgets", [])
    
    # Convert widgets to dashboard schema format matching Sales/Inventory convention
    widget_configs = []
    
    # If we have a "metrics" widget, expand it into individual metric widgets
    for widget in widgets:
        if widget["type"] == "metric" and "metrics" in widget["id"]:
            # Create individual metric widgets like Sales/Inventory do
            metrics_endpoint = widget["data_endpoint"]
            
            # Total Orders metric
            widget_configs.append({
                "id": "total_orders_metric",
                "type": "metric",
                "title": "Total Orders",
                "endpoint": metrics_endpoint,
                "valueField": "total_orders",
                "format": "number",
                "icon": "file-text",
                "color": "blue",
                "span": 1
            })
            
            # Pending Approval metric
            widget_configs.append({
                "id": "pending_approval_metric",
                "type": "metric",
                "title": "Pending Approval",
                "endpoint": metrics_endpoint,
                "valueField": "pending_approval",
                "format": "number",
                "icon": "clock",
                "color": "orange",
                "span": 1
            })
            
            # Active Suppliers metric
            widget_configs.append({
                "id": "active_suppliers_metric",
                "type": "metric",
                "title": "Active Suppliers",
                "endpoint": metrics_endpoint,
                "valueField": "active_suppliers",
                "format": "number",
                "icon": "truck",
                "color": "green",
                "span": 1
            })
            
            # Month Spend metric
            widget_configs.append({
                "id": "month_spend_metric",
                "type": "metric",
                "title": "Month Spend",
                "endpoint": metrics_endpoint,
                "valueField": "month_spend",
                "format": "currency",
                "icon": "dollar-sign",
                "color": "green",
                "span": 1
            })
        else:
            # For other widgets, process normally
            widget_config = {
                "id": widget["id"],
                "type": widget["type"],
                "title": widget["title"],
                "endpoint": widget["data_endpoint"],
                "span": 1
            }
            
            if widget["type"] == "list":
                widget_config["limit"] = 5
                if "recent-orders" in widget["id"]:
                    widget_config["columns"] = [
                        {"field": "po_number", "label": "PO #"},
                        {"field": "supplier", "label": "Supplier"},
                        {"field": "amount", "label": "Amount", "formatter": "currency"}
                    ]
                elif "top-suppliers" in widget["id"]:
                    widget_config["columns"] = [
                        {"field": "name", "label": "Supplier"},
                        {"field": "spend", "label": "Spend", "formatter": "currency"},
                        {"field": "rating", "label": "Rating"}
                    ]
            
            elif widget["type"] == "chart":
                widget_config["chartType"] = "line" if "trend" in widget["id"] else "bar"
                widget_config["height"] = 300
            
            # Set span based on widget size (following Sales/Inventory pattern)
            size = widget.get("size", "medium")
            if size == "large":
                widget_config["span"] = 2
            elif size == "small":
                widget_config["span"] = 1
            else:  # medium
                widget_config["span"] = 1
            
            widget_configs.append(widget_config)
    
    return {
        "title": dashboard.get("title", "Purchasing Dashboard"),
        "description": dashboard.get("description", "Overview of purchasing operations"),
        "breadcrumbs": [
            {"label": "Home", "route": "/"},
            {"label": "Purchasing", "route": "/purchasing/dashboard"}
        ],
        "viewType": "dashboard",
        "refreshInterval": 30000,  # 30 seconds
        "layout": {
            "columns": 3,
            "rows": "auto"
        },
        "widgets": widget_configs
    }


@router.get("/ui-schemas/purchase-orders-list")
async def get_purchase_orders_list_schema():
    """Get list view schema for purchase orders."""
    # Find the purchase orders list in the UI definitions
    for list_def in PURCHASING_UI_PACKAGE.get("lists", []):
        if list_def["id"] == "purchase-orders-list":
            # Convert from UI definition format to schema format
            return {
                "id": list_def["id"],
                "title": list_def["title"],
                "endpoint": list_def["data_endpoint"],  # Frontend expects 'endpoint'
                "dataSource": list_def["data_endpoint"],  # Keep both for compatibility
                "columns": list_def["columns"],
                "filters": list_def.get("filters", []),
                "actions": list_def.get("actions", []),
                "bulkActions": list_def.get("bulkActions", []),
                "pagination": list_def.get("pagination", True),
                "pageSize": list_def.get("pageSize", 20),
                "createRoute": "/purchasing/orders/new",  # Enable New button
                "editRoute": "/purchasing/orders/{id}/edit",  # Enable row click edit
                "viewType": "table",
                "createLabel": "New Purchase Order"
            }
    # Fallback to static schema if not found
    return {
        "id": "purchase-orders-list",
        "title": "Purchase Orders",
        "endpoint": "/api/v1/purchase-orders/",
        "dataSource": "/api/v1/purchase-orders/",
        "columns": [
            {"field": "po_number", "label": "PO Number", "sortable": True, "searchable": True},
            {"field": "supplier_name", "label": "Supplier", "sortable": True, "searchable": True},
            {"field": "order_date", "label": "Order Date", "sortable": True, "formatter": "date"},
            {"field": "total_amount", "label": "Amount", "sortable": True, "formatter": "currency"},
            {"field": "status", "label": "Status", "badge": True},
            {"field": "approval_status", "label": "Approval", "badge": True}
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
        "pageSize": 20,
        "createRoute": "/purchasing/orders/new",  # Enable New button
        "editRoute": "/purchasing/orders/{id}/edit",  # Enable row click edit
        "viewType": "table",
        "createLabel": "New Purchase Order"
    }


@router.get("/ui-schemas/purchase-order-form")
async def get_purchase_order_form_schema():
    """Get form schema for purchase order creation/editing."""
    # Find the purchase order form in the UI definitions
    for form_def in PURCHASING_UI_PACKAGE.get("forms", []):
        if form_def["id"] == "purchase-order-form":
            # Convert from UI definition format to schema format with proper sections
            return {
                "id": form_def["id"],
                "title": form_def["title"],
                "endpoint": "/api/v1/purchase-orders/",  # API endpoint for form submission
                "method": "POST",
                "successRoute": "/purchasing/orders",  # Navigate to list after successful submission
                "cancelRoute": "/purchasing/orders",  # Navigate to list on cancel
                "sections": [
                    {
                        "title": "Basic Information",
                        "fields": form_def.get("fields", [])[:5]  # First 5 fields
                    },
                    {
                        "title": "Line Items",
                        "type": "line_items",  # Special type for LineItemsManager component
                        "key": "items",  # Use 'items' as the key name for the API
                        "component": "LineItemsManager",
                        "config": {
                            "title": "Purchase Order Items",
                            "entityType": "purchase order",
                            "productApiUrl": "http://localhost:9080/api/v1/products",
                            "taxRate": 10  # Default tax rate
                        }
                    }
                ],
                "actions": [
                    {"label": "Save as Draft", "action": "save_draft", "type": "secondary"},
                    {"label": "Submit for Approval", "action": "submit", "type": "primary"}
                ]
            }
    # Fallback to static schema if not found
    return {
        "id": "purchase-order-form",
        "title": "Purchase Order",
        "endpoint": "/api/v1/purchase-orders/",
        "method": "POST",
        "successRoute": "/purchasing/orders",
        "cancelRoute": "/purchasing/orders",
        "sections": [
            {
                "title": "Basic Information",
                "fields": [
                    {"key": "supplier_id", "label": "Supplier", "type": "select", "required": True, "dataSource": "/api/v1/suppliers"},
                    {"key": "supplier_name", "label": "Supplier Name", "type": "text", "required": True},
                    {"key": "order_date", "label": "Order Date", "type": "date", "required": True, "default": "today"},
                    {"key": "expected_delivery", "label": "Expected Delivery", "type": "date"},
                    {"key": "currency_code", "label": "Currency", "type": "select", "options": ["USD", "EUR", "GBP"], "default": "USD"},
                    {"key": "payment_terms", "label": "Payment Terms", "type": "select", "options": ["Net 30", "Net 60", "COD", "Prepaid"], "default": "Net 30"}
                ]
            },
            {
                "title": "Line Items",
                "type": "line_items",
                "key": "items",
                "component": "LineItemsManager",
                "config": {
                    "title": "Purchase Order Items",
                    "entityType": "purchase order",
                    "productApiUrl": "http://localhost:9080/api/v1/products",
                    "taxRate": 10
                }
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
    # Find the suppliers list in the UI definitions
    for list_def in PURCHASING_UI_PACKAGE.get("lists", []):
        if list_def["id"] == "suppliers-list":
            # Convert from UI definition format to schema format
            return {
                "id": list_def["id"],
                "title": list_def["title"],
                "endpoint": list_def["data_endpoint"],  # Frontend expects 'endpoint'
                "dataSource": list_def["data_endpoint"],  # Keep both for compatibility
                "columns": list_def["columns"],
                "filters": list_def.get("filters", []),
                "actions": list_def.get("actions", []),
                "pagination": list_def.get("pagination", True),
                "pageSize": list_def.get("pageSize", 20)
            }
    # Fallback to static schema if not found
    return {
        "id": "suppliers-list",
        "title": "Suppliers",
        "endpoint": "/api/v1/suppliers/",
        "dataSource": "/api/v1/suppliers/",
        "columns": [
            {"field": "code", "label": "Code", "sortable": True, "searchable": True},
            {"field": "name", "label": "Name", "sortable": True, "searchable": True},
            {"field": "category", "label": "Category", "sortable": True},
            {"field": "performance_rating", "label": "Rating", "formatter": "rating"},
            {"field": "total_orders", "label": "Orders", "formatter": "number"},
            {"field": "total_spend", "label": "Total Spend", "formatter": "currency"},
            {"field": "status", "label": "Status", "badge": True}
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
        "pageSize": 20,
        "createRoute": "/purchasing/suppliers/new",
        "editRoute": "/purchasing/suppliers/{id}/edit",
        "viewType": "table",
        "createLabel": "New Supplier"
    }