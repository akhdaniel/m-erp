"""
UI Schema definitions for Sales Service
Provides JSON schemas for dynamic UI rendering
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["UI Schemas"])

# Dashboard Schema
@router.get("/dashboard/ui-schemas")
async def get_dashboard_schema() -> Dict[str, Any]:
    """Get dashboard UI schema"""
    return {
        "title": "Sales Dashboard",
        "description": "Sales performance overview and key metrics",
        "viewType": "dashboard",
        "refreshInterval": 30000,  # 30 seconds
        "layout": {
            "columns": 3,
            "rows": "auto"
        },
        "widgets": [
            {
                "id": "revenue_metric",
                "type": "metric",
                "title": "Monthly Revenue",
                "endpoint": "/dashboard/metrics/revenue",
                "format": "currency",
                "icon": "dollar-sign",
                "color": "green",
                "span": 1
            },
            {
                "id": "quotations_metric",
                "type": "metric",
                "title": "Active Quotations",
                "endpoint": "/dashboard/metrics/quotations",
                "format": "number",
                "icon": "file-text",
                "color": "blue",
                "span": 1
            },
            {
                "id": "orders_metric",
                "type": "metric",
                "title": "Pending Orders",
                "endpoint": "/dashboard/metrics/orders",
                "format": "number",
                "icon": "shopping-bag",
                "color": "orange",
                "span": 1
            },
            {
                "id": "revenue_chart",
                "type": "chart",
                "title": "Revenue Trend",
                "endpoint": "/dashboard/charts/revenue-trend",
                "chartType": "line",
                "span": 2,
                "height": 300
            },
            {
                "id": "pipeline_chart",
                "type": "chart",
                "title": "Sales Pipeline",
                "endpoint": "/dashboard/charts/sales-pipeline",
                "chartType": "bar",
                "span": 1,
                "height": 300
            },
            {
                "id": "recent_quotations",
                "type": "list",
                "title": "Recent Quotations",
                "endpoint": "/dashboard/recent/quotations",
                "limit": 5,
                "span": 1,
                "columns": [
                    {"field": "quotation_number", "label": "Quotation #"},
                    {"field": "customer_name", "label": "Customer"},
                    {"field": "total_amount", "label": "Amount", "formatter": "currency"}
                ]
            },
            {
                "id": "recent_orders",
                "type": "list",
                "title": "Recent Orders",
                "endpoint": "/dashboard/recent/orders",
                "limit": 5,
                "span": 1,
                "columns": [
                    {"field": "order_number", "label": "Order #"},
                    {"field": "customer_name", "label": "Customer"},
                    {"field": "status", "label": "Status"}
                ]
            },
            {
                "id": "top_customers",
                "type": "table",
                "title": "Top Customers",
                "endpoint": "/dashboard/analytics/top-customers",
                "limit": 5,
                "span": 1,
                "columns": [
                    {"field": "name", "label": "Customer"},
                    {"field": "revenue", "label": "Revenue", "formatter": "currency"},
                    {"field": "orders", "label": "Orders", "formatter": "number"}
                ]
            }
        ]
    }


# Quotations List Schema
@router.get("/quotations/ui-schemas/list")
async def get_quotations_list_schema() -> Dict[str, Any]:
    """Get quotations list UI schema"""
    return {
        "title": "Sales Quotations",
        "description": "Manage customer quotations",
        "viewType": "table",
        "endpoint": "/sales/quotations",
        # "dataPath": "/sales/quotations",  # Tell the UI where to find the data in the response
        "searchable": True,
        "searchPlaceholder": "Search quotations...",
        "searchParam": "search",
        "paginated": True,
        "pageSize": 20,
        "columns": [
            {
                "field": "quotation_number",
                "label": "Quotation Number",
                "isTitle": True,
                "sortable": True
            },
            {
                "field": "customer_name",
                "label": "Customer",
                "sortable": True
            },
            {
                "field": "quotation_date",
                "label": "Date",
                "formatter": "date",
                "sortable": True
            },
            {
                "field": "valid_until",
                "label": "Valid Until",
                "formatter": "date",
                "cellClassFunction": """
                    function(value) {
                        const date = new Date(value);
                        const today = new Date();
                        if (date < today) return 'text-red-600';
                        const daysLeft = Math.ceil((date - today) / (1000 * 60 * 60 * 24));
                        if (daysLeft <= 7) return 'text-yellow-600';
                        return 'text-green-600';
                    }
                """
            },
            {
                "field": "total_amount",
                "label": "Total",
                "formatter": "currency",
                "sortable": True
            },
            {
                "field": "status",
                "label": "Status",
                "formatter": """
                    function(value) {
                        const statusMap = {
                            'draft': 'Draft',
                            'sent': 'Sent',
                            'accepted': 'Accepted',
                            'rejected': 'Rejected',
                            'expired': 'Expired'
                        };
                        return statusMap[value] || value;
                    }
                """,
                "cellClassFunction": """
                    function(value) {
                        const statusColors = {
                            'draft': 'text-gray-600',
                            'sent': 'text-blue-600',
                            'accepted': 'text-green-600',
                            'rejected': 'text-red-600',
                            'expired': 'text-gray-400'
                        };
                        return statusColors[value] || '';
                    }
                """
            }
        ],
        "filters": [
            {
                "field": "status",
                "label": "Status",
                "type": "select",
                "options": [
                    {"value": "", "label": "All"},
                    {"value": "draft", "label": "Draft"},
                    {"value": "sent", "label": "Sent"},
                    {"value": "accepted", "label": "Accepted"},
                    {"value": "rejected", "label": "Rejected"},
                    {"value": "expired", "label": "Expired"}
                ]
            },
            {
                "field": "customer_id",
                "label": "Customer",
                "type": "select",
                "optionsEndpoint": "/base/partners?is_customer=true",
                "optionLabelField": "name",
                "optionValueField": "id"
            },
            {
                "field": "date_range",
                "label": "Date Range",
                "type": "date",
                "subType": "range"
            }
        ],
        "createable": True,
        "createLabel": "New Quotation",
        "createRoute": "/sales/quotations/new",
        "editRoute": "/sales/quotations/{id}/edit",
        "clickable": True,
        "rowActions": [
            {
                "id": "view",
                "label": "View",
                "icon": "eye",
                "route": "/sales/quotations/{id}"
            },
            {
                "id": "edit",
                "label": "Edit",
                "icon": "pencil",
                "route": "/sales/quotations/{id}/edit",
                "condition": {"field": "status", "value": "draft"}
            },
            {
                "id": "send",
                "label": "Send",
                "icon": "send",
                "action": "send_quotation",
                "condition": {"field": "status", "value": "draft"}
            },
            {
                "id": "convert",
                "label": "Convert to Order",
                "icon": "arrow-right",
                "action": "convert_to_order",
                "condition": {"field": "status", "value": "accepted"}
            }
        ]
    }


# Quotations Form Schema
@router.get("/quotations/ui-schemas/form")
async def get_quotations_form_schema() -> Dict[str, Any]:
    """Get quotations form UI schema"""
    return {
        "title": "Quotation Details",
        "endpoint": "/sales/quotations",
        "method": "POST",
        "successRoute": "/sales/quotations",
        "cancelRoute": "/sales/quotations",
        "sections": [
            {
                "id": "basic",
                "title": "Quotation Information",
                "fields": [
                    {
                        "name": "title",
                        "label": "Quotation Title",
                        "type": "text",
                        "required": True,
                        "placeholder": "Enter a descriptive title for this quotation"
                    },
                    {
                        "name": "customer_id",
                        "label": "Customer",
                        "type": "autocomplete",
                        "required": True,
                        "optionsEndpoint": "/base/partners?is_customer=true",
                        "optionLabelField": "name",
                        "optionValueField": "id",
                        "placeholder": "Start typing to search customers..."
                    },
                    {
                        "name": "quotation_date",
                        "label": "Quotation Date",
                        "type": "date",
                        "required": True,
                        "defaultValue": "today"
                    },
                    {
                        "name": "valid_until",
                        "label": "Valid Until",
                        "type": "datetime-local",
                        "required": False,
                        "help": "Quotation expiration date",
                        "compute": """
                            function(data) {
                                if (data.quotation_date) {
                                    const date = new Date(data.quotation_date);
                                    date.setDate(date.getDate() + 30);
                                    return date.toISOString().slice(0, 16);
                                }
                                return null;
                            }
                        """
                    },
                    {
                        "name": "description",
                        "label": "Description",
                        "type": "textarea",
                        "rows": 2,
                        "colSpan": 2,
                        "placeholder": "Additional quotation details or notes"
                    }
                ]
            },
            {
                "id": "items",
                "title": "Quotation Items",
                "gridClass": "grid-cols-2",
                "fields": [
                    {
                        "name": "line_items",
                        "type": "component",
                        "component": "LineItemsManager",
                        "label": "Quotation Items",
                        "required": True,
                        "colSpan": 2,
                        "props": {
                            # "title": "Quotation Items",
                            "entityType": "quotation",
                            "taxRate": 0,
                            "productApiUrl": "http://localhost:8006/products"
                        }
                    }
                ]
            },
            {
                "id": "terms",
                "title": "Terms & Conditions",
                "fields": [
                    {
                        "name": "payment_terms_days",
                        "label": "Payment Terms (Days)",
                        "type": "select",
                        "options": [
                            {"value": 30, "label": "Net 30"},
                            {"value": 60, "label": "Net 60"},
                            {"value": 0, "label": "Due on Receipt"},
                            {"value": 10, "label": "Net 10"}
                        ],
                        "defaultValue": 30
                    },
                    {
                        "name": "delivery_terms",
                        "label": "Delivery Terms",
                        "type": "text",
                        "placeholder": "e.g., FOB, Ex Works, etc."
                    },
                    {
                        "name": "internal_notes",
                        "label": "Internal Notes",
                        "type": "textarea",
                        "rows": 2,
                        "placeholder": "Internal notes (not visible to customer)"
                    },
                    {
                        "name": "terms_and_conditions",
                        "label": "Terms and Conditions",
                        "type": "textarea",
                        "rows": 3,
                        "placeholder": "Terms and conditions for the quotation"
                    }
                ]
            }
        ],
        "submitLabel": "Save Quotation",
        "cancelLabel": "Cancel"
    }


# Orders List Schema
@router.get("/orders/ui-schemas/list")
async def get_orders_list_schema() -> Dict[str, Any]:
    """Get orders list UI schema"""
    return {
        "title": "Sales Orders",
        "description": "Manage customer orders",
        "viewType": "table",
        "endpoint": "/sales/orders",
        "searchable": True,
        "searchPlaceholder": "Search orders...",
        "paginated": True,
        "pageSize": 20,
        "columns": [
            {
                "field": "order_number",
                "label": "Order Number",
                "isTitle": True,
                "sortable": True
            },
            {
                "field": "customer_name",
                "label": "Customer",
                "sortable": True
            },
            {
                "field": "order_date",
                "label": "Order Date",
                "formatter": "date",
                "sortable": True
            },
            {
                "field": "delivery_date",
                "label": "Delivery Date",
                "formatter": "date"
            },
            {
                "field": "total_amount",
                "label": "Total",
                "formatter": "currency",
                "sortable": True
            },
            {
                "field": "payment_status",
                "label": "Payment",
                "formatter": """
                    function(value) {
                        const statusMap = {
                            'pending': 'Pending',
                            'partial': 'Partial',
                            'paid': 'Paid',
                            'overdue': 'Overdue'
                        };
                        return statusMap[value] || value;
                    }
                """,
                "cellClassFunction": """
                    function(value) {
                        const colors = {
                            'pending': 'text-yellow-600',
                            'partial': 'text-blue-600',
                            'paid': 'text-green-600',
                            'overdue': 'text-red-600'
                        };
                        return colors[value] || '';
                    }
                """
            },
            {
                "field": "fulfillment_status",
                "label": "Fulfillment",
                "formatter": """
                    function(value) {
                        const statusMap = {
                            'pending': 'Pending',
                            'processing': 'Processing',
                            'shipped': 'Shipped',
                            'delivered': 'Delivered',
                            'cancelled': 'Cancelled'
                        };
                        return statusMap[value] || value;
                    }
                """
            }
        ],
        "filters": [
            {
                "field": "payment_status",
                "label": "Payment Status",
                "type": "select",
                "options": [
                    {"value": "", "label": "All"},
                    {"value": "pending", "label": "Pending"},
                    {"value": "partial", "label": "Partial"},
                    {"value": "paid", "label": "Paid"},
                    {"value": "overdue", "label": "Overdue"}
                ]
            },
            {
                "field": "fulfillment_status",
                "label": "Fulfillment Status",
                "type": "select",
                "options": [
                    {"value": "", "label": "All"},
                    {"value": "pending", "label": "Pending"},
                    {"value": "processing", "label": "Processing"},
                    {"value": "shipped", "label": "Shipped"},
                    {"value": "delivered", "label": "Delivered"}
                ]
            }
        ],
        "createable": True,
        "createLabel": "New Order",
        "createRoute": "/sales/orders/new",
        "editRoute": "/sales/orders/{id}/edit",
        "clickable": True,
        "rowActions": [
            {
                "id": "view",
                "label": "View",
                "icon": "eye",
                "route": "/sales/orders/{id}"
            },
            {
                "id": "invoice",
                "label": "Generate Invoice",
                "icon": "file-text",
                "action": "generate_invoice",
                "condition": {"field": "payment_status", "operator": "!=", "value": "paid"}
            },
            {
                "id": "ship",
                "label": "Ship Order",
                "icon": "truck",
                "action": "ship_order",
                "condition": {"field": "fulfillment_status", "value": "pending"}
            }
        ]
    }


# Pricing Rules List Schema
@router.get("/pricing/ui-schemas/list")
async def get_pricing_rules_list_schema() -> Dict[str, Any]:
    """Get pricing rules list UI schema"""
    return {
        "title": "Pricing Rules",
        "description": "Manage pricing and discount rules",
        "viewType": "table",
        "endpoint": "/sales/pricing/rules/",
        "searchable": True,
        "paginated": True,
        "columns": [
            {
                "field": "name",
                "label": "Rule Name",
                "isTitle": True,
                "sortable": True
            },
            {
                "field": "rule_type",
                "label": "Type",
                "formatter": """
                    function(value) {
                        const types = {
                            'customer_specific': 'Customer Specific',
                            'volume_discount': 'Volume Discount',
                            'promotional': 'Promotional',
                            'product_category': 'Product Category'
                        };
                        return types[value] || value;
                    }
                """
            },
            {
                "field": "discount_type",
                "label": "Discount Type",
                "formatter": """
                    function(value) {
                        return value === 'percentage' ? 'Percentage' : 'Fixed Amount';
                    }
                """
            },
            {
                "field": "discount_value",
                "label": "Discount",
                "formatter": """
                    function(value, item) {
                        if (item.discount_type === 'percentage') {
                            return value + '%';
                        } else {
                            return '$' + value.toFixed(2);
                        }
                    }
                """
            },
            {
                "field": "start_date",
                "label": "Start Date",
                "formatter": "date"
            },
            {
                "field": "end_date",
                "label": "End Date",
                "formatter": "date"
            },
            {
                "field": "is_active",
                "label": "Status",
                "formatter": """
                    function(value) {
                        return value ? 'Active' : 'Inactive';
                    }
                """,
                "cellClassFunction": """
                    function(value) {
                        return value ? 'text-green-600' : 'text-gray-400';
                    }
                """
            }
        ],
        "filters": [
            {
                "field": "rule_type",
                "label": "Rule Type",
                "type": "select",
                "options": [
                    {"value": "", "label": "All"},
                    {"value": "customer_specific", "label": "Customer Specific"},
                    {"value": "volume_discount", "label": "Volume Discount"},
                    {"value": "promotional", "label": "Promotional"},
                    {"value": "product_category", "label": "Product Category"}
                ]
            },
            {
                "field": "is_active",
                "label": "Status",
                "type": "select",
                "options": [
                    {"value": "", "label": "All"},
                    {"value": "true", "label": "Active"},
                    {"value": "false", "label": "Inactive"}
                ]
            }
        ],
        "createable": True,
        "createLabel": "New Pricing Rule",
        "createRoute": "/sales/pricing/new",
        "editRoute": "/sales/pricing/{id}/edit",
        "rowActions": [
            {
                "id": "edit",
                "label": "Edit",
                "icon": "pencil",
                "route": "/sales/pricing/{id}/edit"
            },
            {
                "id": "toggle",
                "label": "Toggle Status",
                "icon": "toggle-left",
                "action": "toggle_status"
            }
        ]
    }


# Customer List Schema (redirects to partners but with customer filter)
@router.get("/customers/ui-schemas/list")
async def get_customers_list_schema() -> Dict[str, Any]:
    """Get customers list UI schema"""
    return {
        "title": "Customers",
        "description": "Manage customer accounts",
        "viewType": "table",
        "endpoint": "/base/partners?is_customer=true",
        # "dataPath": "partners",  # Tell the UI where to find the data in the response
        "searchable": True,
        "paginated": True,
        "columns": [
            {
                "field": "name",
                "label": "Customer Name",
                "isTitle": True,
                "sortable": True
            },
            {
                "field": "email",
                "label": "Email",
                "sortable": True
            },
            {
                "field": "phone",
                "label": "Phone"
            },
            {
                "field": "credit_limit",
                "label": "Credit Limit",
                "formatter": "currency"
            },
            {
                "field": "outstanding_balance",
                "label": "Outstanding",
                "formatter": "currency",
                "cellClassFunction": """
                    function(value, item) {
                        if (value > item.credit_limit) return 'text-red-600';
                        if (value > item.credit_limit * 0.8) return 'text-yellow-600';
                        return 'text-green-600';
                    }
                """
            },
            {
                "field": "is_vip",
                "label": "VIP",
                "formatter": """
                    function(value) {
                        return value ? '⭐ VIP' : '';
                    }
                """,
                "cellClass": "font-semibold text-yellow-600"
            }
        ],
        "createRoute": "/sales/customers/new?type=customer",
        "editRoute": "/sales/customers/{id}/edit",
        "rowActions": [
            {
                "id": "view",
                "label": "View Details",
                "icon": "eye",
                "route": "/partners/{id}"
            },
            {
                "id": "orders",
                "label": "View Orders",
                "icon": "shopping-bag",
                "route": "/sales/orders?customer_id={id}"
            },
            {
                "id": "quotations",
                "label": "View Quotations",
                "icon": "file-text",
                "route": "/sales/quotations?customer_id={id}"
            }
        ]
    }

# Customer Form Schema (redirects to partners but with customer filter)
@router.get("/customers/ui-schemas/form")
async def get_customers_form_schema() -> Dict[str, Any]:
    """Get customers form UI schema"""
    return {
        "title": "Customers",
        "description": "Manage customer",
        "viewType": "form",
        "endpoint": "/base/partners",
        "method": "POST",
        "successRoute": "/sales/customers",
        "cancelRoute": "/sales/customers",
        "dataPath": "partners",  # Tell the UI where to find the data in the response
        "sections": [
            {
                "id": "basic",
                "title": "Customer Information",
                "gridClass": "grid-cols-2",
                "fields": [
                    {
                        "name": "name",
                        "label": "Customer Name",
                        "type": "text",
                        "required": True,
                        "colSpan": 1,
                        "placeholder": "Enter a descriptive name for this order"
                    },
                    {
                        "name": "email",
                        "label": "Customer Email",
                        "type": "text",
                        "required": True,
                        "colSpan": 1,
                        "placeholder": "Enter email for this customer"
                    },
                    {
                        "name": "partner_type",
                        "label": "Customer Type",
                        "type": "text",
                        "required": True,
                        "colSpan": 1,
                        "defaultValue":"customer",
                        "placeholder": "Enter a descriptive name for this order"
                    },
                    {
                        "name": "is_customer",
                        "label": "Is Customer",
                        "type": "checkbox",
                        "required": True,
                        "colSpan": 1,
                        "defaultValue":True,
                        "placeholder": "Enter a descriptive name for this order"
                    },
                    {
                        "name": "company_id",
                        "label": "Specific Company",
                        "type": "select",
                        "required": True,
                        "optionsEndpoint": "/api/v1/base/companies",
                        "optionsDataPath":"companies",
                        "optionLabelField": "name",
                        "optionValueField": "id"
                    },
                ]
            }
        ],
        
    }


# Orders Form Schema
@router.get("/orders/ui-schemas/form")
async def get_orders_form_schema() -> Dict[str, Any]:
    """Get orders form UI schema"""
    return {
        "title": "Order Details",
        "endpoint": "/sales/orders",
        "method": "POST",
        "successRoute": "/sales/orders",
        "cancelRoute": "/sales/orders",
        "sections": [
            {
                "id": "basic",
                "title": "Order Information",
                "gridClass": "grid-cols-2",
                "fields": [
                    {
                        "name": "title",
                        "label": "Order Title",
                        "type": "text",
                        "required": True,
                        "colSpan": 1,
                        "placeholder": "Enter a descriptive title for this order"
                    },
                    {
                        "name": "customer_id",
                        "label": "Customer",
                        "type": "autocomplete",
                        "required": True,
                        "colSpan": 1,
                        "optionsEndpoint": "/base/partners?is_customer=true",
                        "optionLabelField": "name",
                        "optionValueField": "id",
                        "placeholder": "Start typing to search customers..."
                    },
                    {
                        "name": "order_date",
                        "label": "Order Date",
                        "type": "date",
                        "required": True,
                        "defaultValue": "today"
                    },
                    {
                        "name": "delivery_date",
                        "label": "Delivery Date",
                        "type": "date",
                        "required": True,
                        "help": "Expected delivery date"
                    },
                    {
                        "name": "description",
                        "label": "Description",
                        "type": "textarea",
                        "rows": 2,
                        "colSpan": 2,
                        "placeholder": "Additional order details or notes"
                    }
                ]
            },
            {
                "id": "items",
                "title": "Order Items",
                "gridClass": "grid-cols-2",
                "fields": [
                    {
                        "name": "line_items",
                        "type": "component",
                        "component": "LineItemsManager",
                        "label": "Order Items",
                        "required": True,
                        "colSpan":2,
                        "props": {
                            "title": "Order Items",
                            "entityType": "order",
                            "taxRate": 0,
                            "productApiUrl": "/api/v1/inventory/products"
                        }
                    }
                ]
            },
            {
                "id": "payment",
                "title": "Payment Information",
                "gridClass": "grid-cols-2",
                "fields": [
                    {
                        "name": "payment_terms",
                        "label": "Payment Terms",
                        "type": "select",
                        "options": [
                            {"value": "net30", "label": "Net 30"},
                            {"value": "net60", "label": "Net 60"},
                            {"value": "due_on_receipt", "label": "Due on Receipt"},
                            {"value": "2_10_net30", "label": "2/10 Net 30"}
                        ],
                        "defaultValue": "net30"
                    },
                    {
                        "name": "payment_method",
                        "label": "Payment Method",
                        "type": "select",
                        "options": [
                            {"value": "invoice", "label": "Invoice"},
                            {"value": "credit_card", "label": "Credit Card"},
                            {"value": "bank_transfer", "label": "Bank Transfer"},
                            {"value": "cash", "label": "Cash"}
                        ]
                    },
                    {
                        "name": "shipping_address",
                        "label": "Shipping Address",
                        "type": "textarea",
                        "rows": 3,
                        "colSpan": 2,
                        "placeholder": "Enter shipping address"
                    }
                ]
            }
        ],
        "submitLabel": "Create Order",
        "cancelLabel": "Cancel"
    }


# Pricing Rules Form Schema
@router.get("/pricing/ui-schemas/form")
async def get_pricing_rules_form_schema() -> Dict[str, Any]:
    """Get pricing rules form UI schema"""
    return {
        "title": "Pricing Rule",
        "endpoint": "/pricing/rules",
        "method": "POST",
        "successRoute": "/sales/pricing",
        "cancelRoute": "/sales/pricing",
        "sections": [
            {
                "id": "basic",
                "title": "Basic Information",
                "fields": [
                    {
                        "name": "name",
                        "label": "Rule Name",
                        "type": "text",
                        "required": True,
                        "placeholder": "e.g., VIP Customer Discount"
                    },
                    {
                        "name": "description",
                        "label": "Description",
                        "type": "textarea",
                        "rows": 2,
                        "placeholder": "Describe this pricing rule"
                    },
                    {
                        "name": "rule_type",
                        "label": "Rule Type",
                        "type": "select",
                        "required": True,
                        "options": [
                            {"value": "customer_specific", "label": "Customer Specific"},
                            {"value": "volume_discount", "label": "Volume Discount"},
                            {"value": "promotional", "label": "Promotional"},
                            {"value": "product_category", "label": "Product Category"}
                        ]
                    }
                ]
            },
            {
                "id": "discount",
                "title": "Discount Configuration",
                "gridClass": "grid-cols-2",
                "fields": [
                    {
                        "name": "discount_type",
                        "label": "Discount Type",
                        "type": "select",
                        "required": True,
                        "options": [
                            {"value": "percentage", "label": "Percentage"},
                            {"value": "fixed_amount", "label": "Fixed Amount"}
                        ]
                    },
                    {
                        "name": "discount_value",
                        "label": "Discount Value",
                        "type": "number",
                        "required": True,
                        "min": 0,
                        "help": "Enter percentage (0-100) or fixed amount"
                    },
                    {
                        "name": "min_quantity",
                        "label": "Minimum Quantity",
                        "type": "number",
                        "min": 0,
                        "help": "Minimum quantity for volume discounts"
                    },
                    {
                        "name": "min_amount",
                        "label": "Minimum Amount",
                        "type": "number",
                        "min": 0,
                        "prefix": "$",
                        "help": "Minimum order amount to apply rule"
                    }
                ]
            },
            {
                "id": "validity",
                "title": "Validity Period",
                "gridClass": "grid-cols-2",
                "fields": [
                    {
                        "name": "start_date",
                        "label": "Start Date",
                        "type": "date",
                        "required": True
                    },
                    {
                        "name": "end_date",
                        "label": "End Date",
                        "type": "date",
                        "help": "Leave empty for no end date"
                    },
                    {
                        "name": "is_active",
                        "label": "Active",
                        "type": "checkbox",
                        "defaultValue": True,
                        "colSpan": 2
                    }
                ]
            },
            {
                "id": "conditions",
                "title": "Conditions",
                "fields": [
                    {
                        "name": "customer_ids",
                        "label": "Specific Customers",
                        "type": "select",
                        "multiple": True,
                        "optionsEndpoint": "/base/partners?is_customer=true",
                        "optionLabelField": "name",
                        "optionValueField": "id",
                        "help": "Leave empty to apply to all customers",
                        "visible": {
                            "field": "rule_type",
                            "value": "customer_specific"
                        }
                    },
                    {
                        "name": "product_category_ids",
                        "label": "Product Categories",
                        "type": "select",
                        "multiple": True,
                        "optionsEndpoint": "http://localhost:8005/categories",
                        "optionLabelField": "name",
                        "optionValueField": "id",
                        "help": "Select applicable product categories",
                        "visible": {
                            "field": "rule_type",
                            "value": "product_category"
                        }
                    },
                    {
                        "name": "priority",
                        "label": "Priority",
                        "type": "number",
                        "min": 0,
                        "defaultValue": 10,
                        "help": "Higher priority rules are applied first"
                    }
                ]
            }
        ],
        "submitLabel": "Save Pricing Rule",
        "cancelLabel": "Cancel"
    }


# Analytics View Schema
@router.get("/analytics/ui-schemas/dashboard")
async def get_analytics_dashboard_schema() -> Dict[str, Any]:
    """Get sales analytics dashboard schema"""
    return {
        "title": "Sales Analytics",
        "description": "Sales performance analytics and reports",
        "viewType": "dashboard",
        "layout": {
            "columns": 2,
            "rows": "auto"
        },
        "widgets": [
            {
                "id": "revenue_by_month",
                "type": "chart",
                "title": "Revenue by Month",
                "endpoint": "/analytics/revenue-by-month",
                "chartType": "bar",
                "span": 2,
                "height": 350
            },
            {
                "id": "sales_by_product",
                "type": "chart",
                "title": "Sales by Product",
                "endpoint": "/analytics/sales-by-product",
                "chartType": "pie",
                "span": 1,
                "height": 300
            },
            {
                "id": "sales_by_customer",
                "type": "chart",
                "title": "Top 10 Customers",
                "endpoint": "/analytics/top-customers",
                "chartType": "bar",
                "span": 1,
                "height": 300
            },
            {
                "id": "conversion_metrics",
                "type": "metrics",
                "title": "Conversion Metrics",
                "endpoint": "/analytics/conversion-metrics",
                "span": 2,
                "metrics": [
                    {"label": "Quotation to Order", "field": "quotation_conversion", "format": "percentage"},
                    {"label": "Average Order Value", "field": "avg_order_value", "format": "currency"},
                    {"label": "Customer Retention", "field": "retention_rate", "format": "percentage"},
                    {"label": "Sales Growth", "field": "growth_rate", "format": "percentage"}
                ]
            }
        ]
    }


# Transactions List Schema
@router.get("/transactions/ui-schemas/list")
async def get_transactions_list_schema() -> Dict[str, Any]:
    """Get transactions list UI schema"""
    return {
        "title": "Sales Transactions",
        "description": "Manage quotations and orders",
        "viewType": "table",
        "endpoint": "/sales/transactions",
        "searchable": True,
        "searchPlaceholder": "Search transactions...",
        "paginated": True,
        "pageSize": 20,
        "columns": [
            {
                "field": "transaction_number",
                "label": "Transaction #",
                "isTitle": True,
                "sortable": True
            },
            {
                "field": "title",
                "label": "Title",
                "sortable": True
            },
            {
                "field": "customer_name",
                "label": "Customer",
                "sortable": True
            },
            {
                "field": "created_at",
                "label": "Created",
                "formatter": "date",
                "sortable": True
            },
            {
                "field": "total_amount",
                "label": "Total",
                "formatter": "currency",
                "sortable": True
            },
            {
                "field": "state",
                "label": "State",
                "formatter": """
                    function(value) {
                        const stateMap = {
                            'draft': 'Draft',
                            'quote_pending_approval': 'Quote Pending Approval',
                            'quote_approved': 'Quote Approved',
                            'quote_sent': 'Quote Sent',
                            'quote_accepted': 'Quote Accepted',
                            'quote_rejected': 'Quote Rejected',
                            'quote_expired': 'Quote Expired',
                            'order_pending': 'Order Pending',
                            'order_confirmed': 'Order Confirmed',
                            'order_in_production': 'In Production',
                            'order_ready_to_ship': 'Ready to Ship',
                            'order_partially_shipped': 'Partially Shipped',
                            'order_shipped': 'Shipped',
                            'order_delivered': 'Delivered',
                            'order_completed': 'Completed',
                            'order_cancelled': 'Cancelled',
                            'order_on_hold': 'On Hold'
                        };
                        return stateMap[value] || value;
                    }
                """,
                "cellClassFunction": """
                    function(value) {
                        const stateColors = {
                            'draft': 'text-gray-600',
                            'quote_pending_approval': 'text-yellow-600',
                            'quote_approved': 'text-blue-600',
                            'quote_sent': 'text-indigo-600',
                            'quote_accepted': 'text-green-600',
                            'quote_rejected': 'text-red-600',
                            'quote_expired': 'text-gray-400',
                            'order_pending': 'text-yellow-600',
                            'order_confirmed': 'text-blue-600',
                            'order_in_production': 'text-purple-600',
                            'order_ready_to_ship': 'text-indigo-600',
                            'order_partially_shipped': 'text-orange-600',
                            'order_shipped': 'text-blue-600',
                            'order_delivered': 'text-green-600',
                            'order_completed': 'text-green-700',
                            'order_cancelled': 'text-red-600',
                            'order_on_hold': 'text-gray-500'
                        };
                        return stateColors[value] || '';
                    }
                """
            }
        ],
        "filters": [
            {
                "field": "state",
                "label": "State",
                "type": "select",
                "multiple": True,
                "options": [
                    {"value": "", "label": "All"},
                    {"value": "draft", "label": "Draft"},
                    {"value": "quote_pending_approval", "label": "Quote Pending Approval"},
                    {"value": "quote_approved", "label": "Quote Approved"},
                    {"value": "quote_sent", "label": "Quote Sent"},
                    {"value": "quote_accepted", "label": "Quote Accepted"},
                    {"value": "quote_rejected", "label": "Quote Rejected"},
                    {"value": "quote_expired", "label": "Quote Expired"},
                    {"value": "order_pending", "label": "Order Pending"},
                    {"value": "order_confirmed", "label": "Order Confirmed"},
                    {"value": "order_in_production", "label": "In Production"},
                    {"value": "order_ready_to_ship", "label": "Ready to Ship"},
                    {"value": "order_partially_shipped", "label": "Partially Shipped"},
                    {"value": "order_shipped", "label": "Shipped"},
                    {"value": "order_delivered", "label": "Delivered"},
                    {"value": "order_completed", "label": "Completed"},
                    {"value": "order_cancelled", "label": "Cancelled"},
                    {"value": "order_on_hold", "label": "On Hold"}
                ]
            },
            {
                "field": "customer_id",
                "label": "Customer",
                "type": "select",
                "optionsEndpoint": "/base/partners?is_customer=true",
                "optionLabelField": "name",
                "optionValueField": "id"
            },
            {
                "field": "date_range",
                "label": "Date Range",
                "type": "date",
                "subType": "range"
            }
        ],
        "createable": True,
        "createLabel": "New Transaction",
        "createRoute": "/sales/transactions/new",
        "editRoute": "/sales/transactions/{id}/edit",
        "clickable": True,
        "rowActions": [
            {
                "id": "view",
                "label": "View",
                "icon": "eye",
                "route": "/sales/transactions/{id}"
            },
            {
                "id": "edit",
                "label": "Edit",
                "icon": "pencil",
                "route": "/sales/transactions/{id}/edit",
                "condition": {"field": "state", "value": "draft"}
            },
            {
                "id": "convert_to_order",
                "label": "Convert to Order",
                "icon": "arrow-right",
                "action": "convert_to_order",
                "condition": {"field": "state", "value": "quote_accepted"}
            },
            {
                "id": "send",
                "label": "Send",
                "icon": "send",
                "action": "send_transaction",
                "condition": {"field": "state", "value": "draft"}
            }
        ]
    }


# Transactions Form Schema
@router.get("/transactions/ui-schemas/form")
async def get_transactions_form_schema() -> Dict[str, Any]:
    """Get transactions form UI schema"""
    return {
        "title": "Transaction Details",
        "endpoint": "/sales/transactions",
        "method": "POST",
        "successRoute": "/sales/transactions",
        "cancelRoute": "/sales/transactions",
        "sections": [
            {
                "id": "basic",
                "title": "Transaction Information",
                "gridClass": "grid-cols-2",
                "fields": [
                    {
                        "name": "title",
                        "label": "Transaction Title",
                        "type": "text",
                        "required": True,
                        "colSpan": 2,
                        "placeholder": "Enter a descriptive title for this transaction"
                    },
                    {
                        "name": "customer_id",
                        "label": "Customer",
                        "type": "autocomplete",
                        "required": True,
                        "colSpan": 1,
                        "optionsEndpoint": "/base/partners?is_customer=true",
                        "optionLabelField": "name",
                        "optionValueField": "id",
                        "placeholder": "Start typing to search customers..."
                    },
                    {
                        "name": "transaction_date",
                        "label": "Transaction Date",
                        "type": "date",
                        "required": True,
                        "colSpan": 1,
                        "defaultValue": "today"
                    },
                    {
                        "name": "description",
                        "label": "Description",
                        "type": "textarea",
                        "rows": 2,
                        "colSpan": 2,
                        "placeholder": "Additional transaction details or notes"
                    }
                ]
            },
            {
                "id": "items",
                "title": "Transaction Items",
                "gridClass": "grid-cols-2",
                "fields": [
                    {
                        "name": "line_items",
                        "type": "component",
                        "component": "LineItemsManager",
                        "label": "Transaction Items",
                        "required": True,
                        "colSpan": 2,
                        "props": {
                            "title": "Transaction Items",
                            "entityType": "transaction",
                            "taxRate": 0,
                            "productApiUrl": "/api/v1/inventory/products"
                        }
                    }
                ]
            },
            {
                "id": "terms",
                "title": "Terms & Conditions",
                "gridClass": "grid-cols-2",
                "fields": [
                    {
                        "name": "payment_terms_days",
                        "label": "Payment Terms (Days)",
                        "type": "select",
                        "options": [
                            {"value": 30, "label": "Net 30"},
                            {"value": 60, "label": "Net 60"},
                            {"value": 0, "label": "Due on Receipt"},
                            {"value": 10, "label": "Net 10"}
                        ],
                        "defaultValue": 30
                    },
                    {
                        "name": "delivery_terms",
                        "label": "Delivery Terms",
                        "type": "text",
                        "placeholder": "e.g., FOB, Ex Works, etc."
                    },
                    {
                        "name": "internal_notes",
                        "label": "Internal Notes",
                        "type": "textarea",
                        "rows": 2,
                        "colSpan": 2,
                        "placeholder": "Internal notes (not visible to customer)"
                    },
                    {
                        "name": "terms_and_conditions",
                        "label": "Terms and Conditions",
                        "type": "textarea",
                        "rows": 3,
                        "colSpan": 2,
                        "placeholder": "Terms and conditions for the transaction"
                    }
                ]
            }
        ],
        "actions": [
            {
                "id": "save",
                "label": "Save Transaction",
                "type": "submit",
                "variant": "primary"
            },
            {
                "id": "cancel",
                "label": "Cancel",
                "type": "cancel",
                "variant": "secondary"
            },
            {
                "id": "save_and_new",
                "label": "Save and New",
                "type": "submit",
                "action": "save_and_new",
                "variant": "outline"
            }
        ],
        "submitLabel": "Save Transaction",
        "cancelLabel": "Cancel"
    }


# Transaction Details View Schema
@router.get("/transactions/ui-schemas/detail")
async def get_transaction_detail_schema() -> Dict[str, Any]:
    """Get transaction detail view UI schema"""
    return {
        "title": "Transaction Details",
        "viewType": "detail",
        "endpoint": "/sales/transactions",
        "header": {
            "titleField": "transaction_number",
            "subtitleField": "title",
            "statusField": "state",
            "statusFormatter": """
                function(value) {
                    const stateMap = {
                        'draft': 'Draft',
                        'quote_pending_approval': 'Quote Pending Approval',
                        'quote_approved': 'Quote Approved',
                        'quote_sent': 'Quote Sent',
                        'quote_accepted': 'Quote Accepted',
                        'quote_rejected': 'Quote Rejected',
                        'quote_expired': 'Quote Expired',
                        'order_pending': 'Order Pending',
                        'order_confirmed': 'Order Confirmed',
                        'order_in_production': 'In Production',
                        'order_ready_to_ship': 'Ready to Ship',
                        'order_partially_shipped': 'Partially Shipped',
                        'order_shipped': 'Shipped',
                        'order_delivered': 'Delivered',
                        'order_completed': 'Completed',
                        'order_cancelled': 'Cancelled',
                        'order_on_hold': 'On Hold'
                    };
                    return stateMap[value] || value;
                }
            """,
            "statusClassFunction": """
                function(value) {
                    const stateColors = {
                        'draft': 'bg-gray-100 text-gray-800',
                        'quote_pending_approval': 'bg-yellow-100 text-yellow-800',
                        'quote_approved': 'bg-blue-100 text-blue-800',
                        'quote_sent': 'bg-indigo-100 text-indigo-800',
                        'quote_accepted': 'bg-green-100 text-green-800',
                        'quote_rejected': 'bg-red-100 text-red-800',
                        'quote_expired': 'bg-gray-100 text-gray-800',
                        'order_pending': 'bg-yellow-100 text-yellow-800',
                        'order_confirmed': 'bg-blue-100 text-blue-800',
                        'order_in_production': 'bg-purple-100 text-purple-800',
                        'order_ready_to_ship': 'bg-indigo-100 text-indigo-800',
                        'order_partially_shipped': 'bg-orange-100 text-orange-800',
                        'order_shipped': 'bg-blue-100 text-blue-800',
                        'order_delivered': 'bg-green-100 text-green-800',
                        'order_completed': 'bg-green-200 text-green-900',
                        'order_cancelled': 'bg-red-100 text-red-800',
                        'order_on_hold': 'bg-gray-200 text-gray-800'
                    };
                    return stateColors[value] || 'bg-gray-100 text-gray-800';
                }
            """,
            "actions": [
                {
                    "id": "edit",
                    "label": "Edit",
                    "icon": "pencil",
                    "route": "/sales/transactions/{id}/edit",
                    "condition": {"field": "state", "value": "draft"}
                },
                {
                    "id": "convert_to_order",
                    "label": "Convert to Order",
                    "icon": "arrow-right",
                    "action": "convert_to_order",
                    "condition": {"field": "state", "value": "quote_accepted"}
                },
                {
                    "id": "send",
                    "label": "Send",
                    "icon": "send",
                    "action": "send_transaction",
                    "condition": {"field": "state", "value": "draft"}
                },
                {
                    "id": "confirm",
                    "label": "Confirm",
                    "icon": "check",
                    "action": "confirm_transaction",
                    "variant": "primary"
                },
                {
                    "id": "back",
                    "label": "Back",
                    "icon": "arrow-left",
                    "action": "back_transaction"
                },
                {
                    "id": "print",
                    "label": "Print",
                    "icon": "printer",
                    "action": "print_transaction"
                }
            ]
        },
        "sections": [
            {
                "id": "basic_info",
                "title": "Basic Information",
                "type": "keyValue",
                "fields": [
                    {"label": "Transaction Number", "field": "transaction_number"},
                    {"label": "Title", "field": "title"},
                    {"label": "Customer", "field": "customer_name"},
                    {"label": "Created Date", "field": "created_at", "formatter": "date"},
                    {"label": "Last Updated", "field": "updated_at", "formatter": "date"}
                ]
            },
            {
                "id": "financial_info",
                "title": "Financial Information",
                "type": "keyValue",
                "fields": [
                    {"label": "Subtotal", "field": "subtotal", "formatter": "currency"},
                    {"label": "Tax Amount", "field": "tax_amount", "formatter": "currency"},
                    {"label": "Discount", "field": "discount_amount", "formatter": "currency"},
                    {"label": "Total Amount", "field": "total_amount", "formatter": "currency"},
                    {"label": "Currency", "field": "currency_code"}
                ]
            },
            {
                "id": "items",
                "title": "Line Items",
                "type": "table",
                "endpoint": "/sales/transactions/{id}/line-items",
                "columns": [
                    {"field": "line_number", "label": "#", "width": "50px"},
                    {"field": "item_name", "label": "Item"},
                    {"field": "quantity_ordered", "label": "Quantity"},
                    {"field": "unit_price", "label": "Unit Price", "formatter": "currency"},
                    {"field": "line_total", "label": "Total", "formatter": "currency"}
                ]
            },
            {
                "id": "terms",
                "title": "Terms & Conditions",
                "type": "keyValue",
                "fields": [
                    {"label": "Payment Terms", "field": "payment_terms_days", "formatter": "days"},
                    {"label": "Delivery Terms", "field": "delivery_terms"},
                    {"label": "Valid Until", "field": "valid_until", "formatter": "date"}
                ]
            }
        ]
    }