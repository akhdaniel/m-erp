"""
Journal Entry API endpoints for accounting management.

Provides REST API endpoints for journal entry operations including
journal entries, lines, posting, and reversal operations.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field
from datetime import datetime, date
from sqlalchemy.orm import Session

from accounting_module.models.journal_entry import (
    JournalEntry, JournalEntryLine, JournalEntryType, JournalEntryStatus
)
from accounting_module.services.journal_entry_service import JournalEntryService
from accounting_module.database import get_db

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/journal-entries", tags=["journal-entries"])

# Pydantic schemas for request/response
class JournalEntryCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    entry_date: date
    entry_type: JournalEntryType = JournalEntryType.STANDARD
    reference: Optional[str] = Field(None, max_length=100)
    source_module: Optional[str] = Field(None, max_length=100)
    source_document_id: Optional[str] = Field(None, max_length=100)

class JournalEntryUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    entry_date: Optional[date] = None
    entry_type: Optional[JournalEntryType] = None
    reference: Optional[str] = Field(None, max_length=100)
    source_module: Optional[str] = Field(None, max_length=100)
    source_document_id: Optional[str] = Field(None, max_length=100)

class JournalEntryResponse(BaseModel):
    id: int
    entry_number: str
    description: str
    entry_date: date
    entry_type: JournalEntryType
    reference: Optional[str]
    source_module: Optional[str]
    source_document_id: Optional[str]
    status: JournalEntryStatus
    total_debit: Decimal
    total_credit: Decimal
    posting_date: Optional[datetime]
    created_by_user_id: Optional[int]
    posted_by_user_id: Optional[int]
    approved_by_user_id: Optional[int]
    approval_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JournalEntryLineCreate(BaseModel):
    account_id: int
    debit_amount: Decimal = Field(default=0, ge=0)
    credit_amount: Decimal = Field(default=0, ge=0)
    description: Optional[str] = None
    reference: Optional[str] = Field(None, max_length=100)
    tax_code: Optional[str] = Field(None, max_length=50)
    tax_amount: Decimal = Field(default=0)
    department_id: Optional[int] = None
    project_id: Optional[int] = None
    cost_center_id: Optional[int] = None

class JournalEntryLineUpdate(BaseModel):
    account_id: Optional[int] = None
    debit_amount: Optional[Decimal] = Field(None, ge=0)
    credit_amount: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None
    reference: Optional[str] = Field(None, max_length=100)
    tax_code: Optional[str] = Field(None, max_length=50)
    tax_amount: Optional[Decimal] = None
    department_id: Optional[int] = None
    project_id: Optional[int] = None
    cost_center_id: Optional[int] = None

class JournalEntryLineResponse(BaseModel):
    id: int
    journal_entry_id: int
    account_id: int
    debit_amount: Decimal
    credit_amount: Decimal
    description: Optional[str]
    reference: Optional[str]
    line_number: int
    is_posted: bool
    tax_code: Optional[str]
    tax_amount: Decimal
    department_id: Optional[int]
    project_id: Optional[int]
    cost_center_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JournalEntryListResponse(BaseModel):
    """Schema for paginated journal entry list responses."""
    data: List[JournalEntryResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int

class JournalEntryStatisticsResponse(BaseModel):
    """Schema for journal entry statistics response."""
    total: int
    posted: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]

# Dependency injection
def get_journal_entry_service(db: Session = Depends(get_db)) -> JournalEntryService:
    # In production, would get user context from auth
    return JournalEntryService(db_session=db, user_id=1, company_id=1)

# Journal Entry endpoints
@router.post("/", response_model=JournalEntryResponse, status_code=201)
@router.post("", response_model=JournalEntryResponse, status_code=201)
async def create_journal_entry(
    entry_data: JournalEntryCreate,
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """Create a new journal entry."""
    try:
        journal_entry = service.create_journal_entry(**entry_data.dict())
        service.commit()
        return JournalEntryResponse.from_orm(journal_entry)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=JournalEntryListResponse)
@router.get("", response_model=JournalEntryListResponse)
async def list_journal_entries(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    entry_type: Optional[JournalEntryType] = Query(None, description="Filter by entry type"),
    status: Optional[JournalEntryStatus] = Query(None, description="Filter by entry status"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """List journal entries with filtering and pagination."""
    # Calculate offset from page and page_size
    offset = (page - 1) * page_size
    
    # Get filtered journal entries
    journal_entries = service.search_journal_entries(
        entry_type=entry_type,
        status=status,
        date_from=date_from,
        date_to=date_to,
        limit=page_size * 2  # Get more for filtering
    )
    
    # Apply pagination
    paginated_entries = journal_entries[offset:offset + page_size]
    
    # Get total count
    total_count = len(journal_entries)
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
    
    return JournalEntryListResponse(
        data=[JournalEntryResponse.from_orm(entry) for entry in paginated_entries],
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/search", response_model=List[JournalEntryResponse])
async def search_journal_entries(
    q: str = Query(..., min_length=1, description="Search term"),
    entry_type: Optional[JournalEntryType] = Query(None, description="Filter by entry type"),
    status: Optional[JournalEntryStatus] = Query(None, description="Filter by entry status"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """Search journal entries."""
    journal_entries = service.search_journal_entries(
        search_term=q,
        entry_type=entry_type,
        status=status,
        date_from=date_from,
        date_to=date_to,
        limit=limit
    )
    return [JournalEntryResponse.from_orm(entry) for entry in journal_entries]

@router.get("/stats", response_model=JournalEntryStatisticsResponse)
async def get_journal_entry_stats(
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """Get journal entry statistics."""
    stats = service.get_journal_entry_statistics()
    return JournalEntryStatisticsResponse(**stats)

@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: int = Path(..., description="Journal Entry ID"),
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """Get journal entry by ID."""
    journal_entry = service.get_by_id_or_raise(JournalEntry, entry_id)
    return JournalEntryResponse.from_orm(journal_entry)

@router.put("/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: int = Path(..., description="Journal Entry ID"),
    entry_data: JournalEntryUpdate = Body(...),
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """Update journal entry."""
    try:
        journal_entry = service.get_by_id_or_raise(JournalEntry, entry_id)
        updated_entry = service.update(journal_entry, entry_data.dict(exclude_unset=True))
        service.commit()
        return JournalEntryResponse.from_orm(updated_entry)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{entry_id}", status_code=204)
async def delete_journal_entry(
    entry_id: int = Path(..., description="Journal Entry ID"),
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """Delete journal entry (soft delete)."""
    try:
        journal_entry = service.get_by_id_or_raise(JournalEntry, entry_id)
        service.delete(journal_entry)
        service.commit()
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Journal Entry Line endpoints
@router.post("/{entry_id}/lines", response_model=JournalEntryLineResponse, status_code=201)
async def add_journal_entry_line(
    entry_id: int = Path(..., description="Journal Entry ID"),
    line_data: JournalEntryLineCreate = Body(...),
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """Add a line to a journal entry."""
    try:
        journal_entry_line = service.add_journal_entry_line(entry_id, **line_data.dict())
        service.commit()
        return JournalEntryLineResponse.from_orm(journal_entry_line)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{entry_id}/lines", response_model=List[JournalEntryLineResponse])
async def list_journal_entry_lines(
    entry_id: int = Path(..., description="Journal Entry ID"),
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """List lines for a journal entry."""
    lines = service.db.query(JournalEntryLine).filter(
        JournalEntryLine.journal_entry_id == entry_id
    ).order_by(JournalEntryLine.line_number).all()
    
    return [JournalEntryLineResponse.from_orm(line) for line in lines]

@router.get("/lines/{line_id}", response_model=JournalEntryLineResponse)
async def get_journal_entry_line(
    line_id: int = Path(..., description="Journal Entry Line ID"),
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """Get journal entry line by ID."""
    line = service.get_by_id_or_raise(JournalEntryLine, line_id)
    return JournalEntryLineResponse.from_orm(line)

@router.put("/lines/{line_id}", response_model=JournalEntryLineResponse)
async def update_journal_entry_line(
    line_id: int = Path(..., description="Journal Entry Line ID"),
    line_data: JournalEntryLineUpdate = Body(...),
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """Update journal entry line."""
    try:
        updated_line = service.update_journal_entry_line(line_id, **line_data.dict(exclude_unset=True))
        service.commit()
        return JournalEntryLineResponse.from_orm(updated_line)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/lines/{line_id}", status_code=204)
async def delete_journal_entry_line(
    line_id: int = Path(..., description="Journal Entry Line ID"),
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """Delete journal entry line."""
    try:
        service.delete_journal_entry_line(line_id)
        service.commit()
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Journal Entry actions
@router.post("/{entry_id}/post", response_model=JournalEntryResponse)
async def post_journal_entry(
    entry_id: int = Path(..., description="Journal Entry ID"),
    posting_date: Optional[date] = Body(None, description="Posting date (defaults to current date)"),
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """Post a journal entry to the ledger."""
    try:
        posting_datetime = datetime.combine(posting_date, datetime.min.time()) if posting_date else None
        journal_entry = service.post_journal_entry(entry_id, posting_datetime)
        service.commit()
        return JournalEntryResponse.from_orm(journal_entry)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{entry_id}/cancel", response_model=JournalEntryResponse)
async def cancel_journal_entry(
    entry_id: int = Path(..., description="Journal Entry ID"),
    service: JournalEntryService = Depends(get_journal_entry_service)
):
    """Cancel a journal entry."""
    try:
        journal_entry = service.cancel_journal_entry(entry_id)
        service.commit()
        return JournalEntryResponse.from_orm(journal_entry)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))