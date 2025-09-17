"""
Account API endpoints for accounting management.

Provides REST API endpoints for chart of accounts operations including
accounts, account hierarchies, and account-related operations.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session

from accounting_module.models.account import Account, AccountType, AccountSubType, AccountStatus
from accounting_module.services.account_service import AccountService
from accounting_module.database import get_db

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/accounts", tags=["accounts"])

# Pydantic schemas for request/response
class AccountCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    account_type: AccountType
    account_subtype: AccountSubType
    parent_account_id: Optional[int] = None
    is_contra: bool = False
    allow_manual_journal_entries: bool = True
    currency_code: str = Field(default="USD", max_length=3)
    opening_balance: Decimal = Field(default=0)
    is_bank_account: bool = False
    bank_name: Optional[str] = Field(None, max_length=255)
    bank_account_number: Optional[str] = Field(None, max_length=100)
    bank_routing_number: Optional[str] = Field(None, max_length=50)
    tax_code: Optional[str] = Field(None, max_length=50)
    is_tax_account: bool = False

class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    account_type: Optional[AccountType] = None
    account_subtype: Optional[AccountSubType] = None
    parent_account_id: Optional[int] = None
    is_contra: Optional[bool] = None
    allow_manual_journal_entries: Optional[bool] = None
    currency_code: Optional[str] = Field(None, max_length=3)
    opening_balance: Optional[Decimal] = None
    is_bank_account: Optional[bool] = None
    bank_name: Optional[str] = Field(None, max_length=255)
    bank_account_number: Optional[str] = Field(None, max_length=100)
    bank_routing_number: Optional[str] = Field(None, max_length=50)
    tax_code: Optional[str] = Field(None, max_length=50)
    is_tax_account: Optional[bool] = None
    status: Optional[AccountStatus] = None

class AccountResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    account_type: AccountType
    account_subtype: AccountSubType
    parent_account_id: Optional[int]
    is_contra: bool
    allow_manual_journal_entries: bool
    currency_code: str
    opening_balance: Decimal
    current_balance: Decimal
    is_bank_account: bool
    bank_name: Optional[str]
    bank_account_number: Optional[str]
    bank_routing_number: Optional[str]
    tax_code: Optional[str]
    is_tax_account: bool
    status: AccountStatus
    is_system_account: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AccountListResponse(BaseModel):
    """Schema for paginated account list responses."""
    data: List[AccountResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int

class AccountStatisticsResponse(BaseModel):
    """Schema for account statistics response."""
    total: int
    active: int
    by_type: Dict[str, int]

# Dependency injection
def get_account_service(db: Session = Depends(get_db)) -> AccountService:
    # In production, would get user context from auth
    return AccountService(db_session=db, user_id=1, company_id=1)

# Account endpoints
@router.post("/", response_model=AccountResponse, status_code=201)
@router.post("", response_model=AccountResponse, status_code=201)
async def create_account(
    account_data: AccountCreate,
    service: AccountService = Depends(get_account_service)
):
    """Create a new account."""
    try:
        account = service.create_account(**account_data.dict())
        service.commit()
        return AccountResponse.from_orm(account)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=AccountListResponse)
@router.get("", response_model=AccountListResponse)
async def list_accounts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    account_type: Optional[AccountType] = Query(None, description="Filter by account type"),
    status: Optional[AccountStatus] = Query(None, description="Filter by account status"),
    service: AccountService = Depends(get_account_service)
):
    """List accounts with filtering and pagination."""
    # Calculate offset from page and page_size
    offset = (page - 1) * page_size
    
    # Get filtered accounts
    accounts = service.list_all(
        Account,
        active_only=False,  # Get all accounts, filter by status if specified
        limit=page_size,
        offset=offset,
        order_by="code"
    )
    
    # Apply additional filters
    if account_type:
        accounts = [a for a in accounts if a.account_type == account_type]
    if status:
        accounts = [a for a in accounts if a.status == status]
    
    # Get total count
    total_count = service.count_all(Account, active_only=False)
    if account_type:
        # Recalculate total count with filter
        total_count = len([a for a in service.list_all(Account, active_only=False) if a.account_type == account_type])
    if status:
        # Recalculate total count with filter
        total_count = len([a for a in service.list_all(Account, active_only=False) if a.status == status])
    
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
    
    return AccountListResponse(
        data=[AccountResponse.from_orm(account) for account in accounts],
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/search", response_model=List[AccountResponse])
async def search_accounts(
    q: str = Query(..., min_length=1, description="Search term"),
    account_type: Optional[AccountType] = Query(None, description="Filter by account type"),
    status: Optional[AccountStatus] = Query(None, description="Filter by account status"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    service: AccountService = Depends(get_account_service)
):
    """Search accounts."""
    accounts = service.search_accounts(
        search_term=q,
        account_type=account_type,
        status=status,
        limit=limit
    )
    return [AccountResponse.from_orm(account) for account in accounts]

@router.get("/hierarchy", response_model=List[Dict[str, Any]])
async def get_account_hierarchy(
    root_id: Optional[int] = Query(None, description="Root account ID (null for full hierarchy)"),
    service: AccountService = Depends(get_account_service)
):
    """Get hierarchical account structure."""
    return service.get_account_hierarchy(root_id)

@router.get("/stats", response_model=AccountStatisticsResponse)
async def get_account_stats(
    service: AccountService = Depends(get_account_service)
):
    """Get account statistics."""
    stats = service.get_account_statistics()
    return AccountStatisticsResponse(**stats)

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int = Path(..., description="Account ID"),
    service: AccountService = Depends(get_account_service)
):
    """Get account by ID."""
    account = service.get_by_id_or_raise(Account, account_id)
    return AccountResponse.from_orm(account)

@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int = Path(..., description="Account ID"),
    account_data: AccountUpdate = Body(...),
    service: AccountService = Depends(get_account_service)
):
    """Update account."""
    try:
        account = service.get_by_id_or_raise(Account, account_id)
        updated_account = service.update_account(account_id, **account_data.dict(exclude_unset=True))
        service.commit()
        return AccountResponse.from_orm(updated_account)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{account_id}", status_code=204)
async def delete_account(
    account_id: int = Path(..., description="Account ID"),
    service: AccountService = Depends(get_account_service)
):
    """Delete account (soft delete)."""
    try:
        account = service.get_by_id_or_raise(Account, account_id)
        service.delete(account)
        service.commit()
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{account_id}/close", response_model=AccountResponse)
async def close_account(
    account_id: int = Path(..., description="Account ID"),
    service: AccountService = Depends(get_account_service)
):
    """Close an account."""
    try:
        account = service.close_account(account_id)
        service.commit()
        return AccountResponse.from_orm(account)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))