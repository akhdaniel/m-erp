"""
Product API endpoints for inventory management.

Provides REST API endpoints for product catalog operations including
products, categories, variants, and product-related operations.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session

from inventory_module.models import Product, ProductCategory, ProductVariant, ProductType, ProductStatus
from inventory_module.services import ProductService, ProductCategoryService, ProductVariantService
from inventory_module.database import get_db

router = APIRouter(prefix="/products", tags=["products"])


# Pydantic schemas for request/response
class ProductCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    display_order: int = 0
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None
    slug: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class ProductCategoryResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    parent_category_id: Optional[int]
    display_order: int
    color: Optional[str]
    icon: Optional[str]
    slug: Optional[str]
    meta_title: Optional[str]
    meta_description: Optional[str]
    is_active: bool
    product_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    barcode: Optional[str] = Field(None, max_length=100)
    manufacturer_part_number: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None
    product_type: ProductType = ProductType.PHYSICAL
    status: ProductStatus = ProductStatus.ACTIVE
    list_price: Optional[Decimal] = Field(None, ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    currency_code: str = Field(default="USD", max_length=3)
    unit_of_measure: str = "each"
    weight: Optional[Decimal] = Field(None, ge=0)
    weight_unit: str = "kg"
    dimensions: Optional[Dict[str, Any]] = None
    track_inventory: bool = True
    minimum_stock_level: Optional[Decimal] = Field(None, ge=0)
    maximum_stock_level: Optional[Decimal] = Field(None, ge=0)
    reorder_point: Optional[Decimal] = Field(None, ge=0)
    reorder_quantity: Optional[Decimal] = Field(None, ge=0)
    lead_time_days: Optional[int] = Field(None, ge=0)
    primary_supplier_id: Optional[int] = None
    supplier_product_code: Optional[str] = Field(None, max_length=100)
    quality_control_required: bool = False
    hazardous_material: bool = False
    expiration_tracking: bool = False
    batch_tracking: bool = False
    serial_tracking: bool = False
    web_enabled: bool = False
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    primary_image: Optional[str] = None
    documents: Optional[List[str]] = None
    custom_attributes: Optional[Dict[str, Any]] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    barcode: Optional[str] = Field(None, max_length=100)
    manufacturer_part_number: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None
    status: Optional[ProductStatus] = None
    list_price: Optional[Decimal] = Field(None, ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    minimum_stock_level: Optional[Decimal] = Field(None, ge=0)
    maximum_stock_level: Optional[Decimal] = Field(None, ge=0)
    reorder_point: Optional[Decimal] = Field(None, ge=0)
    reorder_quantity: Optional[Decimal] = Field(None, ge=0)
    lead_time_days: Optional[int] = Field(None, ge=0)
    quality_control_required: Optional[bool] = None
    hazardous_material: Optional[bool] = None
    expiration_tracking: Optional[bool] = None
    batch_tracking: Optional[bool] = None
    serial_tracking: Optional[bool] = None
    web_enabled: Optional[bool] = None
    tags: Optional[List[str]] = None
    custom_attributes: Optional[Dict[str, Any]] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    description: Optional[str]
    short_description: Optional[str]
    barcode: Optional[str]
    manufacturer_part_number: Optional[str]
    category_id: Optional[int]
    product_type: ProductType
    status: ProductStatus
    list_price: Optional[Decimal]
    cost_price: Optional[Decimal]
    currency_code: str
    unit_of_measure: str
    weight: Optional[Decimal]
    weight_unit: Optional[str]
    dimensions: Optional[Dict[str, Any]]
    track_inventory: bool
    minimum_stock_level: Optional[Decimal]
    maximum_stock_level: Optional[Decimal]
    reorder_point: Optional[Decimal]
    reorder_quantity: Optional[Decimal]
    lead_time_days: Optional[int]
    primary_supplier_id: Optional[int]
    supplier_product_code: Optional[str]
    quality_control_required: bool
    hazardous_material: bool
    expiration_tracking: bool
    batch_tracking: bool
    serial_tracking: bool
    web_enabled: bool
    meta_title: Optional[str]
    meta_description: Optional[str]
    tags: Optional[List[str]]
    images: Optional[List[str]]
    primary_image: Optional[str]
    documents: Optional[List[str]]
    custom_attributes: Optional[Dict[str, Any]]
    is_active: bool
    discontinued_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductVariantCreate(BaseModel):
    parent_product_id: int
    variant_name: str = Field(..., min_length=1, max_length=255)
    sku: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    attributes: Dict[str, str] = Field(..., min_items=1)
    list_price: Optional[Decimal] = Field(None, ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    price_adjustment: Optional[Decimal] = Field(default=0)
    minimum_stock_level: Optional[Decimal] = Field(None, ge=0)
    maximum_stock_level: Optional[Decimal] = Field(None, ge=0)
    reorder_point: Optional[Decimal] = Field(None, ge=0)
    reorder_quantity: Optional[Decimal] = Field(None, ge=0)
    weight: Optional[Decimal] = Field(None, ge=0)
    dimensions: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    primary_image: Optional[str] = None


class ProductVariantResponse(BaseModel):
    id: int
    parent_product_id: int
    variant_name: str
    sku: str
    barcode: Optional[str]
    attributes: Dict[str, str]
    list_price: Optional[Decimal]
    cost_price: Optional[Decimal]
    price_adjustment: Optional[Decimal]
    minimum_stock_level: Optional[Decimal]
    maximum_stock_level: Optional[Decimal]
    reorder_point: Optional[Decimal]
    reorder_quantity: Optional[Decimal]
    weight: Optional[Decimal]
    dimensions: Optional[Dict[str, Any]]
    images: Optional[List[str]]
    primary_image: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Dependency injection
def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    # In production, would get user context from auth
    return ProductService(db_session=db, user_id=1, company_id=1)


def get_category_service(db: Session = Depends(get_db)) -> ProductCategoryService:
    return ProductCategoryService(db_session=db, user_id=1, company_id=1)


def get_variant_service(db: Session = Depends(get_db)) -> ProductVariantService:
    return ProductVariantService(db_session=db, user_id=1, company_id=1)


# Category endpoints
@router.post("/categories", response_model=ProductCategoryResponse, status_code=201)
async def create_category(
    category_data: ProductCategoryCreate,
    service: ProductCategoryService = Depends(get_category_service)
):
    """Create a new product category."""
    try:
        category = service.create_category(**category_data.dict())
        service.commit()
        return ProductCategoryResponse.from_orm(category)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories", response_model=List[ProductCategoryResponse])
async def list_categories(
    active_only: bool = Query(True, description="Filter active categories only"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of categories to return"),
    offset: int = Query(0, ge=0, description="Number of categories to skip"),
    service: ProductCategoryService = Depends(get_category_service)
):
    """List product categories."""
    categories = service.list_all(
        ProductCategory, 
        active_only=active_only,
        limit=limit,
        offset=offset,
        order_by="name"
    )
    return [ProductCategoryResponse.from_orm(cat) for cat in categories]


@router.get("/categories/tree", response_model=List[Dict[str, Any]])
async def get_category_tree(
    root_id: Optional[int] = Query(None, description="Root category ID (null for full tree)"),
    service: ProductCategoryService = Depends(get_category_service)
):
    """Get hierarchical category tree."""
    return service.get_category_tree(root_id)


@router.get("/categories/{category_id}", response_model=ProductCategoryResponse)
async def get_category(
    category_id: int = Path(..., description="Category ID"),
    service: ProductCategoryService = Depends(get_category_service)
):
    """Get category by ID."""
    category = service.get_by_id_or_raise(ProductCategory, category_id)
    return ProductCategoryResponse.from_orm(category)


@router.put("/categories/{category_id}", response_model=ProductCategoryResponse)
async def update_category(
    category_id: int = Path(..., description="Category ID"),
    category_data: ProductCategoryCreate = ...,
    service: ProductCategoryService = Depends(get_category_service)
):
    """Update category."""
    try:
        category = service.get_by_id_or_raise(ProductCategory, category_id)
        updated_category = service.update(category, category_data.dict(exclude_unset=True))
        service.commit()
        return ProductCategoryResponse.from_orm(updated_category)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(
    category_id: int = Path(..., description="Category ID"),
    hard_delete: bool = Query(False, description="Perform hard delete instead of soft delete"),
    service: ProductCategoryService = Depends(get_category_service)
):
    """Delete category."""
    try:
        category = service.get_by_id_or_raise(ProductCategory, category_id)
        service.delete(category, soft_delete=not hard_delete)
        service.commit()
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Product endpoints
@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    """Create a new product."""
    try:
        product = service.create_product(**product_data.dict())
        service.commit()
        return ProductResponse.from_orm(product)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    active_only: bool = Query(True, description="Filter active products only"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    product_type: Optional[ProductType] = Query(None, description="Filter by product type"),
    status: Optional[ProductStatus] = Query(None, description="Filter by product status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip"),
    service: ProductService = Depends(get_product_service)
):
    """List products with filtering."""
    if category_id:
        products = service.get_products_by_category(category_id, active_only=active_only)
    else:
        products = service.list_all(
            Product,
            active_only=active_only,
            limit=limit,
            offset=offset,
            order_by="name"
        )
    
    # Apply additional filters
    if product_type:
        products = [p for p in products if p.product_type == product_type]
    if status:
        products = [p for p in products if p.status == status]
    
    return [ProductResponse.from_orm(product) for product in products[:limit]]


@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    q: str = Query(..., min_length=1, description="Search term"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    product_type: Optional[ProductType] = Query(None, description="Filter by product type"),
    status: Optional[ProductStatus] = Query(None, description="Filter by product status"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    service: ProductService = Depends(get_product_service)
):
    """Search products."""
    products = service.search_products(
        search_term=q,
        category_id=category_id,
        product_type=product_type,
        status=status,
        limit=limit
    )
    return [ProductResponse.from_orm(product) for product in products]


@router.get("/low-stock", response_model=List[Dict[str, Any]])
async def get_low_stock_products(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    service: ProductService = Depends(get_product_service)
):
    """Get products with low stock levels."""
    return service.get_low_stock_products(limit=limit)


@router.get("/stats")
async def get_product_stats(
    service: ProductService = Depends(get_product_service),
    category_service: ProductCategoryService = Depends(get_category_service)
):
    """Get product statistics."""
    total = service.count_all(Product, active_only=False)
    active = service.count_all(Product, active_only=True)
    inactive = total - active
    categories = category_service.count_all(ProductCategory, active_only=False)
    
    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "categories": categories
    }


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int = Path(..., description="Product ID"),
    service: ProductService = Depends(get_product_service)
):
    """Get product by ID."""
    product = service.get_by_id_or_raise(Product, product_id)
    return ProductResponse.from_orm(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int = Path(..., description="Product ID"),
    product_data: ProductUpdate = ...,
    service: ProductService = Depends(get_product_service)
):
    """Update product."""
    try:
        product = service.get_by_id_or_raise(Product, product_id)
        updated_product = service.update(product, product_data.dict(exclude_unset=True))
        service.commit()
        return ProductResponse.from_orm(updated_product)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{product_id}/pricing")
async def update_product_pricing(
    product_id: int = Path(..., description="Product ID"),
    list_price: Optional[Decimal] = None,
    cost_price: Optional[Decimal] = None,
    service: ProductService = Depends(get_product_service)
):
    """Update product pricing."""
    try:
        product = service.update_product_pricing(product_id, list_price, cost_price)
        service.commit()
        return ProductResponse.from_orm(product)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{product_id}/discontinue", response_model=ProductResponse)
async def discontinue_product(
    product_id: int = Path(..., description="Product ID"),
    discontinuation_date: Optional[datetime] = None,
    service: ProductService = Depends(get_product_service)
):
    """Discontinue a product."""
    try:
        product = service.discontinue_product(product_id, discontinuation_date)
        service.commit()
        return ProductResponse.from_orm(product)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int = Path(..., description="Product ID"),
    hard_delete: bool = Query(False, description="Perform hard delete instead of soft delete"),
    service: ProductService = Depends(get_product_service)
):
    """Delete product."""
    try:
        product = service.get_by_id_or_raise(Product, product_id)
        service.delete(product, soft_delete=not hard_delete)
        service.commit()
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Product variant endpoints
@router.post("/{product_id}/variants", response_model=ProductVariantResponse, status_code=201)
async def create_variant(
    product_id: int = Path(..., description="Parent product ID"),
    variant_data: ProductVariantCreate = ...,
    service: ProductVariantService = Depends(get_variant_service)
):
    """Create a product variant."""
    try:
        variant_data_dict = variant_data.dict()
        variant_data_dict['parent_product_id'] = product_id
        variant = service.create_variant(**variant_data_dict)
        service.commit()
        return ProductVariantResponse.from_orm(variant)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{product_id}/variants", response_model=List[ProductVariantResponse])
async def list_product_variants(
    product_id: int = Path(..., description="Parent product ID"),
    active_only: bool = Query(True, description="Filter active variants only"),
    service: ProductVariantService = Depends(get_variant_service)
):
    """List variants for a product."""
    variants = service.get_product_variants(product_id, active_only=active_only)
    return [ProductVariantResponse.from_orm(variant) for variant in variants]


@router.get("/variants/{variant_id}", response_model=ProductVariantResponse)
async def get_variant(
    variant_id: int = Path(..., description="Variant ID"),
    service: ProductVariantService = Depends(get_variant_service)
):
    """Get variant by ID."""
    variant = service.get_by_id_or_raise(ProductVariant, variant_id)
    return ProductVariantResponse.from_orm(variant)


@router.put("/variants/{variant_id}/attributes", response_model=ProductVariantResponse)
async def update_variant_attributes(
    variant_id: int = Path(..., description="Variant ID"),
    attributes: Dict[str, str] = ...,
    service: ProductVariantService = Depends(get_variant_service)
):
    """Update variant attributes."""
    try:
        variant = service.update_variant_attributes(variant_id, attributes)
        service.commit()
        return ProductVariantResponse.from_orm(variant)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/variants/{variant_id}", status_code=204)
async def delete_variant(
    variant_id: int = Path(..., description="Variant ID"),
    hard_delete: bool = Query(False, description="Perform hard delete instead of soft delete"),
    service: ProductVariantService = Depends(get_variant_service)
):
    """Delete variant."""
    try:
        variant = service.get_by_id_or_raise(ProductVariant, variant_id)
        service.delete(variant, soft_delete=not hard_delete)
        service.commit()
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))