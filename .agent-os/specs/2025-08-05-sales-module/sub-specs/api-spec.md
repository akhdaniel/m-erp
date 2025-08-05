# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-08-05-sales-module/spec.md

> Created: 2025-08-05
> Version: 1.0.0

## API Endpoints Overview

The Sales Module will provide comprehensive REST API endpoints following established patterns from the inventory and purchasing modules, with an estimated **120+ endpoints** across 4 main API modules.

## Quotes API Endpoints

### Core Quote Management
- **POST /api/v1/quotes/** - Create new quote
- **GET /api/v1/quotes/** - List quotes with filtering and pagination
- **GET /api/v1/quotes/{id}/** - Get quote details
- **PUT /api/v1/quotes/{id}/** - Update quote
- **PATCH /api/v1/quotes/{id}/** - Partial quote update
- **DELETE /api/v1/quotes/{id}/** - Delete quote

### Quote Status Management
- **POST /api/v1/quotes/{id}/send/** - Send quote to customer
- **POST /api/v1/quotes/{id}/approve/** - Approve quote
- **POST /api/v1/quotes/{id}/reject/** - Reject quote
- **POST /api/v1/quotes/{id}/convert-to-order/** - Convert quote to sales order
- **POST /api/v1/quotes/{id}/duplicate/** - Duplicate existing quote

### Quote Line Management
- **GET /api/v1/quotes/{id}/lines/** - Get quote lines
- **POST /api/v1/quotes/{id}/lines/** - Add line to quote
- **PUT /api/v1/quotes/{id}/lines/{line_id}/** - Update quote line
- **DELETE /api/v1/quotes/{id}/lines/{line_id}/** - Remove quote line
- **POST /api/v1/quotes/{id}/lines/bulk/** - Bulk add/update lines

### Quote Analytics and Reporting
- **GET /api/v1/quotes/statistics/** - Quote statistics and metrics
- **GET /api/v1/quotes/conversion-rates/** - Quote to order conversion analytics
- **GET /api/v1/quotes/expiring/** - Get expiring quotes
- **GET /api/v1/quotes/by-customer/{customer_id}/** - Get customer quote history

### Quote Search and Filters
- **GET /api/v1/quotes/search/** - Text search across quotes
- **GET /api/v1/quotes/filter/** - Advanced filtering options
- **GET /api/v1/quotes/export/** - Export quotes to CSV/PDF

## Sales Orders API Endpoints

### Core Order Management
- **POST /api/v1/sales-orders/** - Create new sales order
- **GET /api/v1/sales-orders/** - List sales orders with filtering
- **GET /api/v1/sales-orders/{id}/** - Get order details
- **PUT /api/v1/sales-orders/{id}/** - Update sales order
- **PATCH /api/v1/sales-orders/{id}/** - Partial order update
- **DELETE /api/v1/sales-orders/{id}/** - Delete sales order

### Order Status and Fulfillment
- **POST /api/v1/sales-orders/{id}/process/** - Start order processing
- **POST /api/v1/sales-orders/{id}/ship/** - Mark order as shipped
- **POST /api/v1/sales-orders/{id}/deliver/** - Mark order as delivered
- **POST /api/v1/sales-orders/{id}/cancel/** - Cancel sales order
- **GET /api/v1/sales-orders/{id}/status-history/** - Get order status timeline

### Order Line Management
- **GET /api/v1/sales-orders/{id}/lines/** - Get order lines
- **POST /api/v1/sales-orders/{id}/lines/** - Add line to order
- **PUT /api/v1/sales-orders/{id}/lines/{line_id}/** - Update order line
- **DELETE /api/v1/sales-orders/{id}/lines/{line_id}/** - Remove order line
- **POST /api/v1/sales-orders/{id}/lines/{line_id}/ship/** - Ship specific line item

### Inventory Integration
- **POST /api/v1/sales-orders/{id}/reserve-inventory/** - Reserve inventory for order
- **POST /api/v1/sales-orders/{id}/release-inventory/** - Release inventory reservations
- **GET /api/v1/sales-orders/{id}/inventory-status/** - Check inventory reservation status
- **POST /api/v1/sales-orders/{id}/check-availability/** - Verify inventory availability

### Order Analytics and Reporting
- **GET /api/v1/sales-orders/statistics/** - Order statistics and metrics
- **GET /api/v1/sales-orders/fulfillment-metrics/** - Order fulfillment analytics
- **GET /api/v1/sales-orders/overdue/** - Get overdue orders
- **GET /api/v1/sales-orders/by-customer/{customer_id}/** - Get customer order history

## Pricing API Endpoints

### Pricing Rules Management
- **POST /api/v1/pricing-rules/** - Create pricing rule
- **GET /api/v1/pricing-rules/** - List pricing rules
- **GET /api/v1/pricing-rules/{id}/** - Get pricing rule details
- **PUT /api/v1/pricing-rules/{id}/** - Update pricing rule
- **DELETE /api/v1/pricing-rules/{id}/** - Delete pricing rule

### Pricing Rules by Type
- **GET /api/v1/pricing-rules/customer-specific/** - Get customer-specific rules
- **GET /api/v1/pricing-rules/volume-discounts/** - Get volume discount rules
- **GET /api/v1/pricing-rules/promotional/** - Get promotional pricing rules
- **GET /api/v1/pricing-rules/product-category/** - Get category-based rules

### Price Calculation
- **POST /api/v1/pricing/calculate/** - Calculate price for product/customer/quantity
- **POST /api/v1/pricing/calculate-bulk/** - Calculate prices for multiple items
- **POST /api/v1/pricing/quote-totals/** - Calculate quote totals with taxes/discounts
- **POST /api/v1/pricing/validate-discounts/** - Validate discount permissions

### Pricing Analytics
- **GET /api/v1/pricing/rule-usage/** - Pricing rule usage statistics
- **GET /api/v1/pricing/margin-analysis/** - Pricing margin analytics
- **GET /api/v1/pricing/competitive-analysis/** - Price comparison reports

## Sales Analytics API Endpoints

### Sales Performance
- **GET /api/v1/sales-analytics/performance/** - Overall sales performance metrics
- **GET /api/v1/sales-analytics/rep-performance/** - Sales representative performance
- **GET /api/v1/sales-analytics/customer-analytics/** - Customer behavior analytics
- **GET /api/v1/sales-analytics/product-performance/** - Product sales performance

### Sales Forecasting
- **GET /api/v1/sales-analytics/pipeline/** - Sales pipeline analysis
- **GET /api/v1/sales-analytics/forecast/** - Sales forecasting and projections
- **GET /api/v1/sales-analytics/trends/** - Sales trend analysis
- **GET /api/v1/sales-analytics/seasonality/** - Seasonal sales patterns

### Dashboard and Reporting
- **GET /api/v1/sales-analytics/dashboard/** - Sales dashboard summary
- **GET /api/v1/sales-analytics/reports/{report_type}/** - Generate specific reports
- **POST /api/v1/sales-analytics/custom-report/** - Create custom report
- **GET /api/v1/sales-analytics/kpis/** - Key performance indicators

## Integration Endpoints

### Inventory Module Integration
- **GET /api/v1/integration/inventory/availability/{product_id}/** - Check product availability
- **POST /api/v1/integration/inventory/reserve/** - Reserve inventory for quote/order
- **POST /api/v1/integration/inventory/release/** - Release inventory reservations
- **GET /api/v1/integration/inventory/products/search/** - Search products for quotes

### Partner Management Integration
- **GET /api/v1/integration/partners/customers/** - Get customer list for sales
- **GET /api/v1/integration/partners/{id}/sales-history/** - Get customer sales history
- **GET /api/v1/integration/partners/{id}/credit-status/** - Check customer credit status
- **POST /api/v1/integration/partners/{id}/update-sales-data/** - Update customer sales metrics

### Currency Integration
- **GET /api/v1/integration/currency/rates/** - Get current exchange rates
- **POST /api/v1/integration/currency/convert/** - Convert amounts between currencies
- **GET /api/v1/integration/currency/supported/** - Get supported currencies

## Health and System Endpoints

- **GET /health** - Service health check
- **GET /api/docs** - OpenAPI/Swagger documentation
- **GET /api/v1/sales/status** - Sales module status and metrics
- **GET /api/v1/sales/version** - Module version information

## Response Formats

### Standard Response Structure
```json
{
    "success": true,
    "data": {...},
    "message": "Operation completed successfully",
    "meta": {
        "timestamp": "2025-08-05T10:30:00Z",
        "request_id": "req_12345"
    }
}
```

### Error Response Structure
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {...}
    },
    "meta": {
        "timestamp": "2025-08-05T10:30:00Z",
        "request_id": "req_12345"
    }
}
```

### Pagination Structure
```json
{
    "success": true,
    "data": [...],
    "pagination": {
        "page": 1,
        "limit": 50,
        "total": 150,
        "pages": 3,
        "has_next": true,
        "has_prev": false
    }
}
```

## Authentication and Authorization

- **JWT Token Authentication** - Following existing authentication patterns
- **Role-based Access Control** - Integration with existing menu/access rights service
- **Multi-company Data Isolation** - Automatic company_id filtering on all requests
- **Permission Levels** - Read, write, approve, and admin permissions for different operations
- **API Rate Limiting** - Following existing Kong gateway rate limiting rules

## Error Handling

- **HTTP Status Codes** - Proper use of 200, 201, 400, 401, 403, 404, 409, 422, 500
- **Validation Errors** - Detailed field-level validation error messages
- **Business Logic Errors** - Custom error codes for sales-specific business rules
- **Integration Errors** - Proper handling of inventory/partner service communication failures
- **Retry Logic** - Automatic retry for transient failures in external service calls