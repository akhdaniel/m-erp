"""
UI Schema definitions for inventory module
Provides schema definitions for generic UI components
"""

from fastapi import APIRouter, Depends
from typing import Any, Dict

router = APIRouter(prefix="/ui-schemas", tags=["UI Schemas"])


@router.get("/dashboard")
async def get_dashboard_schema() -> Dict[str, Any]:
    """Get UI schema for inventory dashboard"""
    return {
        "title": "Inventory Dashboard",
        "description": "Overview of inventory status and key metrics",
        "viewType": "dashboard",
        "refreshInterval": 30000,  # 30 seconds
        "layout": {
            "columns": 3,
            "rows": "auto"
        },
        "widgets": [
            {
                "id": "total_products",
                "type": "metric",
                "title": "Total Products",
                "endpoint": "/api/v1/products/stats",
                "valueField": "total",
                "format": "number",
                "icon": "package",
                "color": "blue",
                "span": 1
            },
            {
                "id": "active_products",
                "type": "metric",
                "title": "Active Products",
                "endpoint": "/api/v1/products/stats",
                "valueField": "active",
                "format": "number",
                "icon": "check-circle",
                "color": "green",
                "span": 1
            },
            {
                "id": "low_stock",
                "type": "metric",
                "title": "Low Stock Items",
                "endpoint": "/api/v1/stock/stats",
                "valueField": "low_stock_count",
                "format": "number",
                "icon": "alert-triangle",
                "color": "orange",
                "span": 1
            },
            {
                "id": "stock_value",
                "type": "metric",
                "title": "Total Stock Value",
                "endpoint": "/api/v1/stock/stats",
                "valueField": "total_value",
                "format": "currency",
                "icon": "dollar-sign",
                "color": "green",
                "span": 1
            },
            {
                "id": "warehouses",
                "type": "metric",
                "title": "Active Warehouses",
                "endpoint": "/api/v1/warehouses/stats",
                "valueField": "active",
                "format": "number",
                "icon": "building",
                "color": "purple",
                "span": 1
            },
            {
                "id": "pending_receipts",
                "type": "metric",
                "title": "Pending Receipts",
                "endpoint": "/api/v1/receiving/stats",
                "valueField": "pending_count",
                "format": "number",
                "icon": "inbox",
                "color": "yellow",
                "span": 1
            },
            {
                "id": "stock_movements",
                "type": "list",
                "title": "Recent Stock Movements",
                "endpoint": "/api/v1/stock/movements?limit=5",
                "limit": 5,
                "span": 2,
                "columns": [
                    {"field": "product_name", "label": "Product"},
                    {"field": "movement_type", "label": "Type"},
                    {"field": "quantity", "label": "Qty"},
                    {"field": "created_at", "label": "Date", "formatter": "date"}
                ]
            },
            {
                "id": "stock_levels_chart",
                "type": "chart",
                "title": "Stock Levels by Category",
                "endpoint": "/api/v1/stock/by-category",
                "chartType": "bar",
                "span": 1,
                "height": 300
            }
        ]
    }


@router.get("/products/list")
async def get_products_list_schema() -> Dict[str, Any]:
    """Get UI schema for products list view"""
    return {
        "title": "Products",
        "description": "Manage your product catalog and inventory items",
        "viewType": "table",
        "endpoint": "/api/v1/products/",
        "keyField": "id",
        "searchable": True,
        "searchPlaceholder": "Search products by name, SKU, or category...",
        "searchParam": "search",
        "paginated": True,
        "pageSize": 20,
        "refreshable": True,
        "createable": True,
        "createLabel": "New Product",
        "createRoute": "/inventory/products/new",
        "editRoute": "/inventory/products/{id}/edit",
        "clickable": True,
        
        "columns": [
            {
                "field": "name",
                "label": "Product",
                "visible": True,
                "isTitle": True,
                "cellClass": "font-medium text-gray-900"
            },
            {
                "field": "sku",
                "label": "SKU",
                "visible": True
            },
            {
                "field": "category_name",
                "label": "Category",
                "visible": True
            },
            {
                "field": "quantity_on_hand",
                "label": "Stock",
                "visible": True,
                "formatter": "number",
                "cellClassFunction": """
                    function(value) {
                        if (value === 0) return 'text-red-600 font-medium';
                        if (value < 10) return 'text-yellow-600 font-medium';
                        return 'text-green-600 font-medium';
                    }
                """
            },
            {
                "field": "list_price",
                "label": "Price",
                "visible": True,
                "formatter": "currency"
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
            }
        ],
        
        "filters": [
            {
                "field": "category_id",
                "label": "Category",
                "type": "select",
                "placeholder": "All Categories",
                "optionsEndpoint": "/api/v1/products/categories"
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
                "route": "/inventory/products/{id}/edit"
            }
        ],
        
        "headerActions": [
            {
                "id": "export",
                "label": "Export",
                "icon": "download",
                "variant": "secondary"
            }
        ]
    }


@router.get("/products/form")
async def get_products_form_schema() -> Dict[str, Any]:
    """Get UI schema for product form (create/edit)"""
    return {
        "title": "Product Details",
        "description": "Enter product information",
        "endpoint": "/api/v1/products",
        "successRoute": "/inventory/products",
        "cancelRoute": "/inventory/products",
        "submitLabel": "Save Product",
        "cancelLabel": "Cancel",
        
        "breadcrumbs": [
            {"label": "Products", "route": "/inventory/products"},
            {"label": "Product Details"}
        ],
        
        "sections": [
            {
                "id": "basic",
                "title": "Basic Information",
                "gridClass": "grid grid-cols-1 gap-6 sm:grid-cols-1",
                "fields": [
                    {
                        "name": "name",
                        "label": "Product Name",
                        "type": "text",
                        "required": True,
                        "placeholder": "Enter product name",
                        "colSpan": 2
                    },
                    {
                        "name": "sku",
                        "label": "SKU",
                        "type": "text",
                        "required": True,
                        "placeholder": "e.g., PROD-001",
                        "readOnlyOnEdit": True
                    },
                    {
                        "name": "barcode",
                        "label": "Barcode",
                        "type": "text",
                        "placeholder": "Optional barcode"
                    },
                    {
                        "name": "category_id",
                        "label": "Category",
                        "type": "select",
                        "placeholder": "Select a category",
                        "optionsEndpoint": "/api/v1/products/categories",
                        "optionLabelField": "name",
                        "optionValueField": "id"
                    },
                    {
                        "name": "product_type",
                        "label": "Product Type",
                        "type": "select",
                        "defaultValue": "physical",
                        "options": [
                            {"label": "Physical Product", "value": "physical"},
                            {"label": "Service", "value": "service"},
                            {"label": "Digital Product", "value": "digital"}
                        ]
                    },
                    {
                        "name": "description",
                        "label": "Description",
                        "type": "textarea",
                        "rows": 3,
                        "placeholder": "Enter product description",
                        "colSpan": 2
                    }
                ]
            },
            {
                "id": "pricing",
                "title": "Pricing",
                "gridClass": "grid grid-cols-1 gap-6 sm:grid-cols-3",
                "fields": [
                    {
                        "name": "list_price",
                        "label": "List Price",
                        "type": "number",
                        "min": 0,
                        "step": 0.01,
                        "prefix": "$",
                        "placeholder": "0.00"
                    },
                    {
                        "name": "cost_price",
                        "label": "Cost Price",
                        "type": "number",
                        "min": 0,
                        "step": 0.01,
                        "prefix": "$",
                        "placeholder": "0.00"
                    },
                    {
                        "name": "margin",
                        "label": "Margin",
                        "type": "display",
                        "compute": """
                            function(data) {
                                if (!data.list_price || !data.cost_price) return '0.00%';
                                const margin = ((data.list_price - data.cost_price) / data.list_price) * 100;
                                return margin.toFixed(2) + '%';
                            }
                        """
                    }
                ]
            },
            {
                "id": "inventory",
                "title": "Inventory Settings",
                "gridClass": "grid grid-cols-1 gap-6 sm:grid-cols-3",
                "fields": [
                    {
                        "name": "reorder_point",
                        "label": "Reorder Point",
                        "type": "number",
                        "min": 0,
                        "placeholder": "0"
                    },
                    {
                        "name": "reorder_quantity",
                        "label": "Reorder Quantity",
                        "type": "number",
                        "min": 0,
                        "placeholder": "0"
                    },
                    {
                        "name": "unit_of_measure",
                        "label": "Unit of Measure",
                        "type": "text",
                        "placeholder": "e.g., pcs, kg, m"
                    },
                    {
                        "name": "track_inventory",
                        "label": "Track inventory for this product",
                        "type": "checkbox",
                        "defaultValue": True,
                        "colSpan": 3
                    },
                    {
                        "name": "is_active",
                        "label": "Product is active",
                        "type": "checkbox",
                        "defaultValue": True,
                        "colSpan": 3
                    }
                ]
            }
        ]
    }


@router.get("/warehouses/list")
async def get_warehouses_list_schema() -> Dict[str, Any]:
    """Get UI schema for warehouses list view"""
    return {
        "title": "Warehouses",
        "description": "Manage warehouse locations and facilities",
        "viewType": "cards",
        "endpoint": "/api/v1/warehouses/",
        "keyField": "id",
        "createLabel": "New Warehouse",
        "createRoute": "/inventory/warehouses/new",
        "editRoute": "/inventory/warehouses/{id}/edit",
        "clickable": True,
        
        "columns": [
            {
                "field": "name",
                "label": "Warehouse",
                "isTitle": True
            },
            {
                "field": "code",
                "label": "Code"
            },
            {
                "field": "city",
                "label": "Location"
            },
            {
                "field": "total_capacity",
                "label": "Capacity",
                "formatter": "number"
            },
            {
                "field": "is_active",
                "label": "Status",
                "formatter": "boolean"
            }
        ]
    }


@router.get("/stock/movements")
async def get_stock_movements_schema() -> Dict[str, Any]:
    """Get UI schema for stock movements view"""
    return {
        "title": "Stock Movements",
        "description": "Track inventory movements and adjustments",
        "viewType": "table",
        "endpoint": "/api/v1/stock/movements/",
        "keyField": "id",
        "searchable": True,
        "searchPlaceholder": "Search by product or reference...",
        "paginated": True,
        "refreshable": True,
        
        "columns": [
            {
                "field": "movement_date",
                "label": "Date",
                "formatter": "datetime"
            },
            {
                "field": "product_name",
                "label": "Product"
            },
            {
                "field": "movement_type",
                "label": "Type"
            },
            {
                "field": "quantity",
                "label": "Quantity",
                "formatter": "number"
            },
            {
                "field": "from_location",
                "label": "From"
            },
            {
                "field": "to_location",
                "label": "To"
            },
            {
                "field": "reference_number",
                "label": "Reference"
            }
        ],
        
        "filters": [
            {
                "field": "movement_type",
                "label": "Type",
                "type": "select",
                "options": [
                    {"label": "Receipt", "value": "receipt"},
                    {"label": "Issue", "value": "issue"},
                    {"label": "Transfer", "value": "transfer"},
                    {"label": "Adjustment", "value": "adjustment"}
                ]
            },
            {
                "field": "date_from",
                "label": "From Date",
                "type": "date"
            },
            {
                "field": "date_to",
                "label": "To Date",
                "type": "date"
            }
        ]
    }


@router.get("/categories/tree")
async def get_categories_tree_schema() -> Dict[str, Any]:
    """Get UI schema for product categories tree view"""
    return {
        "title": "Product Categories",
        "description": "Organize products into categories",
        "viewType": "tree",
        "endpoint": "/api/v1/products/categories/tree",
        "keyField": "id",
        "parentField": "parent_id",
        "labelField": "name",
        "createLabel": "New Category",
        "editable": True,
        "draggable": True,
        
        "nodeActions": [
            {
                "id": "add-child",
                "label": "Add Subcategory",
                "icon": "plus"
            },
            {
                "id": "edit",
                "label": "Edit",
                "icon": "pencil"
            },
            {
                "id": "delete",
                "label": "Delete",
                "icon": "trash",
                "confirm": True,
                "confirmMessage": "Delete this category and all its subcategories?"
            }
        ]
    }


@router.get("/categories/list")
async def get_categories_list_schema() -> Dict[str, Any]:
    """Get UI schema for product categories list view"""
    return {
        "title": "Product Categories",
        "description": "Manage product categories",
        "viewType": "table",
        "endpoint": "/api/v1/products/categories",
        "keyField": "id",
        "searchable": True,
        "searchPlaceholder": "Search categories by name or code...",
        "searchParam": "search",
        "paginated": True,
        "pageSize": 20,
        "refreshable": True,
        "createable": True,
        "createLabel": "New Category",
        "createRoute": "/inventory/categories/new",
        "editRoute": "/inventory/categories/{id}/edit",
        "clickable": True,
        
        "columns": [
            {
                "field": "name",
                "label": "Category Name",
                "visible": True,
                "isTitle": True,
                "cellClass": "font-medium text-gray-900"
            },
            {
                "field": "code",
                "label": "Code",
                "visible": True
            },
            {
                "field": "parent_category_name",
                "label": "Parent Category",
                "visible": True
            },
            {
                "field": "product_count",
                "label": "Products",
                "visible": True,
                "formatter": "number"
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
            }
        ],
        
        "filters": [
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
                "route": "/inventory/categories/{id}/edit"
            }
        ],
        
        "headerActions": [
            {
                "id": "export",
                "label": "Export",
                "icon": "download",
                "variant": "secondary"
            }
        ]
    }


@router.get("/categories/form")
async def get_categories_form_schema() -> Dict[str, Any]:
    """Get UI schema for category form (create/edit)"""
    return {
        "title": "Category Details",
        "description": "Enter category information",
        "endpoint": "/api/v1/products/categories",
        "successRoute": "/inventory/categories",
        "cancelRoute": "/inventory/categories",
        "submitLabel": "Save Category",
        "cancelLabel": "Cancel",
        
        "breadcrumbs": [
            {"label": "Categories", "route": "/inventory/categories"},
            {"label": "Category Details"}
        ],
        
        "sections": [
            {
                "id": "basic",
                "title": "Basic Information",
                "gridClass": "grid grid-cols-1 gap-6 sm:grid-cols-2",
                "fields": [
                    {
                        "name": "name",
                        "label": "Category Name",
                        "type": "text",
                        "required": True,
                        "placeholder": "Enter category name",
                        "colSpan": 2
                    },
                    {
                        "name": "code",
                        "label": "Code",
                        "type": "text",
                        "required": True,
                        "placeholder": "e.g., ELECTRONICS, CLOTHING",
                        "help": "Unique code for this category"
                    },
                    {
                        "name": "parent_category_id",
                        "label": "Parent Category",
                        "type": "select",
                        "placeholder": "Select a parent category (optional)",
                        "optionsEndpoint": "/api/v1/products/categories?active_only=true",
                        "optionLabelField": "name",
                        "optionValueField": "id"
                    },
                    {
                        "name": "display_order",
                        "label": "Display Order",
                        "type": "number",
                        "min": 0,
                        "defaultValue": 0,
                        "help": "Categories will be displayed in ascending order"
                    },
                    {
                        "name": "color",
                        "label": "Color",
                        "type": "color",
                        "placeholder": "Select a color for this category"
                    },
                    {
                        "name": "icon",
                        "label": "Icon",
                        "type": "text",
                        "placeholder": "e.g., box, tag, shopping-cart"
                    }
                ]
            },
            {
                "id": "description",
                "title": "Description",
                "gridClass": "grid grid-cols-1 gap-6",
                "fields": [
                    {
                        "name": "description",
                        "label": "Description",
                        "type": "textarea",
                        "rows": 3,
                        "placeholder": "Enter category description"
                    }
                ]
            },
            {
                "id": "seo",
                "title": "SEO Information",
                "gridClass": "grid grid-cols-1 gap-6",
                "fields": [
                    {
                        "name": "slug",
                        "label": "URL Slug",
                        "type": "text",
                        "placeholder": "e.g., electronics-category"
                    },
                    {
                        "name": "meta_title",
                        "label": "Meta Title",
                        "type": "text",
                        "maxLength": 255
                    },
                    {
                        "name": "meta_description",
                        "label": "Meta Description",
                        "type": "textarea",
                        "rows": 2,
                        "maxLength": 500
                    }
                ]
            },
            {
                "id": "status",
                "title": "Status",
                "gridClass": "grid grid-cols-1 gap-6",
                "fields": [
                    {
                        "name": "is_active",
                        "label": "Category is active",
                        "type": "checkbox",
                        "defaultValue": True
                    }
                ]
            }
        ]
    }
