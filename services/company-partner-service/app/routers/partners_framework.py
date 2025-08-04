"""
Framework-based Partner API endpoints using Business Object Framework.

Provides standardized REST API operations with automatic audit logging,
event publishing, multi-company data isolation, and consistent error handling.
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.partner_service_framework import partner_framework_service
from app.schemas.partner import (
    PartnerCreate,
    PartnerUpdate,
    PartnerResponse,
    PartnerListResponse
)

router = APIRouter(prefix="/partners", tags=["partners"])


@router.post("/", response_model=PartnerResponse, status_code=status.HTTP_201_CREATED)
async def create_partner(
    partner_data: PartnerCreate,
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Create a new partner using the Business Object Framework.
    
    Features:
    - Automatic audit logging
    - Event publishing for partner creation
    - Multi-company data isolation
    - Standardized error handling
    - Framework version tracking
    """
    try:
        partner = await partner_framework_service.create(
            db=db,
            create_data=partner_data,
            company_id=partner_data.company_id,
            # user_id=current_user.get('id')  # Temporarily disabled
        )
        return partner
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=PartnerListResponse)
async def list_partners(
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for partner name, code, or email"),
    partner_type: Optional[str] = Query(None, description="Filter by partner type (customer, supplier, vendor)"),
    active_only: bool = Query(True, description="Return only active partners"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    List partners with pagination, filtering, and multi-company isolation using the Business Object Framework.
    
    Features:
    - Automatic multi-company data isolation
    - Standardized pagination
    - Built-in search across name, code, and email fields
    - Partner type filtering
    - Active/inactive filtering
    - Consistent response format
    """
    try:
        # For now, default to company_id = 2 (Default Company) if not specified
        # In a real system, this would come from user authentication
        if company_id is None:
            company_id = 2
        
        partners, total = await partner_framework_service.search_partners(
            db=db,
            company_id=company_id,
            search_term=search or "",
            partner_type=partner_type,
            active_only=active_only,
            skip=skip,
            limit=limit
        )
        
        return PartnerListResponse(
            partners=[PartnerResponse.model_validate(partner) for partner in partners],
            total=total,
            page=math.floor(skip / limit) + 1 if limit > 0 else 1,
            per_page=limit,
            pages=math.ceil(total / limit) if limit > 0 else 1
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{partner_id}", response_model=PartnerResponse)
async def get_partner(
    partner_id: int = Path(..., description="Partner ID"),
    company_id: Optional[int] = Query(None, description="Company ID for data isolation"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Get a partner by ID using the Business Object Framework with multi-company isolation.
    """
    try:
        # For now, default to company_id = 2 (Default Company) if not specified
        if company_id is None:
            company_id = 2
            
        partner = await partner_framework_service.get_by_id(
            db=db,
            obj_id=partner_id,
            company_id=company_id
        )
        
        if not partner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partner not found"
            )
        
        return PartnerResponse.model_validate(partner)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/company/{company_id}/code/{code}", response_model=PartnerResponse)
async def get_partner_by_code(
    company_id: int = Path(..., description="Company ID"),
    code: str = Path(..., description="Partner code"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Get a partner by code within a company using the Business Object Framework.
    """
    try:
        partner = await partner_framework_service.get_partner_by_code(
            db=db,
            company_id=company_id,
            code=code
        )
        
        if not partner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partner not found"
            )
        
        return PartnerResponse.model_validate(partner)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{partner_id}", response_model=PartnerResponse)
async def update_partner(
    partner_data: PartnerUpdate,
    partner_id: int = Path(..., description="Partner ID"),
    company_id: Optional[int] = Query(None, description="Company ID for data isolation"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Update a partner using the Business Object Framework.
    
    Features:
    - Automatic audit logging with change tracking
    - Event publishing for partner updates
    - Multi-company data isolation
    - Optimistic updates (only changed fields)
    - Framework version tracking
    """
    try:
        # For now, default to company_id = 2 (Default Company) if not specified
        if company_id is None:
            company_id = 2
            
        partner = await partner_framework_service.update(
            db=db,
            obj_id=partner_id,
            update_data=partner_data,
            company_id=company_id,
            # user_id=current_user.get('id')  # Temporarily disabled
        )
        
        if not partner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partner not found"
            )
        
        return PartnerResponse.model_validate(partner)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{partner_id}")
async def delete_partner(
    partner_id: int = Path(..., description="Partner ID"),
    company_id: Optional[int] = Query(None, description="Company ID for data isolation"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Delete a partner using the Business Object Framework.
    
    Features:
    - Automatic audit logging
    - Event publishing for partner deletion
    - Multi-company data isolation
    - Cascade deletion of related data
    """
    try:
        # For now, default to company_id = 2 (Default Company) if not specified
        if company_id is None:
            company_id = 2
            
        deleted = await partner_framework_service.delete(
            db=db,
            obj_id=partner_id,
            company_id=company_id,
            # user_id=current_user.get('id')  # Temporarily disabled
        )
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partner not found"
            )
        
        return {"message": "Partner deleted successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{partner_id}/activate", response_model=PartnerResponse)
async def activate_partner(
    partner_id: int = Path(..., description="Partner ID"),
    company_id: Optional[int] = Query(None, description="Company ID for data isolation"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Activate a partner (set is_active to True) using the Business Object Framework.
    """
    try:
        # For now, default to company_id = 2 (Default Company) if not specified
        if company_id is None:
            company_id = 2
            
        partner = await partner_framework_service.activate_partner(
            db=db,
            partner_id=partner_id,
            company_id=company_id,
            # user_id=current_user.get('id')  # Temporarily disabled
        )
        
        if not partner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partner not found"
            )
        
        return PartnerResponse.model_validate(partner)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{partner_id}/deactivate", response_model=PartnerResponse)
async def deactivate_partner(
    partner_id: int = Path(..., description="Partner ID"),
    company_id: Optional[int] = Query(None, description="Company ID for data isolation"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Deactivate a partner (set is_active to False) using the Business Object Framework.
    """
    try:
        # For now, default to company_id = 2 (Default Company) if not specified
        if company_id is None:
            company_id = 2
            
        partner = await partner_framework_service.deactivate_partner(
            db=db,
            partner_id=partner_id,
            company_id=company_id,
            # user_id=current_user.get('id')  # Temporarily disabled
        )
        
        if not partner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partner not found"
            )
        
        return PartnerResponse.model_validate(partner)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/company/{company_id}/by-type")
async def get_partners_by_type(
    company_id: int = Path(..., description="Company ID"),
    is_customer: Optional[bool] = Query(None, description="Filter by customer status"),
    is_supplier: Optional[bool] = Query(None, description="Filter by supplier status"),
    is_vendor: Optional[bool] = Query(None, description="Filter by vendor status"),
    active_only: bool = Query(True, description="Return only active partners"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Get partners filtered by their types using the Business Object Framework.
    """
    try:
        partners = await partner_framework_service.get_partners_by_type(
            db=db,
            company_id=company_id,
            is_customer=is_customer,
            is_supplier=is_supplier,
            is_vendor=is_vendor,
            active_only=active_only
        )
        
        return {
            "partners": [PartnerResponse.model_validate(partner) for partner in partners],
            "total": len(partners)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/company/{company_id}/stats/overview")
async def get_partner_statistics(
    company_id: int = Path(..., description="Company ID"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Get partner statistics for a company using the Business Object Framework.
    """
    try:
        stats = await partner_framework_service.get_partner_statistics(
            db=db,
            company_id=company_id
        )
        return stats
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )