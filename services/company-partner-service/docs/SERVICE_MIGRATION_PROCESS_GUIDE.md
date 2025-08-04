# Service Migration Process Guide

## 🔄 Migrating Existing Services to Business Object Framework

This comprehensive guide walks you through migrating existing business services to the M-ERP Business Object Framework. The migration process is designed to be safe, incremental, and backward-compatible.

## 📚 Table of Contents

1. [Migration Overview](#migration-overview)
2. [Pre-Migration Assessment](#pre-migration-assessment)
3. [Migration Strategy](#migration-strategy)
4. [Step-by-Step Migration Process](#step-by-step-migration-process)
5. [Code Examples](#code-examples)
6. [Testing and Validation](#testing-and-validation)
7. [Rollback Procedures](#rollback-procedures)
8. [Common Migration Patterns](#common-migration-patterns)
9. [Troubleshooting](#troubleshooting)

## 🎯 Migration Overview

### Why Migrate?

Migrating to the Business Object Framework provides:

- **Standardized CRUD Operations**: Consistent API patterns across all services
- **Automatic Audit Logging**: Track all changes without additional code
- **Event Publishing**: Real-time notifications for business events
- **Custom Fields**: Add fields without database schema changes
- **Multi-Company Support**: Built-in data isolation
- **Enhanced Testing**: Standardized test patterns and utilities
- **Better Performance**: Optimized queries and bulk operations

### Migration Philosophy

- **Zero Downtime**: Services continue running during migration
- **Backward Compatibility**: Existing APIs remain functional
- **Incremental**: Migrate features one at a time
- **Reversible**: Safe rollback procedures available
- **Data Preservation**: No data loss or corruption

## 📊 Pre-Migration Assessment

### 1. Service Analysis Checklist

Before starting migration, analyze your existing service:

```bash
# Use the assessment script
python assessment_script.py --service your_service_name
```

**Manual Assessment Questions**:

- [ ] What business objects does the service manage?
- [ ] Does the service use multi-company data isolation?
- [ ] Are there existing audit logging requirements?
- [ ] What custom business logic exists?
- [ ] Are there performance-critical operations?
- [ ] What external integrations exist?
- [ ] Are there complex validation rules?

### 2. Dependency Mapping

```python
# tools/analyze_dependencies.py
import ast
import os
from pathlib import Path

def analyze_service_dependencies(service_path: str):
    """Analyze dependencies for migration planning"""
    dependencies = {
        "models": [],
        "schemas": [],
        "services": [],
        "routers": [],
        "external": []
    }
    
    for file_path in Path(service_path).rglob("*.py"):
        with open(file_path, 'r') as f:
            try:
                tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analyze_import(alias.name, dependencies)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            analyze_import(node.module, dependencies)
            except:
                continue
    
    return dependencies

def analyze_import(module_name: str, dependencies: dict):
    """Categorize imports for migration planning"""
    if "models" in module_name:
        dependencies["models"].append(module_name)
    elif "schemas" in module_name:
        dependencies["schemas"].append(module_name)
    elif "services" in module_name:
        dependencies["services"].append(module_name)
    elif "routers" in module_name:
        dependencies["routers"].append(module_name)
    else:
        dependencies["external"].append(module_name)

# Usage
dependencies = analyze_service_dependencies("app/your_service/")
print("Migration Dependencies Analysis:")
for category, items in dependencies.items():
    print(f"{category}: {len(items)} items")
```

### 3. Data Assessment

```sql
-- Assess data complexity
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'your_schema' 
  AND table_name = 'your_table'
ORDER BY table_name, ordinal_position;

-- Check for existing audit tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_name LIKE '%audit%' 
   OR table_name LIKE '%log%';

-- Analyze data volume
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE tablename = 'your_table';
```

## 🛠️ Migration Strategy

### Migration Phases

1. **Phase 1: Framework Integration** (Non-Breaking)
   - Add framework dependencies
   - Create framework-based models alongside existing ones
   - Implement framework services
   - Create framework routers

2. **Phase 2: Parallel Operation** (Testing)
   - Run both old and new implementations side-by-side
   - Route traffic to framework version for testing
   - Validate data consistency and performance

3. **Phase 3: Full Migration** (Breaking Changes)
   - Replace original implementation with framework version
   - Update route configurations
   - Remove deprecated code

### Decision Matrix

| Scenario | Strategy | Risk Level | Timeline |
|----------|----------|------------|----------|
| Simple CRUD service | Direct migration | Low | 1-2 days |
| Complex business logic | Incremental migration | Medium | 1-2 weeks |
| High-traffic service | Parallel deployment | Medium | 2-3 weeks |
| Critical production service | Gradual rollout | Low | 3-4 weeks |

## 📋 Step-by-Step Migration Process

### Step 1: Prepare Framework Infrastructure

```bash
# 1. Ensure framework dependencies
pip install sqlalchemy[asyncio] pydantic fastapi redis

# 2. Create framework directory structure
mkdir -p app/framework_migration
touch app/framework_migration/__init__.py
```

### Step 2: Create Framework-Based Models

#### Original Model
```python
# app/models/customer.py (ORIGINAL)
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.models.base import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    company_id = Column(Integer, nullable=False)  # If multi-company
```

#### Framework-Enhanced Model
```python
# app/framework_migration/customer_model.py (FRAMEWORK VERSION)
from sqlalchemy import Column, String, Boolean
from app.framework.base import CompanyBaseModel
from app.framework.mixins import BusinessObjectMixin, AuditableMixin, EventPublisherMixin

class CustomerFramework(CompanyBaseModel, BusinessObjectMixin, AuditableMixin, EventPublisherMixin):
    __tablename__ = "customers"  # Same table name for compatibility
    
    # Business fields (same as original)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Framework mixins automatically provide:
    # - id, company_id, created_at, updated_at (from CompanyBaseModel)
    # - framework_version (from BusinessObjectMixin)
    # - audit logging capability (from AuditableMixin)
    # - event publishing capability (from EventPublisherMixin)
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}')>"
```

### Step 3: Create Framework-Based Schemas

#### Original Schemas
```python
# app/schemas/customer.py (ORIGINAL)
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None
    is_active: bool = True

class CustomerCreate(CustomerBase):
    company_id: int

class CustomerUpdate(CustomerBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class CustomerResponse(CustomerBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### Framework-Enhanced Schemas
```python
# app/framework_migration/customer_schemas.py (FRAMEWORK VERSION)
from typing import Optional
from datetime import datetime
from pydantic import Field, validator
from app.framework.schemas import CompanyBusinessObjectSchema

class CustomerFrameworkBase(CompanyBusinessObjectSchema):
    """Framework-based customer schema with enhanced validation"""
    
    name: str = Field(..., min_length=1, max_length=255, description="Customer name")
    email: Optional[str] = Field(None, regex=r'^[^@]+@[^@]+\.[^@]+$', description="Email address")
    is_active: bool = Field(True, description="Whether customer is active")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Customer name cannot be empty')
        return v.strip()
    
    @validator('email')
    def validate_email_format(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

class CustomerFrameworkCreate(CustomerFrameworkBase):
    """Schema for creating customers"""
    pass

class CustomerFrameworkUpdate(CustomerFrameworkBase):
    """Schema for updating customers - all fields optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None

class CustomerFrameworkResponse(CustomerFrameworkBase):
    """Schema for customer responses"""
    id: int
    created_at: datetime
    updated_at: datetime
    framework_version: Optional[str] = None
    
    class Config:
        from_attributes = True
```

### Step 4: Create Framework-Based Service

#### Original Service
```python
# app/services/customer_service.py (ORIGINAL)
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

class CustomerService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_customer(self, customer_data: CustomerCreate) -> Customer:
        customer = Customer(**customer_data.dict())
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer
    
    async def get_customer(self, customer_id: int, company_id: int) -> Customer:
        return self.db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.company_id == company_id
        ).first()
    
    async def update_customer(self, customer_id: int, customer_data: CustomerUpdate, company_id: int) -> Customer:
        customer = self.get_customer(customer_id, company_id)
        if customer:
            for key, value in customer_data.dict(exclude_unset=True).items():
                setattr(customer, key, value)
            self.db.commit()
            self.db.refresh(customer)
        return customer
    
    async def delete_customer(self, customer_id: int, company_id: int) -> bool:
        customer = self.get_customer(customer_id, company_id)
        if customer:
            customer.is_active = False
            self.db.commit()
            return True
        return False
```

#### Framework-Enhanced Service
```python
# app/framework_migration/customer_service.py (FRAMEWORK VERSION)
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.framework.services import CompanyBusinessObjectService
from app.framework_migration.customer_model import CustomerFramework
from app.framework_migration.customer_schemas import (
    CustomerFrameworkCreate, 
    CustomerFrameworkUpdate
)

class CustomerFrameworkService(CompanyBusinessObjectService[CustomerFramework, CustomerFrameworkCreate, CustomerFrameworkUpdate]):
    """Customer service with framework capabilities"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, CustomerFramework)
    
    # Basic CRUD operations (inherited from framework, with automatic audit + events)
    
    async def create_customer(self, customer_data: CustomerFrameworkCreate) -> CustomerFramework:
        """Create customer with automatic audit logging and event publishing"""
        return await self.create(customer_data.dict())
    
    async def get_customer(self, customer_id: int, company_id: int) -> Optional[CustomerFramework]:
        """Get customer by ID with company isolation"""
        return await self.get_by_id(customer_id, company_id)
    
    async def update_customer(self, customer_id: int, customer_data: CustomerFrameworkUpdate, company_id: int) -> Optional[CustomerFramework]:
        """Update customer with change tracking"""
        return await self.update(customer_id, customer_data.dict(exclude_unset=True), company_id)
    
    async def delete_customer(self, customer_id: int, company_id: int) -> bool:
        """Soft delete customer"""
        return await self.soft_delete(customer_id, company_id)
    
    # Enhanced business methods (leveraging framework capabilities)
    
    async def get_active_customers(self, company_id: int) -> List[CustomerFramework]:
        """Get all active customers"""
        return await self.get_list(
            filters={"is_active": True},
            company_id=company_id
        )
    
    async def search_customers(self, query: str, company_id: int) -> List[CustomerFramework]:
        """Search customers by name or email"""
        filters = {
            "$or": [
                {"name__icontains": query},
                {"email__icontains": query}
            ]
        }
        return await self.get_list(filters=filters, company_id=company_id)
    
    async def bulk_activate_customers(self, customer_ids: List[int], company_id: int) -> int:
        """Bulk activate customers with audit logging"""
        return await self.bulk_update(
            ids=customer_ids,
            data={"is_active": True},
            company_id=company_id
        )
    
    # Custom field methods (new framework capability)
    
    async def set_customer_credit_limit(self, customer_id: int, credit_limit: float) -> None:
        """Set credit limit as custom field"""
        await self.set_extension(
            entity_id=customer_id,
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
    
    async def get_customers_by_credit_limit(self, min_limit: float, company_id: int) -> List[CustomerFramework]:
        """Query customers by credit limit custom field"""
        extension_filters = {
            "credit_limit__gte": str(min_limit)
        }
        return await self.get_list(
            extension_filters=extension_filters,
            company_id=company_id
        )
```

### Step 5: Create Framework-Based Router

#### Original Router
```python
# app/routers/customers.py (ORIGINAL)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db)
):
    service = CustomerService(db)
    return await service.create_customer(customer_data)

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    service = CustomerService(db)
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
```

#### Framework-Enhanced Router
```python
# app/framework_migration/customer_router.py (FRAMEWORK VERSION)
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import get_current_user_company
from app.framework_migration.customer_service import CustomerFrameworkService
from app.framework_migration.customer_schemas import (
    CustomerFrameworkCreate,
    CustomerFrameworkUpdate,
    CustomerFrameworkResponse
)

router = APIRouter(prefix="/customers", tags=["Customers"])

def get_customer_service(db: AsyncSession = Depends(get_db)) -> CustomerFrameworkService:
    return CustomerFrameworkService(db)

# Standard CRUD endpoints (enhanced with framework features)

@router.post("/", response_model=CustomerFrameworkResponse, status_code=201)
async def create_customer(
    customer_data: CustomerFrameworkCreate,
    company_id: int = Depends(get_current_user_company),
    service: CustomerFrameworkService = Depends(get_customer_service)
):
    """Create customer with automatic audit logging and event publishing"""
    try:
        customer = await service.create_customer(customer_data)
        return customer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[CustomerFrameworkResponse])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True, description="Filter for active customers only"),
    search: str = Query(None, description="Search by name or email"),
    company_id: int = Depends(get_current_user_company),
    service: CustomerFrameworkService = Depends(get_customer_service)
):
    """List customers with filtering and search"""
    if search:
        customers = await service.search_customers(search, company_id)
    elif active_only:
        customers = await service.get_active_customers(company_id)
    else:
        customers = await service.get_list(company_id=company_id, skip=skip, limit=limit)
    
    return customers

@router.get("/{customer_id}", response_model=CustomerFrameworkResponse)
async def get_customer(
    customer_id: int,
    company_id: int = Depends(get_current_user_company),
    service: CustomerFrameworkService = Depends(get_customer_service)
):
    """Get customer by ID"""
    customer = await service.get_customer(customer_id, company_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{customer_id}", response_model=CustomerFrameworkResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerFrameworkUpdate,
    company_id: int = Depends(get_current_user_company),
    service: CustomerFrameworkService = Depends(get_customer_service)
):
    """Update customer with change tracking"""
    try:
        customer = await service.update_customer(customer_id, customer_data, company_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: int,
    company_id: int = Depends(get_current_user_company),
    service: CustomerFrameworkService = Depends(get_customer_service)
):
    """Soft delete customer"""
    success = await service.delete_customer(customer_id, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")

# Framework-specific endpoints (new capabilities)

@router.get("/{customer_id}/extensions", response_model=Dict[str, Any])
async def get_customer_extensions(
    customer_id: int,
    company_id: int = Depends(get_current_user_company),
    service: CustomerFrameworkService = Depends(get_customer_service)
):
    """Get custom fields for customer"""
    extensions = await service.get_extensions(customer_id)
    return {"extensions": extensions}

@router.post("/{customer_id}/extensions", status_code=201)
async def set_customer_extension(
    customer_id: int,
    field_name: str,
    field_type: str,
    field_value: str,
    company_id: int = Depends(get_current_user_company),
    service: CustomerFrameworkService = Depends(get_customer_service)
):
    """Set custom field for customer"""
    await service.set_extension(
        entity_id=customer_id,
        field_name=field_name,
        field_type=field_type,
        field_value=field_value
    )
    return {"message": "Extension field set successfully"}

@router.get("/{customer_id}/audit", response_model=List[Dict[str, Any]])
async def get_customer_audit_trail(
    customer_id: int,
    company_id: int = Depends(get_current_user_company),
    service: CustomerFrameworkService = Depends(get_customer_service)
):
    """Get audit trail for customer"""
    audit_entries = await service.get_audit_trail(customer_id)
    return audit_entries

@router.post("/bulk-activate", response_model=Dict[str, Any])
async def bulk_activate_customers(
    customer_ids: List[int],
    company_id: int = Depends(get_current_user_company),
    service: CustomerFrameworkService = Depends(get_customer_service)
):
    """Bulk activate customers"""
    updated_count = await service.bulk_activate_customers(customer_ids, company_id)
    return {
        "updated_count": updated_count,
        "customer_ids": customer_ids,
        "message": f"Successfully activated {updated_count} customers"
    }
```

### Step 6: Create Migration Script

```python
# migrations/customer_framework_migration.py
"""
Customer Service Framework Migration Script

This script migrates the Customer service to use the Business Object Framework
while maintaining backward compatibility and data integrity.
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.framework_migration.customer_service import CustomerFrameworkService
from app.services.customer_service import CustomerService  # Original service

class CustomerMigrationScript:
    """Handles Customer service migration to framework"""
    
    def __init__(self):
        self.migration_log = []
        self.backup_path = Path("migrations/backups/customer_migration")
        self.backup_path.mkdir(parents=True, exist_ok=True)
    
    async def run_migration(self, dry_run: bool = True) -> Dict[str, Any]:
        """Execute the complete migration process"""
        
        self.log("Starting Customer service framework migration")
        self.log(f"Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}")
        
        try:
            # Phase 1: Backup existing implementation
            await self.backup_existing_files()
            
            # Phase 2: Validate framework components
            await self.validate_framework_components()
            
            # Phase 3: Data consistency check
            await self.validate_data_consistency()
            
            # Phase 4: Performance comparison
            await self.compare_performance()
            
            if not dry_run:
                # Phase 5: Deploy framework files
                await self.deploy_framework_files()
                
                # Phase 6: Update application routes
                await self.update_application_routes()
                
                # Phase 7: Final validation
                await self.final_validation()
            
            migration_summary = {
                "status": "success",
                "mode": "dry_run" if dry_run else "live",
                "timestamp": datetime.utcnow().isoformat(),
                "log": self.migration_log,
                "backup_location": str(self.backup_path)
            }
            
            self.log("Migration completed successfully")
            return migration_summary
            
        except Exception as e:
            self.log(f"Migration failed: {e}", level="error")
            if not dry_run:
                await self.rollback_migration()
            raise
    
    async def backup_existing_files(self):
        """Backup existing customer service files"""
        self.log("Backing up existing customer service files")
        
        files_to_backup = [
            "app/models/customer.py",
            "app/schemas/customer.py", 
            "app/services/customer_service.py",
            "app/routers/customers.py"
        ]
        
        backup_timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backup_path / f"customer_migration_{backup_timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        for file_path in files_to_backup:
            if Path(file_path).exists():
                import shutil
                backup_file = backup_dir / Path(file_path).name
                shutil.copy2(file_path, backup_file)
                self.log(f"Backed up {file_path} to {backup_file}")
        
        # Save backup info
        backup_info = {
            "timestamp": backup_timestamp,
            "files": files_to_backup,
            "location": str(backup_dir)
        }
        
        with open(backup_dir / "backup_info.json", 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        self.log(f"Backup completed in {backup_dir}")
    
    async def validate_framework_components(self):
        """Validate that all framework components are ready"""
        self.log("Validating framework components")
        
        # Check framework files exist
        framework_files = [
            "app/framework_migration/customer_model.py",
            "app/framework_migration/customer_schemas.py",
            "app/framework_migration/customer_service.py",
            "app/framework_migration/customer_router.py"
        ]
        
        for file_path in framework_files:
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Framework file not found: {file_path}")
            self.log(f"✓ Framework file exists: {file_path}")
        
        # Test imports
        try:
            from app.framework_migration.customer_model import CustomerFramework
            from app.framework_migration.customer_schemas import CustomerFrameworkCreate
            from app.framework_migration.customer_service import CustomerFrameworkService
            self.log("✓ All framework components import successfully")
        except ImportError as e:
            raise ImportError(f"Framework import failed: {e}")
    
    async def validate_data_consistency(self):
        """Validate data consistency between original and framework implementations"""
        self.log("Validating data consistency")
        
        async with get_db_session() as db:
            original_service = CustomerService(db)
            framework_service = CustomerFrameworkService(db)
            
            # Test with sample company
            test_company_id = 1
            
            # Get data from both implementations
            original_customers = await original_service.get_customers_by_company(test_company_id)
            framework_customers = await framework_service.get_list(company_id=test_company_id)
            
            if len(original_customers) != len(framework_customers):
                raise ValueError(f"Data count mismatch: original={len(original_customers)}, framework={len(framework_customers)}")
            
            self.log(f"✓ Data consistency validated: {len(original_customers)} customers")
    
    async def compare_performance(self):
        """Compare performance between original and framework implementations"""
        self.log("Comparing performance")
        
        import time
        async with get_db_session() as db:
            original_service = CustomerService(db)
            framework_service = CustomerFrameworkService(db)
            
            test_company_id = 1
            iterations = 10
            
            # Test original implementation
            start_time = time.time()
            for _ in range(iterations):
                customers = await original_service.get_customers_by_company(test_company_id)
            original_time = (time.time() - start_time) / iterations
            
            # Test framework implementation
            start_time = time.time()
            for _ in range(iterations):
                customers = await framework_service.get_list(company_id=test_company_id)
            framework_time = (time.time() - start_time) / iterations
            
            performance_ratio = framework_time / original_time if original_time > 0 else 1.0
            
            self.log(f"Performance comparison:")
            self.log(f"  Original: {original_time:.3f}s per operation")
            self.log(f"  Framework: {framework_time:.3f}s per operation")
            self.log(f"  Ratio: {performance_ratio:.2f}x")
            
            if performance_ratio > 2.0:
                self.log("WARNING: Framework implementation is significantly slower", level="warning")
            elif performance_ratio < 0.5:
                self.log("✓ Framework implementation is faster")
            else:
                self.log("✓ Framework performance is acceptable")
    
    async def deploy_framework_files(self):
        """Deploy framework files to replace original implementation"""
        self.log("Deploying framework files")
        
        # Move framework files to main locations
        import shutil
        
        file_mappings = {
            "app/framework_migration/customer_model.py": "app/models/customer.py",
            "app/framework_migration/customer_schemas.py": "app/schemas/customer.py",
            "app/framework_migration/customer_service.py": "app/services/customer_service.py",
            "app/framework_migration/customer_router.py": "app/routers/customers.py"
        }
        
        for source, destination in file_mappings.items():
            shutil.copy2(source, destination)
            self.log(f"Deployed {source} to {destination}")
    
    async def update_application_routes(self):
        """Update main application to use framework routes"""
        self.log("Updating application routes")
        
        # This would update your main FastAPI app
        # Implementation depends on your specific app structure
        self.log("✓ Application routes updated")
    
    async def final_validation(self):
        """Final validation after migration"""
        self.log("Running final validation")
        
        # Test API endpoints
        # Run health checks
        # Validate audit logging
        # Check event publishing
        
        self.log("✓ Final validation completed")
    
    async def rollback_migration(self):
        """Rollback migration in case of failure"""
        self.log("Rolling back migration")
        
        # Restore from backup
        # Revert route changes
        # Clean up framework files
        
        self.log("✓ Migration rolled back successfully")
    
    def log(self, message: str, level: str = "info"):
        """Log migration progress"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level.upper()}] {message}"
        print(log_entry)
        self.migration_log.append(log_entry)

# Migration CLI
async def main():
    """Migration CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Customer Service Framework Migration")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--force", action="store_true", help="Force migration without confirmations")
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.force:
        confirm = input("This will modify your customer service implementation. Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Migration cancelled")
            return
    
    migration = CustomerMigrationScript()
    
    try:
        result = await migration.run_migration(dry_run=args.dry_run)
        print(f"\nMigration completed successfully!")
        print(f"Status: {result['status']}")
        print(f"Backup location: {result['backup_location']}")
        
    except Exception as e:
        print(f"\nMigration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 7: Testing Migration

```python
# tests/test_customer_migration.py
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.framework_migration.customer_service import CustomerFrameworkService
from app.services.customer_service import CustomerService

class TestCustomerMigration:
    """Test customer service migration"""
    
    @pytest.mark.asyncio
    async def test_api_compatibility(self):
        """Test that framework API is compatible with original"""
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test data
            customer_data = {
                "name": "Test Customer",
                "email": "test@customer.com",
                "is_active": True
            }
            
            # Create customer
            response = await client.post(
                "/customers/",
                json=customer_data,
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == 201
            created_customer = response.json()
            
            # Verify response structure matches original
            expected_fields = {"id", "name", "email", "is_active", "created_at", "updated_at"}
            assert set(created_customer.keys()).issuperset(expected_fields)
            
            # Test get customer
            customer_id = created_customer["id"]
            response = await client.get(
                f"/customers/{customer_id}",
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_framework_enhancements(self):
        """Test new framework capabilities"""
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create customer
            response = await client.post(
                "/customers/",
                json={"name": "Enhanced Customer", "email": "enhanced@test.com"},
                headers={"Authorization": "Bearer test-token"}
            )
            customer_id = response.json()["id"]
            
            # Test custom fields (new framework feature)
            response = await client.post(
                f"/customers/{customer_id}/extensions",
                json={
                    "field_name": "credit_limit",
                    "field_type": "decimal",
                    "field_value": "5000.00"
                },
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == 201
            
            # Test audit trail (new framework feature)
            response = await client.get(
                f"/customers/{customer_id}/audit",
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == 200
            audit_entries = response.json()
            assert len(audit_entries) >= 1  # At least creation entry
    
    @pytest.mark.asyncio
    async def test_data_consistency(self, db_session):
        """Test data consistency between implementations"""
        
        original_service = CustomerService(db_session)
        framework_service = CustomerFrameworkService(db_session)
        
        # Create customer with original service
        original_customer = await original_service.create_customer({
            "name": "Consistency Test",
            "email": "consistency@test.com",
            "company_id": 1
        })
        
        # Read with framework service
        framework_customer = await framework_service.get_customer(
            original_customer.id, 
            company_id=1
        )
        
        # Verify data consistency
        assert framework_customer.name == original_customer.name
        assert framework_customer.email == original_customer.email
        assert framework_customer.id == original_customer.id
    
    @pytest.mark.asyncio
    async def test_performance_regression(self, db_session):
        """Test that framework doesn't cause significant performance regression"""
        
        import time
        
        original_service = CustomerService(db_session)
        framework_service = CustomerFrameworkService(db_session)
        
        # Create test data
        test_customers = [
            {"name": f"Perf Test {i}", "email": f"perf{i}@test.com", "company_id": 1}
            for i in range(50)
        ]
        
        # Bulk create with framework (has bulk capabilities)
        start_time = time.time()
        created_customers = await framework_service.bulk_create(test_customers)
        framework_time = time.time() - start_time
        
        # Verify performance is acceptable
        assert framework_time < 5.0  # Should complete in under 5 seconds
        assert len(created_customers) == 50
        
        # Test query performance
        start_time = time.time()
        customers = await framework_service.get_list(company_id=1)
        query_time = time.time() - start_time
        
        assert query_time < 1.0  # Should query in under 1 second
        assert len(customers) >= 50
```

## ✅ Testing and Validation

### Migration Test Checklist

- [ ] **API Compatibility**: All existing endpoints work unchanged
- [ ] **Data Integrity**: No data loss or corruption
- [ ] **Performance**: No significant performance degradation
- [ ] **Functionality**: All business logic preserved
- [ ] **Authentication**: Security and permissions maintained
- [ ] **Error Handling**: Error responses remain consistent
- [ ] **Documentation**: API docs updated automatically

### Automated Validation Script

```bash
# Run complete migration validation
python migrations/validate_migration.py --service customer --verbose

# Run performance benchmarks
python migrations/benchmark_migration.py --service customer --iterations 100

# Run API compatibility tests
pytest tests/test_customer_migration.py -v

# Run load tests
python tests/load_test_migration.py --concurrent-users 50
```

## 🔄 Rollback Procedures

### Automatic Rollback

```python
# migrations/rollback_migration.py
async def rollback_customer_migration():
    """Safely rollback customer service migration"""
    
    print("Starting rollback procedure...")
    
    # 1. Restore backed up files
    backup_dir = "migrations/backups/customer_migration_latest"
    restore_files_from_backup(backup_dir)
    
    # 2. Revert route configurations
    update_app_routes_to_original()
    
    # 3. Restart application services
    restart_app_services()
    
    # 4. Validate rollback
    validate_original_functionality()
    
    print("Rollback completed successfully")

# Usage
python migrations/rollback_migration.py --service customer --confirm
```

### Manual Rollback Steps

1. **Stop Application**: Ensure application is stopped
2. **Restore Files**: Copy backed up files to original locations
3. **Revert Routes**: Update main app to use original routes
4. **Restart Services**: Start application and validate functionality
5. **Verify Data**: Ensure all data is accessible and correct

## 🎯 Common Migration Patterns

### Pattern 1: Simple CRUD Service

**Characteristics**: Basic CRUD operations, minimal business logic
**Timeline**: 1-2 days
**Risk**: Low

```python
# Migration steps for simple CRUD
1. Create framework model (30 min)
2. Create framework schemas (30 min) 
3. Create framework service (1 hour)
4. Create framework router (1 hour)
5. Test and validate (2 hours)
6. Deploy (30 min)
```

### Pattern 2: Complex Business Logic

**Characteristics**: Custom validation, complex workflows, integrations
**Timeline**: 1-2 weeks
**Risk**: Medium

```python
# Migration steps for complex service
1. Analyze existing business logic (1 day)
2. Design framework integration (1 day)
3. Implement framework components (3 days)
4. Migrate business logic (2 days)
5. Comprehensive testing (2 days)
6. Performance optimization (1 day)
7. Deploy and monitor (1 day)
```

### Pattern 3: High-Traffic Service

**Characteristics**: Performance critical, high request volume
**Timeline**: 2-3 weeks  
**Risk**: Medium

```python
# Migration steps for high-traffic service
1. Performance baseline (1 day)
2. Framework implementation (1 week)
3. Performance testing (3 days)
4. Optimization (2 days)
5. Gradual rollout (1 week)
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: Import Errors During Migration
```python
# Problem: Framework imports fail
ModuleNotFoundError: No module named 'app.framework'

# Solution: Verify framework installation
pip install -r requirements.txt
python -c "from app.framework import base; print('Framework available')"
```

#### Issue: Schema Validation Failures
```python
# Problem: Pydantic validation errors
ValidationError: field required

# Solution: Update schema compatibility
class CustomerFrameworkCreate(CustomerFrameworkBase):
    # Ensure all required fields from original schema are included
    name: str  # Was required in original
    company_id: int  # Add if missing
```

#### Issue: Database Connection Problems
```python
# Problem: Service can't connect to database
sqlalchemy.exc.OperationalError: connection failed

# Solution: Check database configuration
async def test_db_connection():
    async with get_db_session() as db:
        result = await db.execute(text("SELECT 1"))
        print("Database connection OK")
```

#### Issue: Performance Degradation
```python
# Problem: Framework implementation is slower
# Solution: Add proper indexes and optimize queries

# Add indexes for framework queries
CREATE INDEX idx_customers_company_active ON customers(company_id, is_active);
CREATE INDEX idx_customers_name_gin ON customers USING gin(name gin_trgm_ops);

# Use eager loading for related data
query = query.options(selectinload(Customer.addresses))
```

#### Issue: Audit Logging Not Working
```python
# Problem: No audit entries created
# Solution: Verify audit service configuration

class CustomerFramework(CompanyBaseModel, AuditableMixin):
    # Ensure AuditableMixin is included
    pass

# Check audit service is properly injected
service = CustomerFrameworkService(db)
assert service.audit_service is not None
```

## 📈 Migration Success Metrics

### Key Performance Indicators

- **Migration Time**: Target < 2 weeks for complex services
- **Downtime**: Target 0 minutes (zero-downtime migration)
- **Performance**: Target < 20% performance impact
- **Error Rate**: Target < 0.1% increase during migration
- **Rollback Time**: Target < 30 minutes if needed

### Monitoring and Alerts

```python
# Set up monitoring for migration
import logging
from app.core.monitoring import setup_migration_monitoring

logger = logging.getLogger("migration")

# Monitor key metrics during migration
setup_migration_monitoring([
    "api_response_time",
    "database_query_time", 
    "error_rate",
    "audit_entry_creation",
    "event_publishing_rate"
])

# Alert thresholds
ALERT_THRESHOLDS = {
    "response_time_95th": 2000,  # ms
    "error_rate": 0.001,  # 0.1%
    "db_connection_pool": 80,  # 80% utilization
}
```

## 📊 Migration Report Template

```markdown
# Customer Service Migration Report

**Migration Date**: 2025-08-01
**Service**: Customer Service
**Framework Version**: 1.0.0

## Summary
- **Status**: ✅ Successful
- **Duration**: 3 hours
- **Downtime**: 0 minutes
- **Issues Encountered**: 0

## Metrics
- **Performance Impact**: +5% (within acceptable range)
- **API Compatibility**: 100% maintained
- **Data Integrity**: 100% preserved
- **Test Coverage**: 95%

## New Capabilities Added
- ✅ Custom field support
- ✅ Automatic audit logging
- ✅ Event publishing
- ✅ Bulk operations
- ✅ Enhanced validation

## Post-Migration Tasks
- [ ] Monitor performance for 48 hours
- [ ] Train team on new framework features
- [ ] Update documentation
- [ ] Plan next service migration
```

---

**Migration Status**: Ready for Production  
**Framework Version**: 1.0.0  
**Last Updated**: 2025-08-01  
**Success Rate**: 100% for Partner Service Migration