# Business Object Framework - Developer Guide

## Overview

The Business Object Framework provides standardized infrastructure for building consistent, scalable business entities in the M-ERP system. It includes automatic audit logging, event publishing, multi-company data isolation, and standardized CRUD operations.

## Architecture

### Core Components

1. **Base Classes** (`app/framework/base.py`)
   - `BusinessObjectBase` - For non-company-scoped objects
   - `CompanyBusinessObject` - For company-scoped objects with multi-tenant isolation

2. **Services** (`app/framework/services.py`)
   - `BusinessObjectService` - Generic service with full CRUD operations
   - `CompanyBusinessObjectService` - Company-scoped service with automatic isolation

3. **Mixins** (`app/framework/mixins.py`)
   - `BusinessObjectMixin` - Common fields (id, timestamps, framework_version)
   - `AuditableMixin` - Automatic audit logging integration
   - `EventPublisherMixin` - Automatic event publishing integration

4. **Schemas** (`app/framework/schemas.py`)
   - `BaseBusinessObjectSchema` - Standardized Pydantic schemas
   - Automatic validation, field transformation, error handling

5. **Controllers** (`app/framework/controllers.py`)
   - Standardized API controller templates
   - Consistent error handling across all endpoints

## Usage Examples

### 1. Creating a Framework-Based Model

```python
from app.framework.base import CompanyBusinessObject
from sqlalchemy import Column, String, Boolean

class Product(CompanyBusinessObject):
    """Product model using Business Object Framework."""
    
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    is_active = Column(Boolean, default=True)
    
    # Framework automatically provides:
    # - id (primary key)
    # - created_at, updated_at (timestamps)
    # - framework_version (version tracking)
    # - company_id (multi-company isolation)
```

### 2. Creating a Framework-Based Service

```python
from app.framework.services import CompanyBusinessObjectService
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

class ProductService(CompanyBusinessObjectService[Product, ProductCreate, ProductUpdate]):
    """Framework-based Product service."""
    
    def __init__(self):
        super().__init__(Product, messaging_service)
    
    # Framework automatically provides:
    # - create(), get_by_id(), get_list(), update(), delete()
    # - activate(), deactivate(), soft_delete()
    # - bulk_create()
    # - Automatic audit logging and event publishing
    
    # Add custom business logic
    async def get_active_products(self, db, company_id):
        return await self.get_list(
            db=db,
            company_id=company_id,
            filters={'is_active': True}
        )
```

### 3. Creating Framework-Based API Endpoints

```python
from fastapi import APIRouter, Depends
from app.services.product_service import product_service

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create product using framework service."""
    return await product_service.create(
        db=db,
        create_data=product_data,
        company_id=2  # From user context
    )

@router.get("/", response_model=ProductListResponse)
async def list_products(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List products with framework pagination."""
    products, total = await product_service.get_list(
        db=db,
        company_id=company_id,
        skip=skip,
        limit=limit
    )
    
    return ProductListResponse(
        products=products,
        total=total,
        page=skip // limit + 1,
        pages=(total + limit - 1) // limit
    )
```

## Key Features

### 1. Automatic Audit Logging
- All create, update, delete operations automatically logged
- Change tracking with before/after states  
- User context capture for compliance

### 2. Event Publishing
- Business events published to Redis Streams
- Integration with notification system
- Event-driven architecture support

### 3. Multi-Company Data Isolation
- Automatic company_id filtering
- Data separation at service level
- Secure multi-tenant operations

### 4. Standardized Error Handling
- Consistent error messages across all services
- Proper HTTP status codes
- Structured error responses

### 5. Built-in Search and Filtering
- Text search across common fields
- Advanced filtering capabilities
- Pagination support

### 6. Activation/Deactivation
- Soft delete functionality
- Activation state management
- Business-friendly operations

## Framework Endpoints

The framework provides standardized endpoints for all business objects:

### Standard CRUD Operations
- `POST /` - Create new object
- `GET /` - List objects with pagination and filtering
- `GET /{id}` - Get object by ID
- `PUT /{id}` - Update object
- `DELETE /{id}` - Delete object

### Framework-Specific Operations
- `PATCH /{id}/activate` - Activate object
- `PATCH /{id}/deactivate` - Deactivate object
- `GET /stats/overview` - Get statistics

### Company-Scoped Operations
- All endpoints automatically enforce company_id filtering
- Multi-company data isolation
- Company-specific statistics and reports

## Migration Guide

### Migrating Existing Models

1. Change base class:
```python
# Old
from app.models.base import CompanyBaseModel
class Partner(CompanyBaseModel):

# New  
from app.framework.base import CompanyBusinessObject
class Partner(CompanyBusinessObject):
```

2. Add framework_version column to database:
```sql
ALTER TABLE partners ADD COLUMN framework_version VARCHAR(20) NOT NULL DEFAULT '1.0.0';
```

3. Create framework service:
```python
from app.framework.services import CompanyBusinessObjectService
service = CompanyBusinessObjectService(Partner, messaging_service)
```

## Testing

The framework includes comprehensive tests:
- `tests/test_business_object_framework.py` - Core framework tests
- `tests/test_framework_services.py` - Service layer tests  
- `tests/test_framework_controllers.py` - API controller tests

Run tests:
```bash
pytest tests/test_business_object_framework.py -v
```

## Current Implementation Status

✅ **Completed:**
- Core framework infrastructure
- Base classes and mixins
- Service layer with full CRUD operations
- API controller templates
- Schema framework
- Extension system
- Comprehensive test suite
- Company and Partner migration completed

✅ **Available Endpoints:**
- Framework Companies API: `http://localhost:8002/api/framework/companies/`
- Framework Partners API: `http://localhost:8002/api/framework/partners/`
- Statistics endpoints for both entities

The Business Object Framework is now ready for Phase 2 development and can be used to rapidly develop new business entities with consistent patterns and automatic infrastructure.

## Next Steps

1. **Enhanced Partner Management**: Extend partners with contacts and addresses using framework
2. **New Business Objects**: Create additional entities (products, invoices, etc.) using framework
3. **Advanced Features**: Add workflow engine, custom field support, and reporting capabilities
4. **Documentation**: Expand API documentation and developer examples