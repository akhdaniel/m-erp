"""
Partner API endpoints.
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middleware.auth import get_current_active_user, verify_company_access
from app.services.partner_service import PartnerService
from app.services.messaging_service import get_messaging_service
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
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create a new partner.
    
    Requires authentication and company access verification.
    """
    # Verify user has access to the company
    await verify_company_access(partner_data.company_id, current_user)
    
    try:
        partner = await PartnerService.create_partner(db, partner_data)
        
        # Publish partner created event
        messaging_service = await get_messaging_service()
        if messaging_service:
            partner_data_dict = {
                "id": partner.id,
                "name": partner.name,
                "email": partner.email,
                "phone": partner.phone,
                "is_customer": partner.is_customer,
                "is_supplier": partner.is_supplier,
                "company_id": partner.company_id,
                "created_at": partner.created_at.isoformat() if partner.created_at else None
            }
            await messaging_service.publish_partner_created(
                partner_id=partner.id,
                partner_data=partner_data_dict,
                company_id=partner.company_id,
                created_by_user_id=current_user.get("id")
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
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    List partners with pagination and optional filtering.
    
    Supports searching by name, code, or email.
    Can filter by company and partner type.
    """
    # If company_id is specified, verify access
    if company_id:
        await verify_company_access(company_id, current_user)
    
    partners, total = await PartnerService.get_partners(
        db=db,
        company_id=company_id,
        skip=skip,
        limit=limit,
        search=search,
        partner_type=partner_type,
        active_only=active_only
    )
    
    pages = math.ceil(total / limit) if total > 0 else 1
    page = (skip // limit) + 1
    
    return PartnerListResponse(
        partners=partners,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


@router.get("/company/{company_id}", response_model=list[PartnerResponse])
async def get_partners_by_company(
    company_id: int = Path(..., description="Company ID"),
    partner_type: Optional[str] = Query(None, description="Filter by partner type (customer, supplier, vendor)"),
    active_only: bool = Query(True, description="Return only active partners"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get all partners for a specific company.
    """
    # Verify user has access to the company
    await verify_company_access(company_id, current_user)
    
    partners = await PartnerService.get_partners_by_company(
        db=db,
        company_id=company_id,
        partner_type=partner_type,
        active_only=active_only
    )
    
    return partners


@router.get("/{partner_id}", response_model=PartnerResponse)
async def get_partner(
    partner_id: int,
    company_id: Optional[int] = Query(None, description="Company ID for access verification"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get a specific partner by ID.
    
    If company_id is provided, it will be used for access verification.
    """
    partner = await PartnerService.get_partner(db, partner_id, company_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    # Verify user has access to the partner's company
    await verify_company_access(partner.company_id, current_user)
    
    return partner


@router.get("/company/{company_id}/code/{code}", response_model=PartnerResponse)
async def get_partner_by_code(
    company_id: int = Path(..., description="Company ID"),
    code: str = Path(..., description="Partner code"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get a specific partner by code within a company.
    """
    # Verify user has access to the company
    await verify_company_access(company_id, current_user)
    
    partner = await PartnerService.get_partner_by_code(db, company_id, code)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    return partner


@router.put("/{partner_id}", response_model=PartnerResponse)
async def update_partner(
    partner_id: int,
    partner_data: PartnerUpdate,
    company_id: Optional[int] = Query(None, description="Company ID for access verification"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update a partner.
    
    Only provided fields will be updated.
    """
    # First get the partner to verify company access
    partner = await PartnerService.get_partner(db, partner_id, company_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    # Verify user has access to the partner's company
    await verify_company_access(partner.company_id, current_user)
    
    try:
        updated_partner = await PartnerService.update_partner(db, partner_id, partner_data, company_id)
        if not updated_partner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partner not found"
            )
        return updated_partner
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{partner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_partner(
    partner_id: int,
    company_id: Optional[int] = Query(None, description="Company ID for access verification"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Delete a partner (soft delete).
    
    This sets the partner's is_active field to False rather than removing it.
    """
    # First get the partner to verify company access
    partner = await PartnerService.get_partner(db, partner_id, company_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    # Verify user has access to the partner's company
    await verify_company_access(partner.company_id, current_user)
    
    success = await PartnerService.delete_partner(db, partner_id, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )


@router.post("/{partner_id}/activate", response_model=PartnerResponse)
async def activate_partner(
    partner_id: int,
    company_id: Optional[int] = Query(None, description="Company ID for access verification"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Activate a partner.
    
    This sets the partner's is_active field to True.
    """
    # First get the partner to verify company access
    partner = await PartnerService.get_partner(db, partner_id, company_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    # Verify user has access to the partner's company
    await verify_company_access(partner.company_id, current_user)
    
    activated_partner = await PartnerService.activate_partner(db, partner_id, company_id)
    if not activated_partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    return activated_partner


@router.post("/{partner_id}/deactivate", response_model=PartnerResponse)
async def deactivate_partner(
    partner_id: int,
    company_id: Optional[int] = Query(None, description="Company ID for access verification"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Deactivate a partner.
    
    This sets the partner's is_active field to False.
    """
    # First get the partner to verify company access
    partner = await PartnerService.get_partner(db, partner_id, company_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    # Verify user has access to the partner's company
    await verify_company_access(partner.company_id, current_user)
    
    deactivated_partner = await PartnerService.deactivate_partner(db, partner_id, company_id)
    if not deactivated_partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    return deactivated_partner