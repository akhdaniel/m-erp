"""
Product API endpoints for Sales Service.

Provides product search and lookup functionality for quotes and orders,
integrating with the inventory service to retrieve product information.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import JSONResponse
import httpx
import logging
from pydantic import BaseModel
from decimal import Decimal

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1/products", tags=["products"])


# Response models
class ProductSearchItem(BaseModel):
    """Product search result item."""
    id: int
    sku: str
    name: str
    description: Optional[str]
    category: Optional[str]
    list_price: Decimal
    cost_price: Optional[Decimal]
    unit_of_measure: str
    is_active: bool
    stock_on_hand: Optional[int] = 0
    stock_available: Optional[int] = 0


class ProductSearchResponse(BaseModel):
    """Product search response."""
    items: List[ProductSearchItem]
    total: int
    page: int
    page_size: int


# Inventory service URL (would be from config in production)
INVENTORY_SERVICE_URL = "http://inventory-service:8005"


async def fetch_from_inventory(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Fetch data from inventory service."""
    async with httpx.AsyncClient() as client:
        try:
            url = f"{INVENTORY_SERVICE_URL}{endpoint}"
            response = await client.get(url, params=params, timeout=10.0)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Inventory service returned {response.status_code}: {response.text}")
                return None
                
        except httpx.RequestError as e:
            logger.error(f"Error calling inventory service: {e}")
            return None


# IMPORTANT: Specific routes must be defined before the generic /{product_id} route

@router.get("/health/")
async def health_check():
    """Product API health check."""
    return {
        "status": "healthy",
        "service": "sales-products-api",
        "inventory_service": INVENTORY_SERVICE_URL
    }


@router.get("/search/", response_model=ProductSearchResponse)
async def search_products(
    q: Optional[str] = Query(None, description="Search query for product name or SKU"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    active_only: bool = Query(True, description="Only return active products"),
    with_stock: bool = Query(False, description="Only return products with available stock"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Search for products with filtering and pagination.
    
    Returns products matching the search criteria along with basic stock information.
    Integrates with the inventory service to retrieve product and stock data.
    """
    try:
        # Build parameters for inventory service
        # Note: Inventory service might not support all parameters
        params = {}
        
        if q:
            params["search"] = q
        if category_id:
            params["category_id"] = category_id
            
        # Fetch products from inventory service
        products_data = await fetch_from_inventory("/api/v1/products/", params)
        
        if not products_data:
            # Return empty result if inventory service is unavailable
            return ProductSearchResponse(
                items=[],
                total=0,
                page=page,
                page_size=page_size
            )
        
        # Process products and fetch stock levels if needed
        items = []
        # Handle both array and object response formats
        products_list = products_data if isinstance(products_data, list) else products_data.get("items", [])
        
        # Apply manual pagination for array responses
        if isinstance(products_data, list):
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            products_list = products_list[start_idx:end_idx]
        
        for product in products_list:
            # Fetch stock summary for each product if requested
            stock_info = {"on_hand": 0, "available": 0}
            if with_stock:
                stock_data = await fetch_from_inventory(f"/api/v1/stock/summary/product/{product['id']}")
                if stock_data:
                    stock_info = {
                        "on_hand": stock_data.get("total_on_hand", 0),
                        "available": stock_data.get("total_available", 0)
                    }
                    
                    # Skip if no stock available and with_stock filter is on
                    if stock_info["available"] <= 0:
                        continue
            
            items.append(ProductSearchItem(
                id=product["id"],
                sku=product.get("sku", ""),
                name=product["name"],
                description=product.get("description"),
                category=product.get("category_name"),
                list_price=Decimal(str(product.get("list_price", 0))),
                cost_price=Decimal(str(product.get("cost_price", 0))) if product.get("cost_price") else None,
                unit_of_measure=product.get("unit_of_measure", "unit"),
                is_active=product.get("is_active", True),
                stock_on_hand=stock_info["on_hand"],
                stock_available=stock_info["available"]
            ))
        
        # Determine total count  
        if isinstance(products_data, list):
            total = len(products_data)  # Total before pagination
        else:
            total = products_data.get("total", len(items))
        
        return ProductSearchResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search products"
        )


@router.get("/autocomplete/", response_model=List[Dict[str, Any]])
async def autocomplete_products(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results to return")
):
    """
    Autocomplete endpoint for product selection dropdowns.
    
    Returns a simplified list of products for quick selection in forms.
    Optimized for performance with minimal data returned.
    """
    try:
        # Fetch products from inventory service
        # For now, get all products and filter locally
        products_data = await fetch_from_inventory("/api/v1/products/", {})
        
        if not products_data:
            return []
        
        # Return simplified product data for autocomplete
        results = []
        # Handle both array and object response formats
        products_list = products_data if isinstance(products_data, list) else products_data.get("items", [])
        
        # Filter products by search query (case-insensitive)
        q_lower = q.lower()
        filtered_products = []
        for product in products_list:
            if (q_lower in product.get("name", "").lower() or 
                q_lower in product.get("sku", "").lower() or
                q_lower in product.get("description", "").lower()):
                filtered_products.append(product)
                if len(filtered_products) >= limit:
                    break
        
        for product in filtered_products:
            results.append({
                "id": product["id"],
                "sku": product.get("sku", ""),
                "name": product["name"],
                "display": f"{product.get('sku', '')} - {product['name']}",
                "price": float(product.get("list_price", 0)),
                "unit": product.get("unit_of_measure", "unit")
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Error in product autocomplete: {e}")
        return []


@router.get("/categories/", response_model=List[Dict[str, Any]])
async def get_product_categories():
    """
    Get all product categories for filtering.
    
    Returns hierarchical category structure from inventory service.
    """
    try:
        # Fetch categories from inventory service
        categories_data = await fetch_from_inventory("/api/v1/products/categories")
        
        if not categories_data:
            return []
        
        return categories_data
        
    except Exception as e:
        logger.error(f"Error fetching product categories: {e}")
        return []


# Generic route - must be last as it captures all paths
@router.get("/{product_id}", response_model=ProductSearchItem)
async def get_product_details(
    product_id: int,
    with_stock: bool = Query(True, description="Include stock information")
):
    """
    Get detailed information for a specific product.
    
    Returns product details including pricing and optionally stock levels.
    """
    try:
        # Fetch product from inventory service
        product_data = await fetch_from_inventory(f"/api/v1/products/{product_id}")
        
        if not product_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found"
            )
        
        # Fetch stock summary if requested
        stock_info = {"on_hand": 0, "available": 0}
        if with_stock:
            stock_data = await fetch_from_inventory(f"/api/v1/stock/summary/product/{product_id}")
            if stock_data:
                stock_info = {
                    "on_hand": stock_data.get("total_on_hand", 0),
                    "available": stock_data.get("total_available", 0)
                }
        
        return ProductSearchItem(
            id=product_data["id"],
            sku=product_data.get("sku", ""),
            name=product_data["name"],
            description=product_data.get("description"),
            category=product_data.get("category_name"),
            list_price=Decimal(str(product_data.get("list_price", 0))),
            cost_price=Decimal(str(product_data.get("cost_price", 0))) if product_data.get("cost_price") else None,
            unit_of_measure=product_data.get("unit_of_measure", "unit"),
            is_active=product_data.get("is_active", True),
            stock_on_hand=stock_info["on_hand"],
            stock_available=stock_info["available"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get product details"
        )