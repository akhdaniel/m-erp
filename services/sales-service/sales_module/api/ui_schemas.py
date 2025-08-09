"""
UI Schema definitions for Sales Service
Provides JSON schemas for dynamic UI rendering
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/ui-schemas", tags=["UI Schemas"])


# Dashboard Schema
@router.get("/dashboard")
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
                "endpoint": "/api/v1/dashboard/metrics/revenue",
                "format": "currency",
                "icon": "dollar-sign",
                "color": "green",
                "span": 1
            },
            {
                "id": "quotes_metric",
                "type": "metric",
                "title": "Active Quotes",
                "endpoint": "/api/v1/dashboard/metrics/quotes",
                "format": "number",
                "icon": "file-text",
                "color": "blue",
                "span": 1
            },
            {
                "id": "orders_metric",
                "type": "metric",
                "title": "Pending Orders",
                "endpoint": "/api/v1/dashboard/metrics/orders",
                "format": "number",
                "icon": "shopping-bag",
                "color": "orange",
                "span": 1
            },
            {
                "id": "revenue_chart",
                "type": "chart",
                "title": "Revenue Trend",
                "endpoint": "/api/v1/dashboard/charts/revenue-trend",
                "chartType": "line",
                "span": 2,
                "height": 300
            },
            {
                "id": "pipeline_chart",
                "type": "chart",
                "title": "Sales Pipeline",
                "endpoint": "/api/v1/dashboard/charts/sales-pipeline",
                "chartType": "bar",
                "span": 1,
                "height": 300
            },
            {
                "id": "recent_quotes",
                "type": "list",
                "title": "Recent Quotes",
                "endpoint": "/api/v1/dashboard/recent/quotes",
                "limit": 5,
                "span": 1,
                "columns": [
                    {"field": "quote_number", "label": "Quote #"},
                    {"field": "customer_name", "label": "Customer"},
                    {"field": "total_amount", "label": "Amount", "formatter": "currency"}
                ]
            },
            {
                "id": "recent_orders",
                "type": "list",
                "title": "Recent Orders",
                "endpoint": "/api/v1/dashboard/recent/orders",
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
                "endpoint": "/api/v1/dashboard/analytics/top-customers",
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


# Quotes List Schema
@router.get("/quotes/list")
async def get_quotes_list_schema() -> Dict[str, Any]:
    """Get quotes list UI schema"""
    return {
        "title": "Sales Quotes",
        "description": "Manage customer quotations",
        "viewType": "table",
        "endpoint": "/api/v1/quotes/",
        "searchable": True,
        "searchPlaceholder": "Search quotes...",
        "searchParam": "search",
        "paginated": True,
        "pageSize": 20,
        "columns": [
            {
                "field": "quote_number",
                "label": "Quote Number",
                "isTitle": True,
                "sortable": True
            },
            {
                "field": "customer_name",
                "label": "Customer",
                "sortable": True
            },
            {
                "field": "quote_date",
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
                "optionsEndpoint": "/api/v1/customers",
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
        "createLabel": "New Quote",
        "createRoute": "/sales/quotes/new",
        "editRoute": "/sales/quotes/{id}/edit",
        "clickable": True,
        "rowActions": [
            {
                "id": "view",
                "label": "View",
                "icon": "eye",
                "route": "/sales/quotes/{id}"
            },
            {
                "id": "edit",
                "label": "Edit",
                "icon": "pencil",
                "route": "/sales/quotes/{id}/edit",
                "condition": {"field": "status", "value": "draft"}
            },
            {
                "id": "send",
                "label": "Send",
                "icon": "send",
                "action": "send_quote",
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


# Quotes Form Schema
@router.get("/quotes/form")
async def get_quotes_form_schema() -> Dict[str, Any]:
    """Get quotes form UI schema"""
    return {
        "title": "Quote Details",
        "endpoint": "/api/v1/quotes",
        "method": "POST",
        "successRoute": "/sales/quotes",
        "cancelRoute": "/sales/quotes",
        "sections": [
            {
                "id": "customer",
                "title": "Customer Information",
                "gridClass": "grid-cols-2",
                "fields": [
                    {
                        "name": "customer_id",
                        "label": "Customer",
                        "type": "select",
                        "required": True,
                        "colSpan": 2,
                        "optionsEndpoint": "/api/v1/customers",
                        "optionLabelField": "name",
                        "optionValueField": "id",
                        "placeholder": "Select a customer"
                    },
                    {
                        "name": "quote_date",
                        "label": "Quote Date",
                        "type": "date",
                        "required": True,
                        "defaultValue": "today"
                    },
                    {
                        "name": "valid_until",
                        "label": "Valid Until",
                        "type": "date",
                        "required": True,
                        "help": "Quote expiration date",
                        "compute": """
                            function(data) {
                                if (data.quote_date) {
                                    const date = new Date(data.quote_date);
                                    date.setDate(date.getDate() + 30);
                                    return date.toISOString().split('T')[0];
                                }
                                return null;
                            }
                        """
                    }
                ]
            },
            {
                "id": "items",
                "title": "Quote Items",
                "fields": [
                    {
                        "name": "items",
                        "type": "array",
                        "label": "Line Items",
                        "required": True,
                        "minItems": 1,
                        "itemFields": [
                            {
                                "name": "product_id",
                                "label": "Product",
                                "type": "select",
                                "required": True,
                                "optionsEndpoint": "/api/v1/products",
                                "optionLabelField": "name",
                                "optionValueField": "id"
                            },
                            {
                                "name": "quantity",
                                "label": "Quantity",
                                "type": "number",
                                "required": True,
                                "min": 1,
                                "defaultValue": 1
                            },
                            {
                                "name": "unit_price",
                                "label": "Unit Price",
                                "type": "number",
                                "required": True,
                                "prefix": "$",
                                "step": 0.01
                            },
                            {
                                "name": "discount_percent",
                                "label": "Discount %",
                                "type": "number",
                                "min": 0,
                                "max": 100,
                                "defaultValue": 0
                            },
                            {
                                "name": "line_total",
                                "label": "Total",
                                "type": "display",
                                "prefix": "$",
                                "compute": """
                                    function(item) {
                                        const qty = item.quantity || 0;
                                        const price = item.unit_price || 0;
                                        const discount = item.discount_percent || 0;
                                        const subtotal = qty * price;
                                        return subtotal - (subtotal * discount / 100);
                                    }
                                """
                            }
                        ]
                    }
                ]
            },
            {
                "id": "terms",
                "title": "Terms & Conditions",
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
                        "name": "notes",
                        "label": "Notes",
                        "type": "textarea",
                        "rows": 3,
                        "placeholder": "Additional notes or terms"
                    }
                ]
            }
        ],
        "submitLabel": "Save Quote",
        "cancelLabel": "Cancel"
    }


# Orders List Schema
@router.get("/orders/list")
async def get_orders_list_schema() -> Dict[str, Any]:
    """Get orders list UI schema"""
    return {
        "title": "Sales Orders",
        "description": "Manage customer orders",
        "viewType": "table",
        "endpoint": "/api/v1/orders/",
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
@router.get("/pricing/list")
async def get_pricing_rules_list_schema() -> Dict[str, Any]:
    """Get pricing rules list UI schema"""
    return {
        "title": "Pricing Rules",
        "description": "Manage pricing and discount rules",
        "viewType": "table",
        "endpoint": "/api/v1/pricing/rules/",
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
@router.get("/customers/list")
async def get_customers_list_schema() -> Dict[str, Any]:
    """Get customers list UI schema"""
    return {
        "title": "Customers",
        "description": "Manage customer accounts",
        "viewType": "table",
        "endpoint": "/api/v1/partners/?is_customer=true",
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
        "createRoute": "/partners/create?type=customer",
        "editRoute": "/partners/{id}/edit",
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
                "id": "quotes",
                "label": "View Quotes",
                "icon": "file-text",
                "route": "/sales/quotes?customer_id={id}"
            }
        ]
    }


# Orders Form Schema
@router.get("/orders/form")
async def get_orders_form_schema() -> Dict[str, Any]:
    """Get orders form UI schema"""
    return {
        "title": "Order Details",
        "endpoint": "/api/v1/orders",
        "method": "POST",
        "successRoute": "/sales/orders",
        "cancelRoute": "/sales/orders",
        "sections": [
            {
                "id": "customer",
                "title": "Customer Information",
                "gridClass": "grid-cols-2",
                "fields": [
                    {
                        "name": "customer_id",
                        "label": "Customer",
                        "type": "select",
                        "required": True,
                        "colSpan": 2,
                        "optionsEndpoint": "/api/v1/customers",
                        "optionLabelField": "name",
                        "optionValueField": "id",
                        "placeholder": "Select a customer"
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
                    }
                ]
            },
            {
                "id": "items",
                "title": "Order Items",
                "fields": [
                    {
                        "name": "items",
                        "type": "array",
                        "label": "Line Items",
                        "required": True,
                        "minItems": 1,
                        "itemFields": [
                            {
                                "name": "product_id",
                                "label": "Product",
                                "type": "select",
                                "required": True,
                                "optionsEndpoint": "/api/v1/products",
                                "optionLabelField": "name",
                                "optionValueField": "id"
                            },
                            {
                                "name": "quantity",
                                "label": "Quantity",
                                "type": "number",
                                "required": True,
                                "min": 1,
                                "defaultValue": 1
                            },
                            {
                                "name": "unit_price",
                                "label": "Unit Price",
                                "type": "number",
                                "required": True,
                                "prefix": "$",
                                "step": 0.01
                            },
                            {
                                "name": "discount_percent",
                                "label": "Discount %",
                                "type": "number",
                                "min": 0,
                                "max": 100,
                                "defaultValue": 0
                            },
                            {
                                "name": "line_total",
                                "label": "Total",
                                "type": "display",
                                "prefix": "$",
                                "compute": """
                                    function(item) {
                                        const qty = item.quantity || 0;
                                        const price = item.unit_price || 0;
                                        const discount = item.discount_percent || 0;
                                        const subtotal = qty * price;
                                        return subtotal - (subtotal * discount / 100);
                                    }
                                """
                            }
                        ]
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
@router.get("/pricing/form")
async def get_pricing_rules_form_schema() -> Dict[str, Any]:
    """Get pricing rules form UI schema"""
    return {
        "title": "Pricing Rule",
        "endpoint": "/api/v1/pricing/rules",
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
                        "optionsEndpoint": "/api/v1/customers",
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
                        "optionsEndpoint": "/api/v1/product-categories",
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
@router.get("/analytics/dashboard")
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
                "endpoint": "/api/v1/analytics/revenue-by-month",
                "chartType": "bar",
                "span": 2,
                "height": 350
            },
            {
                "id": "sales_by_product",
                "type": "chart",
                "title": "Sales by Product",
                "endpoint": "/api/v1/analytics/sales-by-product",
                "chartType": "pie",
                "span": 1,
                "height": 300
            },
            {
                "id": "sales_by_customer",
                "type": "chart",
                "title": "Top 10 Customers",
                "endpoint": "/api/v1/analytics/top-customers",
                "chartType": "bar",
                "span": 1,
                "height": 300
            },
            {
                "id": "conversion_metrics",
                "type": "metrics",
                "title": "Conversion Metrics",
                "endpoint": "/api/v1/analytics/conversion-metrics",
                "span": 2,
                "metrics": [
                    {"label": "Quote to Order", "field": "quote_conversion", "format": "percentage"},
                    {"label": "Average Order Value", "field": "avg_order_value", "format": "currency"},
                    {"label": "Customer Retention", "field": "retention_rate", "format": "percentage"},
                    {"label": "Sales Growth", "field": "growth_rate", "format": "percentage"}
                ]
            }
        ]
    }