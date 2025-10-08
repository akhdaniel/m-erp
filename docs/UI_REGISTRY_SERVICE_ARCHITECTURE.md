# XERPIUM UI Registry Service - Architecture and Flow

## Overview
The UI Registry Service is a centralized service in the XERPIUM ERP system that allows microservices to register their user interface components, dashboards, widgets, lists, and forms. This enables the main UI service to dynamically render service-specific interfaces based on configuration schemas provided by individual services.

## Architecture Components

### 1. UI Registry Service (`/services/ui-registry-service/main.py`)
This is the central registry that stores UI component configurations from various microservices using Redis as the storage backend.

**Key Features:**
- Stores UI component schemas in Redis with TTL (24 hours)
- Provides API endpoints for registration and retrieval
- Supports various component types (dashboards, widgets, lists, forms)
- Enables service-specific UI package registration

**Supported Component Types:**
- **Components**: Generic UI components with routing capabilities
- **Dashboard Widgets**: Metric, chart, list, table widgets for dashboards
- **List Views**: Configurable table/list views with columns, actions, filters
- **Form Views**: Dynamic forms with validation and field definitions

### 2. UI Registration Client (`/services/shared/ui_registration_client.py`)
A shared client library that services use to register their UI components with the UI Registry.

**Key Classes:**
- `UIComponent`: Generic UI component definition
- `DashboardWidget`: Dashboard widget configuration
- `ListView`: List view configuration
- `FormView`: Form view configuration
- `UIRegistrationClient`: Main registration client

### 3. Service UI Definitions (`/services/*/ui_definitions.py`)
Each service defines its UI components in a structured format that gets registered with the UI Registry.

**Example structure:**
```python
SALES_UI_PACKAGE = {
    "widgets": [...],      # Dashboard widgets
    "lists": [...],        # List view configurations
    "forms": [...],        # Form view configurations
    "components": [...]    # Other UI components
}
```

### 4. Frontend UI Service (`/services/ui-service/src/views/DynamicDashboard.vue` and `DynamicView.vue`)
The frontend components that consume UI schemas from the registry and render dynamic interfaces.

## Registration Process

### 1. Service Startup Registration
When a service starts up, it registers its UI components:

**File: `/services/sales-service/main.py`**
```python
# In startup event
from shared.ui_registration_client import register_service_ui
register_service_ui("sales-service", SALES_UI_PACKAGE)
```

### 2. Registration Flow
1. **Service Initialization**: When a service starts up, it calls `register_service_ui()`
2. **Client Creation**: UIRegistrationClient is instantiated with service name
3. **Component Processing**: The client processes each component type (widgets, lists, forms, etc.)
4. **API Calls**: Individual POST requests to UI Registry endpoints
5. **Storage**: UI Registry stores each component in Redis with service-identifier key

### 3. Redis Storage Structure
The UI Registry stores components using these key patterns:
- `ui:component:{service}:{id}` - Individual UI components
- `ui:dashboard:{service}` - Complete dashboard configurations
- `ui:dashboard:widget:{service}:{id}` - Dashboard widgets
- `ui:list:{service}:{id}` - List view configurations
- `ui:form:{service}:{id}` - Form view configurations
- `ui:package:{service}` - Complete service UI packages

## UI Consumption Process

### 1. Dashboard Retrieval
**File: `/services/ui-service/src/views/DynamicDashboard.vue`**

The process for getting dashboard configurations:

```javascript
// Attempt to get from UI Registry first
const registryEndpoint = `/api/v1/services/${currentService.value}/dashboard`
const registryResponse = await fetch(registryFullUrl)

if (registryResponse.ok) {
  dashboardConfig.value = await registryResponse.json()
} else {
  // Fallback to service's own endpoint
  const serviceUrl = serviceUrls[currentService.value]
  // Try to fetch from service's UI schema endpoint
}
```

### 2. Widget Data Retrieval
Each dashboard widget has a `data_endpoint` that points to the service's API to fetch real-time data:
- Widget configuration specifies data endpoint
- UI service fetches data from the appropriate microservice
- Data is displayed in the configured widget format

### 3. Dynamic View Loading
**File: `/services/ui-service/src/views/DynamicView.vue`**

For list, form, and detail views:
1. Route determines service and view type
2. Endpoint constructed: `/api/v1/{service}/{entity}/ui-schemas/{view-type}`
3. UI schema fetched from service
4. Generic components render based on schema definition

## API Endpoints

### UI Registry Service Endpoints
- `POST /components` - Register a UI component
- `GET /components` - List all components
- `GET /components/{service}/{id}` - Get specific component
- `DELETE /components/{service}/{id}` - Unregister component
- `POST /services/{service}/dashboard` - Register service dashboard
- `GET /services/{service}/dashboard` - Get service dashboard
- `POST /dashboard/widgets` - Register dashboard widget
- `POST /lists` - Register list view
- `POST /forms` - Register form view
- `POST /services/{service}/ui-package` - Register complete UI package

## Component Schema Structure

### Dashboard Widget Schema
```json
{
  "id": "total-sales",
  "service": "sales",
  "title": "Total Sales",
  "type": "metric",
  "size": "small",
  "data_endpoint": "/api/v1/sales/stats",
  "refresh_interval": 60,
  "config": {
    "field": "total_sales",
    "format": "currency",
    "color": "green",
    "icon": "dollar-sign"
  }
}
```

### List View Schema
```json
{
  "id": "orders-list",
  "service": "sales",
  "title": "Orders",
  "entity": "orders",
  "columns": [
    {"key": "order_number", "label": "Order #", "sortable": true},
    {"key": "customer_name", "label": "Customer", "sortable": true},
    {"key": "total_amount", "label": "Total", "format": "currency", "sortable": true}
  ],
  "data_endpoint": "/api/v1/orders",
  "actions": [...],
  "filters": [...],
  "permissions": ["sales.orders.view"]
}
```

### Form View Schema
```json
{
  "id": "order-form",
  "service": "sales",
  "title": "Order Details",
  "entity": "order",
  "mode": "create",
  "submit_endpoint": "/api/v1/orders",
  "fields": [
    {"name": "title", "label": "Order Title", "type": "text", "required": true},
    {"name": "customer_id", "label": "Customer", "type": "autocomplete", "data_source": "/api/v1/partners"}
  ]
}
```

## Integration Pattern

1. **Service Defines UI**: Each service defines its UI components in `ui_definitions.py`
2. **Service Registers**: On startup, service calls `register_service_ui()`
3. **Registry Stores**: UI Registry stores components in Redis
4. **UI Service Loads**: Frontend loads schemas from registry or service endpoints
5. **Dynamic Rendering**: Generic components render based on schema definitions
6. **Data Integration**: UI fetches data from service APIs defined in schema

This architecture enables:
- **Loose Coupling**: Services maintain their own UI definitions
- **Centralized Management**: UI Registry provides unified access
- **Dynamic Rendering**: Single UI codebase handles all service interfaces
- **Scalability**: New services can register UI components without code changes
- **Flexibility**: Runtime UI composition based on service configurations