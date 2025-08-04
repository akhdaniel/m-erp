# Business Object Framework Migration Guide

## Overview

This guide provides comprehensive instructions for migrating existing services to use the Business Object Framework. The framework provides standardized CRUD operations, custom field support, audit logging, and event publishing while maintaining full API compatibility.

## Migration Benefits

### 🚀 Framework Capabilities
- **Standardized CRUD**: Generic create, read, update, delete operations
- **Custom Fields**: Dynamic field addition without schema changes
- **Audit Logging**: Automatic change tracking with complete history
- **Event Publishing**: Automatic Redis event publishing for all operations
- **Multi-Company**: Built-in data isolation enforcement
- **Bulk Operations**: Efficient batch processing capabilities
- **Type Safety**: Full Pydantic validation with comprehensive error handling

### 🔧 Developer Benefits
- **Rapid Development**: 5-minute API setup with factory functions
- **Consistent Patterns**: Standardized service and router implementations
- **Auto-documentation**: Complete OpenAPI specs with examples
- **Test Coverage**: Built-in test patterns and utilities
- **Error Handling**: Consistent error responses across all endpoints

## Migration Process

### Phase 1: Analysis and Planning

1. **Analyze Existing Service**
   - Review current model structure
   - Document existing API endpoints
   - Identify business-specific logic
   - Plan migration approach

2. **Backup Existing Code**
   ```bash
   # Create backup directory
   mkdir -p migrations/backups/$(date +%Y%m%d_%H%M%S)
   
   # Backup critical files
   cp app/models/*.py migrations/backups/$(date +%Y%m%d_%H%M%S)/
   cp app/schemas/*.py migrations/backups/$(date +%Y%m%d_%H%M%S)/
   cp app/services/*.py migrations/backups/$(date +%Y%m%d_%H%M%S)/
   cp app/routers/*.py migrations/backups/$(date +%Y%m%d_%H%M%S)/
   ```

### Phase 2: Framework Integration

1. **Create Framework Schemas**
   ```python
   # app/framework_migration/{service}_schemas.py
   from app.framework.schemas import CompanyBusinessObjectSchema, CreateSchemaBase, UpdateSchemaBase
   
   class {Model}FrameworkBase(CompanyBusinessObjectSchema):
       # Define your model fields here
       name: str = Field(..., min_length=1, max_length=255)
       # ... other fields
   
   class {Model}FrameworkCreate(CreateSchemaBase, {Model}FrameworkBase):
       company_id: int = Field(..., gt=0)
   
   class {Model}FrameworkUpdate(UpdateSchemaBase):
       # All fields optional for updates
       name: Optional[str] = Field(None, min_length=1, max_length=255)
       # ... other fields
   
   class {Model}FrameworkResponse({Model}FrameworkBase):
       id: int
       class Config:
           from_attributes = True
   ```

2. **Create Framework Service**
   ```python
   # app/framework_migration/{service}_service.py
   from app.framework.services import CompanyBusinessObjectService
   
   class {Model}FrameworkService(CompanyBusinessObjectService[{Model}]):
       def __init__(self, db: AsyncSession):
           super().__init__(db, {Model})
       
       # Add business-specific methods
       async def find_by_code(self, code: str, company_id: int):
           return await self.get_by_filters({"code": code, "company_id": company_id})
   ```

3. **Create Framework Router**
   ```python
   # app/framework_migration/{service}_router.py
   from app.framework.controllers import create_business_object_router
   
   # Auto-generated framework router
   framework_router = create_business_object_router(
       model_class={Model},
       service_class={Model}FrameworkService,
       create_schema={Model}FrameworkCreate,
       update_schema={Model}FrameworkUpdate,
       response_schema={Model}FrameworkResponse,
       prefix="/api/v1/{model_plural}",
       tags=["{model_plural}"],
       enable_extensions=True,
       enable_audit_trail=True
   )
   ```

### Phase 3: Testing and Validation

1. **Run Migration Script**
   ```bash
   # Test migration without changes
   python migrations/{service}_framework_migration.py --dry-run
   
   # Run actual migration with backup
   python migrations/{service}_framework_migration.py --backup
   ```

2. **Execute Integration Tests**
   ```bash
   pytest tests/test_{service}_migration_integration.py -v
   ```

3. **Validate API Compatibility**
   ```bash
   # Start development server
   uvicorn app.main:app --reload --port 8001
   
   # Test existing endpoints
   curl -X GET http://localhost:8001/api/v1/{model_plural}/
   curl -X POST http://localhost:8001/api/v1/{model_plural}/ -d '{"name": "Test"}'
   ```

### Phase 4: Deployment

1. **Deploy Side-by-Side**
   - Deploy framework endpoints alongside existing ones
   - Use different prefixes (e.g., `/api/v1/{service}-framework/`)
   - Monitor performance and functionality

2. **Gradual Migration**
   - Migrate one endpoint at a time
   - Use feature flags to control routing
   - Monitor for any issues

3. **Full Migration**
   - Replace existing files with framework versions
   - Update application routing
   - Remove old implementation

## Common Migration Patterns

### Model Compatibility

**Existing Model Structure:**
```python
class Partner(CompanyBaseModel):
    name = Column(String(255), nullable=False)
    code = Column(String(50))
    # ... other fields
```

**Framework Requirements:**
- Model must inherit from `CompanyBaseModel` ✅
- Must have `id`, `company_id`, `created_at`, `updated_at` fields ✅
- Business logic methods preserved ✅

### Schema Migration

**Before (Traditional):**
```python
class PartnerCreate(BaseModel):
    name: str
    company_id: int
    
class PartnerUpdate(BaseModel):
    name: Optional[str] = None
    
class PartnerResponse(BaseModel):
    id: int
    name: str
    company_id: int
```

**After (Framework):**
```python
class PartnerFrameworkCreate(CreateSchemaBase, PartnerFrameworkBase):
    company_id: int = Field(..., gt=0)  # Inherits validation
    
class PartnerFrameworkUpdate(UpdateSchemaBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    
class PartnerFrameworkResponse(PartnerFrameworkBase):
    id: int  # Framework adds timestamps automatically
    class Config:
        from_attributes = True
```

### Service Migration

**Before (Traditional):**
```python
class PartnerService:
    @staticmethod
    async def create_partner(db: AsyncSession, partner_data: PartnerCreate):
        # Manual database operations
        partner = Partner(**partner_data.dict())
        db.add(partner)
        await db.commit()
        return partner
```

**After (Framework):**
```python
class PartnerFrameworkService(CompanyBusinessObjectService[Partner]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Partner)
    
    async def create_partner(self, partner_data: PartnerFrameworkCreate):
        # Framework handles audit logging, event publishing, validation
        return await self.create(partner_data.dict())
```

### Router Migration

**Before (Traditional):**
```python
@router.post("/", response_model=PartnerResponse)
async def create_partner(partner_data: PartnerCreate, db: AsyncSession = Depends(get_db)):
    # Manual error handling, validation, response formatting
    try:
        partner = await PartnerService.create_partner(db, partner_data)
        return partner
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**After (Framework):**
```python
# Option 1: Auto-generated router (recommended)
framework_router = create_business_object_router(
    model_class=Partner,
    service_class=PartnerFrameworkService,
    create_schema=PartnerFrameworkCreate,
    update_schema=PartnerFrameworkUpdate,
    response_schema=PartnerFrameworkResponse
)

# Option 2: Custom router using framework service
@router.post("/", response_model=PartnerFrameworkResponse)
async def create_partner(
    partner_data: PartnerFrameworkCreate,
    partner_service: PartnerFrameworkService = Depends(get_partner_service)
):
    # Framework handles error handling, validation, response formatting
    return await partner_service.create_partner(partner_data)
```

## Advanced Framework Features

### Custom Fields

Add custom fields to any business object without schema changes:

```python
# Add custom field
await partner_service.set_extension(
    object_id=1,
    field_name="credit_limit",
    field_type="decimal",
    field_value="10000.00",
    company_id=1
)

# Query with custom field filters
partners = await partner_service.get_list(
    filters={"company_id": 1},
    extension_filters={"credit_limit__gte": "5000.00"}
)

# Get custom fields
extensions = await partner_service.get_extensions(object_id=1, company_id=1)
```

### Audit Trail

Automatic audit logging for all operations:

```python
# Get complete audit trail
audit_entries = await partner_service.get_audit_trail(object_id=1, company_id=1)

# Get recent changes
recent_changes = await partner_service.get_recent_changes(
    object_id=1,
    company_id=1,
    hours=24
)

# Audit entry structure
{
    "id": "audit_1_123",
    "action": "partner_updated",
    "entity_type": "partner",
    "entity_id": 1,
    "user_id": 123,
    "company_id": 1,
    "timestamp": "2025-08-01T10:00:00Z",
    "changes": {
        "name": {"old": "Old Name", "new": "New Name"},
        "email": {"old": null, "new": "new@email.com"}
    }
}
```

### Event Publishing

Automatic event publishing to Redis for all operations:

```python
# Events published automatically
# - partner_created
# - partner_updated  
# - partner_deleted
# - partner_activated
# - partner_deactivated

# Custom event publishing
await partner_service.publish_event(
    event_type="partner_status_changed",
    entity_id=1,
    data={"status": "vip_customer"},
    company_id=1
)
```

### Bulk Operations

Efficient bulk processing:

```python
# Bulk create
partners_data = [PartnerFrameworkCreate(...), PartnerFrameworkCreate(...)]
partners = await partner_service.bulk_create(
    [p.dict() for p in partners_data]
)

# Bulk update
updates = [
    {"id": 1, "name": "Updated Name 1"},
    {"id": 2, "name": "Updated Name 2"}
]
updated_partners = await partner_service.bulk_update(updates)

# Bulk delete (soft delete)
partner_ids = [1, 2, 3]
result = await partner_service.bulk_soft_delete(partner_ids, company_id=1)
```

## API Enhancements

### Framework-Generated Endpoints

For each business object, the framework automatically generates:

**Standard CRUD:**
- `POST /` - Create object
- `GET /` - List objects with pagination/filtering
- `GET /{id}` - Get object by ID
- `PUT /{id}` - Update object
- `DELETE /{id}` - Soft delete object

**Extension Endpoints:**
- `GET /{id}/extensions` - Get all custom fields
- `POST /{id}/extensions` - Set custom field value
- `DELETE /{id}/extensions/{field_name}` - Remove custom field
- `GET /extensions/fields` - List available custom fields

**Audit Endpoints:**
- `GET /{id}/audit` - Get complete audit trail
- `GET /{id}/changes` - Get recent changes
- `GET /{id}/audit/{action}` - Get specific action history

**Bulk Endpoints:**
- `POST /bulk-create` - Bulk create objects
- `PUT /bulk-update` - Bulk update objects
- `DELETE /bulk-delete` - Bulk soft delete objects

### Enhanced Query Parameters

All list endpoints support advanced filtering:

```bash
# Pagination
GET /partners/?skip=0&limit=50

# Filtering
GET /partners/?company_id=1&is_active=true&partner_type=customer

# Search
GET /partners/?search=acme&search_fields=name,email,code

# Sorting
GET /partners/?sort_by=name&sort_order=asc

# Extension field filtering
GET /partners/?ext.credit_limit__gte=5000&ext.vip_customer=true

# Date range filtering
GET /partners/?created_after=2025-01-01&created_before=2025-12-31
```

## Performance Considerations

### Optimizations

1. **Database Queries**
   - Framework uses efficient SQLAlchemy queries
   - Automatic query optimization for filtering
   - Proper indexing on extension tables

2. **Bulk Operations**
   - Batch database operations reduce round trips
   - Bulk validation and error handling
   - Transaction management for consistency

3. **Caching**
   - Built-in Redis caching for frequently accessed data
   - Configurable cache TTL per operation
   - Automatic cache invalidation on updates

### Monitoring

Framework provides built-in monitoring:

```python
# Performance metrics
from app.framework.monitoring import get_service_metrics

metrics = await get_service_metrics("partner")
# Returns: query_count, avg_response_time, error_rate, cache_hit_ratio
```

## Troubleshooting

### Common Issues

**Import Errors:**
```python
# Problem: Cannot import framework modules
# Solution: Check Python path and module structure
from app.framework.services import CompanyBusinessObjectService  # ✅
```

**Schema Validation Errors:**
```python
# Problem: Pydantic validation fails
# Solution: Ensure field types match model definition
partner_data = PartnerFrameworkCreate(
    name="ACME Corp",  # String required
    company_id=1       # Integer required
)
```

**Database Session Issues:**
```python
# Problem: Framework service can't access database
# Solution: Verify AsyncSession dependency injection
async def get_partner_service(db: AsyncSession = Depends(get_db)):
    return PartnerFrameworkService(db)
```

**Multi-Company Isolation:**
```python
# Problem: Data leakage between companies
# Solution: Always filter by company_id
partners = await partner_service.get_list({"company_id": user.company_id})
```

### Debug Mode

Enable framework debug mode for detailed logging:

```python
# In environment variables or config
FRAMEWORK_DEBUG=true
FRAMEWORK_LOG_LEVEL=DEBUG

# Framework will log:
# - All database queries
# - Audit log entries
# - Event publishing
# - Performance metrics
```

## Migration Checklist

### Pre-Migration
- [ ] Analyze existing service structure
- [ ] Backup all existing files
- [ ] Review framework documentation
- [ ] Plan migration approach
- [ ] Set up test environment

### Migration Execution
- [ ] Create framework schemas
- [ ] Implement framework service
- [ ] Create framework router
- [ ] Write integration tests
- [ ] Run migration script
- [ ] Validate API compatibility

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] API endpoints functional
- [ ] Performance meets requirements
- [ ] Data integrity verified

### Deployment
- [ ] Deploy to staging environment
- [ ] Run end-to-end tests
- [ ] Performance testing
- [ ] User acceptance testing
- [ ] Production deployment
- [ ] Monitor post-deployment

### Post-Migration
- [ ] Verify all functionality working
- [ ] Monitor performance metrics
- [ ] Train team on new capabilities
- [ ] Update documentation
- [ ] Plan next service migration

## Support Resources

### Documentation
- [Framework API Reference](/docs/framework-api.md)
- [Extension System Guide](/docs/extensions.md)
- [Audit System Guide](/docs/audit.md)
- [Performance Guide](/docs/performance.md)

### Examples
- [Partner Migration Example](/services/company-partner-service/framework_migration/)
- [Custom Field Examples](/docs/custom-fields-examples.md)
- [Testing Examples](/docs/testing-examples.md)

### Getting Help
1. Check framework documentation
2. Review example implementations  
3. Run diagnostic tests
4. Check application logs
5. Contact development team

---

*Successfully migrate your services to the Business Object Framework and unlock powerful new capabilities while maintaining full compatibility!*