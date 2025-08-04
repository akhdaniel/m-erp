# Business Object Framework Troubleshooting Guide

## 🔧 Common Issues and Solutions

This guide addresses the most common issues encountered when using the M-ERP Business Object Framework, with step-by-step solutions and preventive measures.

## 📚 Table of Contents

1. [Import and Setup Issues](#import-and-setup-issues)
2. [Database and Migration Issues](#database-and-migration-issues)
3. [Schema and Validation Issues](#schema-and-validation-issues)
4. [Service Layer Issues](#service-layer-issues)
5. [Extension System Issues](#extension-system-issues)
6. [Audit Logging Issues](#audit-logging-issues)
7. [Event Publishing Issues](#event-publishing-issues)
8. [Performance Issues](#performance-issues)
9. [Testing Issues](#testing-issues)
10. [Production Deployment Issues](#production-deployment-issues)

## 🔍 Import and Setup Issues

### Issue 1: Framework Module Import Errors

**Problem**: Cannot import framework modules
```python
ModuleNotFoundError: No module named 'app.framework'
```

**Diagnosis**:
```python
# Check framework directory exists
import os
print(os.path.exists('app/framework'))

# Check Python path
import sys
print(sys.path)

# Test specific imports
try:
    from app.framework.base import CompanyBaseModel
    print("✅ Framework base imports work")
except ImportError as e:
    print(f"❌ Framework import failed: {e}")
```

**Solutions**:
1. **Verify framework installation**:
   ```bash
   # Check framework directory structure
   ls -la app/framework/
   
   # Should see: base.py, mixins.py, schemas.py, services.py, etc.
   ```

2. **Fix Python path issues**:
   ```python
   # Add to your Python path if needed
   import sys
   import os
   sys.path.append(os.path.dirname(os.path.abspath(__file__)))
   ```

3. **Create missing `__init__.py` files**:
   ```bash
   touch app/__init__.py
   touch app/framework/__init__.py
   ```

4. **Verify dependencies**:
   ```bash
   pip install sqlalchemy[asyncio] pydantic fastapi redis
   ```

### Issue 2: Circular Import Dependencies

**Problem**: Circular imports between framework components
```python
ImportError: cannot import name 'BusinessObjectService' from partially initialized module
```

**Diagnosis**:
```python
# Check import order in your modules
# Look for circular dependencies like:
# models.py imports services.py
# services.py imports models.py
```

**Solutions**:
1. **Use TYPE_CHECKING imports**:
   ```python
   from typing import TYPE_CHECKING
   
   if TYPE_CHECKING:
       from app.models.partner import Partner
   
   # Use string annotations
   def create_partner(self, data: Dict[str, Any]) -> 'Partner':
       pass
   ```

2. **Import at function level**:
   ```python
   def get_audit_service(self):
       from app.services.audit_service import AuditService
       return AuditService(self.db)
   ```

3. **Reorganize imports**:
   ```python
   # ✅ Good: Import only what you need
   from app.framework.base import CompanyBaseModel
   
   # ❌ Bad: Import everything
   from app.framework import *
   ```

## 🗄️ Database and Migration Issues

### Issue 3: Database Connection Failures

**Problem**: Framework services can't connect to database
```python
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server failed
```

**Diagnosis**:
```python
# Test database connection
async def test_db_connection():
    from app.core.database import get_db_session
    from sqlalchemy import text
    
    try:
        async with get_db_session() as db:
            result = await db.execute(text("SELECT 1"))
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

# Run diagnosis
import asyncio
asyncio.run(test_db_connection())
```

**Solutions**:
1. **Check database configuration**:
   ```python
   # app/core/config.py
   DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"
   
   # Verify connection string format
   print(f"Database URL: {DATABASE_URL}")
   ```

2. **Verify database server**:
   ```bash
   # Check PostgreSQL is running
   docker ps | grep postgres
   
   # Test direct connection
   psql -h localhost -p 5432 -U username -d dbname
   ```

3. **Check async driver**:
   ```bash
   pip install asyncpg  # For async PostgreSQL
   ```

### Issue 4: Migration Failures

**Problem**: Framework extension tables not created
```python
sqlalchemy.exc.ProgrammingError: relation "business_object_extensions" does not exist
```

**Diagnosis**:
```python
# Check if extension tables exist
async def check_extension_tables():
    from app.core.database import get_db_session
    from sqlalchemy import text
    
    tables_to_check = [
        'business_object_extensions',
        'business_object_validators', 
        'business_object_field_definitions'
    ]
    
    async with get_db_session() as db:
        for table in tables_to_check:
            try:
                result = await db.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                print(f"✅ Table {table} exists")
            except Exception as e:
                print(f"❌ Table {table} missing: {e}")
```

**Solutions**:
1. **Run extension migrations**:
   ```bash
   # Apply framework migrations
   alembic upgrade head
   
   # Or run specific migration
   alembic upgrade 20250801_120000_create_extension_tables
   ```

2. **Create migration manually**:
   ```bash
   # Generate new migration
   alembic revision --autogenerate -m "Create framework extension tables"
   
   # Edit migration file to include extension tables
   # Then apply
   alembic upgrade head
   ```

3. **Check migration files**:
   ```python
   # Verify migration file exists
   import os
   migration_files = os.listdir('migrations/versions/')
   extension_migrations = [f for f in migration_files if 'extension' in f]
   print(f"Extension migrations: {extension_migrations}")
   ```

## 📋 Schema and Validation Issues

### Issue 5: Pydantic Validation Failures

**Problem**: Schema validation errors with framework schemas
```python
pydantic.error_wrappers.ValidationError: 1 validation error for PartnerCreate
company_id
  field required
```

**Diagnosis**:
```python
# Test schema validation
from app.schemas.partner import PartnerCreate

test_data = {
    "name": "Test Partner",
    "email": "test@partner.com"
    # Missing company_id
}

try:
    partner = PartnerCreate(**test_data)
    print("✅ Schema validation passed")
except ValidationError as e:
    print(f"❌ Schema validation failed: {e}")
    print("Missing fields:", [error['loc'] for error in e.errors])
```

**Solutions**:
1. **Check required fields**:
   ```python
   # Ensure all required fields are provided
   class PartnerCreate(CompanyBusinessObjectSchema):
       name: str = Field(..., description="Partner name is required")
       company_id: int = Field(..., description="Company ID is required")
       email: Optional[str] = None  # Optional fields
   ```

2. **Use dependency injection for company_id**:
   ```python
   # In your router
   @router.post("/partners/")
   async def create_partner(
       partner_data: PartnerCreateBase,  # Without company_id
       company_id: int = Depends(get_current_user_company)
   ):
       # Add company_id automatically
       full_data = PartnerCreate(
           **partner_data.dict(),
           company_id=company_id
       )
   ```

3. **Debug validation errors**:
   ```python
   from pydantic import ValidationError
   
   try:
       schema = PartnerCreate(**data)
   except ValidationError as e:
       for error in e.errors():
           print(f"Field: {error['loc']}")
           print(f"Error: {error['msg']}")
           print(f"Type: {error['type']}")
   ```

### Issue 6: Schema Inheritance Problems

**Problem**: Framework schema inheritance not working properly
```python
TypeError: Cannot use multiple inheritance with 'BaseModel' and 'CompanyBusinessObjectSchema'
```

**Solutions**:
1. **Correct inheritance order**:
   ```python
   # ✅ Correct: Framework schema first
   class PartnerBase(CompanyBusinessObjectSchema):
       name: str
       email: Optional[str] = None
   
   # ❌ Wrong: BaseModel conflicts
   class PartnerBase(BaseModel, CompanyBusinessObjectSchema):
       pass
   ```

2. **Use composition instead of inheritance**:
   ```python
   # Alternative approach
   class PartnerBase(BaseModel):
       name: str
       email: Optional[str] = None
       
       # Add framework fields manually
       company_id: int
       created_at: Optional[datetime] = None
   ```

## 🔧 Service Layer Issues

### Issue 7: Service Method Errors

**Problem**: Framework service methods not working
```python
AttributeError: 'PartnerService' object has no attribute 'create'
```

**Diagnosis**:
```python
# Check service inheritance
class PartnerService(CompanyBusinessObjectService):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Partner)  # Must call super().__init__
        
# Test service creation
service = PartnerService(db)
print(f"Service methods: {[m for m in dir(service) if not m.startswith('_')]}")
```

**Solutions**:
1. **Correct service inheritance**:
   ```python
   # ✅ Correct
   class PartnerService(CompanyBusinessObjectService[Partner, PartnerCreate, PartnerUpdate]):
       def __init__(self, db: AsyncSession):
           super().__init__(db, Partner)  # Essential!
   ```

2. **Check generic type parameters**:
   ```python
   # Include all three generic types
   class PartnerService(CompanyBusinessObjectService[
       Partner,        # Model type
       PartnerCreate,  # Create schema type  
       PartnerUpdate   # Update schema type
   ]):
       pass
   ```

3. **Verify model and schema compatibility**:
   ```python
   # Check that model and schemas match
   partner_data = PartnerCreate(name="Test", company_id=1)
   partner_dict = partner_data.dict()
   
   # This should work without errors
   partner = Partner(**partner_dict)
   ```

### Issue 8: Database Session Issues

**Problem**: Database session not properly managed
```python
sqlalchemy.exc.InvalidRequestError: Object '<Partner>' is not bound to a Session
```

**Solutions**:
1. **Use proper async session management**:
   ```python
   # ✅ Correct async session usage
   async def create_partner(partner_data: PartnerCreate):
       async with get_db_session() as db:
           service = PartnerService(db)
           partner = await service.create_partner(partner_data)
           await db.commit()
           return partner
   ```

2. **Ensure session is passed correctly**:
   ```python
   # In your dependencies
   async def get_db():
       async with get_db_session() as session:
           yield session
   
   # In your endpoints
   @router.post("/partners/")
   async def create_partner(
       partner_data: PartnerCreate,
       db: AsyncSession = Depends(get_db)
   ):
       service = PartnerService(db)
       return await service.create_partner(partner_data)
   ```

## 🔌 Extension System Issues

### Issue 9: Custom Field Validation Errors

**Problem**: Custom field validation fails
```python
ValueError: Invalid field type 'custom_type'. Supported types: string, integer, decimal, boolean, date, datetime, json
```

**Diagnosis**:
```python
# Check supported field types
from app.framework.extensions import SUPPORTED_FIELD_TYPES
print(f"Supported types: {SUPPORTED_FIELD_TYPES}")

# Test field type validation
try:
    await service.set_extension(
        entity_id=1,
        field_name="test_field",
        field_type="custom_type",  # Invalid type
        field_value="test"
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

**Solutions**:
1. **Use supported field types**:
   ```python
   # ✅ Valid field types
   supported_types = [
       'string', 'integer', 'decimal', 'boolean', 
       'date', 'datetime', 'json'
   ]
   
   # Example usage
   await service.set_extension(
       entity_id=partner_id,
       field_name="credit_limit",
       field_type="decimal",  # Valid type
       field_value="10000.00"
   )
   ```

2. **Add custom validation**:
   ```python
   # Extend supported types
   CUSTOM_FIELD_TYPES = {
       'email': {'pattern': r'^[^@]+@[^@]+\.[^@]+$'},
       'phone': {'pattern': r'^\+?[\d\s\-\(\)]+$'},
       'url': {'pattern': r'^https?://.*'}
   }
   ```

### Issue 10: Extension Field Querying Problems

**Problem**: Cannot query by extension fields
```python
# This doesn't work as expected
partners = await service.get_list(
    extension_filters={"credit_limit__gte": "5000"}
)
```

**Solutions**:
1. **Use proper extension query syntax**:
   ```python
   # ✅ Correct extension filtering
   partners = await service.get_list(
       company_id=company_id,
       extension_filters={
           "credit_limit__gte": "5000.00"
       }
   )
   ```

2. **Check extension field exists**:
   ```python
   # Verify field exists before querying
   extensions = await service.get_extensions(partner_id)
   if "credit_limit" not in extensions:
       print("Extension field 'credit_limit' not found")
   ```

## 📊 Audit Logging Issues

### Issue 11: Audit Logs Not Created

**Problem**: No audit entries being created
```python
# No audit logs appear after operations
audit_entries = await service.get_audit_trail(partner_id)
print(f"Audit entries: {len(audit_entries)}")  # Returns 0
```

**Diagnosis**:
```python
# Check if audit service is configured
service = PartnerService(db)
print(f"Audit service: {service.audit_service}")
print(f"Has AuditableMixin: {hasattr(Partner, '_audit_logger')}")

# Check audit table exists
async with get_db_session() as db:
    try:
        result = await db.execute(text("SELECT COUNT(*) FROM audit_logs"))
        print(f"Audit table accessible: {result.scalar()}")
    except Exception as e:
        print(f"Audit table error: {e}")
```

**Solutions**:
1. **Verify audit mixin is included**:
   ```python
   # ✅ Ensure AuditableMixin is in model
   class Partner(CompanyBaseModel, BusinessObjectMixin, AuditableMixin, EventPublisherMixin):
       __tablename__ = "partners"
       # ... model fields
   ```

2. **Check audit service configuration**:
   ```python
   # Make sure audit service is injected
   class PartnerService(CompanyBusinessObjectService):
       def __init__(self, db: AsyncSession):
           super().__init__(db, Partner)
           # Audit service should be auto-injected
           assert self.audit_service is not None
   ```

3. **Manually trigger audit logging**:
   ```python
   # For debugging, manually create audit entry
   await service.audit_service.log_partner_created(
       partner_id=partner.id,
       changes={"name": {"old": None, "new": partner.name}},
       user_id=current_user.id,
       correlation_id=generate_correlation_id()
   )
   ```

## 📡 Event Publishing Issues

### Issue 12: Events Not Published to Redis

**Problem**: No events appearing in Redis streams
```python
# Check Redis stream - should show events
XRANGE partner_events - +
# Returns empty
```

**Diagnosis**:
```python
# Test Redis connection
import redis
import asyncio

async def test_redis_connection():
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.ping()
        print("✅ Redis connection successful")
        
        # Test stream publishing
        redis_client.xadd('test_stream', {'message': 'test'})
        print("✅ Redis publishing works")
    except Exception as e:
        print(f"❌ Redis error: {e}")

asyncio.run(test_redis_connection())
```

**Solutions**:
1. **Check Redis configuration**:
   ```python
   # app/core/config.py
   REDIS_URL = "redis://localhost:6379/0"
   
   # Test Redis client setup
   import redis
   redis_client = redis.from_url(REDIS_URL)
   redis_client.ping()
   ```

2. **Verify event publisher mixin**:
   ```python
   # ✅ Ensure EventPublisherMixin is included
   class Partner(CompanyBaseModel, BusinessObjectMixin, AuditableMixin, EventPublisherMixin):
       pass
   ```

3. **Check messaging service**:
   ```python
   # Verify messaging service is configured
   service = PartnerService(db)
   print(f"Messaging service: {service.messaging_service}")
   
   # Test manual event publishing
   await service.messaging_service.publish_partner_created(
       partner_id=partner.id,
       partner_data=partner_data,
       correlation_id="test_correlation"
   )
   ```

## ⚡ Performance Issues

### Issue 13: Slow Query Performance

**Problem**: Framework queries are significantly slower than original
```python
# Framework query takes 2+ seconds
partners = await framework_service.get_list(company_id=1)

# Original query takes 200ms
partners = await original_service.get_partners_by_company(1)
```

**Diagnosis**:
```python
# Enable SQL logging to see queries
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Compare query execution plans
from sqlalchemy import text

async with get_db_session() as db:
    # Check query plan
    result = await db.execute(text("""
        EXPLAIN ANALYZE 
        SELECT * FROM partners 
        WHERE company_id = 1
    """))
    print(result.fetchall())
```

**Solutions**:
1. **Add proper indexes**:
   ```sql
   -- Create indexes for framework queries
   CREATE INDEX idx_partners_company_active ON partners(company_id, is_active);
   CREATE INDEX idx_partners_updated_at ON partners(updated_at);
   CREATE INDEX idx_business_object_extensions_entity ON business_object_extensions(entity_type, entity_id);
   ```

2. **Use eager loading**:
   ```python
   # ✅ Load related data efficiently
   from sqlalchemy.orm import selectinload
   
   query = query.options(
       selectinload(Partner.addresses),
       selectinload(Partner.contacts)
   )
   ```

3. **Optimize framework queries**:
   ```python
   # Use specific fields instead of SELECT *
   query = select(Partner.id, Partner.name, Partner.email).where(
       Partner.company_id == company_id
   )
   ```

### Issue 14: Memory Usage Issues

**Problem**: High memory usage with framework operations
```python
# Memory usage increases significantly
partners = await service.bulk_create(large_dataset)
```

**Solutions**:
1. **Use batch processing**:
   ```python
   # Process in smaller batches
   batch_size = 100
   for i in range(0, len(large_dataset), batch_size):
       batch = large_dataset[i:i + batch_size]
       await service.bulk_create(batch)
       await db.commit()  # Commit each batch
   ```

2. **Implement streaming**:
   ```python
   async def stream_partners(company_id: int):
       async for partner in service.get_partners_stream(company_id):
           yield partner
   ```

## 🧪 Testing Issues

### Issue 15: Test Setup Problems

**Problem**: Framework tests fail with setup errors
```python
# Tests fail with dependency injection issues
ModuleNotFoundError: No module named 'app.framework'
```

**Solutions**:
1. **Proper test configuration**:
   ```python
   # conftest.py
   import sys
   from pathlib import Path
   
   # Add project root to Python path
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root))
   
   @pytest.fixture
   async def framework_service(db_session):
       from app.services.partner_service import PartnerFrameworkService
       return PartnerFrameworkService(db_session)
   ```

2. **Mock framework dependencies**:
   ```python
   # Test with mocked services
   @pytest.fixture
   def mock_audit_service():
       return AsyncMock()
   
   @pytest.fixture  
   def mock_messaging_service():
       return AsyncMock()
   
   @pytest.fixture
   def partner_service(db_session, mock_audit_service, mock_messaging_service):
       service = PartnerService(db_session)
       service.audit_service = mock_audit_service
       service.messaging_service = mock_messaging_service
       return service
   ```

## 🚀 Production Deployment Issues

### Issue 16: Environment Configuration

**Problem**: Framework features don't work in production
```python
# Features work in development but fail in production
```

**Solutions**:
1. **Check environment variables**:
   ```bash
   # Production environment variables
   DATABASE_URL=postgresql://...
   REDIS_URL=redis://...
   AUDIT_ENABLED=true
   EVENT_PUBLISHING_ENABLED=true
   ```

2. **Verify service dependencies**:
   ```bash
   # Check all services are running
   docker ps | grep -E "(postgres|redis|app)"
   
   # Test connectivity
   curl http://app-service:8000/health
   ```

3. **Check logs for errors**:
   ```bash
   # Application logs
   docker logs app-service --tail 100
   
   # Database logs  
   docker logs postgres-service --tail 50
   
   # Redis logs
   docker logs redis-service --tail 50
   ```

## 🔍 Diagnostic Tools

### Framework Health Check

```python
# app/utils/framework_diagnostics.py
async def run_framework_diagnostics():
    """Comprehensive framework health check"""
    
    diagnostics = {
        "imports": check_framework_imports(),
        "database": await check_database_connection(),
        "extensions": await check_extension_tables(),
        "audit": await check_audit_system(),
        "events": await check_event_publishing(),
        "redis": check_redis_connection()
    }
    
    all_passed = all(diagnostics.values())
    
    print("🔍 Framework Diagnostics Results:")
    for check, passed in diagnostics.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check.title()}: {'PASS' if passed else 'FAIL'}")
    
    return all_passed

def check_framework_imports():
    """Check if all framework modules can be imported"""
    try:
        from app.framework.base import CompanyBaseModel
        from app.framework.mixins import BusinessObjectMixin
        from app.framework.services import CompanyBusinessObjectService
        from app.framework.schemas import CompanyBusinessObjectSchema
        return True
    except ImportError:
        return False

async def check_database_connection():
    """Check database connectivity"""
    try:
        from app.core.database import get_db_session
        from sqlalchemy import text
        
        async with get_db_session() as db:
            await db.execute(text("SELECT 1"))
            return True
    except Exception:
        return False

# Usage
if __name__ == "__main__":
    import asyncio
    asyncio.run(run_framework_diagnostics())
```

### Quick Fix Script

```bash
#!/bin/bash
# framework_quick_fix.sh

echo "🔧 Framework Quick Fix Script"

# Fix common permission issues
chmod +x migrations/partner_framework_migration.py

# Install missing dependencies
pip install sqlalchemy[asyncio] pydantic fastapi redis asyncpg

# Create missing directories
mkdir -p app/framework_migration
mkdir -p docs
mkdir -p templates

# Create missing __init__.py files
touch app/__init__.py
touch app/framework/__init__.py  
touch app/framework_migration/__init__.py

# Run diagnostics
python app/utils/framework_diagnostics.py

echo "✅ Quick fix completed"
```

## 📞 Getting Help

### When to Contact Support

1. **Critical Production Issues**: Framework causing production downtime
2. **Data Corruption**: Audit logs or events showing incorrect data
3. **Performance Degradation**: >50% performance impact
4. **Security Concerns**: Potential data leakage or access issues

### Information to Include

When reporting issues, include:

```
Framework Version: 1.0.0
Python Version: 3.12
Database: PostgreSQL 17
Redis Version: 7.0
Operating System: [Your OS]

Error Message:
[Full error traceback]

Steps to Reproduce:
1. [Step 1]
2. [Step 2]
3. [Error occurs]

Expected Behavior:
[What should happen]

Actual Behavior:
[What actually happens]

Diagnostic Output:
[Output from framework_diagnostics.py]
```

### Self-Help Resources

1. **[Developer Guide](BUSINESS_OBJECT_FRAMEWORK_DEVELOPER_GUIDE.md)** - Complete documentation
2. **[Quick Start Guide](FRAMEWORK_QUICK_START_GUIDE.md)** - Step-by-step tutorial
3. **[Migration Guide](SERVICE_MIGRATION_PROCESS_GUIDE.md)** - Migration process
4. **[Usage Examples](FRAMEWORK_USAGE_EXAMPLES.md)** - Common patterns
5. **Test Suite** - Framework tests show correct usage patterns

---

**Troubleshooting Guide Version**: 1.0.0  
**Last Updated**: 2025-08-01  
**Framework Version**: 1.0.0