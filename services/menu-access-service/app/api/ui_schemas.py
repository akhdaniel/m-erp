"""
UI Schema definitions for Menu Configuration
Provides schema definitions for the menu configuration UI
"""

from fastapi import APIRouter, Depends
from typing import Any, Dict

router = APIRouter(prefix="/ui-schemas", tags=["UI Schemas"])


@router.get("/menus/list")
async def get_menus_list_schema() -> Dict[str, Any]:
    """Get UI schema for menus list view"""
    return {
        "title": "Menu Configuration",
        "description": "View and manage all service menus in the system",
        "viewType": "table",
        "endpoint": "/api/v1/menus/",
        "keyField": "id",
        "searchable": True,
        "searchPlaceholder": "Search menus by title or code...",
        "searchParam": "search",
        "paginated": True,
        "pageSize": 20,
        "refreshable": True,
        "createable": True,
        "createLabel": "New Menu",
        "createRoute": "/settings/menus/new",
        "editRoute": "/settings/menus/{id}/edit",
        "clickable": True,
        
        "columns": [
            {
                "field": "title",
                "label": "Menu Title",
                "visible": True,
                "isTitle": True,
                "sortable": True,
                "cellClass": "font-medium text-gray-900"
            },
            {
                "field": "code",
                "label": "Code",
                "visible": True,
                "sortable": True
            },
            {
                "field": "level",
                "label": "Level",
                "visible": True,
                "formatter": "number"
            },
            {
                "field": "item_type",
                "label": "Type",
                "visible": True,
                "formatter": """
                    function(value) {
                        const typeMap = {
                            'link': 'Link',
                            'dropdown': 'Dropdown',
                            'header': 'Header',
                            'divider': 'Divider'
                        };
                        return typeMap[value] || value;
                    }
                """
            },
            {
                "field": "parent_title",
                "label": "Parent",
                "visible": True
            },
            {
                "field": "order_index",
                "label": "Order",
                "visible": True,
                "formatter": "number",
                "sortable": True
            },
            {
                "field": "is_active",
                "label": "Status",
                "visible": True,
                "formatter": "boolean",
                "cellClassFunction": """
                    function(value) {
                        return value ? 'text-green-600' : 'text-gray-400';
                    }
                """
            },
            {
                "field": "required_permission",
                "label": "Permission",
                "visible": True
            }
        ],
        
        "filters": [
            {
                "field": "level",
                "label": "Level",
                "type": "select",
                "placeholder": "All Levels",
                "options": [
                    {"label": "Root (0)", "value": "0"},
                    {"label": "Submenu (1)", "value": "1"},
                    {"label": "Nested (2+)", "value": "2"}
                ]
            },
            {
                "field": "item_type",
                "label": "Type",
                "type": "select",
                "placeholder": "All Types",
                "options": [
                    {"label": "Link", "value": "link"},
                    {"label": "Dropdown", "value": "dropdown"},
                    {"label": "Header", "value": "header"},
                    {"label": "Divider", "value": "divider"}
                ]
            },
            {
                "field": "is_active",
                "label": "Status",
                "type": "select",
                "placeholder": "All Status",
                "options": [
                    {"label": "Active", "value": "true"},
                    {"label": "Inactive", "value": "false"}
                ]
            }
        ],
        
        "rowActions": [
            {
                "id": "edit",
                "label": "Edit",
                "icon": "pencil",
                "route": "/settings/menus/{id}/edit"
            },
            {
                "id": "toggle",
                "label": "Toggle Status",
                "icon": "power",
                "action": "toggle_status"
            },
            {
                "id": "delete",
                "label": "Delete",
                "icon": "trash",
                "action": "delete",
                "confirm": True,
                "confirmMessage": "Are you sure you want to delete this menu item? This will also delete all child items."
            }
        ],
        
        "headerActions": [
            {
                "id": "refresh",
                "label": "Refresh",
                "icon": "refresh"
            },
            {
                "id": "export",
                "label": "Export",
                "icon": "download",
                "variant": "secondary"
            }
        ]
    }


@router.get("/menus/form")
async def get_menus_form_schema() -> Dict[str, Any]:
    """Get UI schema for menu form (create/edit)"""
    return {
        "title": "Menu Item Details",
        "description": "Configure menu item properties",
        "endpoint": "/api/v1/menus",
        "successRoute": "/settings/menus",
        "cancelRoute": "/settings/menus",
        "submitLabel": "Save Menu Item",
        "cancelLabel": "Cancel",
        
        "breadcrumbs": [
            {"label": "Settings", "route": "/settings"},
            {"label": "Menus", "route": "/settings/menus"},
            {"label": "Menu Item Details"}
        ],
        
        "sections": [
            {
                "id": "basic",
                "title": "Basic Information",
                "gridClass": "grid grid-cols-1 gap-6 sm:grid-cols-2",
                "fields": [
                    {
                        "name": "title",
                        "label": "Menu Title",
                        "type": "text",
                        "required": True,
                        "placeholder": "Enter menu title",
                        "colSpan": 2
                    },
                    {
                        "name": "code",
                        "label": "Menu Code",
                        "type": "text",
                        "required": True,
                        "placeholder": "Unique code identifier (e.g., inventory_management)",
                        "help": "Must be unique across all menu items"
                    },
                    {
                        "name": "description",
                        "label": "Description",
                        "type": "textarea",
                        "rows": 2,
                        "placeholder": "Brief description of this menu item"
                    },
                    {
                        "name": "item_type",
                        "label": "Item Type",
                        "type": "select",
                        "required": True,
                        "defaultValue": "link",
                        "options": [
                            {"label": "Link", "value": "link"},
                            {"label": "Dropdown", "value": "dropdown"},
                            {"label": "Header", "value": "header"},
                            {"label": "Divider", "value": "divider"}
                        ],
                        "help": "Link: Navigates to a page, Dropdown: Contains sub-items"
                    }
                ]
            },
            {
                "id": "navigation",
                "title": "Navigation Settings",
                "gridClass": "grid grid-cols-1 gap-6 sm:grid-cols-2",
                "fields": [
                    {
                        "name": "url",
                        "label": "URL Path",
                        "type": "text",
                        "placeholder": "/path/to/page",
                        "help": "URL path for link items (leave empty for dropdowns)",
                        "visible": {
                            "field": "item_type",
                            "operator": "!=",
                            "value": "dropdown"
                        }
                    },
                    {
                        "name": "parent_id",
                        "label": "Parent Menu",
                        "type": "select",
                        "placeholder": "Select parent menu (optional)",
                        "optionsEndpoint": "/api/v1/menus/?level=0",
                        "optionLabelField": "title",
                        "optionValueField": "id",
                        "help": "Select a parent menu to create a submenu item"
                    },
                    {
                        "name": "order_index",
                        "label": "Display Order",
                        "type": "number",
                        "min": 0,
                        "defaultValue": 0,
                        "help": "Lower numbers appear first in the menu"
                    },
                    {
                        "name": "icon",
                        "label": "Icon Class",
                        "type": "text",
                        "placeholder": "fas fa-icon-name",
                        "help": "Font Awesome icon class (e.g., fas fa-box)"
                    }
                ]
            },
            {
                "id": "permissions",
                "title": "Access Control",
                "gridClass": "grid grid-cols-1 gap-6 sm:grid-cols-2",
                "fields": [
                    {
                        "name": "required_permission",
                        "label": "Required Permission",
                        "type": "select",
                        "placeholder": "Select required permission (optional)",
                        "optionsEndpoint": "/api/v1/permissions/",
                        "optionLabelField": "name",
                        "optionValueField": "code",
                        "help": "Users must have this permission to see this menu"
                    },
                    {
                        "name": "required_role_level",
                        "label": "Minimum Role Level",
                        "type": "number",
                        "min": 1,
                        "placeholder": "Enter minimum role level (optional)",
                        "help": "Users must have this role level or higher"
                    },
                    {
                        "name": "is_active",
                        "label": "Active",
                        "type": "checkbox",
                        "defaultValue": True,
                        "colSpan": 2,
                        "help": "Inactive menus are hidden from users"
                    },
                    {
                        "name": "is_visible",
                        "label": "Visible",
                        "type": "checkbox",
                        "defaultValue": True,
                        "colSpan": 2,
                        "help": "Invisible menus are not shown but still functional"
                    }
                ]
            }
        ]
    }


@router.get("/menus/dashboard")
async def get_menus_dashboard_schema() -> Dict[str, Any]:
    """Get UI schema for menus dashboard view"""
    return {
        "title": "Menu Dashboard",
        "description": "Overview of menu system and configuration",
        "viewType": "dashboard",
        "refreshInterval": 30000,  # 30 seconds
        "layout": {
            "columns": 3,
            "rows": "auto"
        },
        "widgets": [
            {
                "id": "total_menus",
                "type": "metric",
                "title": "Total Menu Items",
                "endpoint": "/api/v1/menus/statistics/summary",
                "valueField": "total_menus",
                "format": "number",
                "icon": "bars",
                "color": "blue",
                "span": 1
            },
            {
                "id": "active_menus",
                "type": "metric",
                "title": "Active Menus",
                "endpoint": "/api/v1/menus/statistics/summary",
                "valueField": "active_menus",
                "format": "number",
                "icon": "check-circle",
                "color": "green",
                "span": 1
            },
            {
                "id": "menu_levels",
                "type": "metric",
                "title": "Menu Levels",
                "endpoint": "/api/v1/menus/statistics/summary",
                "valueField": "max_level",
                "format": "number",
                "icon": "sitemap",
                "color": "purple",
                "span": 1
            },
            {
                "id": "menu_distribution",
                "type": "chart",
                "title": "Menu Items by Type",
                "endpoint": "/api/v1/menus/statistics/summary",
                "chartType": "pie",
                "dataField": "by_type",
                "span": 2,
                "height": 300
            },
            {
                "id": "recent_changes",
                "type": "list",
                "title": "Recent Menu Changes",
                "endpoint": "/api/v1/menus/?limit=5&sort=updated_at&order=desc",
                "limit": 5,
                "span": 1,
                "columns": [
                    {"field": "title", "label": "Menu"},
                    {"field": "updated_at", "label": "Updated", "formatter": "datetime"}
                ]
            }
        ]
    }