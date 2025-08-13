# UI Schema Conventions for Service-Driven Architecture

## Overview

This document defines the conventions and standards for creating UI schemas in the XERPIUM microservices architecture. All services that provide UI components must follow these conventions to ensure compatibility with the generic UI components.

## Table of Contents

1. [Core Principles](#core-principles)
2. [Schema Types](#schema-types)
3. [List View Schemas](#list-view-schemas)
4. [Form View Schemas](#form-view-schemas)
5. [Dashboard Schemas](#dashboard-schemas)
6. [Widget Schemas](#widget-schemas)
7. [Common Pitfalls](#common-pitfalls)
8. [Examples](#examples)

## Core Principles

1. **Consistency**: All schemas must use consistent field names across services
2. **Self-Describing**: Schemas should contain all information needed for rendering
3. **Service-Agnostic**: UI components should work with any service following these conventions
4. **Type Safety**: Use proper data types and formats

## Schema Types

### Base Fields

All schemas must include these base fields:

```json
{
  "id": "unique-schema-id",
  "title": "Display Title",
  "description": "Optional description"
}
```

## List View Schemas

List views display tabular data with filtering, sorting, and pagination support.

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique identifier | `"purchase-orders-list"` |
| `title` | string | Display title | `"Purchase Orders"` |
| `endpoint` | string | API endpoint for data | `"/api/v1/purchase-orders/"` |
| `columns` | array | Column definitions | See below |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | string | null | List description |
| `dataSource` | string | null | Legacy field (use `endpoint`) |
| `dataPath` | string | null | Path to data in response (e.g., `"data"`, `"items"`) |
| `filters` | array | [] | Filter definitions |
| `actions` | array | [] | Row-level actions |
| `bulkActions` | array | [] | Bulk actions |
| `pagination` | boolean | true | Enable pagination |
| `pageSize` | number | 20 | Items per page |
| `searchable` | boolean | false | Enable search |
| `createable` | boolean | true | Show create button |
| `refreshable` | boolean | true | Show refresh button |
| `viewType` | string | "table" | Display type ("table", "grid", "cards") |

### Column Definition

```json
{
  "key": "field_name",
  "label": "Display Label",
  "sortable": true,
  "searchable": false,
  "format": "text",  // text, number, currency, date, badge, rating
  "badge": false,     // Display as badge
  "visible": true,
  "width": "auto",
  "align": "left"     // left, center, right
}
```

### Filter Definition

```json
{
  "key": "status",
  "label": "Status",
  "type": "select",  // select, date, daterange, number, text
  "options": ["draft", "approved", "rejected"],  // For select type
  "dataSource": "/api/v1/statuses",  // For dynamic options
  "placeholder": "All Statuses"
}
```

### Action Definition

```json
{
  "label": "Edit",
  "action": "edit",
  "icon": "edit",
  "type": "primary",  // primary, secondary, danger
  "condition": {      // Optional conditional display
    "status": ["draft"],
    "user_role": ["admin"]
  }
}
```

### Complete Example

```json
{
  "id": "purchase-orders-list",
  "title": "Purchase Orders",
  "endpoint": "/api/v1/purchase-orders/",
  "columns": [
    {
      "key": "po_number",
      "label": "PO Number",
      "sortable": true,
      "searchable": true
    },
    {
      "key": "total_amount",
      "label": "Amount",
      "sortable": true,
      "format": "currency"
    },
    {
      "key": "status",
      "label": "Status",
      "badge": true
    }
  ],
  "filters": [
    {
      "key": "status",
      "label": "Status",
      "type": "select",
      "options": ["draft", "approved", "rejected"]
    }
  ],
  "actions": [
    {
      "label": "View",
      "action": "view",
      "icon": "eye"
    },
    {
      "label": "Edit",
      "action": "edit",
      "icon": "edit",
      "condition": {
        "status": ["draft"]
      }
    }
  ],
  "pagination": true,
  "pageSize": 20
}
```

## Form View Schemas

Forms handle data creation and editing.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `title` | string | Form title |
| `sections` | array | Form sections with fields |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `submitEndpoint` | string | API endpoint for submission |
| `dataEndpoint` | string | API endpoint to fetch data (edit mode) |
| `layout` | string | Form layout ("single", "multi-column") |
| `actions` | array | Form actions/buttons |

### Field Definition

```json
{
  "key": "supplier_id",
  "label": "Supplier",
  "type": "select",  // text, email, number, date, select, textarea, toggle
  "required": true,
  "placeholder": "Select a supplier",
  "help": "Choose the supplier for this order",
  "dataSource": "/api/v1/suppliers",  // For dynamic options
  "options": ["Option 1", "Option 2"],  // For static options
  "default": "default_value",
  "validation": {
    "min": 0,
    "max": 100,
    "pattern": "^[A-Z]{3}$"
  }
}
```

## Dashboard Schemas

Dashboards display multiple widgets in a grid layout.

### Required Fields

```json
{
  "id": "purchasing-dashboard",
  "title": "Purchasing Dashboard",
  "widgets": [
    // Widget definitions
  ]
}
```

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `layout` | string | Layout type ("grid", "flex") |
| `refreshInterval` | number | Auto-refresh in milliseconds |
| `columns` | number | Number of grid columns |

## Widget Schemas

Widgets are components displayed on dashboards.

### Required Fields (UI Registry)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique widget ID |
| `title` | string | Widget title (NOT `name`) |
| `type` | string | Widget type |
| `data_endpoint` | string | API endpoint for data (NOT `dataSource`) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `size` | string | Widget size ("small", "medium", "large", "full") |
| `refresh_interval` | number | Refresh interval in seconds |
| `position` | object | Grid position `{x, y, w, h}` |
| `config` | object | Widget-specific configuration |

### Widget Types

- `metric` - Key performance indicators and single metric displays
- `chart` - Line, bar, pie charts
- `list` - Simple data lists
- `table` - Data tables

### Example

```json
{
  "id": "purchasing-metrics",
  "title": "Purchasing Metrics",
  "type": "metric",
  "size": "large",
  "data_endpoint": "/api/v1/dashboard/metrics",
  "refresh_interval": 60
}
```

## Common Pitfalls

### ❌ Wrong Field Names

**Incorrect:**
```json
{
  "name": "Purchase Orders",  // Wrong: should be "title"
  "dataSource": "/api/v1/orders",  // Wrong: should be "endpoint" for lists
  "data_endpoint": "/api/v1/orders"  // Wrong: should be "endpoint" for lists
}
```

**Correct:**
```json
{
  "title": "Purchase Orders",
  "endpoint": "/api/v1/orders/"  // Note: Include trailing slash
}
```

### ❌ Python vs JSON Booleans

**Incorrect (Python):**
```python
"pagination": True  # Python boolean
```

**Correct (JSON):**
```json
"pagination": true  // JSON boolean (lowercase)
```

### ❌ Missing Trailing Slashes

**Incorrect:**
```json
"endpoint": "/api/v1/purchase-orders"
```

**Correct:**
```json
"endpoint": "/api/v1/purchase-orders/"
```

### ❌ Inconsistent Response Formats

Ensure your API responses match expected formats:

**List Response:**
```json
{
  "data": [...],
  "total_count": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

## Service Registration

When registering with UI Registry Service, ensure compatibility with Pydantic models:

### Widget Registration
- Use `title` not `name`
- Use `data_endpoint` not `dataSource` or `endpoint`
- Include `refresh_interval` in seconds

### List Registration
- Use `title` not `name`
- Use `entity` field to identify the data type
- Use `data_endpoint` for registry, but `endpoint` in the actual schema

### Form Registration
- Use `title` not `name`
- Use `submit_endpoint` not `submitEndpoint`
- Include `entity` and `mode` fields

## Testing Your Schemas

1. **Validate JSON syntax:**
```bash
curl -s http://localhost:9080/api/v1/ui-schemas/lists/your-list | python3 -m json.tool
```

2. **Check required fields:**
```bash
curl -s http://localhost:9080/api/v1/ui-schemas/lists/your-list | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print('✓' if 'endpoint' in d else '✗ Missing endpoint')"
```

3. **Test data endpoint:**
```bash
curl -s http://localhost:9080$(curl -s http://localhost:9080/api/v1/ui-schemas/lists/your-list | \
  python3 -c "import json,sys; print(json.load(sys.stdin)['endpoint'])")
```

## Migration Guide

If migrating from an older schema format:

1. Replace `name` → `title`
2. Replace `dataSource` → `endpoint` (for list views)
3. Replace `data_endpoint` → `endpoint` (for list views in schemas)
4. Replace `submitEndpoint` → `submit_endpoint` (for forms)
5. Ensure all boolean values use JSON format (lowercase)
6. Add trailing slashes to all API endpoints
7. Add `entity` field to lists and forms for UI Registry

## Reference Implementation

See the following services for reference implementations:
- **Sales Service**: `/services/sales-service/sales_module/api/ui_schemas.py`
- **Inventory Service**: `/services/inventory-service/inventory_module/api/ui_schemas.py`
- **Purchasing Service**: `/services/purchasing-service/purchasing_module/api/ui_schemas.py`

## Validation Checklist

Before deploying your UI schemas:

- [ ] All required fields are present
- [ ] Field names follow conventions (`title` not `name`, `endpoint` not `data_endpoint`)
- [ ] Boolean values use JSON format (lowercase)
- [ ] API endpoints include trailing slashes
- [ ] Response format matches expected structure
- [ ] UI Registry registration uses correct field names
- [ ] Test data loads correctly in the UI
- [ ] Filters and actions work as expected
- [ ] Pagination returns correct metadata

---

*Last Updated: August 2025*
*Version: 1.0.0*