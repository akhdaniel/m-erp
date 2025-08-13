"""
Supplier API endpoints for purchasing module.

Provides comprehensive REST API for supplier management including
CRUD operations, performance tracking, and evaluation.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status, Body
from decimal import Decimal
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1/suppliers", tags=["suppliers"])

# In-memory storage for demo purposes
mock_suppliers_db = []
next_supplier_id = 1

# Dependencies
def get_current_user_id() -> int:
    """Get current user ID from authentication."""
    return 1

def get_current_company_id() -> int:
    """Get current company ID from context."""
    return 1


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_supplier(
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Create new supplier.
    
    Creates a supplier with contact information and initial performance metrics.
    """
    global next_supplier_id
    
    try:
        supplier_id = next_supplier_id
        next_supplier_id += 1
        
        supplier = {
            "id": supplier_id,
            "code": request.get('code', f"SUP-{supplier_id:05d}"),
            "name": request.get('name'),
            "legal_name": request.get('legal_name'),
            "tax_id": request.get('tax_id'),
            "status": request.get('status', 'active'),
            "category": request.get('category', 'general'),
            "contact_person": request.get('contact_person'),
            "email": request.get('email'),
            "phone": request.get('phone'),
            "website": request.get('website'),
            "address": request.get('address'),
            "city": request.get('city'),
            "state": request.get('state'),
            "country": request.get('country'),
            "postal_code": request.get('postal_code'),
            "payment_terms": request.get('payment_terms', 'Net 30'),
            "currency_code": request.get('currency_code', 'USD'),
            "credit_limit": request.get('credit_limit'),
            "performance_rating": 5.0,
            "delivery_rating": 5.0,
            "quality_rating": 5.0,
            "price_rating": 5.0,
            "communication_rating": 5.0,
            "total_orders": 0,
            "total_spend": "0.00",
            "notes": request.get('notes'),
            "tags": request.get('tags', []),
            "company_id": company_id,
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": None
        }
        
        mock_suppliers_db.append(supplier)
        return supplier
        
    except Exception as e:
        logger.error(f"Error creating supplier: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("")
@router.get("/")
async def list_suppliers(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_rating: Optional[float] = Query(None, ge=1, le=5, description="Minimum performance rating"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    company_id: int = Depends(get_current_company_id)
):
    """
    List suppliers with filtering and pagination.
    
    Returns paginated list of suppliers with optional filters.
    """
    try:
        # Filter suppliers
        filtered_suppliers = [
            s for s in mock_suppliers_db
            if s.get('company_id') == company_id
        ]
        
        if status:
            filtered_suppliers = [s for s in filtered_suppliers if s.get('status') == status]
        
        if category:
            filtered_suppliers = [s for s in filtered_suppliers if s.get('category') == category]
        
        if min_rating:
            filtered_suppliers = [
                s for s in filtered_suppliers 
                if s.get('performance_rating', 0) >= min_rating
            ]
        
        # Sort by name
        filtered_suppliers.sort(key=lambda x: x.get('name', ''))
        
        # Pagination
        total_count = len(filtered_suppliers)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_suppliers = filtered_suppliers[start_idx:end_idx]
        
        return {
            "data": paginated_suppliers,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }
        
    except Exception as e:
        logger.error(f"Error listing suppliers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: int = Path(..., gt=0, description="Supplier ID"),
    company_id: int = Depends(get_current_company_id)
):
    """Get supplier by ID."""
    try:
        for supplier in mock_suppliers_db:
            if supplier.get('id') == supplier_id and supplier.get('company_id') == company_id:
                return supplier
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting supplier: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{supplier_id}")
async def update_supplier(
    supplier_id: int = Path(..., gt=0, description="Supplier ID"),
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """Update supplier information."""
    try:
        for i, supplier in enumerate(mock_suppliers_db):
            if supplier.get('id') == supplier_id and supplier.get('company_id') == company_id:
                # Update fields
                for key, value in request.items():
                    if key not in ['id', 'company_id', 'created_at', 'created_by']:
                        supplier[key] = value
                
                supplier['updated_at'] = datetime.utcnow().isoformat()
                supplier['updated_by'] = user_id
                
                mock_suppliers_db[i] = supplier
                return supplier
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating supplier: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{supplier_id}/performance")
async def get_supplier_performance(
    supplier_id: int = Path(..., gt=0, description="Supplier ID"),
    company_id: int = Depends(get_current_company_id)
):
    """Get supplier performance metrics."""
    try:
        for supplier in mock_suppliers_db:
            if supplier.get('id') == supplier_id and supplier.get('company_id') == company_id:
                return {
                    "supplier_id": supplier_id,
                    "supplier_name": supplier.get('name'),
                    "overall_rating": supplier.get('performance_rating', 5.0),
                    "ratings": {
                        "delivery": supplier.get('delivery_rating', 5.0),
                        "quality": supplier.get('quality_rating', 5.0),
                        "price": supplier.get('price_rating', 5.0),
                        "communication": supplier.get('communication_rating', 5.0)
                    },
                    "statistics": {
                        "total_orders": supplier.get('total_orders', 0),
                        "completed_orders": supplier.get('completed_orders', 0),
                        "on_time_deliveries": supplier.get('on_time_deliveries', 0),
                        "quality_issues": supplier.get('quality_issues', 0),
                        "total_spend": supplier.get('total_spend', "0.00")
                    },
                    "last_evaluation": supplier.get('last_evaluation'),
                    "trend": "stable"  # Would calculate from historical data
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting supplier performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{supplier_id}/evaluate")
async def evaluate_supplier(
    supplier_id: int = Path(..., gt=0, description="Supplier ID"),
    evaluation: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """Submit supplier evaluation."""
    try:
        for supplier in mock_suppliers_db:
            if supplier.get('id') == supplier_id and supplier.get('company_id') == company_id:
                # Update ratings
                if 'delivery_rating' in evaluation:
                    supplier['delivery_rating'] = evaluation['delivery_rating']
                if 'quality_rating' in evaluation:
                    supplier['quality_rating'] = evaluation['quality_rating']
                if 'price_rating' in evaluation:
                    supplier['price_rating'] = evaluation['price_rating']
                if 'communication_rating' in evaluation:
                    supplier['communication_rating'] = evaluation['communication_rating']
                
                # Calculate overall rating
                ratings = [
                    supplier.get('delivery_rating', 5.0),
                    supplier.get('quality_rating', 5.0),
                    supplier.get('price_rating', 5.0),
                    supplier.get('communication_rating', 5.0)
                ]
                supplier['performance_rating'] = sum(ratings) / len(ratings)
                
                supplier['last_evaluation'] = datetime.utcnow().isoformat()
                supplier['last_evaluated_by'] = user_id
                
                return {
                    "message": "Supplier evaluation submitted successfully",
                    "supplier_id": supplier_id,
                    "new_rating": supplier['performance_rating']
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating supplier: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/top-performers")
async def get_top_suppliers(
    limit: int = Query(10, ge=1, le=50, description="Number of suppliers to return"),
    company_id: int = Depends(get_current_company_id)
):
    """Get top performing suppliers."""
    try:
        company_suppliers = [
            s for s in mock_suppliers_db 
            if s.get('company_id') == company_id and s.get('status') == 'active'
        ]
        
        # Sort by performance rating
        company_suppliers.sort(key=lambda x: x.get('performance_rating', 0), reverse=True)
        
        # Return top N
        top_suppliers = company_suppliers[:limit]
        
        return {
            "suppliers": [
                {
                    "id": s['id'],
                    "name": s['name'],
                    "rating": s.get('performance_rating', 5.0),
                    "total_orders": s.get('total_orders', 0),
                    "category": s.get('category')
                }
                for s in top_suppliers
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting top suppliers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )