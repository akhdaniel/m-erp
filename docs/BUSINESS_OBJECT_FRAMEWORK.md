# Business Object Framework Guide

> **Comprehensive guide to XERPIUM's Business Object Framework for rapid service development**
>
> Version: 1.0.0  
> Last Updated: August 8, 2025

## 📋 Table of Contents

1. [Framework Overview](#framework-overview)
2. [Core Components](#core-components)
3. [Base Classes](#base-classes)
4. [Mixins System](#mixins-system)
5. [Service Layer Pattern](#service-layer-pattern)
6. [Schema Framework](#schema-framework)
7. [Controller Templates](#controller-templates)
8. [Multi-Company Integration](#multi-company-integration)
9. [Event Publishing](#event-publishing)
10. [Migration and Extension](#migration-and-extension)

## Framework Overview

The Business Object Framework is XERPIUM's standardized development framework that provides:

- **90% reduction** in development time for new business entities
- **Automatic CRUD operations** with validation and error handling
- **Multi-company data isolation** built-in
- **Event-driven architecture** with automatic event publishing
- **Comprehensive audit trails** for compliance
- **Consistent API patterns** across all services

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Business Object Framework                    │
├─────────────────────────────────────────────────────────────────┤
│  Models Layer                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Base Classes    │  │    Mixins       │  │   Extensions    │ │
│  │ - BusinessBase  │  │ - Auditable     │  │ - Custom Logic  │ │
│  │ - CompanyBase   │  │ - EventPub      │  │ - Field Extensions│ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Service Layer                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Generic Service │  │ CRUD Operations │  │ Business Logic  │ │
│  │ - Base Methods  │  │ - Create/Read   │  │ - Validation    │ │
│  │ - Filtering     │  │ - Update/Delete │  │ - Rules Engine  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Controller Layer                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ API Controllers │  │ Schema Validation│  │ Error Handling │ │
│  │ - REST Endpoints│  │ - Pydantic      │  │ - HTTP Status   │ │
│  │ - Route Templates│  │ - Serialization │  │ - Custom Errors │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Key Benefits

- **Rapid Development**: New business entities in hours, not days
- **Consistent Patterns**: Same approach across all services
- **Built-in Features**: Audit, events, multi-company support included
- **Type Safety**: Full Pydantic validation and type hints
- **Extensibility**: Easy to customize and extend
- **Testing**: Comprehensive test patterns included

## Core Components

### 1. Framework Location

The framework is located in the company-partner-service and can be imported by other services:

```python
# Import framework components
from company_partner_service.app.framework.base import (
    BusinessObjectBase,
    CompanyBusinessObject
)
from company_partner_service.app.framework.mixins import (
    BusinessObjectMixin,
    AuditableMixin, 
    EventPublisherMixin
)
from company_partner_service.app.framework.services import (
    GenericBusinessObjectService
)
from company_partner_service.app.framework.controllers import (
    BusinessObjectController
)
```

### 2. Framework Components

```
app/framework/
├── base.py              # Base classes for business objects
├── mixins.py            # Functionality mixins
├── services.py          # Generic service layer
├── controllers.py       # API controller templates
├── schemas.py           # Pydantic schema patterns
├── extensions.py        # Extension and customization
└── documentation.py     # Framework documentation
```

## Base Classes

### 1. BusinessObjectBase

For system-wide objects that don't need company isolation:

```python
from sqlalchemy import Column, String, Text, Boolean
from app.framework.base import BusinessObjectBase

class SystemConfiguration(BusinessObjectBase):
    """System-wide configuration object."""
    
    __tablename__ = "system_configurations"
    
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(Text)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Automatically includes:
    # - id (primary key)
    # - created_at, updated_at (timestamps)
    # - framework_version (tracking)
    # - audit logging capability
    # - event publishing capability
```

### 2. CompanyBusinessObject

For business entities that need multi-company data isolation:

```python
from sqlalchemy import Column, String, Decimal, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.framework.base import CompanyBusinessObject

class Product(CompanyBusinessObject):
    """Product entity with multi-company isolation."""
    
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), nullable=False, index=True)
    list_price = Column(Decimal(10, 2), default=0.00)
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    
    # Automatically includes:
    # - All BusinessObjectBase features
    # - company_id (foreign key with automatic filtering)
    # - Multi-company data isolation
    # - Company-scoped queries
    
    category = relationship("ProductCategory", back_populates="products")
    
    def __str__(self):
        return f"Product(sku='{self.sku}', name='{self.name}')"
```

### 3. Database Relationships

```python
class ProductCategory(CompanyBusinessObject):
    """Product category with hierarchical structure."""
    
    __tablename__ = "product_categories"
    
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("product_categories.id"))
    
    # Self-referential relationship
    parent = relationship(
        "ProductCategory", 
        remote_side="ProductCategory.id",
        back_populates="children"
    )
    children = relationship(
        "ProductCategory",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    
    # One-to-many relationship
    products = relationship("Product", back_populates="category")
```

## Mixins System

### 1. BusinessObjectMixin

Provides core functionality for all business objects:

```python
class BusinessObjectMixin:
    """Core business object functionality."""
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    framework_version = Column(String(20), default="1.0.0", nullable=False)
    
    def __str__(self) -> str:
        """Smart string representation."""
        # Automatically finds name/title/email fields for display
        for attr in ['name', 'title', 'code', 'email']:
            if hasattr(self, attr) and getattr(self, attr):
                return f"{self.__class__.__name__}(id={self.id}, {attr}='{getattr(self, attr)}')"
        return f"{self.__class__.__name__}(id={self.id})"
```

### 2. AuditableMixin

Provides automatic audit logging:

```python
class AuditableMixin:
    """Automatic audit logging integration."""
    
    def _capture_state(self) -> Dict[str, Any]:
        """Capture current object state for audit logging."""
        state = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name, None)
            if isinstance(value, datetime):
                state[column.name] = value.isoformat()
            elif value is not None:
                state[column.name] = value
        return state
    
    def _publish_audit_event(self, action: str, before_state: Dict = None, after_state: Dict = None):
        """Publish audit event for compliance tracking."""
        audit_data = {
            "table_name": self.__tablename__,
            "record_id": self.id,
            "action": action,
            "before_state": before_state,
            "after_state": after_state,
            "company_id": getattr(self, 'company_id', None),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to audit service
        # (Implementation would use Redis message publisher)
        self._publish_event("AUDIT_LOG_CREATED", audit_data)
```

### 3. EventPublisherMixin

Provides event publishing capabilities:

```python
class EventPublisherMixin:
    """Automatic event publishing integration."""
    
    def _publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """Publish business event to message bus."""
        try:
            from messaging import MessagePublisher, EventType
            
            publisher = MessagePublisher()
            event_payload = {
                "event_type": event_type,
                "entity_type": self.__class__.__name__,
                "entity_id": self.id,
                "company_id": getattr(self, 'company_id', None),
                "data": event_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            publisher.publish_event(EventType(event_type), event_payload)
            
        except Exception as e:
            # Log error but don't fail the main operation
            logger.error(f"Failed to publish event {event_type}: {e}")
    
    def _publish_created_event(self):
        """Publish entity created event."""
        self._publish_event(f"{self.__class__.__name__.upper()}_CREATED", {
            "name": getattr(self, 'name', str(self)),
            "created_at": self.created_at.isoformat()
        })
    
    def _publish_updated_event(self, changed_fields: List[str]):
        """Publish entity updated event."""
        self._publish_event(f"{self.__class__.__name__.upper()}_UPDATED", {
            "name": getattr(self, 'name', str(self)),
            "changed_fields": changed_fields,
            "updated_at": self.updated_at.isoformat()
        })
```

## Service Layer Pattern

### 1. Generic Business Object Service

The framework provides a base service class that handles common operations:

```python
from typing import List, Optional, Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

class GenericBusinessObjectService:
    """Generic service for business object operations."""
    
    def __init__(self, model_class: Type, db_session: Session):
        self.model_class = model_class
        self.db = db_session
        self.is_company_scoped = hasattr(model_class, 'company_id')
    
    def create(self, data: Dict[str, Any], company_id: Optional[int] = None) -> Any:
        """Create new business object with automatic event publishing."""
        # Add company_id for company-scoped objects
        if self.is_company_scoped and company_id is not None:
            data['company_id'] = company_id
        
        # Create object
        obj = self.model_class(**data)
        
        # Capture before state for audit
        before_state = None
        if hasattr(obj, '_capture_state'):
            before_state = obj._capture_state()
        
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        
        # Capture after state and publish events
        if hasattr(obj, '_capture_state'):
            after_state = obj._capture_state()
            obj._publish_audit_event("CREATE", before_state, after_state)
        
        if hasattr(obj, '_publish_created_event'):
            obj._publish_created_event()
        
        return obj
    
    def get_by_id(self, obj_id: int, company_id: Optional[int] = None) -> Optional[Any]:
        """Get object by ID with company filtering."""
        query = self.db.query(self.model_class).filter(
            self.model_class.id == obj_id
        )
        
        if self.is_company_scoped and company_id is not None:
            query = query.filter(self.model_class.company_id == company_id)
        
        return query.first()
    
    def get_all(self, company_id: Optional[int] = None, filters: Optional[Dict] = None) -> List[Any]:
        """Get all objects with optional filtering."""
        query = self.db.query(self.model_class)
        
        # Apply company filtering
        if self.is_company_scoped and company_id is not None:
            query = query.filter(self.model_class.company_id == company_id)
        
        # Apply additional filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model_class, field).in_(value))
                    else:
                        query = query.filter(getattr(self.model_class, field) == value)
        
        return query.all()
    
    def update(self, obj_id: int, update_data: Dict[str, Any], company_id: Optional[int] = None) -> Any:
        """Update object with audit trail."""
        obj = self.get_by_id(obj_id, company_id)
        if not obj:
            raise ValueError(f"{self.model_class.__name__} with ID {obj_id} not found")
        
        # Capture before state
        before_state = obj._capture_state() if hasattr(obj, '_capture_state') else None
        
        # Update fields
        changed_fields = []
        for field, value in update_data.items():
            if hasattr(obj, field) and getattr(obj, field) != value:
                setattr(obj, field, value)
                changed_fields.append(field)
        
        self.db.commit()
        self.db.refresh(obj)
        
        # Publish events if changes were made
        if changed_fields:
            if hasattr(obj, '_capture_state'):
                after_state = obj._capture_state()
                obj._publish_audit_event("UPDATE", before_state, after_state)
            
            if hasattr(obj, '_publish_updated_event'):
                obj._publish_updated_event(changed_fields)
        
        return obj
    
    def delete(self, obj_id: int, company_id: Optional[int] = None) -> bool:
        """Delete object (soft delete if supported)."""
        obj = self.get_by_id(obj_id, company_id)
        if not obj:
            return False
        
        # Soft delete if is_active field exists
        if hasattr(obj, 'is_active'):
            return self.update(obj_id, {"is_active": False}, company_id) is not None
        
        # Hard delete
        before_state = obj._capture_state() if hasattr(obj, '_capture_state') else None
        
        self.db.delete(obj)
        self.db.commit()
        
        # Publish delete event
        if hasattr(obj, '_publish_event'):
            obj._publish_event(f"{self.model_class.__name__.upper()}_DELETED", {
                "deleted_id": obj_id,
                "before_state": before_state
            })
        
        return True
    
    def search(self, search_term: str, company_id: Optional[int] = None, search_fields: List[str] = None) -> List[Any]:
        """Full-text search across specified fields."""
        if not search_fields:
            search_fields = ['name', 'title', 'description', 'code', 'email']
        
        query = self.db.query(self.model_class)
        
        # Apply company filtering
        if self.is_company_scoped and company_id is not None:
            query = query.filter(self.model_class.company_id == company_id)
        
        # Build search conditions
        search_conditions = []
        for field in search_fields:
            if hasattr(self.model_class, field):
                search_conditions.append(
                    getattr(self.model_class, field).ilike(f"%{search_term}%")
                )
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        return query.all()
```

### 2. Specialized Service Implementation

```python
from app.framework.services import GenericBusinessObjectService
from app.models.product import Product

class ProductService(GenericBusinessObjectService):
    """Specialized product service with custom business logic."""
    
    def __init__(self, db_session: Session):
        super().__init__(Product, db_session)
    
    def create_product(self, product_data: Dict[str, Any], company_id: int) -> Product:
        """Create product with SKU validation."""
        # Business rule: SKU must be unique within company
        existing = self.db.query(Product).filter(
            and_(
                Product.company_id == company_id,
                Product.sku == product_data.get('sku')
            )
        ).first()
        
        if existing:
            raise ValueError(f"Product with SKU '{product_data['sku']}' already exists")
        
        return self.create(product_data, company_id)
    
    def calculate_margin(self, product_id: int, company_id: int) -> Dict[str, Any]:
        """Calculate product margin (custom business logic)."""
        product = self.get_by_id(product_id, company_id)
        if not product:
            raise ValueError("Product not found")
        
        margin_amount = product.list_price - product.cost_price
        margin_percentage = (margin_amount / product.list_price) * 100 if product.list_price > 0 else 0
        
        return {
            "product_id": product.id,
            "margin_amount": margin_amount,
            "margin_percentage": margin_percentage
        }
    
    def get_low_stock_products(self, company_id: int, threshold: int = None) -> List[Product]:
        """Get products below minimum stock level."""
        query = self.db.query(Product).filter(
            Product.company_id == company_id,
            Product.track_inventory == True
        )
        
        if threshold is not None:
            query = query.filter(Product.current_stock <= threshold)
        else:
            query = query.filter(Product.current_stock <= Product.minimum_stock)
        
        return query.all()
```

## Schema Framework

### 1. Base Schema Patterns

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class BusinessObjectBaseSchema(BaseModel):
    """Base schema with common patterns."""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z",
            Decimal: lambda v: str(v)
        }

class CreateSchema(BusinessObjectBaseSchema):
    """Base create schema."""
    pass

class UpdateSchema(BaseModel):
    """Base update schema with optional fields."""
    pass

class ResponseSchema(BusinessObjectBaseSchema):
    """Base response schema with automatic fields."""
    id: int
    created_at: datetime
    updated_at: datetime
    framework_version: str

class CompanyResponseSchema(ResponseSchema):
    """Response schema for company-scoped objects."""
    company_id: int
```

### 2. Product Schema Example

```python
class ProductBase(BusinessObjectBaseSchema):
    """Base product schema."""
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    list_price: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    cost_price: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    category_id: Optional[int] = None
    is_active: bool = True
    
    @validator('sku')
    def validate_sku(cls, v):
        """Validate SKU format."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('SKU must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()
    
    @validator('list_price', 'cost_price')
    def validate_prices(cls, v):
        """Validate price values."""
        if v < 0:
            raise ValueError('Prices must be non-negative')
        return v

class ProductCreate(ProductBase):
    """Product creation schema."""
    pass

class ProductUpdate(BaseModel):
    """Product update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    list_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    cost_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    category_id: Optional[int] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase, CompanyResponseSchema):
    """Product response schema."""
    category_name: Optional[str] = None
    margin_percentage: float = 0.0
    
    @validator('margin_percentage', always=True)
    def calculate_margin(cls, v, values):
        """Calculate margin percentage."""
        if 'list_price' in values and 'cost_price' in values:
            list_price = values['list_price']
            cost_price = values['cost_price']
            if list_price > 0:
                return float(((list_price - cost_price) / list_price) * 100)
        return 0.0
```

## Controller Templates

### 1. Generic Controller

```python
from typing import List, Type, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from pydantic import BaseModel

class BusinessObjectController:
    """Generic controller for business object endpoints."""
    
    def __init__(self, 
                 service_class: Type,
                 create_schema: Type[BaseModel],
                 update_schema: Type[BaseModel], 
                 response_schema: Type[BaseModel],
                 prefix: str,
                 tags: List[str]):
        
        self.service_class = service_class
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.response_schema = response_schema
        
        self.router = APIRouter(prefix=prefix, tags=tags)
        self._add_routes()
    
    def _add_routes(self):
        """Add standard CRUD routes."""
        
        @self.router.post("/", response_model=self.response_schema, status_code=status.HTTP_201_CREATED)
        async def create_object(
            obj_data: self.create_schema,
            company_id: int = Depends(get_company_context),
            service = Depends(self._get_service)
        ):
            """Create new object."""
            try:
                obj = service.create(obj_data.model_dump(), company_id)
                return obj
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.router.get("/", response_model=List[self.response_schema])
        async def get_objects(
            company_id: int = Depends(get_company_context),
            service = Depends(self._get_service),
            search: Optional[str] = Query(None),
            is_active: Optional[bool] = Query(None)
        ):
            """Get all objects with filtering."""
            filters = {}
            if is_active is not None:
                filters['is_active'] = is_active
                
            if search:
                return service.search(search, company_id)
            else:
                return service.get_all(company_id, filters)
        
        @self.router.get("/{obj_id}", response_model=self.response_schema)
        async def get_object(
            obj_id: int = Path(..., gt=0),
            company_id: int = Depends(get_company_context),
            service = Depends(self._get_service)
        ):
            """Get object by ID."""
            obj = service.get_by_id(obj_id, company_id)
            if not obj:
                raise HTTPException(status_code=404, detail="Object not found")
            return obj
        
        @self.router.put("/{obj_id}", response_model=self.response_schema)
        async def update_object(
            obj_id: int = Path(..., gt=0),
            obj_data: self.update_schema,
            company_id: int = Depends(get_company_context),
            service = Depends(self._get_service)
        ):
            """Update object."""
            try:
                update_dict = {k: v for k, v in obj_data.model_dump().items() if v is not None}
                if not update_dict:
                    raise HTTPException(status_code=400, detail="No valid update data provided")
                
                obj = service.update(obj_id, update_dict, company_id)
                return obj
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
        
        @self.router.delete("/{obj_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_object(
            obj_id: int = Path(..., gt=0),
            company_id: int = Depends(get_company_context),
            service = Depends(self._get_service)
        ):
            """Delete object."""
            success = service.delete(obj_id, company_id)
            if not success:
                raise HTTPException(status_code=404, detail="Object not found")
    
    def _get_service(self, db: Session = Depends(get_db_session)):
        """Get service instance."""
        return self.service_class(db)
```

### 2. Product Controller Example

```python
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

# Create product controller with framework
product_controller = BusinessObjectController(
    service_class=ProductService,
    create_schema=ProductCreate,
    update_schema=ProductUpdate,
    response_schema=ProductResponse,
    prefix="/api/v1/products",
    tags=["products"]
)

# Get the router
product_router = product_controller.router

# Add custom endpoints
@product_router.get("/{product_id}/margin")
async def get_product_margin(
    product_id: int = Path(..., gt=0),
    company_id: int = Depends(get_company_context),
    service: ProductService = Depends(get_product_service)
):
    """Get product margin calculation."""
    try:
        margin_data = service.calculate_margin(product_id, company_id)
        return margin_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

## Multi-Company Integration

### 1. Automatic Data Filtering

```python
class CompanyBusinessObject(BusinessObjectBase):
    """Base class automatically handles company filtering."""
    
    @declared_attr
    def company_id(cls):
        return Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    @classmethod
    def for_company(cls, company_id: int):
        """Query scope for specific company."""
        return session.query(cls).filter(cls.company_id == company_id)
    
    @classmethod  
    def current_company(cls):
        """Query scope for current company context."""
        # Would get from request context in real implementation
        company_id = get_current_company_id()
        return cls.for_company(company_id)
```

### 2. Service Layer Integration

```python
class ProductService(GenericBusinessObjectService):
    """Product service with automatic company scoping."""
    
    def create_product(self, product_data: Dict[str, Any], company_id: int) -> Product:
        """Create product with company validation."""
        # Ensure company exists and user has access
        if not self.validate_company_access(company_id):
            raise ValueError("Invalid or unauthorized company")
        
        return self.create(product_data, company_id)
    
    def validate_company_access(self, company_id: int) -> bool:
        """Validate user has access to company."""
        # In real implementation, would check user's company memberships
        current_user_companies = get_user_company_ids()
        return company_id in current_user_companies
```

## Event Publishing

### 1. Automatic Event Generation

```python
# Events are automatically published for:
product = service.create_product(product_data, company_id)
# Publishes: PRODUCT_CREATED

service.update_product(product.id, update_data, company_id)  
# Publishes: PRODUCT_UPDATED

service.delete_product(product.id, company_id)
# Publishes: PRODUCT_DELETED
```

### 2. Custom Event Handlers

```python
class ProductService(GenericBusinessObjectService):
    """Service with custom event logic."""
    
    def create_product(self, product_data: Dict[str, Any], company_id: int) -> Product:
        """Create product with custom events."""
        product = super().create(product_data, company_id)
        
        # Custom business events
        if product.list_price > 1000:
            self._publish_custom_event("HIGH_VALUE_PRODUCT_CREATED", {
                "product_id": product.id,
                "price": str(product.list_price),
                "category": product.category.name if product.category else None
            })
        
        return product
    
    def _publish_custom_event(self, event_type: str, data: Dict[str, Any]):
        """Publish custom business event."""
        from messaging import MessagePublisher, EventType
        
        publisher = MessagePublisher()
        publisher.publish_event(EventType.CUSTOM, {
            "custom_event_type": event_type,
            "service": "product-service",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
```

## Migration and Extension

### 1. Migrating Existing Models

```python
# Before: Standard SQLAlchemy model
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# After: Framework-based model
class Product(CompanyBusinessObject):
    __tablename__ = "products"
    
    name = Column(String(255), nullable=False)
    # All other fields automatically inherited:
    # - id, created_at, updated_at, framework_version
    # - company_id (with automatic filtering)
    # - audit logging capability
    # - event publishing capability

# Migration script to add framework columns
def upgrade():
    """Add framework columns to existing table."""
    op.add_column('products', sa.Column('company_id', sa.Integer(), nullable=True))
    op.add_column('products', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('products', sa.Column('framework_version', sa.String(20), server_default='1.0.0'))
    
    # Set default company_id for existing records
    op.execute("UPDATE products SET company_id = 1 WHERE company_id IS NULL")
    
    # Make company_id non-nullable
    op.alter_column('products', 'company_id', nullable=False)
    
    # Add foreign key
    op.create_foreign_key('fk_products_company_id', 'products', 'companies', ['company_id'], ['id'])
    op.create_index('ix_products_company_id', 'products', ['company_id'])
```

### 2. Framework Extensions

```python
from app.framework.base import CompanyBusinessObject
from app.framework.mixins import EventPublisherMixin

class TimestampedBusinessObject(CompanyBusinessObject):
    """Extended base class with additional timestamp tracking."""
    
    __abstract__ = True
    
    last_accessed_at = Column(DateTime)
    accessed_by = Column(String(100))
    
    def record_access(self, user_id: str):
        """Record when object was accessed."""
        self.last_accessed_at = datetime.utcnow()
        self.accessed_by = user_id
        
        # Publish access event
        self._publish_event("OBJECT_ACCESSED", {
            "object_type": self.__class__.__name__,
            "object_id": self.id,
            "accessed_by": user_id,
            "accessed_at": self.last_accessed_at.isoformat()
        })

class GeolocationMixin:
    """Add geolocation fields to business objects."""
    
    latitude = Column(Decimal(10, 8))
    longitude = Column(Decimal(11, 8))
    location_name = Column(String(255))
    
    def set_location(self, lat: float, lng: float, name: str = None):
        """Set object location."""
        self.latitude = Decimal(str(lat))
        self.longitude = Decimal(str(lng))
        self.location_name = name

# Usage in custom models
class Warehouse(TimestampedBusinessObject, GeolocationMixin):
    """Warehouse with timestamp tracking and geolocation."""
    
    __tablename__ = "warehouses"
    
    name = Column(String(255), nullable=False)
    address = Column(Text)
    
    # Inherits all framework features plus:
    # - Access tracking
    # - Geolocation fields
    # - Custom event publishing
```

## Framework Development Checklist

### For New Business Objects

- [ ] **Inherit from appropriate base class** (`BusinessObjectBase` or `CompanyBusinessObject`)
- [ ] **Define table name and columns** following naming conventions
- [ ] **Add relationships** with proper back references
- [ ] **Implement __str__ method** for debugging
- [ ] **Add custom validation** in model or schema
- [ ] **Create Pydantic schemas** for API validation
- [ ] **Implement service class** extending `GenericBusinessObjectService`
- [ ] **Add custom business logic** methods to service
- [ ] **Create API controller** using framework patterns
- [ ] **Add custom endpoints** for business operations
- [ ] **Write comprehensive tests** for model, service, and API
- [ ] **Document API endpoints** with OpenAPI

### For Service Integration

- [ ] **Register service endpoints** with API gateway
- [ ] **Set up event subscriptions** for relevant business events
- [ ] **Configure multi-company isolation** properly
- [ ] **Add proper authentication** and authorization
- [ ] **Implement error handling** with proper HTTP status codes
- [ ] **Add logging and monitoring** for business operations
- [ ] **Create database migrations** for new tables/columns
- [ ] **Update docker configuration** for deployment

---

## Summary

The Business Object Framework provides:

- **Rapid Development**: 90% reduction in code for new business entities
- **Consistency**: Same patterns across all XERPIUM services  
- **Built-in Features**: Multi-company, audit, events, validation included
- **Extensibility**: Easy to customize and extend for specific needs
- **Type Safety**: Full Pydantic validation and SQLAlchemy typing

This framework is the foundation of XERPIUM's development velocity and consistency. Use it as the starting point for all new business entities and services.