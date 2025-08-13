# UI Schema Quick Reference

## 🚀 Quick Start Checklist

### For List Views
```json
{
  "id": "your-list",
  "title": "Your Title",         // ✅ NOT "name"
  "endpoint": "/api/v1/items/",  // ✅ NOT "data_endpoint" or "dataSource"
  "columns": [...],
  "pagination": true              // ✅ lowercase, not True
}
```

### For Forms
```json
{
  "id": "your-form",
  "title": "Your Form",           // ✅ NOT "name"
  "submit_endpoint": "/api/v1/", // ✅ NOT "submitEndpoint"
  "sections": [...],
  "entity": "items",              // ✅ Required for UI Registry
  "mode": "create"                // ✅ Required for UI Registry
}
```

### For Widgets (UI Registry)
```json
{
  "id": "your-widget",
  "title": "Widget Title",        // ✅ NOT "name"
  "data_endpoint": "/api/v1/",    // ✅ NOT "endpoint" for widgets
  "type": "metric",               // ✅ Use "metric" (singular) for consistency
  "refresh_interval": 60           // ✅ In seconds
}
```

## ⚠️ Common Mistakes to Avoid

| ❌ Wrong | ✅ Correct | Where Used |
|----------|-----------|------------|
| `name` | `title` | All schemas |
| `dataSource` | `endpoint` | List views |
| `data_endpoint` | `endpoint` | List views |
| `submitEndpoint` | `submit_endpoint` | Forms |
| `True`/`False` | `true`/`false` | JSON values |
| `/api/v1/items` | `/api/v1/items/` | API endpoints |

## 📋 Required Fields by Schema Type

### List View
- `id` - Unique identifier
- `title` - Display title
- `endpoint` - API endpoint
- `columns` - Array of column definitions

### Form View
- `id` - Unique identifier
- `title` - Display title
- `sections` - Array of form sections
- `entity` - Data entity type (for UI Registry)
- `mode` - Form mode: "create" or "edit"

### Dashboard Widget
- `id` - Unique identifier
- `title` - Display title
- `type` - Widget type
- `data_endpoint` - API endpoint (for widgets only!)

## 🔄 API Response Format

Your API must return data in this format:

```json
{
  "data": [...],        // Array of items
  "total_count": 100,   // Total number of items
  "page": 1,            // Current page
  "page_size": 20,      // Items per page
  "total_pages": 5      // Total pages
}
```

## 🧪 Quick Test Commands

```bash
# Check if your schema has correct fields
curl -s http://localhost:9080/api/v1/ui-schemas/lists/your-list | \
  python3 -c "import json,sys; d=json.load(sys.stdin); \
  print('✓ endpoint' if 'endpoint' in d else '✗ Missing endpoint'); \
  print('✓ title' if 'title' in d else '✗ Missing title')"

# Test your data endpoint
curl -s http://localhost:9080/api/v1/your-endpoint/ | python3 -m json.tool

# Validate JSON syntax
curl -s http://localhost:9080/api/v1/ui-schemas/lists/your-list | python3 -m json.tool
```

## 📚 Full Documentation

For complete documentation, see: [UI_SCHEMA_CONVENTIONS.md](./UI_SCHEMA_CONVENTIONS.md)

---
*Quick Reference v1.0 - August 2025*