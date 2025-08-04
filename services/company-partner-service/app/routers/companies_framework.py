"""
Framework-based Company API endpoints using Business Object Framework.

Provides standardized REST API operations with automatic audit logging,
event publishing, and consistent error handling.
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.company_service_framework import company_framework_service
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
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Create a new company using the Business Object Framework.
    
    Features:
    - Automatic audit logging
    - Event publishing for company creation
    - Standardized error handling
    - Framework version tracking
    """
    try:
        company = await company_framework_service.create(
            db=db,
            create_data=company_data,
            # user_id=current_user.get('id')  # Temporarily disabled
        )
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
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    List companies with pagination and optional filtering using the Business Object Framework.
    
    Features:
    - Standardized pagination
    - Built-in search across name, legal name, and code fields
    - Active/inactive filtering
    - Consistent response format
    """
    try:
        companies, total = await company_framework_service.search_companies(
            db=db,
            search_term=search or "",
            active_only=active_only,
            skip=skip,
            limit=limit
        )
        
        return CompanyListResponse(
            companies=[CompanyResponse.model_validate(company) for company in companies],
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


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Get a company by ID using the Business Object Framework.
    """
    try:
        company = await company_framework_service.get_by_id(
            db=db,
            obj_id=company_id
        )
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return CompanyResponse.model_validate(company)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/code/{code}", response_model=CompanyResponse)
async def get_company_by_code(
    code: str,
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Get a company by code using the Business Object Framework.
    """
    try:
        company = await company_framework_service.get_company_by_code(
            db=db,
            code=code
        )
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return CompanyResponse.model_validate(company)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Update a company using the Business Object Framework.
    
    Features:
    - Automatic audit logging with change tracking
    - Event publishing for company updates
    - Optimistic updates (only changed fields)
    - Framework version tracking
    """
    try:
        company = await company_framework_service.update(
            db=db,
            obj_id=company_id,
            update_data=company_data,
            # user_id=current_user.get('id')  # Temporarily disabled
        )
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return CompanyResponse.model_validate(company)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Delete a company using the Business Object Framework.
    
    Features:
    - Automatic audit logging
    - Event publishing for company deletion
    - Cascade deletion of related data
    """
    try:
        deleted = await company_framework_service.delete(
            db=db,
            obj_id=company_id,
            # user_id=current_user.get('id')  # Temporarily disabled
        )
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return {"message": "Company deleted successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{company_id}/activate", response_model=CompanyResponse)
async def activate_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Activate a company (set is_active to True) using the Business Object Framework.
    """
    try:
        company = await company_framework_service.activate_company(
            db=db,
            company_id=company_id,
            # user_id=current_user.get('id')  # Temporarily disabled
        )
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return CompanyResponse.model_validate(company)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{company_id}/deactivate", response_model=CompanyResponse)
async def deactivate_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Deactivate a company (set is_active to False) using the Business Object Framework.
    """
    try:
        company = await company_framework_service.deactivate_company(
            db=db,
            company_id=company_id,
            # user_id=current_user.get('id')  # Temporarily disabled
        )
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return CompanyResponse.model_validate(company)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/stats/overview")
async def get_company_statistics(
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_active_user)  # Temporarily disabled for development
):
    """
    Get company statistics using the Business Object Framework.
    """
    try:
        stats = await company_framework_service.get_company_statistics(db=db)
        return stats
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )