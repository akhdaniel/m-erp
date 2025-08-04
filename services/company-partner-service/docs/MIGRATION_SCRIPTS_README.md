# Migration Scripts Documentation

## Overview

This directory contains scripts and documentation for migrating existing services to use the Business Object Framework. The migration process is designed to be safe, reversible, and maintain full API compatibility.

## Migration Scripts

### `partner_framework_migration.py`

Comprehensive migration script for transforming the Partner service to use the Business Object Framework.

**Usage:**
```bash
# Test migration without making changes
python migrations/partner_framework_migration.py --dry-run

# Run migration with backup
python migrations/partner_framework_migration.py --backup

# Run migration in specific directory
python migrations/partner_framework_migration.py --service-root /path/to/service
```

**What it creates:**
- `app/framework_migration/partner_schemas.py` - Framework-based Pydantic schemas
- `app/framework_migration/partner_service.py` - Framework-based service class
- `app/framework_migration/partner_router.py` - Framework-based API router
- `app/framework_migration/main_app_update.py` - Application integration code
- `docs/PARTNER_MIGRATION_GUIDE.md` - Detailed migration documentation
- `docs/MIGRATION_TEMPLATE.md` - Template for other service migrations

**Features:**
- ✅ Maintains full API compatibility
- ✅ Adds custom field support
- ✅ Includes audit logging
- ✅ Provides event publishing
- ✅ Creates comprehensive documentation
- ✅ Includes rollback support

## Generated Files Structure

```
app/framework_migration/
├── partner_schemas.py          # Framework-based Pydantic schemas
├── partner_service.py          # Framework-based service implementation
├── partner_router.py           # Framework-based FastAPI router
└── main_app_update.py          # Application integration helpers

docs/
├── PARTNER_MIGRATION_GUIDE.md  # Detailed migration documentation
└── MIGRATION_TEMPLATE.md       # Template for other services

migrations/backups/
└── YYYYMMDD_HHMMSS/           # Timestamped backups (if --backup used)
    ├── app/schemas/partner.py
    ├── app/services/partner_service.py
    └── app/routers/partners.py
```

## Migration Process

### Phase 1: Preparation
1. Run migration script with `--dry-run` to see what will be created
2. Review existing service structure and dependencies
3. Create backup with `--backup` flag

### Phase 2: Framework File Generation
1. Execute migration script to create framework files
2. Review generated schemas, service, and router
3. Run integration tests to verify compatibility

### Phase 3: Side-by-Side Deployment
1. Deploy framework files alongside existing implementation
2. Use different API prefixes to test both versions
3. Validate functionality and performance

### Phase 4: Full Migration
1. Replace existing files with framework versions
2. Update application routing
3. Remove old implementation files

## Framework Enhancements

### Enhanced Schemas
```python
# Before: Basic Pydantic models
class PartnerCreate(BaseModel):
    name: str
    company_id: int

# After: Framework-enhanced with validation, examples, documentation
class PartnerFrameworkCreate(CreateSchemaBase, PartnerFrameworkBase):
    company_id: int = Field(..., gt=0, description="Company ID")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "ACME Corp",
                "code": "ACME001",
                "company_id": 1
            }
        }
```

### Enhanced Service
```python
# Before: Manual database operations
class PartnerService:
    @staticmethod
    async def create_partner(db, partner_data):
        partner = Partner(**partner_data.dict())
        db.add(partner)
        await db.commit()
        return partner

# After: Framework service with automatic audit/events
class PartnerFrameworkService(CompanyBusinessObjectService[Partner]):
    async def create_partner(self, partner_data):
        # Automatic: audit logging, event publishing, validation
        return await self.create(partner_data.dict())
```

### Enhanced Router
```python
# Before: Manual endpoint implementation
@router.post("/")
async def create_partner(partner_data: PartnerCreate, db: AsyncSession = Depends(get_db)):
    try:
        partner = await PartnerService.create_partner(db, partner_data)
        return partner
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# After: Auto-generated with 10+ endpoints
framework_router = create_business_object_router(
    model_class=Partner,
    service_class=PartnerFrameworkService,
    create_schema=PartnerFrameworkCreate,
    update_schema=PartnerFrameworkUpdate,
    response_schema=PartnerFrameworkResponse,
    enable_extensions=True,      # Custom fields endpoints
    enable_audit_trail=True,     # Audit endpoints
    enable_bulk_operations=True  # Bulk endpoints
)
```

## New Capabilities

### Custom Fields
Add fields without database schema changes:
```python
# Add custom field
await partner_service.set_extension(
    object_id=1,
    field_name="credit_limit",
    field_type="decimal",
    field_value="10000.00"
)

# Query with custom fields
partners = await partner_service.get_list(
    extension_filters={"credit_limit__gte": "5000.00"}
)
```

### Audit Trail
Automatic change tracking:
```python
# Get audit trail
audit_entries = await partner_service.get_audit_trail(object_id=1)

# Audit entry structure
{
    "action": "partner_updated",
    "user_id": 123,
    "timestamp": "2025-08-01T10:00:00Z",
    "changes": {
        "name": {"old": "Old Name", "new": "New Name"}
    }
}
```

### Event Publishing
Automatic Redis event publishing:
```python
# Events published automatically:
# - partner_created
# - partner_updated
# - partner_deleted
# - partner_activated
# - partner_deactivated

# Custom events
await partner_service.publish_event(
    event_type="partner_vip_status_changed",
    entity_id=1,
    data={"vip_level": "gold"}
)
```

### Bulk Operations
Efficient batch processing:
```python
# Bulk create
partners = await partner_service.bulk_create([...])

# Bulk update
updated = await partner_service.bulk_update([...])

# Bulk delete
result = await partner_service.bulk_soft_delete([1, 2, 3])
```

## API Enhancements

### Standard Endpoints (Compatible)
- `POST /partners/` - Create partner
- `GET /partners/` - List partners with pagination
- `GET /partners/{id}` - Get partner by ID
- `PUT /partners/{id}` - Update partner
- `DELETE /partners/{id}` - Soft delete partner

### New Framework Endpoints
- `GET /partners/{id}/extensions` - Get custom fields
- `POST /partners/{id}/extensions` - Set custom field
- `DELETE /partners/{id}/extensions/{field}` - Remove custom field
- `GET /partners/{id}/audit` - Get audit trail
- `POST /partners/bulk-create` - Bulk create partners
- `GET /partners/company/{id}/statistics` - Partner statistics

### Enhanced Query Parameters
```bash
# Advanced filtering
GET /partners/?company_id=1&is_active=true&partner_type=customer

# Full-text search
GET /partners/?search=acme&search_fields=name,email,code

# Custom field filtering
GET /partners/?ext.credit_limit__gte=5000&ext.vip_customer=true

# Date range filtering
GET /partners/?created_after=2025-01-01&updated_before=2025-12-31

# Sorting
GET /partners/?sort_by=name&sort_order=desc
```

## Testing

### Integration Tests
Run comprehensive integration tests:
```bash
pytest tests/test_partner_migration_integration.py -v
```

### API Testing
Test both old and new endpoints:
```bash
# Test existing API
curl -X GET http://localhost:8000/api/v1/partners/

# Test framework API  
curl -X GET http://localhost:8000/api/v1/partners-framework/

# Test new capabilities
curl -X GET http://localhost:8000/api/v1/partners/1/extensions
curl -X GET http://localhost:8000/api/v1/partners/1/audit
```

### Performance Testing
```bash
# Load test with existing implementation
ab -n 1000 -c 10 http://localhost:8000/api/v1/partners/

# Load test with framework implementation
ab -n 1000 -c 10 http://localhost:8000/api/v1/partners-framework/
```

## Rollback Procedure

### Safe Rollback Steps
1. **Stop Application**
   ```bash
   sudo systemctl stop your-app
   ```

2. **Restore Backup Files**
   ```bash
   # Find backup directory
   ls migrations/backups/
   
   # Restore from backup (replace TIMESTAMP)
   cp migrations/backups/TIMESTAMP/app/schemas/partner.py app/schemas/
   cp migrations/backups/TIMESTAMP/app/services/partner_service.py app/services/
   cp migrations/backups/TIMESTAMP/app/routers/partners.py app/routers/
   ```

3. **Update Application Routes**
   ```python
   # In main.py, revert to original router
   from app.routers.partners import router as partner_router
   app.include_router(partner_router, prefix="/api/v1")
   ```

4. **Restart Application**
   ```bash
   sudo systemctl start your-app
   ```

5. **Verify Functionality**
   ```bash
   curl -X GET http://localhost:8000/api/v1/partners/
   ```

### Rollback Triggers
- Performance degradation > 20%
- Critical functionality broken
- Data integrity issues
- User-reported errors

## Monitoring

### Health Checks
Framework provides health check endpoints:
```bash
# Service health
GET /partners/health

# Framework health
GET /framework/health

# Extension system health
GET /framework/extensions/health
```

### Metrics
Monitor key metrics:
- Response times
- Error rates
- Database query performance
- Event publishing success rate
- Custom field usage

### Logging
Framework provides comprehensive logging:
```python
# Enable debug logging
FRAMEWORK_DEBUG=true
FRAMEWORK_LOG_LEVEL=DEBUG

# Logs include:
# - Database queries
# - Audit entries
# - Event publishing
# - Performance metrics
```

## Support

### Documentation
- [Business Object Migration Guide](BUSINESS_OBJECT_MIGRATION_GUIDE.md)
- [Framework API Reference](/docs/framework-api.md)
- [Extension System Guide](/docs/extensions.md)

### Getting Help
1. Review migration documentation
2. Check integration test results
3. Examine application logs
4. Run diagnostic commands
5. Contact development team

### Common Issues

**Import Errors:**
```bash
# Problem: Cannot find framework modules
# Solution: Check PYTHONPATH and module structure
export PYTHONPATH=$PYTHONPATH:/path/to/service
```

**Database Errors:**
```bash
# Problem: Extension tables not found
# Solution: Run extension migration
alembic upgrade head
```

**Performance Issues:**
```bash
# Problem: Slow queries
# Solution: Check database indexes
python -c "from app.core.database import check_indexes; check_indexes()"
```

## Next Steps

1. **Review Generated Files**: Examine all framework migration files
2. **Run Integration Tests**: Verify compatibility and functionality
3. **Performance Testing**: Ensure performance meets requirements
4. **Staging Deployment**: Deploy to staging environment for testing
5. **Production Migration**: Deploy when ready and monitor carefully

---

*Migration scripts provide a safe, comprehensive path to Business Object Framework adoption with full rollback capability.*