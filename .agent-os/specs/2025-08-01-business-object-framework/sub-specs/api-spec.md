# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-08-01-business-object-framework/spec.md

> Created: 2025-08-01
> Version: 1.0.0

## Framework API Patterns

The Business Object Framework establishes standardized API patterns that all business objects will follow. These patterns are implemented as base classes and templates that business object services inherit from.

## Standard CRUD Endpoints

### Base URL Pattern
All business object APIs follow the pattern: `/api/v1/{entity_type}`

Examples:
- `/api/v1/partners`
- `/api/v1/companies` 
- `/api/v1/products`
- `/api/v1/invoices`

### Endpoint Templates

#### GET /{entity_type}
**Purpose:** List entities with pagination and filtering
**Parameters:** 
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)
- `company_id`: Company filter (auto-applied from user context)
- `search`: Full-text search across searchable fields
- `is_active`: Filter by active status (default: true)
- `sort_by`: Sort field (default: 'created_at')
- `sort_direction`: 'asc' or 'desc' (default: 'desc')

**Response:** 
```json
{
  "items": [BusinessObjectResponse],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "pages": 8,
  "has_next": true,
  "has_prev": false
}
```

**Errors:** 
- 401: Unauthorized
- 403: Insufficient permissions

#### POST /{entity_type}
**Purpose:** Create new entity
**Parameters:** BusinessObjectCreate schema
**Response:** BusinessObjectResponse schema with 201 status
**Errors:**
- 400: Validation errors
- 401: Unauthorized
- 403: Insufficient permissions
- 409: Duplicate entity (if applicable)

#### GET /{entity_type}/{id}
**Purpose:** Get single entity by ID
**Parameters:** 
- `id`: Entity ID
- `include_extensions`: Include custom fields (default: false)

**Response:** BusinessObjectResponse schema
**Errors:**
- 404: Entity not found
- 401: Unauthorized
- 403: Insufficient permissions (cross-company access)

#### PUT /{entity_type}/{id}
**Purpose:** Update entity
**Parameters:** BusinessObjectUpdate schema
**Response:** BusinessObjectResponse schema
**Errors:**
- 400: Validation errors
- 401: Unauthorized
- 403: Insufficient permissions
- 404: Entity not found

#### DELETE /{entity_type}/{id}
**Purpose:** Delete entity (soft delete by default)
**Parameters:** 
- `permanent`: Force permanent deletion (admin only)

**Response:** `{"deleted": true, "id": 123}`
**Errors:**
- 401: Unauthorized
- 403: Insufficient permissions
- 404: Entity not found

## Framework-Specific Endpoints

### Extension Fields Management

#### GET /{entity_type}/{id}/extensions
**Purpose:** Get custom fields for an entity
**Response:**
```json
{
  "extensions": {
    "custom_field_1": "value1",
    "custom_field_2": 42,
    "custom_field_3": {"complex": "object"}
  }
}
```

#### PUT /{entity_type}/{id}/extensions
**Purpose:** Update custom fields for an entity
**Parameters:**
```json
{
  "extensions": {
    "field_name": "field_value"
  }
}
```

#### GET /{entity_type}/validators
**Purpose:** Get validation rules for entity type
**Response:**
```json
{
  "validators": [
    {
      "validator_name": "email_format",
      "field_name": "email",
      "validator_type": "format",
      "config": {"pattern": "email"},
      "is_active": true
    }
  ]
}
```

### Audit Trail Access

#### GET /{entity_type}/{id}/audit
**Purpose:** Get audit trail for specific entity
**Parameters:**
- `page`: Page number
- `per_page`: Items per page
- `action_type`: Filter by action ('create', 'update', 'delete')
- `date_from`: Start date filter
- `date_to`: End date filter

**Response:**
```json
{
  "audit_logs": [
    {
      "id": 456,
      "action": "update",
      "entity_type": "partner",
      "entity_id": 123,
      "user_id": 1,
      "user_name": "John Doe",
      "company_id": 1,
      "changes": {
        "name": {"old": "Old Name", "new": "New Name"},
        "email": {"old": "old@example.com", "new": "new@example.com"}
      },
      "timestamp": "2025-08-01T10:30:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10
}
```

## Service Layer Controllers

### Base Controller Template

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.framework.services import BusinessObjectService
from app.framework.schemas import (
    BusinessObjectCreate, 
    BusinessObjectUpdate, 
    BusinessObjectResponse,
    PaginatedResponse
)

def create_business_object_router(
    entity_type: str,
    service_class: BusinessObjectService,
    create_schema: type,
    update_schema: type,
    response_schema: type,
    prefix: str
) -> APIRouter:
    
    router = APIRouter(prefix=f"/api/v1/{prefix}", tags=[entity_type])
    
    @router.get("/", response_model=PaginatedResponse[response_schema])
    async def list_entities(
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        is_active: bool = True,
        sort_by: str = "created_at",
        sort_direction: str = "desc",
        db: AsyncSession = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
        """List entities with pagination and filtering."""
        return await service_class.list_paginated(
            db=db,
            company_id=current_user.company_id,
            page=page,
            per_page=per_page,
            search=search,
            filters={"is_active": is_active},
            sort_by=sort_by,
            sort_direction=sort_direction
        )
    
    @router.post("/", response_model=response_schema, status_code=status.HTTP_201_CREATED)
    async def create_entity(
        entity_data: create_schema,
        db: AsyncSession = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
        """Create new entity."""
        return await service_class.create(
            db=db,
            data=entity_data,
            user_context=current_user
        )
    
    @router.get("/{entity_id}", response_model=response_schema)
    async def get_entity(
        entity_id: int,
        include_extensions: bool = False,
        db: AsyncSession = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
        """Get entity by ID."""
        entity = await service_class.get(
            db=db,
            entity_id=entity_id,
            company_id=current_user.company_id,
            include_extensions=include_extensions
        )
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{entity_type} not found"
            )
        return entity
    
    @router.put("/{entity_id}", response_model=response_schema)
    async def update_entity(
        entity_id: int,
        entity_data: update_schema,
        db: AsyncSession = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
        """Update entity."""
        return await service_class.update(
            db=db,
            entity_id=entity_id,
            data=entity_data,
            user_context=current_user
        )
    
    @router.delete("/{entity_id}")
    async def delete_entity(
        entity_id: int,
        permanent: bool = False,
        db: AsyncSession = Depends(get_db),
        current_user = Depends(get_current_user)
    ):
        """Delete entity."""
        success = await service_class.delete(
            db=db,
            entity_id=entity_id,
            company_id=current_user.company_id,
            permanent=permanent,
            user_context=current_user
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{entity_type} not found"
            )
        return {"deleted": True, "id": entity_id}
    
    return router
```

## Response Schema Templates

### Standard Response Formats

#### Success Response
```json
{
  "id": 123,
  "name": "Example Entity",
  "company_id": 1,
  "is_active": true,
  "created_at": "2025-08-01T10:00:00Z",
  "updated_at": "2025-08-01T10:30:00Z",
  "created_by": 1,
  "framework_version": "1.0"
}
```

#### Error Response
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "type": "value_error.email"
    }
  ],
  "type": "validation_error"
}
```

#### Paginated Response
```json
{
  "items": [BusinessObjectResponse],
  "pagination": {
    "total": 150,
    "page": 1,
    "per_page": 20,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  },
  "filters_applied": {
    "is_active": true,
    "search": "search term"
  }
}
```

## Authentication and Authorization

### Request Headers
- `Authorization: Bearer {jwt_token}` - Required for all endpoints
- `Content-Type: application/json` - Required for POST/PUT requests
- `X-Company-ID: {company_id}` - Optional company override (admin only)

### Permission Validation
- All endpoints automatically validate user permissions based on company_id
- Cross-company access is blocked unless user has admin privileges
- Extension field access requires additional permissions for sensitive fields

### Rate Limiting
- Standard rate limits apply: 1000 requests per hour per user
- Bulk operations have separate limits: 100 requests per hour
- Admin users have higher limits: 5000 requests per hour