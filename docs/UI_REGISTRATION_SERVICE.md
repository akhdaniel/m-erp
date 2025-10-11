# XERPIUM UI Registration Service

## Overview
The UI Registration Service is a centralized service in the XERPIUM ERP system that manages UI component registrations from various microservices. It allows services to register their dashboards, forms, lists, and other UI components for dynamic rendering in the generic UI.

## Architecture
The service is built with FastAPI and uses Redis for storage of UI component configurations. It provides RESTful endpoints for registering, retrieving, and managing UI components across all services.

## Key Features
1. **Component Registration**: Services can register UI components (dashboards, forms, lists, charts, widgets)
2. **Dynamic UI Generation**: Generic UI components can consume registered schemas for rendering
3. **Hierarchical Organization**: Support for nested components and hierarchical structures
4. **Permission-Based Access**: Components can be registered with required permissions
5. **Service Integration**: Seamless integration with the existing microservices architecture

## Core Components

### 1. UI Component Model
The service defines several Pydantic models for different UI components:

#### UIComponent
Base model for all UI components:
- `id`: Unique identifier for the component
- `service`: Service that owns the component
- `type`: Component type (dashboard, list, form, chart, widget, etc.)
- `title`: Human-readable title
- `description`: Optional description
- `path`: URL path for routing
- `config`: Component-specific configuration
- `permissions`: Required permissions to view/access
- `order`: Display order
- `icon`: Icon identifier
- `parent_id`: Parent component for hierarchical structures
- `metadata`: Additional metadata

#### DashboardWidget
Model for dashboard widgets:
- `id`: Unique widget identifier
- `service`: Owning service
- `title`: Widget title
- `type`: Widget type (metric, chart, list, table, etc.)
- `size`: Widget size (small, medium, large, full)
- `position`: Grid position coordinates
- `data_endpoint`: API endpoint for widget data
- `refresh_interval`: Auto-refresh interval in seconds
- `config`: Widget-specific configuration
- `permissions`: Required permissions

#### ListView
Model for list/table views:
- `id`: Unique list identifier
- `service`: Owning service
- `title`: List title
- `entity`: Entity type being displayed
- `columns`: Column definitions
- `data_endpoint`: API endpoint for list data
- `actions`: Available row actions
- `filters`: Available filters
- `sorting`: Default sorting configuration
- `pagination`: Whether pagination is enabled
- `permissions`: Required permissions

#### FormView
Model for form views:
- `id`: Unique form identifier
- `service`: Owning service
- `title`: Form title
- `entity`: Entity type being edited
- `mode`: Form mode (create, edit, view)
- `fields`: Form field definitions
- `submit_endpoint`: API endpoint for form submission
- `data_endpoint`: API endpoint for loading existing data
- `validation_rules`: Field validation rules
- `layout`: Form layout (single, multi-column, wizard)
- `permissions`: Required permissions

## API Endpoints

### Component Registration
- `POST /components`: Register a UI component
- `GET /components`: List all registered UI components
- `GET /components/{service}/{component_id}`: Get specific component
- `DELETE /components/{service}/{component_id}`: Unregister component

### Dashboard Registration
- `POST /services/{service}/dashboard`: Register complete dashboard for service
- `GET /services/{service}/dashboard`: Get service dashboard configuration

### Widget Registration
- `POST /dashboard/widgets`: Register dashboard widget
- `GET /dashboard/widgets`: List all dashboard widgets

### List Registration
- `POST /lists`: Register list view configuration
- `GET /lists`: List all list view configurations

### Form Registration
- `POST /forms`: Register form view configuration
- `GET /forms`: List all form view configurations

### Service UI Packages
- `POST /services/{service}/ui-package`: Register complete UI package for service
- `GET /services/{service}/ui-package`: Get complete UI package for service

## Registration Process

### 1. Service Startup
When a service starts up, it registers its UI components with the UI Registry:

```python
# In service startup
from shared.ui_registration_client import register_service_ui

# Register UI package with UI Registry
register_service_ui("sales-service", SALES_UI_PACKAGE)
```

### 2. UI Package Definition
Services define their UI components in a structured package:

```python
SALES_UI_PACKAGE = {
    "widgets": [
        {
            "id": "total-quotes",
            "title": "Active Quotations",
            "type": "metric",
            "size": "small",
            "data_endpoint": "/api/v1/quotes/stats",
            "refresh_interval": 300,
            "config": {
                "field": "active_quotes",
                "format": "number",
                "color": "blue",
                "icon": "file-text",
                "link": "/sales/quotes"
            }
        }
    ],
    "lists": [
        {
            "id": "quotes-list",
            "title": "Quotations",
            "entity": "quotes",
            "data_endpoint": "/api/v1/quotes",
            "columns": [
                {"key": "quote_number", "label": "Quotation #", "sortable": True},
                {"key": "title", "label": "Title", "sortable": True},
                {"key": "customer_name", "label": "Customer", "sortable": True}
            ],
            "actions": [
                {"id": "view", "label": "View", "icon": "eye"},
                {"id": "edit", "label": "Edit", "icon": "edit"}
            ]
        }
    ],
    "forms": [
        {
            "id": "quote-form",
            "title": "Quotation Details",
            "entity": "quote",
            "mode": "create",
            "submit_endpoint": "/api/v1/quotes",
            "fields": [
                {"name": "title", "label": "Quotation Title", "type": "text", "required": True},
                {"name": "customer_id", "label": "Customer", "type": "autocomplete", 
                 "data_source": "/api/v1/partners?is_customer=true", "required": True}
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
                    {"widget": "total-quotes", "row": 0, "col": 0}
                ]
            }
        }
    ]
}
```

### 3. Registration Client
Services use a shared client to register with the UI Registry:

```python
from shared.ui_registration_client import UIRegistrationClient

client = UIRegistrationClient("sales-service")
client.register_ui_package(SALES_UI_PACKAGE)
```

## Consumption Process

### 1. Generic UI Service
The UI service fetches registered components from the UI Registry:

```javascript
// Fetch dashboard configuration from UI Registry
const uiRegistryUrl = import.meta.env.VITE_UI_REGISTRY_API || '/api'
const registryEndpoint = `/api/v1/${currentService.value}/dashboard`
const registryFullUrl = `${uiRegistryUrl.replace(/\/api\/v1$/, '')}${registryEndpoint}`

const registryResponse = await fetch(registryFullUrl)
if (registryResponse.ok) {
  dashboardConfig.value = await registryResponse.json()
}
```

### 2. Dynamic Component Rendering
Generic UI components render based on the registered schemas:

```vue
<!-- Dynamic Dashboard Component -->
<template>
  <div v-if="dashboardConfig">
    <h1>{{ dashboardConfig.title }}</h1>
    <div :class="getGridClass(dashboardConfig.layout)">
      <div v-for="widget in dashboardConfig.widgets" 
           :key="widget.id"
           :class="getWidgetClass(widget)">
        <component :is="getWidgetComponent(widget.type)" 
                   :config="widget" 
                   :data="widgetData[widget.id]" />
      </div>
    </div>
  </div>
</template>
```

## Storage Implementation
The service uses Redis for storing UI component configurations with automatic expiration (TTL):

```python
# Store component with 24-hour TTL
key = f"ui:component:{component.service}:{component.id}"
redis_client.setex(key, 86400, json.dumps(component.dict()))
```

## Security Considerations
1. **Service Authentication**: Services authenticate with the UI Registry using service tokens
2. **Permission Checking**: Components can specify required permissions
3. **Data Validation**: All registered data is validated with Pydantic models
4. **Input Sanitization**: Special characters are sanitized in component data

## Best Practices

### For Service Developers
1. **Follow Naming Conventions**: Use consistent naming for components and fields
2. **Provide Descriptive Metadata**: Include titles, descriptions, and help text
3. **Specify Required Permissions**: Define appropriate access controls
4. **Use Standard Formats**: Follow UI schema conventions for consistency
5. **Include Error Handling**: Provide fallback UI for missing data

### For UI Developers
1. **Validate Component Data**: Always validate data before rendering
2. **Handle Missing Components**: Gracefully handle missing or invalid components
3. **Implement Caching**: Cache frequently accessed components
4. **Support Theming**: Use CSS variables for consistent styling
5. **Provide Loading States**: Show loading indicators for async data

## Integration Examples

### Sales Service Registration
```python
# sales_module/ui_definitions.py
SALES_UI_PACKAGE = {
    "widgets": [
        {
            "id": "monthly-revenue",
            "title": "Monthly Revenue",
            "type": "metric",
            "size": "small",
            "data_endpoint": "/api/v1/orders/analytics/summary",
            "refresh_interval": 3600,
            "config": {
                "field": "current_month_revenue",
                "format": "currency",
                "color": "green",
                "icon": "dollar-sign"
            }
        }
    ]
}

# Register on startup
register_service_ui("sales-service", SALES_UI_PACKAGE)
```

### UI Service Consumption
```javascript
// Fetch and render registered dashboard
async function fetchDashboardConfig() {
  try {
    const uiRegistryUrl = import.meta.env.VITE_UI_REGISTRY_API || '/api'
    const registryEndpoint = `/api/v1/${currentService.value}/dashboard`
    const registryFullUrl = uiRegistryUrl && registryEndpoint.startsWith('/api/v1')
      ? `${uiRegistryUrl.replace(/\/api\/v1$/, '')}${registryEndpoint}`
      : `${uiRegistryUrl}${registryEndpoint}`

    const registryResponse = await fetch(registryFullUrl)
    
    if (registryResponse.ok) {
      dashboardConfig.value = await registryResponse.json()
    }
  } catch (err) {
    console.error('Error loading dashboard config:', err)
  }
}
```

## Monitoring and Maintenance
1. **Health Checks**: Service provides `/health` endpoint
2. **Logging**: Comprehensive logging for debugging and monitoring
3. **Metrics**: Tracking of registration and access patterns
4. **Cleanup**: Automatic expiration of stale component registrations
5. **Backup**: Regular backup of component configurations

## Future Enhancements
1. **Versioning**: Support for component versioning
2. **Validation**: Enhanced schema validation
3. **Caching**: Improved caching strategies
4. **Analytics**: Usage analytics for components
5. **Notifications**: Real-time updates for component changes