# Service Development Tutorial

> **Step-by-Step Guide to Building Services in XERPIUM**
> 
> This tutorial walks you through creating a complete business service from scratch, following XERPIUM's established patterns and integrating with the existing infrastructure.

## 📋 What You'll Build

In this tutorial, we'll build a **Product Catalog Service** that demonstrates:
- Business Object Framework usage
- Multi-company data isolation
- Event-driven architecture
- REST API implementation
- Database integration
- Service registration

## Prerequisites

- XERPIUM development environment running
- Basic understanding of Python/FastAPI
- Familiarity with SQLAlchemy ORM
- PostgreSQL database access

## Step 1: Service Structure Setup

### 1.1 Create Service Directory

```bash
cd services/
mkdir product-catalog-service
cd product-catalog-service

# Create the standard service structure
mkdir -p {app/{core,models,schemas,routers,services,middleware},tests,migrations}
touch app/__init__.py app/main.py
```

### 1.2 Basic Service Files

**app/core/config.py**
```python
"""Configuration settings for Product Catalog Service."""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/xerpium_products"
    )
    
    # Service Configuration
    SERVICE_NAME: str = "product-catalog-service"
    SERVICE_HOST: str = os.getenv("SERVICE_HOST", "0.0.0.0")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8007"))
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Service Registry
    SERVICE_REGISTRY_URL: str = os.getenv(
        "SERVICE_REGISTRY_URL", 
        "http://localhost:8003"
    )
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**app/core/database.py**
```python
"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db_session():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**requirements.txt**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.0.3
redis==5.0.1
requests==2.31.0
pytest==7.4.3
pytest-asyncio==0.21.1
```

## Step 2: Implement Business Objects

### 2.1 Create Product Model

**app/models/product.py**
```python
"""Product model using Business Object Framework."""

from sqlalchemy import Column, String, Text, Decimal, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

# Import the Business Object Framework
# Note: In a real implementation, you'd copy the framework or import from shared package
from company_partner_service.app.framework.base import CompanyBusinessObject

class ProductCategory(CompanyBusinessObject):
    """Product category for organizing products."""
    
    __tablename__ = "product_categories"
    
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("product_categories.id"))
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    parent = relationship("ProductCategory", remote_side="ProductCategory.id")
    children = relationship("ProductCategory", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category")
    
    def __str__(self):
        return f"ProductCategory(name='{self.name}')"

class Product(CompanyBusinessObject):
    """Main product entity."""
    
    __tablename__ = "products"
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    sku = Column(String(100), nullable=False, index=True)  # Stock Keeping Unit
    barcode = Column(String(50), index=True)
    
    # Pricing
    list_price = Column(Decimal(10, 2), default=0.00)
    cost_price = Column(Decimal(10, 2), default=0.00)
    
    # Categorization
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_sellable = Column(Boolean, default=True, nullable=False)
    is_purchasable = Column(Boolean, default=True, nullable=False)
    
    # Inventory Settings
    track_inventory = Column(Boolean, default=True, nullable=False)
    minimum_stock = Column(Integer, default=0)
    maximum_stock = Column(Integer, default=0)
    
    # Relationships
    category = relationship("ProductCategory", back_populates="products")
    
    def __str__(self):
        return f"Product(sku='{self.sku}', name='{self.name}')"
    
    @property
    def margin_percentage(self):
        """Calculate margin percentage."""
        if self.cost_price and self.cost_price > 0:
            margin = self.list_price - self.cost_price
            return (margin / self.list_price) * 100
        return 0.0
```

### 2.2 Create Database Migration

**create_migration.py**
```python
"""Create Alembic migration for product tables."""

import subprocess
import sys
from datetime import datetime

def create_migration():
    """Create migration for product catalog tables."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    migration_name = f"create_product_catalog_tables"
    
    command = [
        "alembic", "revision", "--autogenerate", 
        "-m", migration_name
    ]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Migration created successfully!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error creating migration: {e}")
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    create_migration()
```

**alembic.ini**
```ini
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://user:password@localhost:5432/xerpium_products

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

## Step 3: Implement Service Layer

### 3.1 Business Logic Service

**app/services/product_service.py**
```python
"""Product business logic service."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from decimal import Decimal

from app.models.product import Product, ProductCategory
from app.core.database import get_db_session

class ProductService:
    """Service class for product business logic."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    # Category Management
    def create_category(self, category_data: Dict[str, Any], company_id: int) -> ProductCategory:
        """Create a new product category."""
        category = ProductCategory(
            company_id=company_id,
            **category_data
        )
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        # Publish event (would integrate with event system)
        self._publish_event("CATEGORY_CREATED", {
            "category_id": category.id,
            "company_id": company_id,
            "name": category.name
        })
        
        return category
    
    def get_categories(self, company_id: int, active_only: bool = True) -> List[ProductCategory]:
        """Get all categories for a company."""
        query = self.db.query(ProductCategory).filter(
            ProductCategory.company_id == company_id
        )
        
        if active_only:
            query = query.filter(ProductCategory.is_active == True)
        
        return query.order_by(ProductCategory.name).all()
    
    # Product Management
    def create_product(self, product_data: Dict[str, Any], company_id: int) -> Product:
        """Create a new product."""
        
        # Validate SKU uniqueness within company
        existing_product = self.db.query(Product).filter(
            and_(
                Product.company_id == company_id,
                Product.sku == product_data.get('sku')
            )
        ).first()
        
        if existing_product:
            raise ValueError(f"Product with SKU '{product_data['sku']}' already exists")
        
        product = Product(
            company_id=company_id,
            **product_data
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        # Publish event
        self._publish_event("PRODUCT_CREATED", {
            "product_id": product.id,
            "company_id": company_id,
            "sku": product.sku,
            "name": product.name
        })
        
        return product
    
    def get_products(self, 
                    company_id: int, 
                    category_id: Optional[int] = None,
                    active_only: bool = True,
                    search_term: Optional[str] = None) -> List[Product]:
        """Get products with optional filtering."""
        
        query = self.db.query(Product).filter(Product.company_id == company_id)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if active_only:
            query = query.filter(Product.is_active == True)
        
        if search_term:
            search_filter = or_(
                Product.name.ilike(f"%{search_term}%"),
                Product.sku.ilike(f"%{search_term}%"),
                Product.description.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter)
        
        return query.order_by(Product.name).all()
    
    def get_product_by_id(self, product_id: int, company_id: int) -> Optional[Product]:
        """Get product by ID."""
        return self.db.query(Product).filter(
            and_(
                Product.id == product_id,
                Product.company_id == company_id
            )
        ).first()
    
    def get_product_by_sku(self, sku: str, company_id: int) -> Optional[Product]:
        """Get product by SKU."""
        return self.db.query(Product).filter(
            and_(
                Product.sku == sku,
                Product.company_id == company_id
            )
        ).first()
    
    def update_product(self, product_id: int, update_data: Dict[str, Any], company_id: int) -> Product:
        """Update an existing product."""
        
        product = self.get_product_by_id(product_id, company_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Store original state for events
        original_data = {
            "sku": product.sku,
            "name": product.name,
            "list_price": product.list_price
        }
        
        # Update fields
        for field, value in update_data.items():
            if hasattr(product, field):
                setattr(product, field, value)
        
        self.db.commit()
        self.db.refresh(product)
        
        # Publish event
        self._publish_event("PRODUCT_UPDATED", {
            "product_id": product.id,
            "company_id": company_id,
            "original_data": original_data,
            "updated_fields": list(update_data.keys())
        })
        
        return product
    
    def deactivate_product(self, product_id: int, company_id: int) -> bool:
        """Deactivate a product instead of deleting."""
        product = self.get_product_by_id(product_id, company_id)
        if not product:
            return False
        
        product.is_active = False
        self.db.commit()
        
        self._publish_event("PRODUCT_DEACTIVATED", {
            "product_id": product.id,
            "company_id": company_id,
            "sku": product.sku
        })
        
        return True
    
    # Business Logic Methods
    def calculate_margin(self, product_id: int, company_id: int) -> Dict[str, Any]:
        """Calculate product margin details."""
        product = self.get_product_by_id(product_id, company_id)
        if not product:
            raise ValueError("Product not found")
        
        margin_amount = product.list_price - product.cost_price
        margin_percentage = product.margin_percentage
        
        return {
            "product_id": product.id,
            "sku": product.sku,
            "list_price": product.list_price,
            "cost_price": product.cost_price,
            "margin_amount": margin_amount,
            "margin_percentage": margin_percentage
        }
    
    def bulk_update_prices(self, price_updates: List[Dict[str, Any]], company_id: int) -> Dict[str, Any]:
        """Bulk update product prices."""
        updated_count = 0
        errors = []
        
        for update in price_updates:
            try:
                product_id = update['product_id']
                new_price = update['list_price']
                
                product = self.get_product_by_id(product_id, company_id)
                if product:
                    product.list_price = Decimal(str(new_price))
                    updated_count += 1
                else:
                    errors.append(f"Product ID {product_id} not found")
                    
            except Exception as e:
                errors.append(f"Error updating product {update.get('product_id', 'unknown')}: {str(e)}")
        
        if updated_count > 0:
            self.db.commit()
        
        return {
            "updated_count": updated_count,
            "errors": errors,
            "total_attempted": len(price_updates)
        }
    
    def _publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """Publish event to message bus (placeholder for actual implementation)."""
        # In real implementation, would use Redis Streams or message publisher
        print(f"EVENT: {event_type} - {event_data}")
```

## Step 4: Create API Schemas

### 4.1 Pydantic Schemas

**app/schemas/product.py**
```python
"""Pydantic schemas for product API validation."""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator

# Category Schemas
class ProductCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None

class ProductCategoryResponse(ProductCategoryBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sku: str = Field(..., min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=50)
    list_price: Decimal = Field(default=Decimal('0.00'), ge=0)
    cost_price: Decimal = Field(default=Decimal('0.00'), ge=0)
    category_id: Optional[int] = None
    is_active: bool = True
    is_sellable: bool = True
    is_purchasable: bool = True
    track_inventory: bool = True
    minimum_stock: int = Field(default=0, ge=0)
    maximum_stock: int = Field(default=0, ge=0)

class ProductCreate(ProductBase):
    @validator('maximum_stock')
    def validate_stock_levels(cls, v, values):
        if 'minimum_stock' in values and v > 0 and v < values['minimum_stock']:
            raise ValueError('Maximum stock must be greater than minimum stock')
        return v

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=50)
    list_price: Optional[Decimal] = Field(None, ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    category_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_sellable: Optional[bool] = None
    is_purchasable: Optional[bool] = None
    track_inventory: Optional[bool] = None
    minimum_stock: Optional[int] = Field(None, ge=0)
    maximum_stock: Optional[int] = Field(None, ge=0)

class ProductResponse(ProductBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    margin_percentage: float
    category: Optional[ProductCategoryResponse] = None
    
    class Config:
        from_attributes = True

# List and Pagination Schemas
class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    per_page: int
    pages: int

class CategoryListResponse(BaseModel):
    categories: List[ProductCategoryResponse]
    total: int

# Business Logic Schemas
class MarginCalculationResponse(BaseModel):
    product_id: int
    sku: str
    list_price: Decimal
    cost_price: Decimal
    margin_amount: Decimal
    margin_percentage: float

class BulkPriceUpdate(BaseModel):
    updates: List[Dict[str, Any]] = Field(..., min_items=1)

class BulkUpdateResponse(BaseModel):
    updated_count: int
    errors: List[str]
    total_attempted: int
    success_rate: float

    @validator('success_rate', always=True)
    def calculate_success_rate(cls, v, values):
        if 'total_attempted' in values and values['total_attempted'] > 0:
            return (values.get('updated_count', 0) / values['total_attempted']) * 100
        return 0.0

# Search and Filter Schemas
class ProductSearchParams(BaseModel):
    search_term: Optional[str] = None
    category_id: Optional[int] = None
    is_active: bool = True
    is_sellable: Optional[bool] = None
    is_purchasable: Optional[bool] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=100)
```

## Step 5: Implement REST API

### 5.1 API Router

**app/routers/products.py**
```python
"""Product API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.services.product_service import ProductService
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryResponse, CategoryListResponse,
    MarginCalculationResponse, BulkPriceUpdate, BulkUpdateResponse,
    ProductSearchParams
)

router = APIRouter(prefix="/api/v1", tags=["products"])

# Dependencies
def get_product_service(db: Session = Depends(get_db_session)) -> ProductService:
    """Get product service instance."""
    return ProductService(db_session=db)

def get_current_company_id() -> int:
    """Get current company ID (in production, from JWT token)."""
    # Placeholder - would extract from authentication token
    return 1

# Category Endpoints
@router.post("/categories/", response_model=ProductCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: ProductCategoryCreate,
    company_id: int = Depends(get_current_company_id),
    service: ProductService = Depends(get_product_service)
):
    """Create a new product category."""
    try:
        category = service.create_category(
            category_data.model_dump(), 
            company_id
        )
        return category
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/categories/", response_model=CategoryListResponse)
async def get_categories(
    active_only: bool = Query(True, description="Filter active categories only"),
    company_id: int = Depends(get_current_company_id),
    service: ProductService = Depends(get_product_service)
):
    """Get all product categories."""
    categories = service.get_categories(company_id, active_only)
    return {
        "categories": categories,
        "total": len(categories)
    }

# Product Endpoints
@router.post("/products/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    company_id: int = Depends(get_current_company_id),
    service: ProductService = Depends(get_product_service)
):
    """Create a new product."""
    try:
        product = service.create_product(
            product_data.model_dump(), 
            company_id
        )
        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/products/", response_model=List[ProductResponse])
async def get_products(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    active_only: bool = Query(True, description="Filter active products only"),
    search_term: Optional[str] = Query(None, description="Search in name, SKU, description"),
    company_id: int = Depends(get_current_company_id),
    service: ProductService = Depends(get_product_service)
):
    """Get products with optional filtering."""
    products = service.get_products(
        company_id=company_id,
        category_id=category_id,
        active_only=active_only,
        search_term=search_term
    )
    return products

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int = Path(..., gt=0),
    company_id: int = Depends(get_current_company_id),
    service: ProductService = Depends(get_product_service)
):
    """Get product by ID."""
    product = service.get_product_by_id(product_id, company_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return product

@router.get("/products/by-sku/{sku}", response_model=ProductResponse)
async def get_product_by_sku(
    sku: str = Path(..., min_length=1),
    company_id: int = Depends(get_current_company_id),
    service: ProductService = Depends(get_product_service)
):
    """Get product by SKU."""
    product = service.get_product_by_sku(sku, company_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU '{sku}' not found"
        )
    return product

@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int = Path(..., gt=0),
    update_data: ProductUpdate = ...,
    company_id: int = Depends(get_current_company_id),
    service: ProductService = Depends(get_product_service)
):
    """Update an existing product."""
    try:
        # Filter out None values
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid update data provided"
            )
        
        product = service.update_product(product_id, update_dict, company_id)
        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_product(
    product_id: int = Path(..., gt=0),
    company_id: int = Depends(get_current_company_id),
    service: ProductService = Depends(get_product_service)
):
    """Deactivate a product (soft delete)."""
    success = service.deactivate_product(product_id, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

# Business Logic Endpoints
@router.get("/products/{product_id}/margin", response_model=MarginCalculationResponse)
async def calculate_product_margin(
    product_id: int = Path(..., gt=0),
    company_id: int = Depends(get_current_company_id),
    service: ProductService = Depends(get_product_service)
):
    """Calculate margin for a specific product."""
    try:
        margin_data = service.calculate_margin(product_id, company_id)
        return margin_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/products/bulk-price-update", response_model=BulkUpdateResponse)
async def bulk_update_prices(
    bulk_update: BulkPriceUpdate,
    company_id: int = Depends(get_current_company_id),
    service: ProductService = Depends(get_product_service)
):
    """Bulk update product prices."""
    result = service.bulk_update_prices(bulk_update.updates, company_id)
    return result

# Health Check
@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Service health check."""
    return {"status": "healthy", "service": "product-catalog-service"}
```

## Step 6: Main Application

### 6.1 FastAPI App

**app/main.py**
```python
"""Main FastAPI application for Product Catalog Service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.routers import products
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="XERPIUM Product Catalog Service",
    description="Product and category management service for XERPIUM ERP platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router)

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    logger.info(f"Starting {settings.SERVICE_NAME}")
    logger.info(f"Service running on {settings.SERVICE_HOST}:{settings.SERVICE_PORT}")
    
    # Register with service registry (in production)
    # await register_service()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info(f"Shutting down {settings.SERVICE_NAME}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=True
    )
```

## Step 7: Testing

### 7.1 Basic Tests

**tests/test_product_service.py**
```python
"""Tests for product service."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.product_service import ProductService
from app.models.product import Product, ProductCategory

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def product_service(db_session):
    """Create product service with test database."""
    return ProductService(db_session)

def test_create_category(product_service):
    """Test category creation."""
    category_data = {
        "name": "Electronics",
        "description": "Electronic products"
    }
    
    category = product_service.create_category(category_data, company_id=1)
    
    assert category.name == "Electronics"
    assert category.company_id == 1
    assert category.id is not None

def test_create_product(product_service):
    """Test product creation."""
    product_data = {
        "name": "iPhone 15",
        "sku": "IPHONE15-128",
        "list_price": 999.99,
        "cost_price": 800.00
    }
    
    product = product_service.create_product(product_data, company_id=1)
    
    assert product.name == "iPhone 15"
    assert product.sku == "IPHONE15-128"
    assert product.company_id == 1

def test_duplicate_sku_validation(product_service):
    """Test SKU uniqueness validation."""
    product_data = {
        "name": "Product 1",
        "sku": "TEST-SKU",
        "list_price": 100.00
    }
    
    # Create first product
    product_service.create_product(product_data, company_id=1)
    
    # Try to create duplicate SKU
    with pytest.raises(ValueError, match="already exists"):
        product_service.create_product(product_data, company_id=1)

def test_margin_calculation(product_service):
    """Test product margin calculation."""
    product_data = {
        "name": "Test Product",
        "sku": "MARGIN-TEST",
        "list_price": 100.00,
        "cost_price": 75.00
    }
    
    product = product_service.create_product(product_data, company_id=1)
    margin_data = product_service.calculate_margin(product.id, company_id=1)
    
    assert margin_data["margin_amount"] == 25.00
    assert margin_data["margin_percentage"] == 25.0
```

## Step 8: Docker Integration

### 8.1 Dockerfile

**Dockerfile**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8007

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8007/health || exit 1

# Run application
CMD ["python", "-m", "app.main"]
```

### 8.2 Add to Docker Compose

Update the main `docker-compose.yml`:

```yaml
services:
  # ... existing services ...
  
  product-catalog-service:
    build: ./services/product-catalog-service
    container_name: xerpium-product-catalog
    ports:
      - "8007:8007"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/xerpium_products
      - REDIS_URL=redis://redis:6379/0
      - SERVICE_REGISTRY_URL=http://service-registry:8003
    depends_on:
      - postgres
      - redis
      - service-registry
    networks:
      - xerpium-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8007/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Step 9: Integration with XERPIUM

### 9.1 Service Registration

**service_registration.py**
```python
"""Register service with XERPIUM service registry."""

import asyncio
import aiohttp
from app.core.config import settings

async def register_service():
    """Register this service with the service registry."""
    service_info = {
        "name": settings.SERVICE_NAME,
        "version": "1.0.0",
        "host": settings.SERVICE_HOST,
        "port": settings.SERVICE_PORT,
        "health_check_url": f"http://{settings.SERVICE_HOST}:{settings.SERVICE_PORT}/health",
        "api_docs_url": f"http://{settings.SERVICE_HOST}:{settings.SERVICE_PORT}/api/docs",
        "tags": ["products", "catalog", "inventory"]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.SERVICE_REGISTRY_URL}/register",
                json=service_info
            ) as response:
                if response.status == 200:
                    print(f"Successfully registered {settings.SERVICE_NAME}")
                else:
                    print(f"Failed to register service: {response.status}")
    except Exception as e:
        print(f"Service registration failed: {e}")
```

### 9.2 Menu Integration

**menu_integration.py**
```python
"""Register menu items with XERPIUM menu system."""

import requests
from app.core.config import settings

def register_menu_items():
    """Register this service's menu items."""
    
    menu_items = [
        {
            "name": "Product Catalog",
            "path": "/products",
            "icon": "package",
            "parent_id": None,
            "order_number": 100,
            "required_permissions": ["catalog.view"]
        },
        {
            "name": "Products",
            "path": "/products/list",
            "icon": "box",
            "parent_name": "Product Catalog",
            "order_number": 1,
            "required_permissions": ["product.view"]
        },
        {
            "name": "Categories",
            "path": "/products/categories",
            "icon": "folder",
            "parent_name": "Product Catalog",
            "order_number": 2,
            "required_permissions": ["category.view"]
        }
    ]
    
    menu_service_url = "http://menu-access-service:8004"
    
    for item in menu_items:
        try:
            response = requests.post(
                f"{menu_service_url}/api/v1/menu-items/",
                json=item,
                timeout=5
            )
            if response.status_code == 201:
                print(f"Registered menu item: {item['name']}")
            else:
                print(f"Failed to register menu item {item['name']}: {response.status_code}")
        except Exception as e:
            print(f"Menu registration error for {item['name']}: {e}")
```

## Step 10: Testing Integration

### 10.1 Test the Service

```bash
# Start the service
cd services/product-catalog-service
python -m app.main

# Test API endpoints
curl -X GET http://localhost:8007/health
curl -X GET http://localhost:8007/api/docs

# Create a category
curl -X POST http://localhost:8007/api/v1/categories/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electronics",
    "description": "Electronic products"
  }'

# Create a product
curl -X POST http://localhost:8007/api/v1/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone 15",
    "sku": "IPHONE15-128",
    "list_price": 999.99,
    "cost_price": 800.00,
    "category_id": 1
  }'

# Test margin calculation
curl -X GET http://localhost:8007/api/v1/products/1/margin
```

## 🎉 Congratulations!

You've successfully built a complete XERPIUM service that includes:

✅ **Business Object Framework Integration**  
✅ **Multi-Company Data Isolation**  
✅ **RESTful API with Validation**  
✅ **Event-Driven Architecture**  
✅ **Comprehensive Testing**  
✅ **Docker Integration**  
✅ **Service Registration**  

## Next Steps

1. **Add Event Publishing**: Integrate with Redis Streams for event-driven communication
2. **Enhance UI Integration**: Create Vue.js components for the admin interface  
3. **Add Advanced Features**: Implement search, bulk operations, and reporting
4. **Security Enhancement**: Add JWT authentication and authorization
5. **Performance Optimization**: Add caching and query optimization

## Key Takeaways

- **Framework Usage**: The Business Object Framework significantly reduces development time
- **Multi-Company Design**: Always design with multi-tenancy from the start
- **Event-Driven Communication**: Services communicate through events, not direct calls
- **API Standards**: Follow consistent patterns across all endpoints
- **Testing Strategy**: Test business logic, API endpoints, and integration points

This tutorial demonstrated the complete XERPIUM development workflow. Use these patterns as templates for building additional services in the platform.