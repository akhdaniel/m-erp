"""
Partner Category API endpoints.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.partner_category_service import PartnerCategoryService
from app.schemas.partner_category import (
    PartnerCategoryCreate,
    PartnerCategoryUpdate,
    PartnerCategoryResponse,
    PartnerCategoryTreeResponse,
    PartnerCategoryListResponse,
    PartnerCategoryStatsResponse
)

router = APIRouter(prefix="/partner-categories", tags=["partner-categories"])
category_service = PartnerCategoryService()


@router.post("/", response_model=PartnerCategoryResponse)
def create_partner_category(
    category_data: PartnerCategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new partner category."""
    try:
        category = category_service.create(db, category_data)
        return category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PartnerCategoryListResponse)
def list_partner_categories(
    company_id: int = Query(..., description="Company ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: str = Query(None, description="Search term for name or code"),
    active_only: bool = Query(True, description="Filter active categories only"),
    db: Session = Depends(get_db)
):
    """List partner categories with pagination and filtering."""
    try:
        categories, total = category_service.get_list(
            db=db,
            company_id=company_id,
            skip=skip,
            limit=limit,
            search=search,
            active_only=active_only
        )
        
        return PartnerCategoryListResponse(
            categories=categories,
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            pages=(total + limit - 1) // limit
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tree", response_model=List[PartnerCategoryTreeResponse])
def get_category_tree(
    company_id: int = Query(..., description="Company ID"),
    db: Session = Depends(get_db)
):
    """Get hierarchical tree of partner categories."""
    try:
        return category_service.get_category_tree(db, company_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics", response_model=PartnerCategoryStatsResponse)
def get_category_statistics(
    company_id: int = Query(..., description="Company ID"),
    db: Session = Depends(get_db)
):
    """Get partner category statistics."""
    try:
        return category_service.get_statistics(db, company_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{category_id}", response_model=PartnerCategoryResponse)
def get_partner_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific partner category by ID."""
    category = category_service.get(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Partner category not found")
    return category


@router.put("/{category_id}", response_model=PartnerCategoryResponse)
def update_partner_category(
    category_id: int,
    update_data: PartnerCategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a partner category."""
    # Validate hierarchy if parent is being changed
    if update_data.parent_category_id is not None:
        if not category_service.validate_hierarchy(db, category_id, update_data.parent_category_id):
            raise HTTPException(
                status_code=400, 
                detail="Invalid parent category - would create circular reference"
            )
    
    category = category_service.update(db, category_id, update_data)
    if not category:
        raise HTTPException(status_code=404, detail="Partner category not found")
    return category


@router.delete("/{category_id}")
def delete_partner_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Delete a partner category."""
    category = category_service.get(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Partner category not found")
    
    if not category.can_be_deleted():
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete category with child categories or assigned partners"
        )
    
    success = category_service.delete(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Partner category not found")
    
    return {"message": "Partner category deleted successfully"}


@router.post("/companies/{company_id}/default-categories")
def create_default_categories(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Create default partner categories for a company."""
    try:
        categories = category_service.create_default_categories(db, company_id)
        return {
            "message": f"Created {len(categories)} default categories",
            "categories": [{"id": c.id, "name": c.name, "code": c.code} for c in categories]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{from_category_id}/move-partners/{to_category_id}")
def move_partners_between_categories(
    from_category_id: int,
    to_category_id: int,
    company_id: int = Query(..., description="Company ID"),
    db: Session = Depends(get_db)
):
    """Move all partners from one category to another."""
    try:
        moved_count = category_service.move_partners_to_category(
            db, from_category_id, to_category_id, company_id
        )
        return {
            "message": f"Moved {moved_count} partners to new category",
            "moved_count": moved_count
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies/{company_id}/usage-report")
def get_category_usage_report(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed category usage report."""
    try:
        return category_service.get_category_usage_report(db, company_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))