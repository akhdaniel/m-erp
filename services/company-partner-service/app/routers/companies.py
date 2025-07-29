"""
Company API endpoints.
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middleware.auth import get_current_active_user
from app.services.company_service import CompanyService
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse
)

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create a new company.
    
    Requires authentication. Only admin users should be able to create companies.
    """
    try:
        company = await CompanyService.create_company(db, company_data)
        return company
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=CompanyListResponse)
async def list_companies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"), 
    search: Optional[str] = Query(None, description="Search term for company name, legal name, or code"),
    active_only: bool = Query(False, description="Return only active companies"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    List companies with pagination and optional filtering.
    
    Supports searching by name, legal name, or code.
    """
    companies, total = await CompanyService.get_companies(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        active_only=active_only
    )
    
    pages = math.ceil(total / limit) if total > 0 else 1
    page = (skip // limit) + 1
    
    return CompanyListResponse(
        companies=companies,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get a specific company by ID.
    """
    company = await CompanyService.get_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company


@router.get("/code/{code}", response_model=CompanyResponse)
async def get_company_by_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get a specific company by code.
    """
    company = await CompanyService.get_company_by_code(db, code)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update a company.
    
    Only provided fields will be updated.
    """
    try:
        company = await CompanyService.update_company(db, company_id, company_data)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        return company
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Delete a company (soft delete).
    
    This sets the company's is_active field to False rather than removing it.
    """
    success = await CompanyService.delete_company(db, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )


@router.post("/{company_id}/activate", response_model=CompanyResponse)
async def activate_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Activate a company.
    
    This sets the company's is_active field to True.
    """
    company = await CompanyService.activate_company(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company