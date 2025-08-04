# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-08-02-extension-system-purchasing-module/spec.md

> Created: 2025-08-02
> Version: 1.0.0

## Module Registry Service API

### Module Management Endpoints

#### GET /api/v1/modules
**Purpose:** List all available modules with optional filtering
**Parameters:** 
- `status`: Filter by module status (available, installed, disabled)
- `search`: Search by name or description
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset
**Response:** List of module metadata with installation status
**Errors:** 400 (Invalid parameters), 401 (Unauthorized), 500 (Server error)

#### POST /api/v1/modules
**Purpose:** Register a new module in the registry
**Parameters:** Module manifest file upload with package
**Response:** Created module with ID and validation results
**Errors:** 400 (Invalid manifest), 409 (Module already exists), 422 (Validation error)

#### GET /api/v1/modules/{module_id}
**Purpose:** Get detailed information about a specific module
**Parameters:** module_id (UUID)
**Response:** Complete module details including manifest, dependencies, and installation status
**Errors:** 404 (Module not found), 401 (Unauthorized)

#### PUT /api/v1/modules/{module_id}
**Purpose:** Update module metadata and package
**Parameters:** module_id (UUID), updated manifest and optional package
**Response:** Updated module information
**Errors:** 404 (Module not found), 400 (Invalid update), 409 (Version conflict)

#### DELETE /api/v1/modules/{module_id}
**Purpose:** Remove module from registry (only if no active installations)
**Parameters:** module_id (UUID)
**Response:** Success confirmation
**Errors:** 404 (Module not found), 409 (Active installations exist), 403 (Forbidden)

### Module Installation Endpoints

#### POST /api/v1/modules/{module_id}/install
**Purpose:** Install module for current company
**Parameters:** 
- module_id (UUID)
- configuration (JSON object)
**Response:** Installation job ID and status
**Errors:** 404 (Module not found), 409 (Already installed), 422 (Configuration invalid)

#### GET /api/v1/installations
**Purpose:** List module installations for current company
**Parameters:** 
- `status`: Filter by installation status
- `module_name`: Filter by module name
**Response:** List of module installations with health status
**Errors:** 401 (Unauthorized), 500 (Server error)

#### GET /api/v1/installations/{installation_id}
**Purpose:** Get detailed installation information
**Parameters:** installation_id (UUID)
**Response:** Complete installation details including configuration and health
**Errors:** 404 (Installation not found), 403 (Different company)

#### PUT /api/v1/installations/{installation_id}/config
**Purpose:** Update module configuration
**Parameters:** 
- installation_id (UUID)
- configuration (JSON object)
**Response:** Updated configuration and restart status
**Errors:** 404 (Installation not found), 422 (Invalid configuration)

#### POST /api/v1/installations/{installation_id}/disable
**Purpose:** Disable module installation
**Parameters:** installation_id (UUID)
**Response:** Success confirmation
**Errors:** 404 (Installation not found), 409 (Cannot disable)

#### POST /api/v1/installations/{installation_id}/enable
**Purpose:** Enable disabled module installation
**Parameters:** installation_id (UUID)
**Response:** Success confirmation and health check result
**Errors:** 404 (Installation not found), 422 (Failed health check)

#### DELETE /api/v1/installations/{installation_id}
**Purpose:** Uninstall module from company
**Parameters:** installation_id (UUID)
**Response:** Uninstallation job ID
**Errors:** 404 (Installation not found), 409 (Cannot uninstall)

### Module Health and Monitoring

#### GET /api/v1/installations/{installation_id}/health
**Purpose:** Check module health status
**Parameters:** installation_id (UUID)
**Response:** Health status with metrics and last check time
**Errors:** 404 (Installation not found), 503 (Module unhealthy)

#### POST /api/v1/installations/{installation_id}/health-check
**Purpose:** Trigger immediate health check
**Parameters:** installation_id (UUID)
**Response:** Health check results
**Errors:** 404 (Installation not found), 500 (Health check failed)

## Purchasing Module API

### Purchase Order Management

#### GET /api/v1/purchase-orders
**Purpose:** List purchase orders with filtering and pagination
**Parameters:**
- `status`: Filter by PO status
- `supplier_id`: Filter by supplier
- `date_from`: Start date filter
- `date_to`: End date filter
- `search`: Search by PO number or description
- `limit`: Page size (default: 50)
- `offset`: Pagination offset
**Response:** List of purchase orders with summary information
**Errors:** 400 (Invalid parameters), 401 (Unauthorized)

#### POST /api/v1/purchase-orders
**Purpose:** Create new purchase order
**Parameters:** Purchase order data including line items
**Response:** Created purchase order with generated PO number
**Errors:** 400 (Invalid data), 422 (Validation error), 404 (Supplier not found)

#### GET /api/v1/purchase-orders/{po_id}
**Purpose:** Get complete purchase order details
**Parameters:** po_id (UUID)
**Response:** Full purchase order with line items and approval status
**Errors:** 404 (PO not found), 403 (Different company)

#### PUT /api/v1/purchase-orders/{po_id}
**Purpose:** Update purchase order (only if draft or pending approval)
**Parameters:** po_id (UUID), updated purchase order data
**Response:** Updated purchase order
**Errors:** 404 (PO not found), 409 (Cannot modify), 422 (Validation error)

#### DELETE /api/v1/purchase-orders/{po_id}
**Purpose:** Cancel purchase order
**Parameters:** po_id (UUID)
**Response:** Success confirmation
**Errors:** 404 (PO not found), 409 (Cannot cancel)

### Purchase Order Line Items

#### POST /api/v1/purchase-orders/{po_id}/lines
**Purpose:** Add line item to purchase order
**Parameters:** po_id (UUID), line item data
**Response:** Created line item with calculated totals
**Errors:** 404 (PO not found), 409 (Cannot modify), 422 (Invalid line data)

#### PUT /api/v1/purchase-orders/{po_id}/lines/{line_id}
**Purpose:** Update purchase order line item
**Parameters:** po_id (UUID), line_id (UUID), updated line data
**Response:** Updated line item with recalculated totals
**Errors:** 404 (Line not found), 409 (Cannot modify), 422 (Invalid data)

#### DELETE /api/v1/purchase-orders/{po_id}/lines/{line_id}
**Purpose:** Remove line item from purchase order
**Parameters:** po_id (UUID), line_id (UUID)
**Response:** Success confirmation with updated totals
**Errors:** 404 (Line not found), 409 (Cannot modify)

### Approval Workflow

#### POST /api/v1/purchase-orders/{po_id}/submit-for-approval
**Purpose:** Submit purchase order for approval workflow
**Parameters:** po_id (UUID)
**Response:** Approval workflow initiation with approver assignments
**Errors:** 404 (PO not found), 409 (Invalid status), 422 (Missing required data)

#### GET /api/v1/purchase-orders/{po_id}/approvals
**Purpose:** Get approval status and history
**Parameters:** po_id (UUID)
**Response:** List of approval steps with current status
**Errors:** 404 (PO not found), 403 (Access denied)

#### POST /api/v1/purchase-orders/{po_id}/approve
**Purpose:** Approve purchase order at current approval level
**Parameters:** po_id (UUID), approval comments (optional)
**Response:** Updated approval status
**Errors:** 404 (PO not found), 403 (Not authorized to approve), 409 (Already processed)

#### POST /api/v1/purchase-orders/{po_id}/reject
**Purpose:** Reject purchase order at current approval level
**Parameters:** po_id (UUID), rejection reason (required)
**Response:** Rejection confirmation with workflow termination
**Errors:** 404 (PO not found), 403 (Not authorized), 400 (Missing reason)

### Supplier Management Integration

#### GET /api/v1/suppliers
**Purpose:** List approved suppliers for purchasing
**Parameters:** 
- `search`: Search by name or code
- `category`: Filter by supplier category
- `active_only`: Show only active suppliers (default: true)
**Response:** List of suppliers with contact information
**Errors:** 401 (Unauthorized)

#### GET /api/v1/suppliers/{supplier_id}/evaluations
**Purpose:** Get supplier performance evaluations
**Parameters:** supplier_id (UUID)
**Response:** List of evaluations with ratings and trends
**Errors:** 404 (Supplier not found), 403 (Access denied)

#### POST /api/v1/suppliers/{supplier_id}/evaluations
**Purpose:** Create new supplier evaluation
**Parameters:** supplier_id (UUID), evaluation data
**Response:** Created evaluation
**Errors:** 404 (Supplier not found), 422 (Invalid evaluation data)

### Reporting and Analytics

#### GET /api/v1/purchase-orders/reports/summary
**Purpose:** Get purchase order summary statistics
**Parameters:**
- `period`: Time period (month, quarter, year)
- `start_date`: Report start date
- `end_date`: Report end date
**Response:** Purchase order metrics and trends
**Errors:** 400 (Invalid parameters), 401 (Unauthorized)

#### GET /api/v1/suppliers/reports/performance
**Purpose:** Get supplier performance report
**Parameters:**
- `period`: Time period for analysis
- `minimum_orders`: Minimum order count for inclusion
**Response:** Supplier performance metrics and rankings
**Errors:** 400 (Invalid parameters), 401 (Unauthorized)

## Module Extension Points

### Custom Endpoint Registration

#### POST /api/v1/modules/{module_id}/endpoints
**Purpose:** Register custom API endpoints for module
**Parameters:** module_id (UUID), endpoint definitions
**Response:** Registered endpoints with generated paths
**Errors:** 404 (Module not found), 409 (Path conflict), 422 (Invalid endpoint)

### Event Hook Registration

#### POST /api/v1/modules/{module_id}/event-hooks
**Purpose:** Register event handlers for module
**Parameters:** module_id (UUID), event hook configurations
**Response:** Registered event hooks with subscription details
**Errors:** 404 (Module not found), 422 (Invalid hook configuration)

## Authentication and Authorization

### API Authentication
- **JWT Bearer Tokens**: All endpoints require valid JWT tokens from user authentication service
- **Service-to-Service**: Module registry endpoints support service authentication for automated operations
- **Company Context**: All endpoints automatically filter data by user's company context

### Permission Requirements
- **Module Management**: Requires 'system.modules.manage' permission
- **Module Installation**: Requires 'company.modules.install' permission
- **Purchase Order Creation**: Requires 'purchasing.orders.create' permission
- **Purchase Order Approval**: Requires dynamic permissions based on approval workflow configuration
- **Supplier Evaluation**: Requires 'purchasing.suppliers.evaluate' permission

## Error Handling

### Standard Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request data is invalid",
    "details": {
      "field": "po_number",
      "issue": "PO number already exists"
    },
    "correlation_id": "uuid-v4-correlation-id"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Request data validation failed
- `RESOURCE_NOT_FOUND`: Requested resource does not exist
- `ACCESS_DENIED`: Insufficient permissions for operation
- `CONFLICT`: Operation conflicts with current state
- `MODULE_UNAVAILABLE`: Module is not available or healthy
- `APPROVAL_REQUIRED`: Operation requires approval workflow completion