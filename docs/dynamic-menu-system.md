# Dynamic Menu System Documentation

## Overview

The XERPIUM dynamic menu system allows services to register their menu items and have them automatically displayed in the UI based on user permissions. This enables each microservice (Inventory, Sales, etc.) to define its own navigation structure while maintaining centralized access control.

## Architecture

### Components

1. **Menu-Access Service** (`menu-access-service`)
   - Stores menu definitions in PostgreSQL
   - Provides REST API for menu retrieval
   - Filters menus based on user permissions and roles
   - Located at: `/services/menu-access-service`

2. **UI Service** (`ui-service`)
   - Fetches menu structure from Menu-Access Service
   - Dynamically renders navigation based on user permissions
   - Supports both desktop and mobile navigation
   - Located at: `/services/ui-service`

3. **Permission System**
   - Each menu item can require specific permissions
   - Permissions are checked server-side before returning menus
   - Role-based access control with level requirements

## Menu Structure

### Menu Item Properties

```typescript
interface MenuItem {
  id: number
  code: string              // Unique identifier
  title: string             // Display name
  description?: string      // Optional description
  url?: string             // Navigation URL
  icon?: string            // Font Awesome icon class
  parent_id?: number       // For hierarchical menus
  order_index: number      // Display order
  level: number            // Hierarchy level (0 = root)
  item_type: 'link' | 'dropdown' | 'divider' | 'header'
  required_permission?: string  // Permission code required
  required_role_level?: number  // Minimum role level
  is_active: boolean
  is_visible: boolean
  children?: MenuItem[]    // Nested items
}
```

### Example Menu Structure

```
Dashboard (always visible)
Companies (requires: companies.view)
Partners (requires: partners.view)
Sales Management (dropdown, requires: sales.access)
  ├── Sales Quotes (requires: quotes.view)
  ├── Sales Orders (requires: orders.view)
  └── Customers (requires: customers.view)
Inventory Management (dropdown, requires: inventory.access)
  ├── Products (requires: products.view)
  ├── Stock Levels (requires: stock.view)
  └── Warehouses (requires: warehouses.view)
Users (requires: admin.access)
```

## Setting Up Menus

### 1. Start the Services

```bash
# Start all services
docker compose up -d

# Wait for services to be healthy
docker compose ps
```

### 2. Run Menu Setup Scripts

The system includes setup scripts to populate initial menu items:

```bash
# Basic menus (Companies, Partners, Users)
docker exec -it m-erp-menu-access python /app/scripts/setup_basic_menus.py

# Inventory and Sales menus
docker exec -it m-erp-menu-access python /app/scripts/setup_inventory_sales_menus.py
```

### 3. Restart Services

After adding menus, restart the menu-access-service to ensure changes are loaded:

```bash
docker compose restart menu-access-service
docker compose restart kong
```

## API Endpoints

### Get User Menu Tree

```http
GET /api/v1/menus/tree
Authorization: Bearer <token>
```

Returns hierarchical menu structure filtered by user permissions.

### Get All Menus (Admin)

```http
GET /api/v1/menus
Authorization: Bearer <token>
```

Returns flat list of all menu items.

### Create Menu Item

```http
POST /api/v1/menus
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "reports",
  "title": "Reports",
  "url": "/reports",
  "icon": "fas fa-chart-bar",
  "order_index": 50,
  "required_permission": "reports.view"
}
```

## User Permissions

### Setting Up Permissions

1. Create permissions in the system:

```python
Permission(
    code="inventory.access",
    name="Inventory Management",
    description="Access to inventory management system",
    category="inventory",
    action="access"
)
```

2. Assign permissions to roles:
   - Navigate to Users section in UI
   - Edit role and add required permissions
   - Or use the API to manage role permissions

### Testing Different Access Levels

1. **Admin User**: Has access to all menus
2. **Inventory User**: Create role with inventory permissions
3. **Sales User**: Create role with sales permissions
4. **Basic User**: Only sees Companies and Partners

## UI Integration

The UI automatically:
1. Fetches menus on login
2. Refreshes menus when permissions change
3. Handles dropdown menus with children
4. Shows icons when specified
5. Maintains active state for current route

### Menu Store (Pinia)

```typescript
// Access menu store
import { useMenuStore } from '@/stores/menu'

const menuStore = useMenuStore()

// Fetch menus
await menuStore.fetchMenus()

// Access menus
menuStore.topLevelMenus  // Root level items
menuStore.getMenuByCode('inventory_management')
```

## Adding New Service Menus

### 1. Create Menu Setup Script

```python
# Example: services/your-service/scripts/setup_menus.py
async def create_your_service_menus():
    # Create permissions
    permissions = [
        Permission(code="your_service.access", ...),
        Permission(code="your_feature.view", ...)
    ]
    
    # Create menu structure
    menu = MenuItem(
        code="your_service",
        title="Your Service",
        url="/your-service",
        icon="fas fa-your-icon",
        required_permission="your_service.access"
    )
    
    # Add sub-menus
    sub_menus = [...]
```

### 2. Update Kong Routes

Add routes in `services/api-gateway/kong.yml`:

```yaml
- name: your-service
  url: http://your-service:8000
  routes:
    - name: your-service-routes
      paths:
        - /your-service
        - /api/v1/your-service
```

### 3. Create UI Routes

Add routes in `services/ui-service/src/router/index.ts`:

```typescript
{
  path: '/your-service',
  name: 'YourService',
  component: () => import('@/views/your-service/Dashboard.vue'),
  meta: { requiresAuth: true, title: 'Your Service' }
}
```

## Troubleshooting

### Menus Not Appearing

1. Check user permissions:
   ```bash
   # View user's permissions in UI or check API response
   GET /api/v1/menus/tree?include_permissions=true
   ```

2. Verify menu is active:
   ```sql
   SELECT * FROM menu_items WHERE code = 'your_menu_code';
   ```

3. Check service health:
   ```bash
   curl http://localhost:8003/health  # Menu-access service
   ```

### Permission Denied

1. Ensure user has required permission
2. Check role level if menu has `required_role_level`
3. Verify permission exists in database

### Icons Not Showing

1. Ensure Font Awesome is loaded in UI
2. Use correct icon class format: `fas fa-icon-name`
3. Check browser console for errors

## Security Considerations

1. **Server-Side Filtering**: Menus are filtered server-side based on JWT token permissions
2. **No Client-Side Permissions**: Never rely on client-side permission checks
3. **Route Guards**: UI routes also check permissions independently
4. **API Protection**: All menu modification endpoints require authentication

## Future Enhancements

1. **Menu Caching**: Cache menu structure with Redis
2. **Real-time Updates**: Push menu updates via WebSocket
3. **Menu Templates**: Pre-defined menu structures for common use cases
4. **A/B Testing**: Support multiple menu variations
5. **Analytics**: Track menu usage and navigation patterns