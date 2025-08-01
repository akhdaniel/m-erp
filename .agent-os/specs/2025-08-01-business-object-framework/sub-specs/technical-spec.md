# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-08-01-business-object-framework/spec.md

> Created: 2025-08-01
> Version: 1.0.0

## Technical Requirements

### Core Framework Components

- **Base Model Classes** - Enhanced SQLAlchemy base classes extending existing `BaseModel` and `CompanyBaseModel` with audit and event integration
- **Schema Framework** - Pydantic base schemas with automatic validation rules and type safety
- **Service Layer Templates** - Abstract service classes with standardized CRUD operations and error handling
- **Event Integration** - Automatic event publishing using existing Redis Streams messaging system
- **Audit Integration** - Seamless integration with existing audit service for all business object changes
- **Extension Points** - Decorator-based system for custom fields, validators, and lifecycle hooks
- **Migration Templates** - Alembic migration patterns for consistent database schema evolution

### Integration Requirements

- **Existing Messaging System** - Must integrate with current Redis Streams architecture and event types
- **Audit Service Compatibility** - Must use existing audit service API and schema structure
- **Authentication Context** - Must respect existing JWT token validation and user context
- **Multi-Company Isolation** - Must enforce existing company_id filtering patterns
- **Database Connection** - Must work with existing SQLAlchemy async session management

### Performance Criteria

- **Database Query Efficiency** - Framework should not add more than 5% overhead to basic CRUD operations
- **Event Publishing Latency** - Event publishing should not block CRUD operations (async/fire-and-forget)
- **Memory Usage** - Framework classes should have minimal memory footprint impact
- **Type Safety** - Full static type checking with mypy/pylint compatibility

## Approach Options

**Option A: Extend Existing Base Classes**
- Pros: Minimal disruption to existing code, leverages current patterns, easy migration path
- Cons: May be constrained by existing design decisions, harder to add major new features

**Option B: Create New Framework with Migration Path** (Selected)
- Pros: Clean slate design, can optimize for all requirements, better long-term architecture
- Cons: Requires migration of existing services, more initial development work

**Option C: Mixin-Based Architecture**
- Pros: Highly flexible, allows selective feature adoption, minimal inheritance chains
- Cons: Complex composition patterns, potential for inconsistent implementations

### Rationale for Option B

The new framework approach allows us to design optimal integration with audit and event systems from the ground up, while providing a clear migration path for existing services. This ensures we can meet all technical requirements without being constrained by current implementation limitations.

## Architecture Design

### Base Class Hierarchy

```python
# New framework base classes
class BusinessObjectMixin:
    """Core business object functionality"""
    
class AuditableMixin:
    """Automatic audit logging"""
    
class EventPublisherMixin:
    """Automatic event publishing"""
    
class ExtensibleMixin:
    """Custom field and validation support"""
    
class BusinessObjectBase(Base, BusinessObjectMixin, AuditableMixin, EventPublisherMixin):
    """Base for non-company objects"""
    
class CompanyBusinessObject(BusinessObjectBase, ExtensibleMixin):
    """Base for company-scoped objects"""
```

### Schema Framework

```python
# Base schema classes with automatic patterns
class BusinessObjectSchema(BaseModel):
    """Base schema with common validation"""
    
class CreateSchemaBase(BusinessObjectSchema):
    """Template for create operations"""
    
class UpdateSchemaBase(BusinessObjectSchema):
    """Template for update operations"""
    
class ResponseSchemaBase(BusinessObjectSchema):
    """Template for API responses"""
```

### Service Layer Pattern

```python
# Standardized service class template
class BusinessObjectService(Generic[T]):
    """Generic service with CRUD operations"""
    
    async def create(self, db: AsyncSession, data: CreateSchema) -> T:
        """Create with audit and events"""
    
    async def update(self, db: AsyncSession, obj_id: int, data: UpdateSchema) -> T:
        """Update with audit and events""" 
    
    async def delete(self, db: AsyncSession, obj_id: int) -> bool:
        """Delete with audit and events"""
```

## External Dependencies

### New Libraries

- **pydantic[email]** (v2.0+) - Enhanced validation including email validation for business objects
  - **Justification:** Current Pydantic version may not include all validation features needed for comprehensive business object validation

- **SQLAlchemy-Utils** (v0.41+) - Additional field types and utilities for business objects
  - **Justification:** Provides useful field types like UUIDType, EmailType, and other business-specific field types

### Enhanced Existing Dependencies

- **redis[hiredis]** - High-performance Redis client for improved event publishing
  - **Justification:** Current Redis dependency may not include hiredis for optimal performance

- **alembic** - Database migration management (already included but may need version upgrade)
  - **Justification:** Ensure compatibility with latest SQLAlchemy async features

## Implementation Details

### Event Publishing Integration

The framework will integrate with the existing messaging system by:

1. **Automatic Event Detection** - Base classes will automatically detect CRUD operations and publish appropriate events
2. **Event Type Mapping** - Business object types will map to corresponding EventType enum values
3. **Audit Data Integration** - Before/after data snapshots will be automatically captured and included in events
4. **User Context Propagation** - Current user and company context will be automatically included in all events

### Audit Service Integration

The framework will integrate with the existing audit service by:

1. **Automatic Audit Logging** - All CRUD operations will automatically create audit log entries
2. **Change Detection** - Framework will compare before/after states to identify specific field changes
3. **User Context Tracking** - Current user information will be automatically captured from request context
4. **Async Audit Calls** - Audit logging will be performed asynchronously to avoid blocking business operations

### Multi-Company Data Isolation

The framework will enforce multi-company isolation through:

1. **Automatic Company ID Injection** - All queries will automatically filter by company_id from user context
2. **Create/Update Validation** - Company ID will be automatically set and validated on create/update operations
3. **Cross-Company Access Prevention** - Framework will prevent access to objects from different companies
4. **Query Builder Integration** - All standard queries will include automatic company filtering