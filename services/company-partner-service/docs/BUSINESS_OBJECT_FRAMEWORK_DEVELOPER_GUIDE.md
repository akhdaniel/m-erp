# Business Object Framework Developer Guide

## 🚀 Overview

The XERPIUM Business Object Framework is a comprehensive system for building standardized, extensible business objects with automatic audit logging, event publishing, and custom field support. This guide provides developers with everything needed to leverage the framework effectively.

## 📚 Table of Contents

1. [Framework Architecture](#framework-architecture)
2. [Getting Started](#getting-started)
3. [Core Components](#core-components)
4. [Schema Development](#schema-development)
5. [Service Layer](#service-layer)
6. [API Controllers](#api-controllers)
7. [Extension System](#extension-system)
8. [Audit Logging](#audit-logging)
9. [Event Publishing](#event-publishing)
10. [Best Practices](#best-practices)
11. [Testing Patterns](#testing-patterns)
12. [Performance Optimization](#performance-optimization)

## 🏗️ Framework Architecture

### Core Principles

The Business Object Framework follows these architectural principles:

1. **Standardization**: Consistent patterns across all business objects
2. **Extensibility**: Custom fields without database schema changes
3. **Auditability**: Automatic tracking of all changes
4. **Event-Driven**: Real-time notifications for business events
5. **Multi-Company**: Built-in data isolation for multi-tenant applications

### Framework Layers

```
┌─────────────────────────────────────┐
│           API Controllers           │  ← FastAPI routers with standardized endpoints
├─────────────────────────────────────┤
│           Service Layer             │  ← Business logic and CRUD operations
├─────────────────────────────────────┤
│          Schema Layer               │  ← Pydantic validation and serialization
├─────────────────────────────────────┤
│          Model Layer                │  ← SQLAlchemy models with framework mixins
├─────────────────────────────────────┤
│         Extension System            │  ← Custom fields and validation rules
├─────────────────────────────────────┤
│      Audit & Event System          │  ← Change tracking and event publishing
└─────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites

```bash
# Required dependencies
pip install fastapi sqlalchemy pydantic redis asyncpg alembic
```

### Framework Structure

```
app/
├── framework/
│   ├── __init__.py          # Framework exports
│   ├── base.py              # Base classes and mixins
│   ├── mixins.py            # Framework mixins
│   ├── schemas.py           # Base schema classes
│   ├── services.py          # Service layer templates
│   ├── controllers.py       # API controller factories
│   ├── extensions.py        # Extension system
│   └── documentation.py     # Auto-documentation tools
└── your_service/
    ├── models.py            # Your business models
    ├── schemas.py           # Your Pydantic schemas
    ├── services.py          # Your service classes
    └── routers.py           # Your API routers
```

### Basic Setup

```python
# app/your_service/models.py
from app.framework.base import CompanyBaseModel
from app.framework.mixins import BusinessObjectMixin, AuditableMixin, EventPublisherMixin

class YourModel(CompanyBaseModel, BusinessObjectMixin, AuditableMixin, EventPublisherMixin):
    __tablename__ = "your_models"
    
    name: str = Column(String(255), nullable=False)
    description: str = Column(Text, nullable=True)
    is_active: bool = Column(Boolean, default=True)
```

## 🧱 Core Components

### 1. Base Models

The framework provides base model classes with essential functionality:

```python
from app.framework.base import CompanyBaseModel, BaseModel

# For multi-company models
class Partner(CompanyBaseModel):
    __tablename__ = "partners"
    
    name: str = Column(String(255), nullable=False)
    email: str = Column(String(255), nullable=True)

# For shared/system models  
class Currency(BaseModel):
    __tablename__ = "currencies"
    
    code: str = Column(String(3), nullable=False, unique=True)
    name: str = Column(String(100), nullable=False)
```

### 2. Framework Mixins

Mixins provide standardized functionality:

```python
from app.framework.mixins import BusinessObjectMixin, AuditableMixin, EventPublisherMixin

class BusinessModel(CompanyBaseModel, BusinessObjectMixin, AuditableMixin, EventPublisherMixin):
    """
    BusinessObjectMixin: Adds timestamps, framework version
    AuditableMixin: Enables automatic audit logging
    EventPublisherMixin: Enables automatic event publishing
    """
    __tablename__ = "business_models"
    
    # Your business fields
    name: str = Column(String(255), nullable=False)
```

## 📋 Schema Development

### Base Schema Classes

```python
from app.framework.schemas import BaseBusinessObjectSchema, CompanyBusinessObjectSchema
from pydantic import Field, validator

# For models with company_id
class PartnerBase(CompanyBusinessObjectSchema):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, regex=r'^[^@]+@[^@]+\.[^@]+$')
    phone: Optional[str] = Field(None, max_length=50)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

# Create/Update/Response schemas
class PartnerCreate(PartnerBase):
    """Schema for creating partners"""
    pass

class PartnerUpdate(PartnerBase):
    """Schema for updating partners"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)

class PartnerResponse(PartnerBase):
    """Schema for partner responses"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### Schema Factory Functions

```python
from app.framework.schemas import create_business_object_schemas

# Auto-generate schemas
PartnerCreate, PartnerUpdate, PartnerResponse = create_business_object_schemas(
    "Partner",
    base_fields={
        "name": (str, Field(..., min_length=1, max_length=255)),
        "email": (Optional[str], Field(None, regex=r'^[^@]+@[^@]+\.[^@]+$')),
        "phone": (Optional[str], Field(None, max_length=50))
    },
    company_scoped=True
)
```

### Advanced Validation

```python
from app.framework.schemas import BaseBusinessObjectSchema
from pydantic import validator, root_validator

class AdvancedPartnerSchema(BaseBusinessObjectSchema):
    name: str
    email: Optional[str] = None
    partner_type: str = Field(..., regex=r'^(customer|supplier|both)$')
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    
    @validator('email')
    def validate_email_required_for_customers(cls, v, values):
        if values.get('partner_type') == 'customer' and not v:
            raise ValueError('Email is required for customers')
        return v
    
    @root_validator
    def validate_business_rules(cls, values):
        partner_type = values.get('partner_type')
        credit_limit = values.get('credit_limit')
        
        if partner_type == 'supplier' and credit_limit:
            raise ValueError('Suppliers cannot have credit limits')
        
        return values
```

## 🔧 Service Layer

### Basic Service Implementation

```python
from app.framework.services import CompanyBusinessObjectService
from app.models.partner import Partner
from app.schemas.partner import PartnerCreate, PartnerUpdate, PartnerResponse

class PartnerService(CompanyBusinessObjectService[Partner, PartnerCreate, PartnerUpdate]):
    """Partner service with framework capabilities"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Partner)
    
    async def create_partner(self, partner_data: PartnerCreate) -> Partner:
        """Create a new partner with automatic audit logging and event publishing"""
        return await self.create(partner_data.dict())
    
    async def get_partner(self, partner_id: int, company_id: int) -> Optional[Partner]:
        """Get partner by ID with company isolation"""
        return await self.get_by_id(partner_id, company_id)
    
    async def update_partner(self, partner_id: int, partner_data: PartnerUpdate, company_id: int) -> Optional[Partner]:
        """Update partner with change tracking"""
        return await self.update(partner_id, partner_data.dict(exclude_unset=True), company_id)
    
    async def delete_partner(self, partner_id: int, company_id: int) -> bool:
        """Soft delete partner"""
        return await self.soft_delete(partner_id, company_id)
```

### Advanced Service Features

```python
from app.framework.services import CompanyBusinessObjectService
from typing import List, Dict, Any

class AdvancedPartnerService(CompanyBusinessObjectService):
    
    async def get_active_customers(self, company_id: int) -> List[Partner]:
        """Get all active customer partners"""
        filters = {
            "partner_type": "customer",
            "is_active": True
        }
        return await self.get_list(filters=filters, company_id=company_id)
    
    async def bulk_create_partners(self, partners_data: List[PartnerCreate]) -> List[Partner]:
        """Bulk create partners with batch audit logging"""
        return await self.bulk_create([p.dict() for p in partners_data])
    
    async def get_partners_with_extensions(self, company_id: int) -> List[Dict[str, Any]]:
        """Get partners with their custom fields"""
        partners = await self.get_list(company_id=company_id)
        
        result = []
        for partner in partners:
            partner_dict = {
                "id": partner.id,
                "name": partner.name,
                "email": partner.email,
                "extensions": await self.get_extensions(partner.id)
            }
            result.append(partner_dict)
        
        return result
    
    async def search_partners(self, query: str, company_id: int) -> List[Partner]:
        """Search partners by name or email"""
        filters = {
            "$or": [
                {"name__icontains": query},
                {"email__icontains": query}
            ]
        }
        return await self.get_list(filters=filters, company_id=company_id)
```

### Service Factory Pattern

```python
from app.framework.services import create_business_object_service

# Auto-generate service class
PartnerService = create_business_object_service(
    Partner,
    PartnerCreate,
    PartnerUpdate,
    company_scoped=True,
    additional_methods={
        "get_active": lambda self, company_id: self.get_list(
            filters={"is_active": True}, 
            company_id=company_id
        )
    }
)
```

## 🌐 API Controllers

### Basic Router Implementation

```python
from app.framework.controllers import create_business_object_router
from app.services.partner_service import PartnerService
from app.schemas.partner import PartnerCreate, PartnerUpdate, PartnerResponse

# Auto-generate router with standard CRUD endpoints
partner_router = create_business_object_router(
    service_class=PartnerService,
    create_schema=PartnerCreate,
    update_schema=PartnerUpdate,
    response_schema=PartnerResponse,
    prefix="/partners",
    tags=["Partners"],
    company_scoped=True
)
```

### Custom Router with Additional Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException
from app.framework.controllers import BusinessObjectRouter
from app.dependencies import get_current_user, get_db
from typing import List

class PartnerRouter(BusinessObjectRouter):
    
    def __init__(self):
        super().__init__(
            service_class=PartnerService,
            create_schema=PartnerCreate,
            update_schema=PartnerUpdate,
            response_schema=PartnerResponse,
            prefix="/partners",
            tags=["Partners"]
        )
        
        # Add custom endpoints
        self.add_custom_endpoints()
    
    def add_custom_endpoints(self):
        
        @self.router.get("/active", response_model=List[PartnerResponse])
        async def get_active_partners(
            company_id: int = Depends(get_current_user_company),
            db: AsyncSession = Depends(get_db)
        ):
            """Get all active partners"""
            service = PartnerService(db)
            partners = await service.get_active_customers(company_id)
            return partners
        
        @self.router.post("/{partner_id}/add-contact")
        async def add_partner_contact(
            partner_id: int,
            contact_data: ContactCreate,
            company_id: int = Depends(get_current_user_company),
            db: AsyncSession = Depends(get_db)
        ):
            """Add a contact to a partner"""
            service = PartnerService(db)
            
            # Verify partner exists and belongs to company
            partner = await service.get_partner(partner_id, company_id)
            if not partner:
                raise HTTPException(status_code=404, detail="Partner not found")
            
            # Add contact logic here
            contact = await ContactService(db).create_contact(contact_data)
            return contact

# Create router instance
router = PartnerRouter().router
```

### Error Handling and Response Formatting

```python
from app.framework.controllers import StandardizedErrorHandler, ResponseFormatter
from fastapi import HTTPException

class CustomPartnerRouter:
    
    def __init__(self):
        self.error_handler = StandardizedErrorHandler()
        self.response_formatter = ResponseFormatter()
        self.router = APIRouter()
        self.setup_routes()
    
    def setup_routes(self):
        
        @self.router.post("/partners/", response_model=Dict[str, Any])
        async def create_partner(
            partner_data: PartnerCreate,
            db: AsyncSession = Depends(get_db)
        ):
            try:
                service = PartnerService(db)
                partner = await service.create_partner(partner_data)
                
                return self.response_formatter.success_response(
                    data=partner,
                    message="Partner created successfully",
                    status_code=201
                )
                
            except ValidationError as e:
                return self.error_handler.validation_error_response(e)
            except Exception as e:
                return self.error_handler.internal_error_response(e)
```

## 🔌 Extension System

### Adding Custom Fields

```python
from app.framework.extensions import ExtensibleMixin

class PartnerService(CompanyBusinessObjectService):
    
    async def add_credit_limit_field(self, partner_id: int, credit_limit: Decimal) -> None:
        """Add credit limit as custom field"""
        await self.set_extension(
            entity_id=partner_id,
            field_name="credit_limit",
            field_type="decimal",
            field_value=str(credit_limit),
            validation_rules=[
                {
                    "validator_type": "range",
                    "config": {"min_value": 0, "max_value": 1000000}
                }
            ]
        )
    
    async def get_partners_by_credit_limit(self, min_limit: Decimal, company_id: int) -> List[Partner]:
        """Query partners by credit limit custom field"""
        extension_filters = {
            "credit_limit__gte": str(min_limit)
        }
        return await self.get_list(
            extension_filters=extension_filters,
            company_id=company_id
        )
```

### Custom Field Types

```python
from app.framework.extensions import ExtensionValidator

# String field with pattern validation
await service.set_extension(
    entity_id=partner_id,
    field_name="tax_id",
    field_type="string",
    field_value="12-3456789",
    validation_rules=[
        {
            "validator_type": "pattern",
            "config": {"pattern": r'^\d{2}-\d{7}$'}
        }
    ]
)

# JSON field for complex data
await service.set_extension(
    entity_id=partner_id,
    field_name="address",
    field_type="json",
    field_value=json.dumps({
        "street": "123 Main St",
        "city": "Anytown",
        "postal_code": "12345",
        "country": "US"
    }),
    validation_rules=[
        {
            "validator_type": "required",
            "config": {"required_keys": ["street", "city", "country"]}
        }
    ]
)

# Date field with range validation
await service.set_extension(
    entity_id=partner_id,
    field_name="contract_expiry",
    field_type="date",
    field_value="2025-12-31",
    validation_rules=[
        {
            "validator_type": "range",
            "config": {
                "min_value": "2025-01-01",
                "max_value": "2030-12-31"
            }
        }
    ]
)
```

### Dynamic Validation Rules

```python
from app.framework.extensions import ExtensionValidator

class CustomPartnerValidator(ExtensionValidator):
    
    async def validate_credit_rating(self, value: str, config: Dict[str, Any]) -> bool:
        """Custom validator for credit ratings"""
        valid_ratings = config.get("valid_ratings", ["A", "B", "C", "D"])
        return value in valid_ratings
    
    async def validate_partner_category(self, value: str, config: Dict[str, Any]) -> bool:
        """Custom validator for partner categories"""
        # Business logic to validate partner category
        if value == "premium" and not await self.check_premium_eligibility():
            return False
        return True

# Register custom validators
validator = CustomPartnerValidator()
await service.set_extension(
    entity_id=partner_id,
    field_name="credit_rating",
    field_type="string",
    field_value="A",
    validation_rules=[
        {
            "validator_type": "custom",
            "validator_function": "validate_credit_rating",
            "config": {"valid_ratings": ["A", "B", "C"]}
        }
    ]
)
```

## 📊 Audit Logging

### Automatic Audit Logging

```python
# Audit logging is automatic when using framework services
service = PartnerService(db)

# This automatically creates an audit log entry
partner = await service.create_partner(partner_data)
# Audit entry: action="partner_created", changes={"name": {"old": None, "new": "ACME Corp"}}

# This automatically logs the changes
updated_partner = await service.update_partner(partner.id, {"email": "new@acme.com"}, company_id)
# Audit entry: action="partner_updated", changes={"email": {"old": None, "new": "new@acme.com"}}
```

### Retrieving Audit Trail

```python
from app.services.audit_service import AuditService

class PartnerService(CompanyBusinessObjectService):
    
    async def get_partner_audit_trail(self, partner_id: int, company_id: int) -> List[Dict[str, Any]]:
        """Get complete audit trail for a partner"""
        audit_service = AuditService(self.db)
        
        audit_entries = await audit_service.get_audit_trail(
            entity_type="partner",
            entity_id=partner_id,
            company_id=company_id
        )
        
        return [
            {
                "action": entry.action,
                "timestamp": entry.timestamp,
                "user_id": entry.user_id,
                "changes": entry.changes,
                "correlation_id": entry.correlation_id
            }
            for entry in audit_entries
        ]
    
    async def get_recent_partner_changes(self, partner_id: int, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent changes to a partner"""
        audit_service = AuditService(self.db)
        
        since = datetime.utcnow() - timedelta(hours=hours)
        return await audit_service.get_changes_since(
            entity_type="partner",
            entity_id=partner_id,
            since=since
        )
```

### Custom Audit Events

```python
from app.framework.mixins import AuditableMixin

class PartnerService(CompanyBusinessObjectService):
    
    async def approve_partner(self, partner_id: int, approver_id: int, company_id: int) -> bool:
        """Approve a partner with custom audit event"""
        partner = await self.get_by_id(partner_id, company_id)
        if not partner:
            return False
        
        # Update partner status
        partner.status = "approved"
        partner.approved_by = approver_id
        partner.approved_at = datetime.utcnow()
        
        # Create custom audit event
        await self.audit_service.log_custom_event(
            action="partner_approved",
            entity_type="partner",
            entity_id=partner_id,
            user_id=approver_id,
            company_id=company_id,
            changes={
                "status": {"old": "pending", "new": "approved"},
                "approved_by": {"old": None, "new": approver_id},
                "approved_at": {"old": None, "new": partner.approved_at.isoformat()}
            },
            metadata={
                "approval_workflow": "standard",
                "approval_level": "manager"
            }
        )
        
        await self.db.commit()
        return True
```

## 📡 Event Publishing

### Automatic Event Publishing

```python
# Events are automatically published when using framework services
service = PartnerService(db)

# This publishes a "partner_created" event to Redis Streams
partner = await service.create_partner(partner_data)

# This publishes a "partner_updated" event
updated_partner = await service.update_partner(partner.id, updates, company_id)

# This publishes a "partner_deleted" event
await service.delete_partner(partner.id, company_id)
```

### Custom Events

```python
from app.services.messaging_service import MessagingService

class PartnerService(CompanyBusinessObjectService):
    
    async def send_welcome_email(self, partner_id: int, company_id: int) -> bool:
        """Send welcome email and publish custom event"""
        partner = await self.get_by_id(partner_id, company_id)
        if not partner:
            return False
        
        # Send email logic here
        email_sent = await self.email_service.send_welcome(partner.email)
        
        if email_sent:
            # Publish custom event
            await self.messaging_service.publish_custom_event(
                event_type="partner_welcome_email_sent",
                entity_type="partner",
                entity_id=partner_id,
                company_id=company_id,
                data={
                    "email": partner.email,
                    "template": "welcome_email",
                    "sent_at": datetime.utcnow().isoformat()
                }
            )
        
        return email_sent
    
    async def bulk_update_status(self, partner_ids: List[int], new_status: str, company_id: int) -> int:
        """Bulk update partner status with batch event"""
        updated_count = 0
        
        for partner_id in partner_ids:
            partner = await self.get_by_id(partner_id, company_id)
            if partner:
                old_status = partner.status
                partner.status = new_status
                updated_count += 1
                
                # Individual update event
                await self.messaging_service.publish_partner_updated(
                    partner_id=partner_id,
                    changes={"status": {"old": old_status, "new": new_status}},
                    correlation_id=f"bulk_update_{uuid.uuid4()}"
                )
        
        # Bulk operation summary event
        await self.messaging_service.publish_custom_event(
            event_type="partner_bulk_status_update",
            entity_type="partner",
            entity_id=None,
            company_id=company_id,
            data={
                "partner_ids": partner_ids,
                "new_status": new_status,
                "updated_count": updated_count,
                "operation_id": str(uuid.uuid4())
            }
        )
        
        await self.db.commit()
        return updated_count
```

### Event Consumers

```python
from app.messaging.consumer import EventConsumer

class PartnerEventConsumer(EventConsumer):
    
    async def handle_partner_created(self, event_data: Dict[str, Any]) -> None:
        """Handle partner creation events"""
        partner_id = event_data["entity_id"]
        company_id = event_data["company_id"]
        
        # Business logic for new partner
        await self.setup_default_credit_limit(partner_id, company_id)
        await self.send_welcome_email(partner_id)
        await self.notify_sales_team(partner_id, company_id)
    
    async def handle_partner_updated(self, event_data: Dict[str, Any]) -> None:
        """Handle partner update events"""
        changes = event_data["data"].get("changes", {})
        
        if "email" in changes:
            # Email changed - update mailing lists
            await self.update_mailing_lists(event_data["entity_id"])
        
        if "status" in changes and changes["status"]["new"] == "inactive":
            # Partner deactivated - cleanup tasks
            await self.cleanup_inactive_partner(event_data["entity_id"])

# Register event handlers
consumer = PartnerEventConsumer()
consumer.register_handler("partner_created", consumer.handle_partner_created)
consumer.register_handler("partner_updated", consumer.handle_partner_updated)
```

## 💡 Best Practices

### 1. Schema Design

```python
# ✅ Good: Clear, specific validation
class PartnerCreate(BaseBusinessObjectSchema):
    name: str = Field(..., min_length=1, max_length=255, description="Partner company name")
    email: Optional[str] = Field(None, regex=r'^[^@]+@[^@]+\.[^@]+$', description="Primary email address")
    partner_type: str = Field(..., regex=r'^(customer|supplier|both)$', description="Partner business relationship")
    
    @validator('name')
    def validate_name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Partner name cannot be empty or whitespace')
        return v.strip()

# ❌ Bad: Vague validation
class PartnerCreate(BaseModel):
    name: str
    email: str = None
    type: str
```

### 2. Service Layer Organization

```python
# ✅ Good: Focused, single-responsibility methods
class PartnerService(CompanyBusinessObjectService):
    
    async def create_customer_partner(self, partner_data: CustomerPartnerCreate) -> Partner:
        """Create a customer partner with default settings"""
        data = partner_data.dict()
        data.update({
            "partner_type": "customer",
            "payment_terms": "net_30",
            "credit_limit": 0
        })
        return await self.create(data)
    
    async def activate_partner(self, partner_id: int, company_id: int) -> bool:
        """Activate a partner and trigger related processes"""
        partner = await self.get_by_id(partner_id, company_id)
        if not partner:
            return False
        
        partner.is_active = True
        partner.activated_at = datetime.utcnow()
        
        # Trigger welcome process
        await self.send_welcome_email(partner_id, company_id)
        
        await self.db.commit()
        return True

# ❌ Bad: God methods doing too much
class PartnerService(CompanyBusinessObjectService):
    
    async def create_partner_and_setup_everything(self, partner_data, setup_accounts, send_emails, create_contacts):
        # Too many responsibilities in one method
        pass
```

### 3. Error Handling

```python
# ✅ Good: Specific error handling with proper logging
from app.framework.exceptions import BusinessLogicError, ValidationError
import logging

logger = logging.getLogger(__name__)

class PartnerService(CompanyBusinessObjectService):
    
    async def update_credit_limit(self, partner_id: int, credit_limit: Decimal, company_id: int) -> Partner:
        """Update partner credit limit with business rules"""
        try:
            partner = await self.get_by_id(partner_id, company_id)
            if not partner:
                raise BusinessLogicError(f"Partner {partner_id} not found")
            
            if partner.partner_type != "customer":
                raise BusinessLogicError("Only customers can have credit limits")
            
            if credit_limit < 0:
                raise ValidationError("Credit limit cannot be negative")
            
            # Check if increase requires approval
            if credit_limit > partner.credit_limit and credit_limit > 10000:
                await self.request_credit_approval(partner_id, credit_limit)
                return partner  # Don't update until approved
            
            old_limit = partner.credit_limit
            partner.credit_limit = credit_limit
            
            await self.db.commit()
            
            logger.info(f"Credit limit updated for partner {partner_id}: {old_limit} -> {credit_limit}")
            return partner
            
        except Exception as e:
            logger.error(f"Failed to update credit limit for partner {partner_id}: {e}")
            await self.db.rollback()
            raise

# ❌ Bad: Generic error handling
async def update_credit_limit(self, partner_id, credit_limit):
    try:
        # Some code
        pass
    except Exception as e:
        print(f"Error: {e}")
        return None
```

### 4. Testing Patterns

```python
# ✅ Good: Comprehensive test coverage
import pytest
from unittest.mock import AsyncMock, patch

class TestPartnerService:
    
    @pytest.fixture
    async def partner_service(self, db_session):
        return PartnerService(db_session)
    
    @pytest.fixture
    def partner_data(self):
        return PartnerCreate(
            name="Test Partner",
            email="test@partner.com",
            partner_type="customer"
        )
    
    async def test_create_partner_success(self, partner_service, partner_data):
        """Test successful partner creation"""
        partner = await partner_service.create_partner(partner_data)
        
        assert partner.name == "Test Partner"
        assert partner.email == "test@partner.com"
        assert partner.partner_type == "customer"
        assert partner.is_active == True
    
    async def test_create_partner_duplicate_email(self, partner_service, partner_data):
        """Test partner creation with duplicate email"""
        # Create first partner
        await partner_service.create_partner(partner_data)
        
        # Try to create second partner with same email
        with pytest.raises(ValidationError, match="Email already exists"):
            await partner_service.create_partner(partner_data)
    
    @patch('app.services.messaging_service.MessagingService.publish_partner_created')
    async def test_create_partner_publishes_event(self, mock_publish, partner_service, partner_data):
        """Test that partner creation publishes event"""
        partner = await partner_service.create_partner(partner_data)
        
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args[1]
        assert call_args['partner_id'] == partner.id
        assert 'correlation_id' in call_args

# ❌ Bad: Minimal, unclear tests
def test_partner():
    # Create partner
    partner = create_partner("Test")
    
    # Check it exists
    assert partner
```

### 5. Performance Optimization

```python
# ✅ Good: Efficient queries with proper indexing
class PartnerService(CompanyBusinessObjectService):
    
    async def get_partners_with_recent_orders(self, company_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get partners with recent orders using efficient query"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Single query with joins instead of N+1 queries
        query = (
            select(Partner, func.count(Order.id).label('order_count'))
            .join(Order, Partner.id == Order.partner_id)
            .where(
                and_(
                    Partner.company_id == company_id,
                    Partner.is_active == True,
                    Order.created_at >= since_date
                )
            )
            .group_by(Partner.id)
            .options(selectinload(Partner.contacts))  # Eager load related data
        )
        
        result = await self.db.execute(query)
        return [
            {
                "partner": partner,
                "order_count": order_count,
                "contacts": partner.contacts
            }
            for partner, order_count in result
        ]
    
    async def bulk_update_status(self, partner_ids: List[int], status: str, company_id: int) -> int:
        """Efficient bulk update using single query"""
        query = (
            update(Partner)
            .where(
                and_(
                    Partner.id.in_(partner_ids),
                    Partner.company_id == company_id
                )
            )
            .values(
                status=status,
                updated_at=datetime.utcnow()
            )
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount

# ❌ Bad: N+1 queries and inefficient operations
async def get_partners_with_orders(self, company_id):
    partners = await self.get_list(company_id=company_id)
    
    result = []
    for partner in partners:  # N+1 query problem
        orders = await self.get_partner_orders(partner.id)
        contacts = await self.get_partner_contacts(partner.id)
        result.append({
            "partner": partner,
            "orders": orders,
            "contacts": contacts
        })
    
    return result
```

## 🧪 Testing Patterns

### Unit Testing Framework Components

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.framework.services import CompanyBusinessObjectService
from app.models.partner import Partner

class TestBusinessObjectFramework:
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        db = AsyncMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.rollback = AsyncMock()
        return db
    
    @pytest.fixture
    def partner_service(self, mock_db):
        """Partner service with mocked dependencies"""
        service = PartnerService(mock_db)
        service.audit_service = AsyncMock()
        service.messaging_service = AsyncMock()
        return service
    
    async def test_create_with_audit_logging(self, partner_service):
        """Test that creation triggers audit logging"""
        partner_data = {"name": "Test Partner", "company_id": 1}
        
        # Mock partner creation
        mock_partner = MagicMock()
        mock_partner.id = 1
        mock_partner.name = "Test Partner"
        partner_service.create = AsyncMock(return_value=mock_partner)
        
        # Execute
        result = await partner_service.create_partner(PartnerCreate(**partner_data))
        
        # Verify audit logging was called
        partner_service.audit_service.log_partner_created.assert_called_once()
        assert result.name == "Test Partner"
    
    async def test_extension_field_validation(self, partner_service):
        """Test custom field validation"""
        with pytest.raises(ValidationError, match="Credit limit cannot be negative"):
            await partner_service.set_extension(
                entity_id=1,
                field_name="credit_limit",
                field_type="decimal",
                field_value="-1000.00"
            )
```

### Integration Testing

```python
import pytest
from httpx import AsyncClient
from app.main import app
from app.core.database import get_db
from tests.conftest import override_get_db

class TestPartnerAPIIntegration:
    
    @pytest.mark.asyncio
    async def test_partner_crud_workflow(self, client: AsyncClient, auth_headers):
        """Test complete partner CRUD workflow"""
        
        # 1. Create partner
        partner_data = {
            "name": "Integration Test Partner",
            "email": "integration@test.com",
            "partner_type": "customer"
        }
        
        create_response = await client.post(
            "/partners/",
            json=partner_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        partner = create_response.json()["data"]
        partner_id = partner["id"]
        
        # 2. Get partner
        get_response = await client.get(
            f"/partners/{partner_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["data"]["name"] == "Integration Test Partner"
        
        # 3. Update partner
        update_data = {"email": "updated@test.com"}
        update_response = await client.put(
            f"/partners/{partner_id}",
            json=update_data,
            headers=auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["data"]["email"] == "updated@test.com"
        
        # 4. Add custom field
        extension_response = await client.post(
            f"/partners/{partner_id}/extensions",
            json={
                "field_name": "credit_limit",
                "field_type": "decimal",
                "field_value": "5000.00"
            },
            headers=auth_headers
        )
        assert extension_response.status_code == 201
        
        # 5. Get audit trail
        audit_response = await client.get(
            f"/partners/{partner_id}/audit",
            headers=auth_headers
        )
        assert audit_response.status_code == 200
        audit_entries = audit_response.json()["data"]
        assert len(audit_entries) >= 2  # Create and update
        
        # 6. Delete partner
        delete_response = await client.delete(
            f"/partners/{partner_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204
```

### Performance Testing

```python
import pytest
import asyncio
import time
from app.services.partner_service import PartnerService

class TestFrameworkPerformance:
    
    @pytest.mark.asyncio
    async def test_bulk_operations_performance(self, db_session):
        """Test bulk operations meet performance requirements"""
        service = PartnerService(db_session)
        
        # Prepare test data
        partner_data = [
            PartnerCreate(
                name=f"Bulk Partner {i}",
                email=f"bulk{i}@test.com",
                partner_type="customer"
            )
            for i in range(100)
        ]
        
        # Test bulk creation performance
        start_time = time.time()
        partners = await service.bulk_create_partners(partner_data)
        end_time = time.time()
        
        # Assertions
        assert len(partners) == 100
        assert end_time - start_time < 5.0  # Should complete in under 5 seconds
        
        # Test bulk query performance
        start_time = time.time()
        all_partners = await service.get_list(company_id=1)
        end_time = time.time()
        
        assert len(all_partners) >= 100
        assert end_time - start_time < 2.0  # Should query in under 2 seconds
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, db_session):
        """Test framework handles concurrent operations"""
        service = PartnerService(db_session)
        
        async def create_partner(index):
            partner_data = PartnerCreate(
                name=f"Concurrent Partner {index}",
                email=f"concurrent{index}@test.com",
                partner_type="customer"
            )
            return await service.create_partner(partner_data)
        
        # Run 20 concurrent partner creations
        tasks = [create_partner(i) for i in range(20)]
        partners = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        assert len(partners) == 20
        assert all(partner.id for partner in partners)
        
        # Verify unique IDs
        partner_ids = [partner.id for partner in partners]
        assert len(set(partner_ids)) == 20  # All unique
```

## ⚡ Performance Optimization

### Database Query Optimization

```python
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select, and_, or_

class OptimizedPartnerService(CompanyBusinessObjectService):
    
    async def get_partners_with_contacts_and_orders(self, company_id: int) -> List[Partner]:
        """Optimized query using eager loading"""
        query = (
            select(Partner)
            .where(Partner.company_id == company_id)
            .options(
                selectinload(Partner.contacts),  # Load contacts in separate query
                selectinload(Partner.orders).selectinload(Order.order_items)  # Load orders and items
            )
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def search_partners_optimized(self, search_term: str, company_id: int) -> List[Partner]:
        """Optimized search using database indexes"""
        # Ensure you have indexes on name, email, and company_id
        query = (
            select(Partner)
            .where(
                and_(
                    Partner.company_id == company_id,
                    or_(
                        Partner.name.ilike(f"%{search_term}%"),
                        Partner.email.ilike(f"%{search_term}%")
                    )
                )
            )
            .order_by(Partner.name)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
```

### Caching Strategies

```python
from functools import lru_cache
from app.core.cache import cache_manager
import json

class CachedPartnerService(CompanyBusinessObjectService):
    
    @cache_manager.cached(timeout=300)  # Cache for 5 minutes
    async def get_partner_statistics(self, company_id: int) -> Dict[str, Any]:
        """Get partner statistics with caching"""
        query = """
        SELECT 
            COUNT(*) as total_partners,
            COUNT(CASE WHEN partner_type = 'customer' THEN 1 END) as customers,
            COUNT(CASE WHEN partner_type = 'supplier' THEN 1 END) as suppliers,
            COUNT(CASE WHEN is_active = true THEN 1 END) as active_partners
        FROM partners 
        WHERE company_id = :company_id
        """
        
        result = await self.db.execute(text(query), {"company_id": company_id})
        row = result.fetchone()
        
        return {
            "total_partners": row.total_partners,
            "customers": row.customers,
            "suppliers": row.suppliers,
            "active_partners": row.active_partners,
            "cached_at": datetime.utcnow().isoformat()
        }
    
    async def invalidate_partner_cache(self, company_id: int):
        """Invalidate cached partner data when partners change"""
        cache_key = f"partner_statistics:{company_id}"
        await cache_manager.delete(cache_key)
    
    async def create_partner(self, partner_data: PartnerCreate) -> Partner:
        """Create partner and invalidate related cache"""
        partner = await super().create_partner(partner_data)
        
        # Invalidate cache since statistics changed
        await self.invalidate_partner_cache(partner.company_id)
        
        return partner
```

### Batch Processing

```python
from sqlalchemy import update, delete
from typing import List, Dict, Any

class BatchPartnerService(CompanyBusinessObjectService):
    
    async def bulk_update_fields(self, updates: List[Dict[str, Any]], company_id: int) -> int:
        """Efficient bulk field updates"""
        # Group updates by field combinations
        update_groups = {}
        for update_data in updates:
            partner_id = update_data.pop("id")
            field_hash = hash(frozenset(update_data.keys()))
            
            if field_hash not in update_groups:
                update_groups[field_hash] = {"fields": update_data, "ids": []}
            
            update_groups[field_hash]["ids"].append(partner_id)
        
        total_updated = 0
        
        # Execute batch updates for each field combination
        for group in update_groups.values():
            query = (
                update(Partner)
                .where(
                    and_(
                        Partner.id.in_(group["ids"]),
                        Partner.company_id == company_id
                    )
                )
                .values(**group["fields"])
            )
            
            result = await self.db.execute(query)
            total_updated += result.rowcount
        
        await self.db.commit()
        return total_updated
    
    async def cleanup_inactive_partners(self, inactive_days: int = 365, company_id: int = None) -> int:
        """Batch cleanup of inactive partners"""
        cutoff_date = datetime.utcnow() - timedelta(days=inactive_days)
        
        conditions = [
            Partner.is_active == False,
            Partner.updated_at < cutoff_date
        ]
        
        if company_id:
            conditions.append(Partner.company_id == company_id)
        
        # Soft delete in batches to avoid long-running transactions
        batch_size = 1000
        total_deleted = 0
        
        while True:
            # Get batch of IDs to delete
            id_query = (
                select(Partner.id)
                .where(and_(*conditions))
                .limit(batch_size)
            )
            
            result = await self.db.execute(id_query)
            partner_ids = [row[0] for row in result.fetchall()]
            
            if not partner_ids:
                break
            
            # Soft delete batch
            delete_query = (
                update(Partner)
                .where(Partner.id.in_(partner_ids))
                .values(
                    deleted_at=datetime.utcnow(),
                    is_active=False
                )
            )
            
            result = await self.db.execute(delete_query)
            total_deleted += result.rowcount
            
            await self.db.commit()
        
        return total_deleted
```

## 📝 Summary

This developer guide provides comprehensive coverage of the XERPIUM Business Object Framework, including:

- **Architecture Overview**: Understanding the framework layers and principles
- **Core Components**: Base models, mixins, and essential building blocks
- **Schema Development**: Pydantic validation and serialization patterns
- **Service Layer**: Business logic implementation with framework capabilities
- **API Controllers**: RESTful API development with standardized patterns
- **Extension System**: Custom fields and dynamic business object enhancement
- **Audit Logging**: Automatic change tracking and audit trail management
- **Event Publishing**: Real-time event broadcasting for business processes
- **Best Practices**: Proven patterns for maintainable and scalable code
- **Testing Strategies**: Comprehensive testing approaches for framework code
- **Performance Optimization**: Database, caching, and batch processing optimization

The framework enables rapid development of business objects while maintaining consistency, auditability, and extensibility across your entire application.

For additional resources:
- **Quick Start Guide**: Step-by-step setup instructions
- **Migration Guide**: Converting existing services to the framework
- **API Documentation**: Auto-generated API documentation
- **Troubleshooting Guide**: Common issues and solutions

---

*Framework Version: 1.0.0*  
*Last Updated: 2025-08-01*  
*Documentation Status: Complete*