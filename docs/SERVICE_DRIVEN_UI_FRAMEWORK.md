# Service-Driven UI Framework Documentation

> **Version**: 1.1.0  
> **Last Updated**: August 9, 2025  
> **Status**: Production Ready

## Overview

The Service-Driven UI Framework revolutionizes how XERPIUM handles user interfaces by allowing backend services to define their UI structure through JSON schemas. This eliminates the need for custom frontend code for each service, dramatically reducing development time and ensuring UI consistency across the platform.

## Table of Contents

1. [Architecture](#architecture)
2. [Core Concepts](#core-concepts)
3. [Schema Reference](#schema-reference)
4. [Implementation Guide](#implementation-guide)
5. [Generic Components](#generic-components)
6. [Advanced Features](#advanced-features)
7. [Best Practices](#best-practices)
8. [Migration Guide](#migration-guide)

## Architecture

### How It Works

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Browser   │────▶│  UI Service  │────▶│   Backend   │
│             │     │              │     │   Service   │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │                    │
       │                    ▼                    ▼
       │            ┌──────────────┐     ┌─────────────┐
       │            │  DynamicView │────▶│ UI Schemas  │
       │            │  Component   │     │  Endpoint   │
       │            └──────────────┘     └─────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐     ┌──────────────┐
│   Rendered  │◀────│   Generic    │
│      UI     │     │  Components  │
└─────────────┘     └──────────────┘
```

### Request Flow

1. **User navigates** to a route (e.g., `/inventory/products`)
2. **DynamicView component** determines the service and view type
3. **Fetches UI schema** from service endpoint (e.g., `/api/v1/ui-schemas/products/list`)
4. **Selects generic component** based on schema type (list, form, tree, etc.)
5. **Renders UI** using the schema definition
6. **Data operations** use endpoints defined in the schema

## Core Concepts

### UI Schemas

UI schemas are JSON documents that describe:
- **Structure**: How data should be displayed (tables, forms, trees)
- **Behavior**: Actions, navigation, validation rules
- **Data Sources**: API endpoints for CRUD operations
- **Presentation**: Formatting, styling, conditional display

### Generic Components

Pre-built Vue.js components that render based on schemas:
- **GenericListView**: Tables, cards, and list displays
- **GenericFormView**: Dynamic forms with validation
- **GenericTreeView**: Hierarchical data structures
- **GenericDashboard**: Widget-based dashboards

### Dynamic Routing

Routes automatically map to schema endpoints:
- `/inventory/products` → `/api/v1/ui-schemas/products/list`
- `/inventory/products/new` → `/api/v1/ui-schemas/products/form`
- `/inventory/products/:id/edit` → `/api/v1/ui-schemas/products/form`

## Schema Reference

### List View Schema

```typescript
interface ListViewSchema {
  // Basic Configuration
  title: string                    // Page title
  description?: string             // Page description
  viewType: 'table' | 'cards' | 'list'
  endpoint: string                 // Data endpoint
  
  // Data Configuration
  keyField?: string               // Primary key field (default: 'id')
  dataPath?: string              // Path to data in response
  paginated?: boolean            // Enable pagination
  pageSize?: number              // Items per page
  
  // Search & Filter
  searchable?: boolean           // Enable search
  searchPlaceholder?: string     // Search input placeholder
  searchParam?: string          // Query parameter name
  filters?: FilterConfig[]       // Filter definitions
  
  // Actions
  createable?: boolean          // Show create button
  createLabel?: string         // Create button text
  createRoute?: string        // Create navigation route
  editRoute?: string         // Edit route template
  clickable?: boolean       // Row click navigation
  rowActions?: Action[]    // Per-row action buttons
  headerActions?: Action[] // Header action buttons
  
  // Display Configuration
  columns: ColumnConfig[]      // Column definitions
  emptyTitle?: string         // Empty state title
  emptyMessage?: string      // Empty state message
  refreshable?: boolean     // Show refresh button
}

interface ColumnConfig {
  field: string              // Data field name
  label: string             // Column header
  visible?: boolean        // Show/hide column
  formatter?: string | Function  // Value formatter
  cellClass?: string           // CSS classes
  cellClassFunction?: Function // Dynamic CSS
  isTitle?: boolean           // Primary column
  sortable?: boolean         // Enable sorting
}

interface FilterConfig {
  field: string             // Filter field
  label: string            // Filter label
  type: 'select' | 'date' | 'text' | 'number'
  placeholder?: string     // Placeholder text
  options?: Option[]      // Static options
  optionsEndpoint?: string // Dynamic options endpoint
}
```

### Form View Schema

```typescript
interface FormViewSchema {
  // Basic Configuration
  title: string                   // Form title
  description?: string           // Form description
  endpoint: string              // Submit endpoint
  method?: 'POST' | 'PUT'      // HTTP method
  
  // Navigation
  successRoute?: string        // After save navigation
  cancelRoute?: string        // Cancel navigation
  breadcrumbs?: Breadcrumb[]  // Breadcrumb trail
  
  // Form Structure
  sections: Section[]          // Form sections
  
  // Actions
  submitLabel?: string        // Submit button text
  cancelLabel?: string       // Cancel button text
  actions?: Action[]        // Additional actions
  customSubmit?: boolean   // Handle submit externally
}

interface Section {
  id: string                // Section identifier
  title?: string           // Section heading
  description?: string    // Section description
  gridClass?: string     // Grid CSS classes
  fields: Field[]       // Section fields
}

interface Field {
  name: string           // Field name
  label: string         // Field label
  type: FieldType      // Field type
  required?: boolean   // Required field
  disabled?: boolean  // Disabled state
  placeholder?: string // Placeholder text
  defaultValue?: any  // Default value
  
  // Validation
  pattern?: string      // Regex pattern
  min?: number         // Min value/length
  max?: number        // Max value/length
  validate?: Function // Custom validation
  
  // Display
  colSpan?: number     // Grid columns
  help?: string       // Help text
  prefix?: string    // Input prefix
  suffix?: string   // Input suffix
  
  // Options (for select/radio)
  options?: Option[]          // Static options
  optionsEndpoint?: string   // Dynamic options
  optionLabelField?: string // Option label field
  optionValueField?: string // Option value field
  
  // Special
  readOnlyOnEdit?: boolean  // Read-only in edit mode
  compute?: Function       // Computed value
  component?: Component   // Custom component
}

type FieldType = 'text' | 'number' | 'email' | 'tel' | 'url' | 
                 'textarea' | 'select' | 'checkbox' | 'radio' |
                 'date' | 'datetime-local' | 'file' | 'display'
```

## Implementation Guide

### Step 1: Create UI Schema Endpoints

```python
# inventory_module/api/ui_schemas.py
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/ui-schemas", tags=["UI Schemas"])

@router.get("/products/list")
async def get_products_list_schema() -> Dict[str, Any]:
    return {
        "title": "Products",
        "description": "Manage your product catalog",
        "viewType": "table",
        "endpoint": "/api/v1/products/",
        "searchable": True,
        "columns": [
            {
                "field": "name",
                "label": "Product Name",
                "isTitle": True
            },
            {
                "field": "price",
                "label": "Price",
                "formatter": "currency"
            },
            {
                "field": "stock_level",
                "label": "Stock",
                "formatter": "number",
                "cellClassFunction": """
                    function(value) {
                        if (value === 0) return 'text-red-600';
                        if (value < 10) return 'text-yellow-600';
                        return 'text-green-600';
                    }
                """
            }
        ],
        "filters": [
            {
                "field": "category_id",
                "label": "Category",
                "type": "select",
                "optionsEndpoint": "/api/v1/categories"
            }
        ],
        "createRoute": "/inventory/products/new",
        "editRoute": "/inventory/products/{id}/edit"
    }

@router.get("/products/form")
async def get_products_form_schema() -> Dict[str, Any]:
    return {
        "title": "Product Details",
        "endpoint": "/api/v1/products",
        "successRoute": "/inventory/products",
        "sections": [
            {
                "id": "basic",
                "title": "Basic Information",
                "fields": [
                    {
                        "name": "name",
                        "label": "Product Name",
                        "type": "text",
                        "required": True,
                        "placeholder": "Enter product name"
                    },
                    {
                        "name": "sku",
                        "label": "SKU",
                        "type": "text",
                        "required": True,
                        "readOnlyOnEdit": True
                    },
                    {
                        "name": "category_id",
                        "label": "Category",
                        "type": "select",
                        "optionsEndpoint": "/api/v1/categories"
                    }
                ]
            },
            {
                "id": "pricing",
                "title": "Pricing",
                "fields": [
                    {
                        "name": "price",
                        "label": "Price",
                        "type": "number",
                        "min": 0,
                        "step": 0.01,
                        "prefix": "$",
                        "required": True
                    },
                    {
                        "name": "cost",
                        "label": "Cost",
                        "type": "number",
                        "min": 0,
                        "step": 0.01,
                        "prefix": "$"
                    }
                ]
            }
        ]
    }
```

### Step 2: Register Schema Router

```python
# main.py
from inventory_module.api.ui_schemas import router as ui_schemas_router

app.include_router(ui_schemas_router, prefix="/api/v1")
```

### Step 3: Configure Routes in UI Service

```typescript
// router/index.ts
const routes = [
  {
    path: '/inventory/products',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/inventory/products/new',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/inventory/products/:id/edit',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true }
  }
]
```

## Generic Components

### GenericListView

Renders data in table, card, or list format.

**Features:**
- Pagination
- Search and filtering
- Sorting
- Row actions
- Bulk operations
- Export functionality
- Responsive design

**Usage:**
```vue
<GenericListView
  :schema="listSchema"
  :service-url="serviceUrl"
  @row-click="handleRowClick"
  @action="handleAction"
/>
```

### GenericFormView

Renders dynamic forms with validation.

**Features:**
- Multi-section forms
- Field validation
- Conditional fields
- File uploads
- Custom components
- Computed fields
- Form wizards

**Usage:**
```vue
<GenericFormView
  :schema="formSchema"
  :service-url="serviceUrl"
  :id="recordId"
  @submit="handleSubmit"
  @cancel="handleCancel"
/>
```

### DynamicView

Wrapper component that loads schemas and selects appropriate generic component.

**Features:**
- Automatic schema loading
- Component selection
- Error handling
- Loading states
- Route-based configuration

## Advanced Features

### Custom Formatters

```javascript
// Define custom formatters
const formatters = {
  status: (value) => {
    const statusMap = {
      'active': 'Active',
      'inactive': 'Inactive',
      'pending': 'Pending'
    }
    return statusMap[value] || value
  }
}

// Use in schema
{
  "field": "status",
  "formatter": "status"
}
```

### Conditional Display

```python
{
    "name": "discount_percentage",
    "label": "Discount %",
    "type": "number",
    "visible": {
        "field": "has_discount",
        "value": True
    }
}
```

### Custom Validation

```python
{
    "name": "email",
    "type": "email",
    "validate": """
        function(value) {
            if (!value.includes('@company.com')) {
                return 'Must be a company email address';
            }
            return null;
        }
    """
}
```

### Dynamic Options

```python
{
    "name": "subcategory_id",
    "type": "select",
    "optionsEndpoint": "/api/v1/subcategories",
    "optionsParams": {
        "category_id": "{category_id}"  # Reference other field
    }
}
```

## Best Practices

### 1. Schema Organization

```python
# Organize schemas in dedicated module
inventory_module/
  api/
    ui_schemas/
      __init__.py
      products.py
      warehouses.py
      stock.py
```

### 2. Schema Validation

```python
# Use Pydantic for schema validation
from pydantic import BaseModel
from typing import List, Optional

class ColumnSchema(BaseModel):
    field: str
    label: str
    formatter: Optional[str] = None
    visible: bool = True

class ListViewSchema(BaseModel):
    title: str
    columns: List[ColumnSchema]
    endpoint: str
```

### 3. Reusable Schema Components

```python
# Define reusable field definitions
COMMON_FIELDS = {
    "company_id": {
        "name": "company_id",
        "type": "hidden",
        "defaultValue": "current_company"
    },
    "is_active": {
        "name": "is_active",
        "label": "Active",
        "type": "checkbox",
        "defaultValue": True
    }
}

def get_form_schema():
    return {
        "fields": [
            COMMON_FIELDS["company_id"],
            {"name": "name", "label": "Name", "type": "text"},
            COMMON_FIELDS["is_active"]
        ]
    }
```

### 4. Performance Optimization

```python
# Cache schemas for better performance
from functools import lru_cache

@router.get("/products/list")
@lru_cache(maxsize=1)
async def get_products_list_schema():
    # Schema definition
    pass
```

### 5. Internationalization

```python
# Support multiple languages
def get_schema(lang: str = "en"):
    translations = {
        "en": {"title": "Products", "new": "New Product"},
        "es": {"title": "Productos", "new": "Nuevo Producto"}
    }
    
    return {
        "title": translations[lang]["title"],
        "createLabel": translations[lang]["new"]
    }
```

## Migration Guide

### Migrating from Hard-Coded Views

#### Before (Hard-Coded View)

```vue
<!-- ProductListView.vue -->
<template>
  <div>
    <h1>Products</h1>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Price</th>
          <th>Stock</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="product in products" :key="product.id">
          <td>{{ product.name }}</td>
          <td>${{ product.price }}</td>
          <td>{{ product.stock }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() {
    return { products: [] }
  },
  async mounted() {
    const response = await fetch('/api/products')
    this.products = await response.json()
  }
}
</script>
```

#### After (Service-Driven)

```python
# Backend: ui_schemas.py
@router.get("/ui-schemas/products/list")
async def get_products_list_schema():
    return {
        "title": "Products",
        "endpoint": "/api/v1/products",
        "columns": [
            {"field": "name", "label": "Name"},
            {"field": "price", "label": "Price", "formatter": "currency"},
            {"field": "stock", "label": "Stock", "formatter": "number"}
        ]
    }
```

```typescript
// Frontend: router.ts
{
  path: '/products',
  component: () => import('@/views/DynamicView.vue')
}
```

### Benefits of Migration

1. **Reduced Code**: 90% less frontend code
2. **Consistency**: Uniform UI across all modules
3. **Flexibility**: Change UI without deploying frontend
4. **Speed**: New features get UI automatically
5. **Maintenance**: Single point of update for UI logic

## Troubleshooting

### Common Issues

#### Schema Not Loading

```javascript
// Check service URL mapping
const SERVICE_MAPPING = {
  'inventory': 'http://localhost:8005',  // Verify port
  'sales': 'http://localhost:8006'
}

// Check schema endpoint
console.log('Schema URL:', `${serviceUrl}/api/v1/ui-schemas/products/list`)
```

#### Function Strings Not Executing

```python
# Wrap functions properly
"cellClassFunction": """
    function(value, item) {
        return value > 0 ? 'text-green' : 'text-red';
    }
"""

# Not like this
"cellClassFunction": "return value > 0 ? 'text-green' : 'text-red'"
```

#### Data Not Displaying

```python
# Specify correct data path
{
    "dataPath": "items",  # If response is {items: [...], total: 100}
    # or
    "dataPath": "data"    # If response is {data: [...], count: 100}
}
```

## Future Enhancements

### Planned Features

1. **Schema Versioning**: Support multiple schema versions
2. **Schema Inheritance**: Base schemas with overrides
3. **Visual Schema Builder**: GUI for creating schemas
4. **Schema Testing Tools**: Validate schemas before deployment
5. **Advanced Components**: Gantt charts, calendars, kanban boards
6. **Real-time Updates**: WebSocket support for live data
7. **Offline Support**: Cache schemas and data locally
8. **Mobile Optimization**: Responsive schemas for mobile apps

### Contributing

To contribute to the Service-Driven UI Framework:

1. Review existing schemas in `services/*/api/ui_schemas.py`
2. Follow schema conventions and patterns
3. Test with generic components
4. Document new schema features
5. Submit PR with examples

---

*For questions or support, refer to the main [Developer Guide](../DEVELOPER_GUIDE.md) or review working examples in the inventory and sales services.*