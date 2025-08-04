"""
Framework-based Partner router using Business Object Framework.

This router demonstrates how to migrate existing Partner API endpoints to use
the Business Object Framework while maintaining full API compatibility.
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middleware.auth import get_current_active_user, verify_company_access
from app.models.partner import Partner
from app.framework.controllers import create_business_object_router
from app.framework_migration.partner_service import PartnerFrameworkService, create_partner_service
from app.framework_migration.partner_schemas import (
    PartnerFrameworkCreate,
    PartnerFrameworkUpdate,
    PartnerFrameworkResponse,
    PartnerFrameworkListResponse
)


# === Framework-Generated Router ===
# This demonstrates the new framework approach with automatic CRUD operations

framework_partner_router = create_business_object_router(
    model_class=Partner,
    service_class=PartnerFrameworkService,
    create_schema=PartnerFrameworkCreate,
    update_schema=PartnerFrameworkUpdate,
    response_schema=PartnerFrameworkResponse,
    prefix="/api/v1/partners",
    tags=["partners-framework"],
    enable_extensions=True,
    enable_audit_trail=True,
    enable_bulk_operations=True
)


# === Custom Router with Business Logic ===
# This maintains existing API patterns while using framework services

router = APIRouter(prefix="/partners-framework", tags=["partners-framework"])


async def get_partner_service(db: AsyncSession = Depends(get_db)) -> PartnerFrameworkService:
    """Dependency to get Partner service instance."""
    return create_partner_service(db)


@router.post("/", response_model=PartnerFrameworkResponse, status_code=status.HTTP_201_CREATED)
async def create_partner(
    partner_data: PartnerFrameworkCreate,
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create a new partner using framework service.
    
    Enhanced with automatic audit logging and event publishing.
    """
    # Verify user has access to the company
    await verify_company_access(partner_data.company_id, current_user)
    
    try:
        # Framework automatically handles audit logging and event publishing
        partner = await partner_service.create_partner(partner_data)
        return partner
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=PartnerFrameworkListResponse)
async def list_partners(
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for partner name, code, or email"),
    partner_type: Optional[str] = Query(None, description="Filter by partner type (customer, supplier, vendor)"),
    active_only: bool = Query(True, description="Return only active partners"),
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """
    List partners with pagination and filtering using framework service.
    
    Enhanced with automatic multi-company data isolation.
    """
    # If company_id is specified, verify access
    if company_id:
        await verify_company_access(company_id, current_user)
    
    partners, total = await partner_service.get_partners(
        company_id=company_id,
        skip=skip,
        limit=limit,
        search=search,
        partner_type=partner_type,
        active_only=active_only
    )
    
    pages = math.ceil(total / limit) if total > 0 else 1
    page = (skip // limit) + 1
    
    return PartnerFrameworkListResponse(
        partners=partners,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


@router.get("/company/{company_id}", response_model=list[PartnerFrameworkResponse])
async def get_partners_by_company(
    company_id: int = Path(..., description="Company ID"),
    partner_type: Optional[str] = Query(None, description="Filter by partner type (customer, supplier, vendor)"),
    active_only: bool = Query(True, description="Return only active partners"),
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all partners for a specific company using framework service."""
    # Verify user has access to the company
    await verify_company_access(company_id, current_user)
    
    partners = await partner_service.get_partners_by_company(
        company_id=company_id,
        partner_type=partner_type,
        active_only=active_only
    )
    
    return partners


@router.get("/{partner_id}", response_model=PartnerFrameworkResponse)
async def get_partner(
    partner_id: int,
    company_id: Optional[int] = Query(None, description="Company ID for access verification"),
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific partner by ID using framework service."""
    partner = await partner_service.get_partner(partner_id, company_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    # Verify user has access to the partner's company
    await verify_company_access(partner.company_id, current_user)
    
    return partner


@router.get("/company/{company_id}/code/{code}", response_model=PartnerFrameworkResponse)
async def get_partner_by_code(
    company_id: int = Path(..., description="Company ID"),
    code: str = Path(..., description="Partner code"),
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific partner by code within a company using framework service."""
    # Verify user has access to the company
    await verify_company_access(company_id, current_user)
    
    partner = await partner_service.get_partner_by_code(company_id, code)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    return partner


@router.put("/{partner_id}", response_model=PartnerFrameworkResponse)
async def update_partner(
    partner_id: int,
    partner_data: PartnerFrameworkUpdate,
    company_id: Optional[int] = Query(None, description="Company ID for access verification"),
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Update a partner using framework service with automatic audit logging."""
    # First get the partner to verify company access
    partner = await partner_service.get_partner(partner_id, company_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    # Verify user has access to the partner's company
    await verify_company_access(partner.company_id, current_user)
    
    try:
        # Framework automatically handles audit logging and event publishing
        updated_partner = await partner_service.update_partner(partner_id, partner_data, company_id)
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
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Delete a partner (soft delete) using framework service."""
    # First get the partner to verify company access
    partner = await partner_service.get_partner(partner_id, company_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    # Verify user has access to the partner's company
    await verify_company_access(partner.company_id, current_user)
    
    success = await partner_service.delete_partner(partner_id, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )


@router.post("/{partner_id}/activate", response_model=PartnerFrameworkResponse)
async def activate_partner(
    partner_id: int,
    company_id: Optional[int] = Query(None, description="Company ID for access verification"),
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Activate a partner using framework service."""
    # First get the partner to verify company access
    partner = await partner_service.get_partner(partner_id, company_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    # Verify user has access to the partner's company
    await verify_company_access(partner.company_id, current_user)
    
    activated_partner = await partner_service.activate_partner(partner_id, company_id)
    if not activated_partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    return activated_partner


@router.post("/{partner_id}/deactivate", response_model=PartnerFrameworkResponse)
async def deactivate_partner(
    partner_id: int,
    company_id: Optional[int] = Query(None, description="Company ID for access verification"),
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Deactivate a partner using framework service."""
    # First get the partner to verify company access
    partner = await partner_service.get_partner(partner_id, company_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    # Verify user has access to the partner's company
    await verify_company_access(partner.company_id, current_user)
    
    deactivated_partner = await partner_service.deactivate_partner(partner_id, company_id)
    if not deactivated_partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    return deactivated_partner


# === Business Intelligence Endpoints ===

@router.get("/company/{company_id}/statistics")
async def get_partner_statistics(
    company_id: int = Path(..., description="Company ID"),
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Get partner statistics for a company."""
    # Verify user has access to the company
    await verify_company_access(company_id, current_user)
    
    statistics = await partner_service.get_partner_statistics(company_id)
    return statistics


@router.get("/company/{company_id}/customers", response_model=list[PartnerFrameworkResponse])
async def get_customers(
    company_id: int = Path(..., description="Company ID"),
    active_only: bool = Query(True, description="Return only active customers"),
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all customers for a company."""
    await verify_company_access(company_id, current_user)
    return await partner_service.find_customers(company_id, active_only)


@router.get("/company/{company_id}/suppliers", response_model=list[PartnerFrameworkResponse])
async def get_suppliers(
    company_id: int = Path(..., description="Company ID"),
    active_only: bool = Query(True, description="Return only active suppliers"),
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all suppliers for a company."""
    await verify_company_access(company_id, current_user)
    return await partner_service.find_suppliers(company_id, active_only)


@router.get("/company/{company_id}/vendors", response_model=list[PartnerFrameworkResponse])
async def get_vendors(
    company_id: int = Path(..., description="Company ID"),
    active_only: bool = Query(True, description="Return only active vendors"),
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all vendors for a company."""
    await verify_company_access(company_id, current_user)
    return await partner_service.find_vendors(company_id, active_only)


# === Bulk Operations ===

@router.post("/bulk-create", response_model=list[PartnerFrameworkResponse])
async def bulk_create_partners(
    partners_data: list[PartnerFrameworkCreate],
    partner_service: PartnerFrameworkService = Depends(get_partner_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Bulk create partners using framework service."""
    # Verify access to all companies
    company_ids = {p.company_id for p in partners_data}
    for company_id in company_ids:
        await verify_company_access(company_id, current_user)
    
    try:
        partners = await partner_service.bulk_create_partners(partners_data)
        return partners
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )