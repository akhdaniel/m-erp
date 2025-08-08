# API Standards for XERPIUM

> **Comprehensive guide to REST API conventions, patterns, and standards used across all XERPIUM services**
>
> Version: 1.0.0  
> Last Updated: August 8, 2025

## 📋 Table of Contents

1. [Overview](#overview)
2. [URL Structure & Naming](#url-structure--naming)
3. [HTTP Methods & Status Codes](#http-methods--status-codes)
4. [Request & Response Formats](#request--response-formats)
5. [Authentication & Authorization](#authentication--authorization)
6. [Error Handling](#error-handling)
7. [Pagination & Filtering](#pagination--filtering)
8. [Validation Patterns](#validation-patterns)
9. [Multi-Company Support](#multi-company-support)
10. [API Documentation](#api-documentation)

## Overview

XERPIUM follows RESTful API design principles with consistent patterns across all services. This ensures:
- **Predictable API behavior** for developers
- **Consistent user experience** across modules
- **Easy integration** between services
- **Clear documentation** and testing

### Design Principles

- **Resource-based URLs**: URLs represent resources, not actions
- **HTTP methods**: Use appropriate HTTP verbs for operations
- **Stateless**: Each request contains all necessary information
- **Consistent responses**: Standardized response formats
- **Multi-tenant aware**: Company-scoped data isolation
- **Event-driven**: Operations trigger appropriate events

## URL Structure & Naming

### Base URL Pattern

```
http://{service-host}:{port}/api/{version}/{resource}
```

### Examples from XERPIUM Services

```bash
# User Authentication Service (Port 8001)
GET  http://localhost:8001/api/v1/users/
POST http://localhost:8001/api/v1/users/
GET  http://localhost:8001/api/v1/users/123

# Company & Partner Service (Port 8002)  
GET  http://localhost:8002/api/v1/companies/
GET  http://localhost:8002/api/v1/partners/
POST http://localhost:8002/api/v1/partner-communications/

# Inventory Service (Port 8005)
GET  http://localhost:8005/api/v1/products/
GET  http://localhost:8005/api/v1/stock/movements/
POST http://localhost:8005/api/v1/warehouses/

# Sales Service (Port 8006)
GET  http://localhost:8006/api/v1/quotes/
POST http://localhost:8006/pricing/calculate/
```

### Resource Naming Conventions

| Convention | Example | Description |
|------------|---------|-------------|
| **Plural nouns** | `/products/` not `/product/` | Collections use plural |
| **Lowercase** | `/user-profiles/` not `/UserProfiles/` | All lowercase with hyphens |
| **Hierarchical** | `/quotes/123/line-items/` | Show resource relationships |
| **No verbs in URLs** | `/products/` not `/getProducts/` | Actions via HTTP methods |

### Nested Resources

```bash
# Good: Shows relationship
GET /quotes/123/line-items/
GET /warehouses/5/locations/

# Avoid: Too deep nesting
GET /companies/1/warehouses/5/locations/10/products/
```

### Special Endpoints

```bash
# Health checks
GET /health

# Service information
GET /

# API documentation
GET /api/docs
GET /api/redoc

# Bulk operations
POST /products/bulk-update
POST /quotes/bulk-approve

# Business logic endpoints
GET /products/123/margin
POST /pricing/calculate
GET /inventory/123/availability
```

## HTTP Methods & Status Codes

### HTTP Methods Usage

| Method | Purpose | Example | Idempotent |
|--------|---------|---------|------------|
| `GET` | Retrieve resource(s) | `GET /products/` | ✅ Yes |
| `POST` | Create new resource | `POST /products/` | ❌ No |
| `PUT` | Update entire resource | `PUT /products/123` | ✅ Yes |
| `PATCH` | Partial update | `PATCH /products/123` | ❌ No |
| `DELETE` | Remove resource | `DELETE /products/123` | ✅ Yes |

### Standard Status Codes

#### Success Responses (2xx)

```python
# Creation successful
HTTP 201 Created
{
  "id": 123,
  "name": "New Product",
  "created_at": "2025-08-08T10:30:00Z"
}

# Operation successful 
HTTP 200 OK
{
  "products": [...],
  "total": 25
}

# Update successful, no content returned
HTTP 204 No Content
```

#### Client Error Responses (4xx)

```python
# Validation failed
HTTP 400 Bad Request
{
  "error": "Validation Error",
  "details": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}

# Authentication required
HTTP 401 Unauthorized
{
  "error": "Authentication required",
  "message": "Please provide valid JWT token"
}

# Access forbidden
HTTP 403 Forbidden
{
  "error": "Insufficient permissions",
  "message": "User lacks 'product.edit' permission"
}

# Resource not found
HTTP 404 Not Found
{
  "error": "Resource not found",
  "message": "Product with ID 123 not found"
}

# Business rule violation
HTTP 409 Conflict
{
  "error": "Business rule violation",
  "message": "Product with SKU 'ABC123' already exists"
}
```

#### Server Error Responses (5xx)

```python
# Internal server error
HTTP 500 Internal Server Error
{
  "error": "Internal server error",
  "message": "An unexpected error occurred",
  "trace_id": "abc123def456"
}

# Service unavailable
HTTP 503 Service Unavailable
{
  "error": "Service temporarily unavailable",
  "message": "Database maintenance in progress"
}
```

## Request & Response Formats

### Request Format

#### JSON Content Type
```bash
Content-Type: application/json
```

#### Standard Request Body Structure

```python
# Simple creation
{
  "name": "iPhone 15",
  "sku": "IPHONE15-128",
  "list_price": 999.99
}

# Complex nested structure
{
  "quote": {
    "customer_id": 123,
    "valid_until": "2025-09-01",
    "line_items": [
      {
        "product_id": 456,
        "quantity": 2,
        "unit_price": 99.99
      }
    ]
  }
}

# Bulk operations
{
  "operations": [
    {"id": 1, "action": "activate"},
    {"id": 2, "action": "deactivate"}
  ]
}
```

### Response Format

#### Standard Response Structure

```python
# Single resource
{
  "id": 123,
  "name": "Product Name",
  "sku": "PRODUCT-SKU",
  "created_at": "2025-08-08T10:30:00Z",
  "updated_at": "2025-08-08T10:30:00Z",
  "company_id": 1
}

# Collection with metadata
{
  "items": [...],
  "total": 150,
  "page": 1,
  "per_page": 50,
  "pages": 3,
  "has_next": true,
  "has_prev": false
}

# Business operation result
{
  "success": true,
  "message": "Operation completed",
  "results": {
    "processed": 25,
    "successful": 23,
    "failed": 2
  },
  "errors": [
    {
      "item_id": 10,
      "error": "Insufficient inventory"
    }
  ]
}
```

#### Timestamps and Dates

```python
# Always use ISO 8601 format with UTC timezone
{
  "created_at": "2025-08-08T10:30:00Z",
  "updated_at": "2025-08-08T15:45:30Z",
  "due_date": "2025-08-15",
  "scheduled_at": "2025-08-10T09:00:00Z"
}
```

#### Decimal Values

```python
# Use string representation for precise decimals
{
  "price": "99.99",
  "tax_amount": "8.00",
  "discount_percentage": "15.50"
}
```

## Authentication & Authorization

### JWT Token Authentication

#### Request Headers
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

#### Token Validation Pattern

```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and validate JWT token."""
    try:
        # Validate token with auth service
        user_data = validate_jwt_token(credentials.credentials)
        return user_data
    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

def get_current_company_id(user_data=Depends(get_current_user)):
    """Extract company ID from user context."""
    return user_data.get("company_id")
```

### Permission-Based Authorization

```python
def require_permission(permission: str):
    """Decorator to require specific permission."""
    def permission_checker(user_data=Depends(get_current_user)):
        if permission not in user_data.get("permissions", []):
            raise HTTPException(
                status_code=403,
                detail=f"Required permission: {permission}"
            )
        return user_data
    return permission_checker

# Usage in endpoints
@router.post("/products/")
async def create_product(
    product_data: ProductCreate,
    user_data=Depends(require_permission("product.create"))
):
    # Implementation
    pass
```

## Error Handling

### Error Response Schema

```python
from pydantic import BaseModel
from typing import List, Optional

class ErrorDetail(BaseModel):
    field: str
    message: str
    code: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    trace_id: Optional[str] = None
```

### Exception Handling Patterns

```python
from fastapi import HTTPException, status

class XerpiumException(Exception):
    """Base exception for XERPIUM services."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class ValidationError(XerpiumException):
    """Validation error exception."""
    def __init__(self, message: str, details: List[dict] = None):
        super().__init__(message, 400)
        self.details = details or []

class NotFoundError(XerpiumException):
    """Resource not found exception."""
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, 404)

class BusinessRuleError(XerpiumException):
    """Business rule violation exception."""
    def __init__(self, message: str):
        super().__init__(message, 409)

# Global exception handler
@app.exception_handler(XerpiumException)
async def xerpium_exception_handler(request, exc: XerpiumException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": getattr(exc, 'details', None)
        }
    )
```

### Validation Error Examples

```python
# Field validation errors
HTTP 400 Bad Request
{
  "error": "ValidationError",
  "message": "Request validation failed",
  "details": [
    {
      "field": "email",
      "message": "Field required",
      "code": "missing"
    },
    {
      "field": "price",
      "message": "Value must be greater than 0",
      "code": "value_error"
    }
  ]
}

# Business rule validation
HTTP 409 Conflict
{
  "error": "BusinessRuleError", 
  "message": "Cannot delete product with active orders",
  "details": [
    {
      "field": "active_orders",
      "message": "Product has 3 active orders",
      "code": "business_constraint"
    }
  ]
}
```

## Pagination & Filtering

### Query Parameters

```python
from typing import Optional
from fastapi import Query

class PaginationParams(BaseModel):
    page: int = Query(1, ge=1, description="Page number")
    per_page: int = Query(50, ge=1, le=100, description="Items per page")

class FilterParams(BaseModel):
    search: Optional[str] = Query(None, description="Search term")
    is_active: Optional[bool] = Query(None, description="Filter by active status")
    created_after: Optional[datetime] = Query(None, description="Created after date")
    created_before: Optional[datetime] = Query(None, description="Created before date")
```

### Pagination Response

```python
# Request
GET /products/?page=2&per_page=25&search=iphone&is_active=true

# Response  
{
  "items": [...],
  "pagination": {
    "page": 2,
    "per_page": 25,
    "total": 150,
    "pages": 6,
    "has_next": true,
    "has_prev": true,
    "next_page": 3,
    "prev_page": 1
  },
  "filters": {
    "search": "iphone",
    "is_active": true,
    "applied_count": 2
  }
}
```

### Sorting

```bash
# Single field sort
GET /products/?sort=name

# Multiple field sort  
GET /products/?sort=category_id,name

# Descending sort
GET /products/?sort=-created_at,name

# Complex sort
GET /products/?sort=category_id,-price,name
```

### Advanced Filtering

```bash
# Range filters
GET /products/?price_min=10.00&price_max=100.00

# Date range  
GET /orders/?created_after=2025-01-01&created_before=2025-08-31

# Multiple values
GET /products/?category_id=1,2,3&status=active,draft

# Nested filtering
GET /quotes/?customer.company_type=enterprise&line_items.product.category=electronics
```

## Validation Patterns

### Pydantic Schema Standards

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    sku: str = Field(..., min_length=1, max_length=100, description="Stock keeping unit")
    price: Decimal = Field(..., ge=0, decimal_places=2, description="Product price")
    category_id: Optional[int] = Field(None, ge=1, description="Category ID")
    is_active: bool = Field(True, description="Active status")
    
    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('sku')
    def validate_sku_format(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('SKU must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()

class ProductCreate(ProductBase):
    """Schema for creating products."""
    pass

class ProductUpdate(BaseModel):
    """Schema for updating products."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    category_id: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    """Schema for product responses."""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    margin_percentage: float
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z",
            Decimal: lambda v: str(v)
        }
```

### Custom Validators

```python
from typing import Any, Dict

@validator('email')
def validate_email(cls, v):
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, v):
        raise ValueError('Invalid email format')
    return v.lower()

@validator('phone_number')
def validate_phone(cls, v):
    """Validate phone number format."""
    if v and not re.match(r'^\+?[\d\s\-\(\)]+$', v):
        raise ValueError('Invalid phone number format')
    return v

@validator('quantity')
def validate_quantity(cls, v, values):
    """Cross-field validation."""
    if v <= 0:
        raise ValueError('Quantity must be positive')
    
    # Check against maximum if available
    max_quantity = values.get('max_available')
    if max_quantity and v > max_quantity:
        raise ValueError(f'Quantity cannot exceed {max_quantity}')
    
    return v
```

## Multi-Company Support

### Company Context Injection

```python
def get_company_context(
    user_data=Depends(get_current_user)
) -> int:
    """Extract company ID from authenticated user context."""
    company_id = user_data.get("company_id")
    if not company_id:
        raise HTTPException(
            status_code=400,
            detail="No company context available"
        )
    return company_id

# Usage in endpoints
@router.get("/products/")
async def get_products(
    company_id: int = Depends(get_company_context),
    service: ProductService = Depends(get_product_service)
):
    return service.get_products(company_id=company_id)
```

### Data Isolation Patterns

```python
# Service layer automatically filters by company
class ProductService:
    def get_products(self, company_id: int) -> List[Product]:
        """Get products for specific company only."""
        return self.db.query(Product).filter(
            Product.company_id == company_id
        ).all()
    
    def create_product(self, product_data: dict, company_id: int) -> Product:
        """Create product with company isolation."""
        product = Product(
            company_id=company_id,  # Always set company_id
            **product_data
        )
        self.db.add(product)
        self.db.commit()
        return product
```

### Cross-Company Operations

```python
# Explicit cross-company access (requires special permissions)
@router.get("/admin/all-companies/products/")
async def get_all_company_products(
    user_data=Depends(require_permission("admin.cross_company_view")),
    service: ProductService = Depends(get_product_service)
):
    """Admin endpoint to view products across all companies."""
    return service.get_all_products()  # No company filter
```

## API Documentation

### OpenAPI/Swagger Configuration

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="XERPIUM Product Service",
    description="Product catalog management for XERPIUM ERP platform",
    version="1.0.0",
    contact={
        "name": "XERPIUM Development Team",
        "email": "dev@xerpium.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

def custom_openapi():
    """Custom OpenAPI schema with enhanced documentation."""
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token from XERPIUM authentication service"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### Endpoint Documentation

```python
@router.post(
    "/products/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new product",
    description="Create a new product in the catalog with validation and business rules",
    responses={
        201: {
            "description": "Product created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "name": "iPhone 15",
                        "sku": "IPHONE15-128",
                        "price": "999.99"
                    }
                }
            }
        },
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "ValidationError",
                        "message": "Invalid input data",
                        "details": [
                            {
                                "field": "price",
                                "message": "Price must be positive"
                            }
                        ]
                    }
                }
            }
        },
        409: {
            "description": "Business rule violation",
            "content": {
                "application/json": {
                    "example": {
                        "error": "BusinessRuleError",
                        "message": "Product with SKU 'IPHONE15-128' already exists"
                    }
                }
            }
        }
    },
    tags=["products"]
)
async def create_product(
    product_data: ProductCreate,
    company_id: int = Depends(get_company_context),
    service: ProductService = Depends(get_product_service)
):
    """Create a new product with comprehensive validation."""
    try:
        product = service.create_product(product_data.model_dump(), company_id)
        return product
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
```

## Testing API Standards

### Test Structure

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_product_success():
    """Test successful product creation."""
    product_data = {
        "name": "Test Product",
        "sku": "TEST-001",
        "price": "99.99"
    }
    
    response = client.post(
        "/api/v1/products/",
        json=product_data,
        headers={"Authorization": "Bearer valid-token"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["sku"] == product_data["sku"]
    assert "id" in data
    assert "created_at" in data

def test_create_product_validation_error():
    """Test validation error handling."""
    invalid_data = {
        "name": "",  # Empty name should fail
        "price": -10  # Negative price should fail
    }
    
    response = client.post(
        "/api/v1/products/",
        json=invalid_data,
        headers={"Authorization": "Bearer valid-token"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "ValidationError"
    assert "details" in data
    assert len(data["details"]) >= 2  # At least 2 validation errors

def test_unauthorized_access():
    """Test unauthorized access handling."""
    response = client.get("/api/v1/products/")
    
    assert response.status_code == 401
    data = response.json()
    assert "Authentication required" in data["message"]
```

## API Standards Checklist

### For Every Endpoint

- [ ] **URL follows naming conventions** (plural, lowercase, hyphenated)
- [ ] **HTTP method is appropriate** for the operation
- [ ] **Status codes are correct** for all scenarios
- [ ] **Request/response schemas are defined** with Pydantic
- [ ] **Authentication is implemented** where required
- [ ] **Authorization is checked** for protected resources
- [ ] **Company context is enforced** for multi-tenant data
- [ ] **Error handling is comprehensive** with proper error responses
- [ ] **Validation is thorough** with clear error messages
- [ ] **Documentation is complete** with examples and descriptions

### For Collections

- [ ] **Pagination is implemented** with metadata
- [ ] **Filtering options are available** for common use cases  
- [ ] **Sorting is supported** with multiple field options
- [ ] **Search functionality** is provided where appropriate
- [ ] **Performance is optimized** with proper indexing

### For Business Operations

- [ ] **Business rules are validated** before operations
- [ ] **Events are published** for significant actions
- [ ] **Transactions are handled** properly with rollback
- [ ] **Audit trails are created** for compliance
- [ ] **Error recovery is planned** for failed operations

---

## Summary

Following these API standards ensures:
- **Consistency** across all XERPIUM services
- **Developer productivity** through predictable patterns
- **Integration reliability** between modules
- **Maintainability** of the platform
- **User experience** quality across the admin interface

Refer to existing services (inventory-service, sales-service) for implementation examples that follow these standards.