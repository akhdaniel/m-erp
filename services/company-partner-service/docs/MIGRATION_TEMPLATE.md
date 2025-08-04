# Business Object Migration Template

## Service Migration Checklist

### 1. Schema Migration
- [ ] Create `{service}_schemas.py` based on framework base classes
- [ ] Implement Create, Update, Response schemas
- [ ] Add validation rules and examples
- [ ] Test schema compatibility

### 2. Service Migration  
- [ ] Create `{service}_service.py` extending CompanyBusinessObjectService
- [ ] Implement business-specific methods
- [ ] Add bulk operations support
- [ ] Test service functionality

### 3. Router Migration
- [ ] Create `{service}_router.py` with framework patterns
- [ ] Maintain existing API compatibility
- [ ] Add framework endpoints (extensions, audit)
- [ ] Test API endpoints

### 4. Integration
- [ ] Update main application
- [ ] Add integration tests
- [ ] Deploy side-by-side
- [ ] Switch when ready

## Code Templates

### Schema Template
```python
from app.framework.schemas import CompanyBusinessObjectSchema, CreateSchemaBase, UpdateSchemaBase

class {Model}FrameworkBase(CompanyBusinessObjectSchema):
    # Add model fields here
    pass

class {Model}FrameworkCreate(CreateSchemaBase, {Model}FrameworkBase):
    company_id: int = Field(..., gt=0)

class {Model}FrameworkUpdate(UpdateSchemaBase):
    # All fields optional for updates
    pass

class {Model}FrameworkResponse({Model}FrameworkBase):
    id: int
    class Config:
        from_attributes = True
```

### Service Template
```python
from app.framework.services import CompanyBusinessObjectService

class {Model}FrameworkService(CompanyBusinessObjectService[{Model}]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, {Model})
    
    # Add business-specific methods here
```

### Router Template
```python
from app.framework.controllers import create_business_object_router

# Auto-generated router
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

Replace `{Model}`, `{service}`, and `{model_plural}` with appropriate values for your service.