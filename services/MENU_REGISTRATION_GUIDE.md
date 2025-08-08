# Menu Registration System Guide

## Overview

Each microservice in XERPIUM is responsible for registering and managing its own menu items. This ensures service autonomy and follows microservices best practices.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│ Inventory       │────▶│ Menu Access      │◀────│ UI Service  │
│ Service         │     │ Service          │     │             │
└─────────────────┘     │                  │     └─────────────┘
                        │ - Menu Registry  │
┌─────────────────┐     │ - Permission    │
│ Sales           │────▶│   Management     │
│ Service         │     │ - Access Control │
└─────────────────┘     └──────────────────┘
                              ▲
┌─────────────────┐           │
│ User Auth       │───────────┘
│ Service         │
└─────────────────┘
```

## Implementation

### 1. Service Responsibilities

Each service must:
- Define its own menu structure
- Define required permissions
- Register menus on startup
- Unregister menus on shutdown (optional)

### 2. Menu Registration Files

Each service should have a `menu_init.py` file that:

```python
# services/[service-name]/[module]/menu_init.py

# Define permissions
SERVICE_PERMISSIONS = [
    MenuPermission(
        code="permission_code",
        name="Permission Name",
        description="Description",
        category="service_category",
        action="view|manage|approve"
    ),
    # ... more permissions
]

# Define menu structure
SERVICE_MENUS = [
    MenuItem(
        code="menu_code",
        title="Menu Title",
        parent_code=None,  # or parent menu code
        url="/path/to/page",
        icon="icon-name",
        required_permission="permission_code"
    ),
    # ... more menu items
]
```

### 3. Service Startup Integration

Add menu initialization to your service startup:

```python
# main.py or app.py

from [module].menu_init import init_menus_on_startup

@app.on_event("startup")
async def startup_event():
    try:
        init_menus_on_startup()
        logger.info("Menu initialization completed")
    except Exception as e:
        logger.error(f"Failed to initialize menus: {e}")
        # Don't fail startup on menu registration error
```

## Service Menu Definitions

### Inventory Service
- **Parent Menu**: Inventory
- **Permissions**: `access_inventory`, `view_products`, `manage_products`, etc.
- **Submenus**: Products, Stock, Warehouses, Receiving, Reports

### Sales Service
- **Parent Menu**: Sales
- **Permissions**: `access_sales`, `manage_quotes`, `manage_orders`, etc.
- **Submenus**: Quotes, Orders, Pricing Rules, Customers, Analytics

### User Auth Service
- **Parent Menu**: Administration
- **Permissions**: `access_admin`, `manage_users`, `manage_roles`, etc.
- **Submenus**: Users, Roles, Permissions, Audit Logs, Settings
- **Public Menus**: Dashboard, Profile

## Menu Structure Guidelines

### Menu Types
- `dropdown`: Parent menu with children
- `link`: Direct link menu item
- `divider`: Visual separator
- `header`: Section header

### Permission Strategy
- Parent menus usually require basic `access_*` permission
- Child menus have specific action permissions
- Public menus have `required_permission=None`

### Icon Selection
Use consistent icon names across services:
- `home`: Dashboard
- `users`: User/Customer management
- `shopping-cart`: Sales
- `warehouse`: Inventory
- `settings`: Configuration
- `file-text`: Documents/Reports
- `bar-chart`: Analytics

## Best Practices

1. **Service Autonomy**: Each service manages its own menus
2. **Permission Naming**: Use pattern `[action]_[resource]` (e.g., `manage_products`)
3. **Menu Codes**: Use pattern `[service]_[function]` (e.g., `inventory_products`)
4. **Order Index**: Use consistent ordering (1-10 scale)
5. **Error Handling**: Don't fail service startup if menu registration fails
6. **Idempotency**: Use `ON CONFLICT DO NOTHING` for SQL inserts

## Testing Menu Registration

```bash
# Test inventory menu registration
python services/inventory-service/inventory_module/menu_init.py

# Test sales menu registration  
python services/sales-service/sales_module/menu_init.py

# Test user menu registration
python services/user-auth-service/app/menu_init.py
```

## Future Enhancements

1. **Dynamic Updates**: Services can update menus without restart
2. **Menu Versioning**: Track menu structure changes
3. **Feature Flags**: Enable/disable menus based on feature flags
4. **Multi-tenant**: Different menu structures per tenant
5. **Menu Analytics**: Track menu usage patterns

## Troubleshooting

### Menus Not Appearing
1. Check service logs for registration errors
2. Verify permissions are correctly defined
3. Ensure user has required roles/permissions
4. User must re-login after role changes (JWT token refresh)

### Permission Denied
1. Check permission exists in menu-access-service
2. Verify role has the permission
3. Check user has the role assigned
4. Ensure JWT token is current

### Service Communication
1. Verify menu-access-service is running
2. Check network connectivity between services
3. Verify service URLs in environment variables