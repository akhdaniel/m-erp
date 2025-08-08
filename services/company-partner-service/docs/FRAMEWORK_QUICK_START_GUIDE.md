# Business Object Framework Quick Start Guide

## 🚀 Get Started in 15 Minutes

This guide will walk you through creating your first business object using the XERPIUM Business Object Framework. By the end, you'll have a fully functional business object with CRUD operations, audit logging, event publishing, and custom field support.

## 📋 Prerequisites

- Python 3.12+
- FastAPI project setup
- PostgreSQL database
- Redis for messaging
- Basic knowledge of SQLAlchemy and Pydantic

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install fastapi sqlalchemy pydantic redis asyncpg alembic
```

### 2. Framework Directory Structure

Ensure your project has this structure:

```
your_project/
├── app/
│   ├── framework/          # Framework components (already provided)
│   ├── models/            # Your business models
│   ├── schemas/           # Your Pydantic schemas  
│   ├── services/          # Your service classes
│   ├── routers/           # Your API routers
│   └── main.py           # FastAPI application
├── migrations/            # Alembic migrations
└── requirements.txt
```

## 📝 Step 1: Create Your Business Model

Let's create a simple `Product` business object.

### Create the Model

```python
# app/models/product.py
from sqlalchemy import Column, String, Text, Decimal, Boolean, Integer
from app.framework.base import CompanyBaseModel
from app.framework.mixins import BusinessObjectMixin, AuditableMixin, EventPublisherMixin

class Product(CompanyBaseModel, BusinessObjectMixin, AuditableMixin, EventPublisherMixin):
    """Product business object with framework capabilities"""
    
    __tablename__ = "products"
    
    # Business fields
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    sku = Column(String(100), nullable=False, unique=True, index=True)
    price = Column(Decimal(10, 2), nullable=False, default=0.00)
    category = Column(String(100), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"
```

### What the Mixins Provide

- **CompanyBaseModel**: Adds `id`, `company_id`, `created_at`, `updated_at`
- **BusinessObjectMixin**: Adds framework version tracking
- **AuditableMixin**: Enables automatic audit logging
- **EventPublisherMixin**: Enables automatic event publishing

## 📋 Step 2: Create Pydantic Schemas

### Define Your Schemas

```python
# app/schemas/product.py
from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import Field, validator
from app.framework.schemas import CompanyBusinessObjectSchema

class ProductBase(CompanyBusinessObjectSchema):
    """Base product schema with validation"""
    
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, max_length=1000, description="Product description")
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    price: Decimal = Field(..., ge=0, description="Product price")
    category: Optional[str] = Field(None, max_length=100, description="Product category")
    stock_quantity: int = Field(0, ge=0, description="Stock quantity")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Product name cannot be empty')
        return v.strip()
    
    @validator('sku')
    def validate_sku(cls, v):
        # SKU should be uppercase and alphanumeric
        cleaned_sku = v.strip().upper()
        if not cleaned_sku.replace('-', '').replace('_', '').isalnum():
            raise ValueError('SKU must be alphanumeric (hyphens and underscores allowed)')
        return cleaned_sku

class ProductCreate(ProductBase):
    """Schema for creating products"""
    pass

class ProductUpdate(ProductBase):
    """Schema for updating products - all fields optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0)

class ProductResponse(ProductBase):
    """Schema for product responses"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

## 🔧 Step 3: Create Your Service

### Implement the Service Class

```python
# app/services/product_service.py
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.framework.services import CompanyBusinessObjectService
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

class ProductService(CompanyBusinessObjectService[Product, ProductCreate, ProductUpdate]):
    """Product service with framework capabilities"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Product)
    
    # Basic CRUD operations (inherited from framework)
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        return await self.create(product_data.dict())
    
    async def get_product(self, product_id: int, company_id: int) -> Optional[Product]:
        """Get product by ID"""
        return await self.get_by_id(product_id, company_id)
    
    async def update_product(self, product_id: int, product_data: ProductUpdate, company_id: int) -> Optional[Product]:
        """Update product"""
        return await self.update(product_id, product_data.dict(exclude_unset=True), company_id)
    
    async def delete_product(self, product_id: int, company_id: int) -> bool:
        """Soft delete product"""
        return await self.soft_delete(product_id, company_id)
    
    async def list_products(self, company_id: int, skip: int = 0, limit: int = 100) -> List[Product]:
        """List products with pagination"""
        return await self.get_list(
            filters={"is_active": True},
            company_id=company_id,
            skip=skip,
            limit=limit
        )
    
    # Business-specific methods
    
    async def get_products_by_category(self, category: str, company_id: int) -> List[Product]:
        """Get products by category"""
        return await self.get_list(
            filters={"category": category, "is_active": True},
            company_id=company_id
        )
    
    async def update_stock(self, product_id: int, quantity_change: int, company_id: int) -> Optional[Product]:
        """Update product stock quantity"""
        product = await self.get_by_id(product_id, company_id)
        if not product:
            return None
        
        new_quantity = product.stock_quantity + quantity_change
        if new_quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        
        return await self.update(
            product_id, 
            {"stock_quantity": new_quantity}, 
            company_id
        )
    
    async def bulk_update_prices(self, price_updates: List[Dict[str, Any]], company_id: int) -> int:
        """Bulk update product prices"""
        updated_count = 0
        
        for update_data in price_updates:
            product_id = update_data["product_id"]
            new_price = update_data["price"]
            
            product = await self.update(
                product_id,
                {"price": new_price},
                company_id
            )
            
            if product:
                updated_count += 1
        
        return updated_count
```

## 🌐 Step 4: Create API Router

### Implement the Router

```python
# app/routers/products.py
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies import get_current_user, get_current_user_company
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])

# Dependency to get product service
def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(db)

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product_data: ProductCreate,
    company_id: int = Depends(get_current_user_company),
    service: ProductService = Depends(get_product_service)
):
    """Create a new product"""
    try:
        product = await service.create_product(product_data)
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of products to return"),
    category: str = Query(None, description="Filter by category"),
    company_id: int = Depends(get_current_user_company),
    service: ProductService = Depends(get_product_service)
):
    """List products with optional filtering"""
    if category:
        products = await service.get_products_by_category(category, company_id)
    else:
        products = await service.list_products(company_id, skip, limit)
    
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    company_id: int = Depends(get_current_user_company),
    service: ProductService = Depends(get_product_service)
):
    """Get product by ID"""
    product = await service.get_product(product_id, company_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    company_id: int = Depends(get_current_user_company),
    service: ProductService = Depends(get_product_service)
):
    """Update product"""
    try:
        product = await service.update_product(product_id, product_data, company_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    company_id: int = Depends(get_current_user_company),
    service: ProductService = Depends(get_product_service)
):
    """Delete product"""
    success = await service.delete_product(product_id, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")

@router.post("/{product_id}/stock", response_model=ProductResponse)
async def update_stock(
    product_id: int,
    quantity_change: int,
    company_id: int = Depends(get_current_user_company),
    service: ProductService = Depends(get_product_service)
):
    """Update product stock quantity"""
    try:
        product = await service.update_stock(product_id, quantity_change, company_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Framework-provided endpoints (automatically available)

@router.get("/{product_id}/extensions")
async def get_product_extensions(
    product_id: int,
    company_id: int = Depends(get_current_user_company),
    service: ProductService = Depends(get_product_service)
):
    """Get custom fields for product"""
    extensions = await service.get_extensions(product_id)
    return {"extensions": extensions}

@router.post("/{product_id}/extensions")
async def set_product_extension(
    product_id: int,
    field_name: str,
    field_type: str,
    field_value: str,
    company_id: int = Depends(get_current_user_company),
    service: ProductService = Depends(get_product_service)
):
    """Set custom field for product"""
    await service.set_extension(
        entity_id=product_id,
        field_name=field_name,
        field_type=field_type,
        field_value=field_value
    )
    return {"message": "Extension field set successfully"}

@router.get("/{product_id}/audit")
async def get_product_audit_trail(
    product_id: int,
    company_id: int = Depends(get_current_user_company),
    service: ProductService = Depends(get_product_service)
):
    """Get audit trail for product"""
    # This would integrate with your audit service
    # audit_entries = await service.get_audit_trail(product_id)
    return {"message": "Audit trail endpoint - integrate with audit service"}
```

## 🗄️ Step 5: Create Database Migration

### Generate Migration

```python
# migrations/versions/create_products_table.py
"""Create products table

Revision ID: 001_create_products
Revises: base
Create Date: 2025-08-01

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001_create_products'
down_revision = 'base'  # Update to your latest migration
branch_labels = None
depends_on = None

def upgrade():
    """Create products table"""
    op.create_table(
        'products',
        # Base model columns (from CompanyBaseModel)
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Business Object Framework columns (from BusinessObjectMixin)
        sa.Column('framework_version', sa.String(50), nullable=True),
        
        # Business-specific columns
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sku', sa.String(100), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('stock_quantity', sa.Integer(), nullable=False, default=0),
        
        # Primary key and constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.UniqueConstraint('sku'),
    )
    
    # Create indexes for performance
    op.create_index('ix_products_company_id', 'products', ['company_id'])
    op.create_index('ix_products_name', 'products', ['name'])
    op.create_index('ix_products_sku', 'products', ['sku'])
    op.create_index('ix_products_category', 'products', ['category'])
    op.create_index('ix_products_is_active', 'products', ['is_active'])

def downgrade():
    """Drop products table"""
    op.drop_table('products')
```

### Run Migration

```bash
# Generate migration
alembic revision --autogenerate -m "Create products table"

# Apply migration
alembic upgrade head
```

## 📱 Step 6: Integrate with FastAPI App

### Update Main Application

```python
# app/main.py
from fastapi import FastAPI
from app.routers import products
from app.core.database import init_db

app = FastAPI(
    title="XERPIUM Product Service",
    description="Product management with Business Object Framework",
    version="1.0.0"
)

# Include routers
app.include_router(products.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()

@app.get("/")
async def root():
    return {"message": "XERPIUM Product Service with Business Object Framework"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "framework": "business-object-framework"}
```

## 🧪 Step 7: Test Your Implementation

### Create a Simple Test

```python
# tests/test_products.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_product_crud():
    """Test complete product CRUD workflow"""
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        
        # 1. Create product
        product_data = {
            "name": "Test Product",
            "description": "A test product",
            "sku": "TEST-001",
            "price": "29.99",
            "category": "electronics",
            "stock_quantity": 100
        }
        
        create_response = await client.post(
            "/api/v1/products/",
            json=product_data,
            headers={"Authorization": "Bearer test-token"}  # Mock auth
        )
        assert create_response.status_code == 201
        product = create_response.json()
        
        # 2. Get product
        get_response = await client.get(
            f"/api/v1/products/{product['id']}",
            headers={"Authorization": "Bearer test-token"}
        )
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Test Product"
        
        # 3. Update product
        update_response = await client.put(
            f"/api/v1/products/{product['id']}",
            json={"price": "39.99"},
            headers={"Authorization": "Bearer test-token"}
        )
        assert update_response.status_code == 200
        assert float(update_response.json()["price"]) == 39.99
        
        # 4. List products
        list_response = await client.get(
            "/api/v1/products/",
            headers={"Authorization": "Bearer test-token"}
        )
        assert list_response.status_code == 200
        assert len(list_response.json()) >= 1

# Run test
# pytest tests/test_products.py -v
```

## 🎯 Step 8: Use Framework Features

### Add Custom Fields

```python
# Add custom field to a product
async def add_warranty_info():
    service = ProductService(db)
    
    # Add warranty period as custom field
    await service.set_extension(
        entity_id=1,  # Product ID
        field_name="warranty_months",
        field_type="integer",
        field_value="24",
        validation_rules=[
            {
                "validator_type": "range",
                "config": {"min_value": 0, "max_value": 120}
            }
        ]
    )
    
    # Add warranty type
    await service.set_extension(
        entity_id=1,
        field_name="warranty_type",
        field_type="string",
        field_value="manufacturer",
        validation_rules=[
            {
                "validator_type": "options",
                "config": {"valid_options": ["manufacturer", "extended", "third_party"]}
            }
        ]
    )
```

### Query with Custom Fields

```python
# Find products with warranty > 12 months
async def find_products_with_long_warranty():
    service = ProductService(db)
    
    products = await service.get_list(
        filters={"category": "electronics"},
        extension_filters={
            "warranty_months__gte": "12"
        },
        company_id=1
    )
    
    return products
```

### Get Audit Trail

```python
# Get audit trail for a product
async def get_product_history():
    service = ProductService(db)
    
    # Get complete audit trail
    audit_entries = await service.get_audit_trail(
        entity_id=1,  # Product ID
        entity_type="product"
    )
    
    for entry in audit_entries:
        print(f"Action: {entry.action}")
        print(f"Changes: {entry.changes}")
        print(f"Timestamp: {entry.timestamp}")
        print("---")
```

## 🚀 Step 9: Run Your Application

### Start the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Test Your API

```bash
# Create a product
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "name": "Awesome Widget",
    "description": "The best widget ever made",
    "sku": "AWG-001",
    "price": "49.99",
    "category": "widgets",
    "stock_quantity": 50
  }'

# Get all products
curl -X GET "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer your-token"

# Add custom field
curl -X POST "http://localhost:8000/api/v1/products/1/extensions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "field_name": "color",
    "field_type": "string", 
    "field_value": "blue"
  }'
```

## 🎉 Congratulations!

You've successfully created a complete business object with the XERPIUM Business Object Framework! Your `Product` business object now has:

### ✅ **Core Features**
- ✅ Full CRUD operations with automatic validation
- ✅ Multi-company data isolation 
- ✅ Automatic audit logging for all changes
- ✅ Event publishing to Redis Streams
- ✅ RESTful API with comprehensive endpoints

### ✅ **Advanced Features**  
- ✅ Custom field support without database changes
- ✅ Validation rules for custom fields
- ✅ Bulk operations for performance
- ✅ Audit trail retrieval
- ✅ Extension field management API

### ✅ **Developer Experience**
- ✅ Type-safe Pydantic schemas with validation
- ✅ Auto-generated API documentation
- ✅ Standardized error handling
- ✅ Consistent response formatting

## 🔄 Next Steps

### 1. **Explore Advanced Features**
- Add complex validation rules
- Implement custom event handlers
- Create business-specific API endpoints
- Add search and filtering capabilities

### 2. **Add More Business Objects**
- Use the same pattern for Orders, Customers, Suppliers
- Reference this Product implementation as a template
- Leverage framework services for rapid development

### 3. **Customize for Your Needs**
- Add business-specific validation rules
- Implement custom audit events
- Create specialized extension field types
- Add performance optimizations

### 4. **Scale and Deploy**
- Set up proper authentication and authorization
- Configure production database and Redis
- Implement monitoring and logging
- Deploy with Docker and orchestration

## 📚 Additional Resources

- **[Developer Guide](BUSINESS_OBJECT_FRAMEWORK_DEVELOPER_GUIDE.md)**: Comprehensive framework documentation
- **[Migration Guide](BUSINESS_OBJECT_MIGRATION_GUIDE.md)**: Converting existing services to the framework
- **[API Documentation](http://localhost:8000/docs)**: Auto-generated OpenAPI documentation
- **[Troubleshooting Guide](FRAMEWORK_TROUBLESHOOTING_GUIDE.md)**: Common issues and solutions

---

**🎯 Framework Features Used**: Base Models, Mixins, Schemas, Services, Controllers, Extensions, Audit Logging, Event Publishing  
**⏱️ Time to Complete**: ~15 minutes  
**🔧 Framework Version**: 1.0.0  
**📅 Last Updated**: 2025-08-01