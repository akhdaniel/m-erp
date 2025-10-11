"""
UI component definitions for the Sales Service.

Defines dashboard widgets, list views, and forms that the sales service
registers with the UI Registry for display in the generic UI service.
"""

SALES_UI_PACKAGE = {
    "version": "1.0.0", 
    "widgets": [
        {
            "id": "total-quotes",
            "title": "Active Quotations",
            "type": "metric",
            "size": "small",
            "endpoint": "/api/v1/sales/metrics/quotes",
            "refresh_interval": 300,
            "config": {
                "field": "active_quotes",
                "format": "number",
                "color": "blue",
                "icon": "file-text",
                "link": "/sales/quotes"
            }
        },
        {
            "id": "pending-orders",
            "title": "Pending Orders",
            "type": "metric", 
            "size": "small",
            "endpoint": "/api/v1/sales/metrics/orders",
            "refresh_interval": 60,
            "valueField":"total_revenue",
            "config": {
                "field": "pending_orders",
                "format": "number",
                "color": "orange",
                "icon": "clock",
                "link": "/sales/orders?status=pending"
            }
        },
        {
            "id": "monthly-revenue",
            "title": "Monthly Revenue",
            "type": "metric",
            "size": "small",
            "endpoint": "/api/v1/sales/metrics/orders",
            "refresh_interval": 3600,
            "valueField":"total_revenue",
            "config": {
                "field": "current_month_revenue",
                "format": "currency",
                "color": "green",
                "icon": "dollar-sign"
            }
        },
        {
            "id": "conversion-rate",
            "title": "Quotation Conversion Rate",
            "type": "metric",
            "size": "small",
            "endpoint": "/api/v1/sales/metrics/quotes/analytics",
            "refresh_interval": 3600,
            "config": {
                "field": "conversion_rate",
                "format": "percentage",
                "color": "purple",
                "icon": "trending-up"
            }
        },
        {
            "id": "recent-orders",
            "title": "Recent Orders",
            "type": "list",
            "size": "large",
            "endpoint": "/api/v1/sales/transactions?limit=10",
            "refresh_interval": 60,
            "config": {
                "limit": 10,
                "columns": ["order_number", "customer_name", "total_amount", "status", "order_date"],
                "link_pattern": "/transactions/{id}"
            }
        },
        {
            "id": "revenue-chart",
            "title": "Revenue Trend",
            "type": "chart",
            "size": "medium",
            "endpoint": "/api/v1/sales/orders/analytics/revenue-trend",
            "refresh_interval": 3600,
            "config": {
                "chart_type": "line",
                "x_field": "date",
                "y_field": "revenue",
                "period": "last_30_days"
            }
        },
        {
            "id": "top-customers",
            "title": "Top Customers",
            "type": "table",
            "size": "medium",
            "endpoint": "/api/v1/sales/orders/analytics/top-customers",
            "refresh_interval": 3600,
            "config": {
                "columns": [{"field":"customer_name","label":"Customer"}, 
                            {"field":"order_count","label":"Order Count","formatter":"number"}, 
                            {"field":"total_revenue","label":"Total Revenue","formatter":"currency"}, 
                            {"field":"average_order_value","label":"Average Order","formatter":"currency"}],
                "limit": 5,
                "sortable": True
            }
        },
        {
            "id": "sales-pipeline",
            "title": "Sales Pipeline",
            "type": "chart",
            "size": "medium",
            "endpoint": "/api/v1/sales/quotations/pipeline",
            "refresh_interval": 600,
            "config": {
                "chart_type": "funnel",
                "stages": ["draft", "sent", "viewed", "accepted", "rejected"]
            }
        }
    ],
    "lists": [
        {
            "id": "quotes-list",
            "title": "Quotations",
            "entity": "quotes",
            "endpoint": "/api/v1/sales/quotes",
            "columns": [
                {"key": "quote_number", "label": "Quotation #", "sortable": True},
                {"key": "title", "label": "Title", "sortable": True},
                {"key": "customer_name", "label": "Customer", "sortable": True},
                {"key": "total_amount", "label": "Amount", "format": "currency", "sortable": True},
                {"key": "status", "label": "Status", "format": "badge"},
                {"key": "valid_until", "label": "Valid Until", "format": "date"},
                {"key": "created_at", "label": "Created", "format": "datetime", "sortable": True}
            ],
            "actions": [
                {"id": "view", "label": "View", "icon": "eye"},
                {"id": "edit", "label": "Edit", "icon": "edit"},
                {"id": "send", "label": "Send", "icon": "send"},
                {"id": "convert", "label": "Convert to Order", "icon": "arrow-right"},
                {"id": "delete", "label": "Delete", "icon": "trash", "confirm": True}
            ],
            "filters": [
                {"field": "status", "type": "select", "label": "Status", 
                 "options": ["draft", "sent", "viewed", "accepted", "rejected", "expired"]},
                {"field": "customer_id", "type": "autocomplete", "label": "Customer", "data_source": "/api/v1/sales/partners"},
                {"field": "date_range", "type": "daterange", "label": "Date Range"}
            ],
            "pagination": True,
            "permissions": ["sales.quotes.view"]
        },
        {
            "id": "orders-list",
            "title": "Orders",
            "entity": "orders",
            "endpoint": "/api/v1/sales/orders",
            "columns": [
                {"key": "order_number", "label": "Order #", "sortable": True},
                {"key": "customer_name", "label": "Customer", "sortable": True},
                {"key": "total_amount", "label": "Total", "format": "currency", "sortable": True},
                {"key": "status", "label": "Status", "format": "badge"},
                {"key": "payment_status", "label": "Payment", "format": "badge"},
                {"key": "order_date", "label": "Order Date", "format": "date", "sortable": True},
                {"key": "required_date", "label": "Required By", "format": "date"}
            ],
            "actions": [
                {"id": "view", "label": "View", "icon": "eye"},
                {"id": "edit", "label": "Edit", "icon": "edit"},
                {"id": "ship", "label": "Create Shipment", "icon": "truck"},
                {"id": "invoice", "label": "Create Invoice", "icon": "file-text"},
                {"id": "cancel", "label": "Cancel", "icon": "x-circle", "confirm": True}
            ],
            "filters": [
                {"field": "status", "type": "select", "label": "Order Status",
                 "options": ["pending", "confirmed", "processing", "shipped", "delivered", "completed", "cancelled"]},
                {"field": "payment_status", "type": "select", "label": "Payment Status",
                 "options": ["unpaid", "partial", "paid", "refunded"]},
                {"field": "customer_id", "type": "autocomplete", "label": "Customer", "data_source": "/api/v1/sales/partners"},
                {"field": "date_range", "type": "daterange", "label": "Order Date"}
            ],
            "pagination": True,
            "permissions": ["sales.orders.view"]
        },
        {
            "id": "pricing-rules-list",
            "title": "Pricing Rules",
            "entity": "pricing_rules",
            "endpoint": "/api/v1/sales/pricing/rules",
            "columns": [
                {"key": "rule_name", "label": "Rule Name", "sortable": True},
                {"key": "rule_type", "label": "Type", "format": "badge"},
                {"key": "priority", "label": "Priority", "sortable": True},
                {"key": "discount_percentage", "label": "Discount %", "format": "percentage"},
                {"key": "valid_from", "label": "Valid From", "format": "date"},
                {"key": "valid_to", "label": "Valid To", "format": "date"},
                {"key": "is_active", "label": "Active", "format": "boolean"}
            ],
            "actions": [
                {"id": "edit", "label": "Edit", "icon": "edit"},
                {"id": "duplicate", "label": "Duplicate", "icon": "copy"},
                {"id": "toggle", "label": "Enable/Disable", "icon": "toggle-left"},
                {"id": "delete", "label": "Delete", "icon": "trash", "confirm": True}
            ],
            "filters": [
                {"field": "rule_type", "type": "select", "label": "Rule Type",
                 "options": ["customer_specific", "volume_discount", "promotional", "product_category"]},
                {"field": "is_active", "type": "boolean", "label": "Active Only"}
            ],
            "pagination": True,
            "permissions": ["sales.pricing.manage"]
        }
    ],
    "forms": [
        {
            "id": "quote-form",
            "title": "Quotation Details",
            "entity": "quote",
            "mode": "create",
            "submit_endpoint": "/api/v1/sales/quotes",
            "endpoint": "/api/v1/sales/quotes/{id}",
            "fields": [
                {"name": "title", "label": "Quotation Title", "type": "text", "required": True},
                {"name": "customer_id", "label": "Customer", "type": "autocomplete", 
                 "data_source": "/api/v1/sales/partners?type=customer", "required": True},
                {"name": "valid_until", "label": "Valid Until", "type": "date", "required": True},
                {"name": "payment_terms_days", "label": "Payment Terms (days)", "type": "number", 
                 "min": 0, "max": 365, "default": 30},
                {"name": "currency_code", "label": "Currency", "type": "select", 
                 "options": ["USD", "EUR", "GBP"], "default": "USD"},
                {"name": "description", "label": "Description", "type": "textarea"},
                {"name": "terms_and_conditions", "label": "Terms & Conditions", "type": "textarea"},
                {"name": "line_items", "label": "Line Items", "type": "array",
                 "fields": [
                    {"name": "product_id", "label": "Product", "type": "select", "data_source": "/api/v1/sales/products"},
                    {"name": "quantity", "label": "Quantity", "type": "number", "min": 1},
                    {"name": "unit_price", "label": "Unit Price", "type": "number", "min": 0},
                    {"name": "discount_percentage", "label": "Discount %", "type": "number", "min": 0, "max": 100}
                 ]}
            ],
            "layout": "single",
            "permissions": ["sales.quotes.create"],
            "validation_rules": {
                "valid_until": {"min": "today"}
            }
        },
        {
            "id": "order-form",
            "title": "Order Details",
            "entity": "order",
            "mode": "create",
            "submit_endpoint": "/api/v1/sales/orders",
            "endpoint": "/api/v1/sales/orders/{id}",
            "fields": [
                {"name": "title", "label": "Order Title", "type": "text", "required": True},
                {"name": "customer_id", "label": "Customer", "type": "autocomplete",
                 "data_source": "/api/v1/sales/partners?type=customer", "required": True},
                {"name": "quote_id", "label": "From Quotation", "type": "select",
                 "data_source": "/api/v1/sales/quotes?status=accepted"},
                {"name": "required_date", "label": "Required Date", "type": "date"},
                {"name": "priority", "label": "Priority", "type": "select",
                 "options": ["low", "normal", "high", "urgent"], "default": "normal"},
                {"name": "payment_terms_days", "label": "Payment Terms (days)", "type": "number",
                 "min": 0, "max": 365, "default": 30},
                {"name": "shipping_method", "label": "Shipping Method", "type": "select",
                 "options": ["standard", "express", "overnight"]},
                {"name": "billing_address", "label": "Billing Address", "type": "address"},
                {"name": "shipping_address", "label": "Shipping Address", "type": "address"},
                {"name": "line_items", "label": "Line Items", "type": "array",
                 "fields": [
                    {"name": "product_id", "label": "Product", "type": "select", "data_source": "/api/v1/sales/products"},
                    {"name": "quantity", "label": "Quantity", "type": "number", "min": 1},
                    {"name": "unit_price", "label": "Unit Price", "type": "number", "min": 0}
                 ]}
            ],
            "layout": "multi-column",
            "permissions": ["sales.orders.create"]
        },
        {
            "id": "pricing-rule-form",
            "title": "Pricing Rule",
            "entity": "pricing_rule",
            "mode": "create",
            "submit_endpoint": "/api/v1/sales/pricing/rules",
            "endpoint": "/api/v1/sales/pricing/rules/{id}",
            "fields": [
                {"name": "rule_name", "label": "Rule Name", "type": "text", "required": True},
                {"name": "rule_type", "label": "Rule Type", "type": "select",
                 "options": ["customer_specific", "volume_discount", "promotional", "product_category"],
                 "required": True},
                {"name": "priority", "label": "Priority", "type": "number", "min": 0, "max": 100, "default": 50},
                {"name": "discount_percentage", "label": "Discount %", "type": "number", 
                 "min": 0, "max": 100, "step": 0.01},
                {"name": "fixed_discount_amount", "label": "Fixed Discount", "type": "number", "min": 0},
                {"name": "min_quantity", "label": "Minimum Quantity", "type": "number", "min": 0},
                {"name": "max_quantity", "label": "Maximum Quantity", "type": "number", "min": 0},
                {"name": "valid_from", "label": "Valid From", "type": "datetime"},
                {"name": "valid_to", "label": "Valid To", "type": "datetime"},
                {"name": "customer_ids", "label": "Specific Customers", "type": "multiselect",
                 "data_source": "/api/v1/sales/partners?type=customer"},
                {"name": "product_ids", "label": "Specific Products", "type": "multiselect",
                 "data_source": "/api/v1/sales/products"},
                {"name": "is_active", "label": "Active", "type": "boolean", "default": True}
            ],
            "layout": "single",
            "permissions": ["sales.pricing.manage"]
        }
    ],
    "dashboard": {
        "id": "sales-dashboard",
        "type": "dashboard",
        "title": "Sales Dashboard",
        "path": "/sales/dashboard",
        "icon": "shopping-cart",
        "config": {
            "layout": [
                {"widget": "total-quotes", "row": 0, "col": 0},
                {"widget": "pending-orders", "row": 0, "col": 1},
                {"widget": "monthly-revenue", "row": 0, "col": 2},
                {"widget": "conversion-rate", "row": 0, "col": 3},
                {"widget": "recent-orders", "row": 1, "col": 0, "colspan": 2},
                {"widget": "revenue-chart", "row": 1, "col": 2, "colspan": 2},
                {"widget": "top-customers", "row": 2, "col": 0, "colspan": 2},
                {"widget": "sales-pipeline", "row": 2, "col": 2, "colspan": 2}
            ]
        },
        "permissions": ["sales.dashboard.view"],
        "order": 2,
        "metadata": {
            "refresh_interval": 60,
            "mobile_layout": "stacked"
        }
    }
    
}