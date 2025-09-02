#!/usr/bin/env python3
"""
Script to register menu service UI components with the UI Registry.
"""
import httpx
import json
import sys
import os

# UI Registry endpoint - detect if running in container or host
# If in container, use Kong gateway; if on host, use direct access
if os.path.exists('/.dockerenv'):
    # Running inside container - use Kong gateway
    UI_REGISTRY_URL = "http://kong:8000"
    UI_REGISTRY_PATH_PREFIX = "/api/v1/ui-registry"
else:
    # Running on host - use direct access
    UI_REGISTRY_URL = "http://localhost:8010"
    UI_REGISTRY_PATH_PREFIX = "/api/v1"

# Menu Service UI Package Definition
MENU_UI_PACKAGE = {
    "widgets": [
        {
            "id": "total-menus",
            "title": "Total Menu Items",
            "type": "metric",
            "size": "small",
            "data_endpoint": "/api/v1/menus/statistics/summary",
            "refresh_interval": 300,
            "config": {
                "field": "total_menus",
                "format": "number",
                "color": "blue",
                "icon": "bars"
            }
        },
        {
            "id": "active-menus",
            "title": "Active Menus",
            "type": "metric",
            "size": "small",
            "data_endpoint": "/api/v1/menus/statistics/summary",
            "refresh_interval": 300,
            "config": {
                "field": "active_menus",
                "format": "number",
                "color": "green",
                "icon": "check-circle"
            }
        },
        {
            "id": "menu-levels",
            "title": "Menu Levels",
            "type": "metric",
            "size": "small",
            "data_endpoint": "/api/v1/menus/statistics/summary",
            "refresh_interval": 600,
            "config": {
                "field": "max_level",
                "format": "number",
                "color": "purple",
                "icon": "sitemap"
            }
        },
        {
            "id": "menu-distribution",
            "title": "Menu Items by Type",
            "type": "chart",
            "size": "medium",
            "data_endpoint": "/api/v1/menus/statistics/summary",
            "refresh_interval": 600,
            "config": {
                "chart_type": "pie",
                "data_field": "by_type",
                "x_field": "type",
                "y_field": "count"
            }
        },
        {
            "id": "recent-menu-changes",
            "title": "Recent Menu Changes",
            "type": "list",
            "size": "large",
            "data_endpoint": "/api/v1/menus/?limit=5&sort=updated_at&order=desc",
            "refresh_interval": 60,
            "config": {
                "limit": 5,
                "columns": ["title", "updated_at"]
            }
        }
    ],
    "lists": [
        {
            "id": "menus-list",
            "title": "Menu Configuration",
            "entity": "menus",
            "data_endpoint": "/api/v1/menus",
            "columns": [
                {"key": "title", "label": "Menu Title", "sortable": True},
                {"key": "code", "label": "Code", "sortable": True},
                {"key": "level", "label": "Level", "format": "number"},
                {"key": "item_type", "label": "Type"},
                {"key": "parent_title", "label": "Parent"},
                {"key": "order_index", "label": "Order", "format": "number"},
                {"key": "is_active", "label": "Status", "format": "badge"}
            ],
            "actions": [
                {"id": "edit", "label": "Edit", "icon": "pencil"},
                {"id": "toggle", "label": "Toggle Status", "icon": "power"},
                {"id": "delete", "label": "Delete", "icon": "trash", "confirm": True}
            ],
            "filters": [
                {"field": "level", "type": "select", "label": "Level", "options": ["0", "1", "2"]},
                {"field": "item_type", "type": "select", "label": "Type", "options": ["link", "dropdown", "header", "divider"]},
                {"field": "is_active", "type": "select", "label": "Status", "options": ["true", "false"]}
            ]
        }
    ],
    "forms": [
        {
            "id": "menu-form",
            "title": "Menu Item Details",
            "entity": "menu",
            "mode": "create",
            "submit_endpoint": "/api/v1/menus",
            "data_endpoint": "/api/v1/menus/{id}",
            "fields": [
                {"name": "title", "label": "Menu Title", "type": "text", "required": True},
                {"name": "code", "label": "Menu Code", "type": "text", "required": True},
                {"name": "description", "label": "Description", "type": "textarea"},
                {"name": "item_type", "label": "Item Type", "type": "select", "options": [
                    {"label": "Link", "value": "link"},
                    {"label": "Dropdown", "value": "dropdown"},
                    {"label": "Header", "value": "header"},
                    {"label": "Divider", "value": "divider"}
                ], "required": True},
                {"name": "url", "label": "URL Path", "type": "text"},
                {"name": "parent_id", "label": "Parent Menu", "type": "select", "data_source": "/api/v1/menus?level=0"},
                {"name": "order_index", "label": "Display Order", "type": "number", "min": 0},
                {"name": "icon", "label": "Icon Class", "type": "text"},
                {"name": "required_permission", "label": "Required Permission", "type": "select", "data_source": "/api/v1/permissions"},
                {"name": "required_role_level", "label": "Minimum Role Level", "type": "number", "min": 1},
                {"name": "is_active", "label": "Active", "type": "checkbox", "defaultValue": True},
                {"name": "is_visible", "label": "Visible", "type": "checkbox", "defaultValue": True}
            ],
            "layout": "single"
        }
    ],
    "components": [
        {
            "id": "menu-dashboard",
            "type": "dashboard",
            "title": "Menu Dashboard",
            "path": "/settings/menus/dashboard",
            "icon": "chart-bar",
            "config": {
                "layout": [
                    {"widget": "total-menus", "row": 0, "col": 0},
                    {"widget": "active-menus", "row": 0, "col": 1},
                    {"widget": "menu-levels", "row": 0, "col": 2},
                    {"widget": "menu-distribution", "row": 1, "col": 0, "colspan": 2},
                    {"widget": "recent-menu-changes", "row": 1, "col": 2}
                ]
            }
        }
    ]
}

async def register_ui_package():
    """Register the menu UI package with the UI Registry"""
    try:
        print(f"Attempting to connect to UI Registry at: {UI_REGISTRY_URL}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Register the complete UI package
            url = f"{UI_REGISTRY_URL}{UI_REGISTRY_PATH_PREFIX}/services/menu-access-service/ui-package"
            print(f"Sending POST request to: {url}")
            response = await client.post(
                url,
                json=MENU_UI_PACKAGE,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ Successfully registered menu UI package")
                result = response.json()
                print(f"   Status: {result.get('status')}")
                print(f"   Service: {result.get('service')}")
                
                # Verify registration
                print("\n📊 Registered components:")
                
                # Check widgets
                widgets_response = await client.get(f"{UI_REGISTRY_URL}{UI_REGISTRY_PATH_PREFIX}/dashboard/widgets")
                if widgets_response.status_code == 200:
                    widgets = widgets_response.json()
                    menu_widgets = [w for w in widgets if w.get('service') == 'menu-access-service']
                    print(f"   - {len(menu_widgets)} dashboard widgets")
                    for widget in menu_widgets:
                        print(f"     • {widget['id']}: {widget['title']}")
                
                # Check lists
                lists_response = await client.get(f"{UI_REGISTRY_URL}{UI_REGISTRY_PATH_PREFIX}/lists")
                if lists_response.status_code == 200:
                    lists = lists_response.json()
                    menu_lists = [l for l in lists if l.get('service') == 'menu-access-service']
                    print(f"   - {len(menu_lists)} list views")
                    for lst in menu_lists:
                        print(f"     • {lst['id']}: {lst['title']}")
                
                # Check forms
                forms_response = await client.get(f"{UI_REGISTRY_URL}{UI_REGISTRY_PATH_PREFIX}/forms")
                if forms_response.status_code == 200:
                    forms = forms_response.json()
                    menu_forms = [f for f in forms if f.get('service') == 'menu-access-service']
                    print(f"   - {len(menu_forms)} form views")
                    for form in menu_forms:
                        print(f"     • {form['id']}: {form['title']}")
                
                return True
            else:
                print(f"❌ Failed to register UI package: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except httpx.ConnectError as e:
        print(f"❌ Could not connect to UI Registry Service: {e}")
        print(f"   Make sure the service is running at {UI_REGISTRY_URL}")
        return False
    except httpx.TimeoutException as e:
        print(f"❌ Timeout connecting to UI Registry Service: {e}")
        return False
    except Exception as e:
        print(f"❌ Error registering UI package: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 Registering Menu Service UI Components")
    print("=" * 50)
    
    success = await register_ui_package()
    
    if success:
        print("\n✨ Menu UI components are now available in the UI Registry!")
        print("   The UI service can now fetch and render these components dynamically.")
    else:
        print("\n⚠️  Failed to register UI components. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())