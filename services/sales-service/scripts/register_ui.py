#!/usr/bin/env python3
"""
Script to register sales service UI components with the UI Registry.
This demonstrates the service-driven UI architecture.
"""

import requests
import json
import sys

# UI Registry endpoint
UI_REGISTRY_URL = "http://ui-registry-service:8010"

# Sales UI Package Definition
SALES_UI_PACKAGE = {
    "widgets": [
        {
            "id": "monthly-revenue",
            "title": "Monthly Revenue",
            "type": "metric",
            "size": "small",
            "data_endpoint": "/api/v1/dashboard/metrics/revenue",
            "refresh_interval": 300,
            "config": {
                "field": "amount",
                "format": "currency",
                "color": "green",
                "icon": "dollar-sign"
            }
        },
        {
            "id": "active-quotations",
            "title": "Active Quotations",
            "type": "metric",
            "size": "small",
            "data_endpoint": "/api/v1/dashboard/metrics/quotations",
            "refresh_interval": 300,
            "config": {
                "field": "count",
                "format": "number",
                "color": "blue",
                "icon": "file-text"
            }
        },
        {
            "id": "pending-orders",
            "title": "Pending Orders",
            "type": "metric",
            "size": "small",
            "data_endpoint": "/api/v1/dashboard/metrics/orders",
            "refresh_interval": 300,
            "config": {
                "field": "count",
                "format": "number",
                "color": "orange",
                "icon": "shopping-bag"
            }
        },
        {
            "id": "revenue-trend",
            "title": "Revenue Trend",
            "type": "chart",
            "size": "medium",
            "data_endpoint": "/api/v1/dashboard/charts/revenue-trend",
            "refresh_interval": 600,
            "config": {
                "chart_type": "line",
                "x_field": "month",
                "y_field": "revenue"
            }
        },
        {
            "id": "sales-pipeline",
            "title": "Sales Pipeline",
            "type": "chart",
            "size": "medium",
            "data_endpoint": "/api/v1/dashboard/charts/sales-pipeline",
            "refresh_interval": 600,
            "config": {
                "chart_type": "bar",
                "x_field": "stage",
                "y_field": "value"
            }
        },
        {
            "id": "recent-quotations",
            "title": "Recent Quotations",
            "type": "list",
            "size": "large",
            "data_endpoint": "/api/v1/dashboard/recent/quotations",
            "refresh_interval": 60,
            "config": {
                "limit": 5,
                "columns": ["quotation_number", "customer_name", "total_amount"]
            }
        },
        {
            "id": "top-customers",
            "title": "Top Customers",
            "type": "table",
            "size": "large",
            "data_endpoint": "/api/v1/dashboard/analytics/top-customers",
            "refresh_interval": 600,
            "config": {
                "limit": 5,
                "columns": ["name", "revenue", "orders"]
            }
        }
    ],
    "lists": [
        {
            "id": "quotations-list",
            "title": "Sales Quotations",
            "entity": "quotations",
            "data_endpoint": "/api/v1/quotations",
            "columns": [
                {"key": "quotation_number", "label": "Quotation #", "sortable": True},
                {"key": "customer_name", "label": "Customer", "sortable": True},
                {"key": "quotation_date", "label": "Date", "format": "date"},
                {"key": "total_amount", "label": "Amount", "format": "currency"},
                {"key": "status", "label": "Status", "format": "badge"}
            ],
            "actions": [
                {"id": "view", "label": "View", "icon": "eye"},
                {"id": "edit", "label": "Edit", "icon": "edit"},
                {"id": "send", "label": "Send", "icon": "send"},
                {"id": "convert", "label": "Convert to Order", "icon": "arrow-right"}
            ],
            "filters": [
                {"field": "status", "type": "select", "label": "Status", "options": ["draft", "sent", "accepted", "rejected"]},
                {"field": "customer_id", "type": "select", "label": "Customer", "data_source": "/api/v1/partners?is_customer=true"}
            ]
        },
        {
            "id": "orders-list",
            "title": "Sales Orders",
            "entity": "orders",
            "data_endpoint": "/api/v1/orders",
            "columns": [
                {"key": "order_number", "label": "Order #", "sortable": True},
                {"key": "customer_name", "label": "Customer", "sortable": True},
                {"key": "order_date", "label": "Date", "format": "date"},
                {"key": "total_amount", "label": "Amount", "format": "currency"},
                {"key": "payment_status", "label": "Payment", "format": "badge"},
                {"key": "fulfillment_status", "label": "Fulfillment", "format": "badge"}
            ],
            "actions": [
                {"id": "view", "label": "View", "icon": "eye"},
                {"id": "invoice", "label": "Generate Invoice", "icon": "file-text"},
                {"id": "ship", "label": "Ship Order", "icon": "truck"}
            ]
        },
        {
            "id": "customers-list",
            "title": "Customers",
            "entity": "customers",
            "data_endpoint": "/api/v1/partners?is_customer=true",
            "columns": [
                {"key": "name", "label": "Customer Name", "sortable": True},
                {"key": "email", "label": "Email"},
                {"key": "phone", "label": "Phone"},
                {"key": "credit_limit", "label": "Credit Limit", "format": "currency"},
                {"key": "outstanding_balance", "label": "Outstanding", "format": "currency"}
            ],
            "actions": [
                {"id": "view", "label": "View Details", "icon": "eye"},
                {"id": "orders", "label": "View Orders", "icon": "shopping-bag"},
                {"id": "quotations", "label": "View Quotations", "icon": "file-text"}
            ]
        },
        {
            "id": "pricing-rules-list",
            "title": "Pricing Rules",
            "entity": "pricing_rules",
            "data_endpoint": "/api/v1/pricing/rules",
            "columns": [
                {"key": "name", "label": "Rule Name", "sortable": True},
                {"key": "rule_type", "label": "Type"},
                {"key": "discount_value", "label": "Discount"},
                {"key": "start_date", "label": "Start Date", "format": "date"},
                {"key": "end_date", "label": "End Date", "format": "date"},
                {"key": "is_active", "label": "Status", "format": "badge"}
            ],
            "actions": [
                {"id": "edit", "label": "Edit", "icon": "edit"},
                {"id": "toggle", "label": "Toggle Status", "icon": "toggle-left"}
            ]
        }
    ],
    "forms": [
        {
            "id": "quotation-form",
            "title": "Quotation Details",
            "entity": "quotation",
            "mode": "create",
            "submit_endpoint": "/api/v1/quotations",
            "data_endpoint": "/api/v1/quotations/{id}",
            "fields": [
                {"name": "title", "label": "Quotation Title", "type": "text", "required": True},
                {"name": "customer_id", "label": "Customer", "type": "select", "data_source": "/api/v1/partners?is_customer=true", "required": True},
                {"name": "quotation_date", "label": "Quotation Date", "type": "date", "required": True},
                {"name": "valid_until", "label": "Valid Until", "type": "datetime-local"},
                {"name": "description", "label": "Description", "type": "textarea"},
                {"name": "line_items", "label": "Quotation Items", "type": "component", "component": "LineItemsManager"},
                {"name": "payment_terms_days", "label": "Payment Terms (Days)", "type": "select", "options": [
                    {"label": "Net 30", "value": 30},
                    {"label": "Net 60", "value": 60},
                    {"label": "Due on Receipt", "value": 0}
                ]},
                {"name": "internal_notes", "label": "Internal Notes", "type": "textarea"},
                {"name": "terms_and_conditions", "label": "Terms and Conditions", "type": "textarea"}
            ],
            "layout": "single"
        },
        {
            "id": "order-form",
            "title": "Order Details",
            "entity": "order",
            "submit_endpoint": "/api/v1/orders",
            "data_endpoint": "/api/v1/orders/{id}",
            "fields": [
                {"name": "title", "label": "Order Title", "type": "text", "required": True},
                {"name": "customer_id", "label": "Customer", "type": "select", "data_source": "/api/v1/partners?is_customer=true", "required": True},
                {"name": "order_date", "label": "Order Date", "type": "date", "required": True},
                {"name": "delivery_date", "label": "Delivery Date", "type": "date", "required": True},
                {"name": "description", "label": "Description", "type": "textarea"},
                {"name": "line_items", "label": "Order Items", "type": "component", "component": "LineItemsManager"},
                {"name": "payment_terms", "label": "Payment Terms", "type": "select", "options": [
                    {"label": "Net 30", "value": "net30"},
                    {"label": "Net 60", "value": "net60"},
                    {"label": "Due on Receipt", "value": "due_on_receipt"}
                ]},
                {"name": "shipping_address", "label": "Shipping Address", "type": "textarea"}
            ]
        },
        {
            "id": "pricing-rule-form",
            "title": "Pricing Rule",
            "entity": "pricing_rule",
            "submit_endpoint": "/api/v1/pricing/rules",
            "data_endpoint": "/api/v1/pricing/rules/{id}",
            "fields": [
                {"name": "name", "label": "Rule Name", "type": "text", "required": True},
                {"name": "description", "label": "Description", "type": "textarea"},
                {"name": "rule_type", "label": "Rule Type", "type": "select", "options": [
                    {"label": "Customer Specific", "value": "customer_specific"},
                    {"label": "Volume Discount", "value": "volume_discount"},
                    {"label": "Promotional", "value": "promotional"}
                ], "required": True},
                {"name": "discount_type", "label": "Discount Type", "type": "select", "options": [
                    {"label": "Percentage", "value": "percentage"},
                    {"label": "Fixed Amount", "value": "fixed_amount"}
                ], "required": True},
                {"name": "discount_value", "label": "Discount Value", "type": "number", "min": 0, "required": True},
                {"name": "start_date", "label": "Start Date", "type": "date", "required": True},
                {"name": "end_date", "label": "End Date", "type": "date"},
                {"name": "is_active", "label": "Active", "type": "checkbox", "defaultValue": True},
                {"name": "customer_ids", "label": "Specific Customers", "type": "select", "multiple": True, 
                 "data_source": "/api/v1/partners?is_customer=true", "visible_condition": "rule_type == 'customer_specific'"}
            ]
        }
    ],
    "components": [
        {
            "id": "sales-dashboard",
            "type": "dashboard",
            "title": "Sales Dashboard",
            "path": "/sales/dashboard",
            "icon": "shopping-cart",
            "config": {
                "layout": [
                    {"widget": "monthly-revenue", "row": 0, "col": 0},
                    {"widget": "active-quotations", "row": 0, "col": 1},
                    {"widget": "pending-orders", "row": 0, "col": 2},
                    {"widget": "revenue-trend", "row": 1, "col": 0, "colspan": 2},
                    {"widget": "sales-pipeline", "row": 1, "col": 2},
                    {"widget": "recent-quotations", "row": 2, "col": 0, "colspan": 2},
                    {"widget": "top-customers", "row": 2, "col": 2}
                ]
            }
        }
    ]
}

def register_ui_package():
    """Register the sales UI package with the UI Registry"""
    try:
        # Register the complete UI package
        response = requests.post(
            f"{UI_REGISTRY_URL}/api/v1/services/sales-service/ui-package",
            json=SALES_UI_PACKAGE,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Successfully registered sales UI package")
            result = response.json()
            print(f"   Status: {result.get('status')}")
            print(f"   Service: {result.get('service')}")
            
            # Verify registration
            print("\n📊 Registered components:")
            
            # Check widgets
            widgets_response = requests.get(f"{UI_REGISTRY_URL}/api/v1/dashboard/widgets")
            if widgets_response.status_code == 200:
                widgets = widgets_response.json()
                sales_widgets = [w for w in widgets if w.get('service') == 'sales-service']
                print(f"   - {len(sales_widgets)} dashboard widgets")
                for widget in sales_widgets:
                    print(f"     • {widget['id']}: {widget['title']}")
            
            # Check lists
            lists_response = requests.get(f"{UI_REGISTRY_URL}/api/v1/lists")
            if lists_response.status_code == 200:
                lists = lists_response.json()
                sales_lists = [l for l in lists if l.get('service') == 'sales-service']
                print(f"   - {len(sales_lists)} list views")
                for lst in sales_lists:
                    print(f"     • {lst['id']}: {lst['title']}")
            
            # Check forms
            forms_response = requests.get(f"{UI_REGISTRY_URL}/api/v1/forms")
            if forms_response.status_code == 200:
                forms = forms_response.json()
                sales_forms = [f for f in forms if f.get('service') == 'sales-service']
                print(f"   - {len(sales_forms)} form views")
                for form in sales_forms:
                    print(f"     • {form['id']}: {form['title']}")
            
            return True
        else:
            print(f"❌ Failed to register UI package: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to UI Registry Service")
        print("   Make sure the service is running on http://ui-registry-service:8010")
        return False
    except Exception as e:
        print(f"❌ Error registering UI package: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Registering Sales Service UI Components")
    print("=" * 50)
    
    success = register_ui_package()
    
    if success:
        print("\n✨ Sales UI components are now available in the UI Registry!")
        print("   The UI service can now fetch and render these components dynamically.")
    else:
        print("\n⚠️  Failed to register UI components. Please check the errors above.")
        sys.exit(1)