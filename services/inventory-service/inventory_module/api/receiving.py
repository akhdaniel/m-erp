"""
Receiving API endpoints for inventory management.

Provides REST API endpoints for receiving operations including
receiving records, line item management, and quality control.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from datetime import datetime

from inventory_module.models import ReceivingRecord, ReceivingLineItem, ReceivingStatus, ReceivingLineStatus
from inventory_module.services import ReceivingService

router = APIRouter(prefix="/receiving", tags=["receiving"])


# Pydantic schemas
class ReceivingLineItemCreate(BaseModel):
    product_id: int
    product_variant_id: Optional[int] = None
    quantity_expected: Decimal = Field(..., gt=0)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    batch_number: Optional[str] = None
    expiration_date: Optional[datetime] = None
    put_away_location_id: Optional[int] = None
    quality_check_required: bool = False
    notes: Optional[str] = None


class ReceivingRecordCreate(BaseModel):
    source_document_type: str = Field(..., min_length=1, max_length=50)
    source_document_id: int
    source_document_number: Optional[str] = Field(None, max_length=100)
    supplier_id: int
    supplier_invoice_number: Optional[str] = Field(None, max_length=100)
    supplier_delivery_note: Optional[str] = Field(None, max_length=100)
    warehouse_id: int
    receiving_location_id: Optional[int] = None
    expected_date: Optional[datetime] = None
    scheduled_date: Optional[datetime] = None
    quality_inspection_required: bool = False
    carrier_name: Optional[str] = Field(None, max_length=255)
    tracking_number: Optional[str] = Field(None, max_length=100)
    freight_cost: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
    attachments: Optional[List[str]] = None
    line_items: List[ReceivingLineItemCreate] = Field(..., min_items=1)


class ReceivingRecordResponse(BaseModel):
    id: int
    receipt_number: str
    source_document_type: str
    source_document_id: int
    source_document_number: Optional[str]
    supplier_id: int
    supplier_invoice_number: Optional[str]
    supplier_delivery_note: Optional[str]
    warehouse_id: int
    receiving_location_id: Optional[int]
    expected_date: Optional[datetime]
    received_date: Optional[datetime]
    scheduled_date: Optional[datetime]
    status: ReceivingStatus
    total_quantity_expected: Decimal
    total_quantity_received: Decimal
    total_value_expected: Optional[Decimal]
    total_value_received: Optional[Decimal]
    quality_inspection_required: bool
    quality_inspection_passed: Optional[bool]
    quality_notes: Optional[str]
    received_by_user_id: Optional[int]
    approved_by_user_id: Optional[int]
    approved_at: Optional[datetime]
    carrier_name: Optional[str]
    tracking_number: Optional[str]
    freight_cost: Optional[Decimal]
    notes: Optional[str]
    attachments: Optional[List[str]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReceivingLineItemResponse(BaseModel):
    id: int
    receiving_record_id: int
    product_id: int
    product_variant_id: Optional[int]
    line_number: int
    quantity_expected: Decimal
    quantity_received: Decimal
    quantity_accepted: Decimal
    quantity_rejected: Decimal
    quantity_damaged: Decimal
    unit_cost: Optional[Decimal]
    total_cost: Optional[Decimal]
    batch_number: Optional[str]
    serial_numbers: Optional[List[str]]
    expiration_date: Optional[datetime]
    put_away_location_id: Optional[int]
    status: ReceivingLineStatus
    received_date: Optional[datetime]
    quality_check_required: bool
    quality_check_passed: Optional[bool]
    quality_notes: Optional[str]
    inspected_by_user_id: Optional[int]
    inspected_at: Optional[datetime]
    rejection_reason: Optional[str]
    damage_description: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReceiveQuantityRequest(BaseModel):
    quantity: Decimal = Field(..., gt=0)
    location_id: Optional[int] = None
    batch_number: Optional[str] = None
    serial_numbers: Optional[List[str]] = None
    expiration_date: Optional[datetime] = None
    quality_notes: Optional[str] = None


class RejectQuantityRequest(BaseModel):
    quantity: Decimal = Field(..., gt=0)
    reason: str = Field(..., min_length=1)


class MarkDamagedRequest(BaseModel):
    quantity: Decimal = Field(..., gt=0)
    description: str = Field(..., min_length=1)


class QualityInspectionRequest(BaseModel):
    passed: bool
    notes: Optional[str] = None


# Dependency injection
def get_receiving_service() -> ReceivingService:
    return ReceivingService(db_session=None, user_id=1, company_id=1)


# Receiving record endpoints
@router.post("/", response_model=ReceivingRecordResponse, status_code=201)
async def create_receiving_record(
    record_data: ReceivingRecordCreate,
    service: ReceivingService = Depends(get_receiving_service)
):
    """Create a new receiving record with line items."""
    try:
        # Extract line items
        line_items_data = record_data.line_items
        record_dict = record_data.dict(exclude={'line_items'})
        
        # Convert line items to dict format
        line_items = [item.dict() for item in line_items_data]
        
        record = service.create_receiving_record(
            line_items=line_items,
            **record_dict
        )
        service.commit()
        return ReceivingRecordResponse.from_orm(record)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ReceivingRecordResponse])
async def list_receiving_records(
    status: Optional[ReceivingStatus] = Query(None, description="Filter by status"),
    supplier_id: Optional[int] = Query(None, description="Filter by supplier ID"),
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse ID"),
    overdue_only: bool = Query(False, description="Show only overdue records"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    service: ReceivingService = Depends(get_receiving_service)
):
    """List receiving records with filtering."""
    if overdue_only:
        records = service.get_overdue_receipts()
    elif status:
        records = service.get_receipts_by_status(status, limit=limit)
    elif supplier_id:
        records = service.get_receipts_by_supplier(supplier_id, limit=limit)
    else:
        records = service.list_all(
            ReceivingRecord,
            limit=limit,
            offset=offset,
            order_by="created_at",
            order_desc=True
        )
    
    # Apply warehouse filter if specified
    if warehouse_id:
        records = [r for r in records if r.warehouse_id == warehouse_id]
    
    return [ReceivingRecordResponse.from_orm(record) for record in records[:limit]]


@router.get("/search", response_model=List[ReceivingRecordResponse])
async def search_receiving_records(
    q: str = Query(..., min_length=1, description="Search term"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    service: ReceivingService = Depends(get_receiving_service)
):
    """Search receiving records."""
    records = service.search_receipts(search_term=q, limit=limit)
    return [ReceivingRecordResponse.from_orm(record) for record in records]


@router.get("/overdue", response_model=List[ReceivingRecordResponse])
async def get_overdue_receipts(
    days_overdue: int = Query(1, ge=1, description="Minimum days overdue"),
    service: ReceivingService = Depends(get_receiving_service)
):
    """Get overdue receiving records."""
    records = service.get_overdue_receipts(days_overdue=days_overdue)
    return [ReceivingRecordResponse.from_orm(record) for record in records]


@router.get("/statistics", response_model=Dict[str, Any])
async def get_receiving_statistics(
    days_back: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    service: ReceivingService = Depends(get_receiving_service)
):
    """Get receiving statistics for reporting."""
    return service.calculate_receiving_statistics(days_back=days_back)


@router.get("/{record_id}", response_model=ReceivingRecordResponse)
async def get_receiving_record(
    record_id: int = Path(..., description="Receiving record ID"),
    service: ReceivingService = Depends(get_receiving_service)
):
    """Get receiving record by ID."""
    record = service.get_by_id_or_raise(ReceivingRecord, record_id)
    return ReceivingRecordResponse.from_orm(record)


@router.get("/by-number/{receipt_number}", response_model=Optional[ReceivingRecordResponse])
async def get_receiving_record_by_number(
    receipt_number: str = Path(..., description="Receipt number"),
    service: ReceivingService = Depends(get_receiving_service)
):
    """Get receiving record by receipt number."""
    record = service.get_receiving_record_by_number(receipt_number)
    return ReceivingRecordResponse.from_orm(record) if record else None


@router.put("/{record_id}/start", response_model=ReceivingRecordResponse)
async def start_receiving(
    record_id: int = Path(..., description="Receiving record ID"),
    service: ReceivingService = Depends(get_receiving_service)
):
    """Start the receiving process."""
    try:
        record = service.start_receiving(record_id)
        service.commit()
        return ReceivingRecordResponse.from_orm(record)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{record_id}/complete", response_model=ReceivingRecordResponse)
async def complete_receiving(
    record_id: int = Path(..., description="Receiving record ID"),
    service: ReceivingService = Depends(get_receiving_service)
):
    """Complete the receiving process."""
    try:
        record = service.complete_receiving(record_id)
        service.commit()
        return ReceivingRecordResponse.from_orm(record)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{record_id}/cancel", response_model=ReceivingRecordResponse)
async def cancel_receiving(
    record_id: int = Path(..., description="Receiving record ID"),
    reason: str = Query(..., min_length=1, description="Cancellation reason"),
    service: ReceivingService = Depends(get_receiving_service)
):
    """Cancel the receiving process."""
    try:
        record = service.cancel_receiving(record_id, reason)
        service.commit()
        return ReceivingRecordResponse.from_orm(record)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Line item endpoints
@router.get("/{record_id}/line-items", response_model=List[ReceivingLineItemResponse])
async def get_receiving_line_items(
    record_id: int = Path(..., description="Receiving record ID"),
    service: ReceivingService = Depends(get_receiving_service)
):
    """Get all line items for a receiving record."""
    line_items = service.get_receiving_line_items(record_id)
    return [ReceivingLineItemResponse.from_orm(item) for item in line_items]


@router.get("/{record_id}/line-items/pending", response_model=List[ReceivingLineItemResponse])
async def get_pending_line_items(
    record_id: int = Path(..., description="Receiving record ID"),
    service: ReceivingService = Depends(get_receiving_service)
):
    """Get pending line items for a receiving record."""
    line_items = service.get_pending_line_items(record_id)
    return [ReceivingLineItemResponse.from_orm(item) for item in line_items]


@router.get("/line-items/{line_item_id}", response_model=ReceivingLineItemResponse)
async def get_line_item(
    line_item_id: int = Path(..., description="Line item ID"),
    service: ReceivingService = Depends(get_receiving_service)
):
    """Get line item by ID."""
    line_item = service.get_by_id_or_raise(ReceivingLineItem, line_item_id)
    return ReceivingLineItemResponse.from_orm(line_item)


@router.put("/line-items/{line_item_id}/receive", response_model=ReceivingLineItemResponse)
async def receive_line_item_quantity(
    line_item_id: int = Path(..., description="Line item ID"),
    request: ReceiveQuantityRequest = ...,
    service: ReceivingService = Depends(get_receiving_service)
):
    """Receive quantity for a line item."""
    try:
        line_item = service.receive_line_item(
            line_item_id=line_item_id,
            quantity=request.quantity,
            location_id=request.location_id,
            batch_number=request.batch_number,
            serial_numbers=request.serial_numbers,
            expiration_date=request.expiration_date,
            quality_notes=request.quality_notes
        )
        service.commit()
        return ReceivingLineItemResponse.from_orm(line_item)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/line-items/{line_item_id}/reject", response_model=ReceivingLineItemResponse)
async def reject_line_item_quantity(
    line_item_id: int = Path(..., description="Line item ID"),
    request: RejectQuantityRequest = ...,
    service: ReceivingService = Depends(get_receiving_service)
):
    """Reject quantity for a line item."""
    try:
        line_item = service.reject_line_item_quantity(
            line_item_id=line_item_id,
            quantity=request.quantity,
            reason=request.reason
        )
        service.commit()
        return ReceivingLineItemResponse.from_orm(line_item)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/line-items/{line_item_id}/mark-damaged", response_model=ReceivingLineItemResponse)
async def mark_line_item_damaged(
    line_item_id: int = Path(..., description="Line item ID"),
    request: MarkDamagedRequest = ...,
    service: ReceivingService = Depends(get_receiving_service)
):
    """Mark quantity as damaged for a line item."""
    try:
        line_item = service.mark_line_item_damaged(
            line_item_id=line_item_id,
            quantity=request.quantity,
            description=request.description
        )
        service.commit()
        return ReceivingLineItemResponse.from_orm(line_item)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/line-items/{line_item_id}/quality-inspection", response_model=ReceivingLineItemResponse)
async def perform_quality_inspection(
    line_item_id: int = Path(..., description="Line item ID"),
    request: QualityInspectionRequest = ...,
    service: ReceivingService = Depends(get_receiving_service)
):
    """Perform quality inspection on a line item."""
    try:
        line_item = service.perform_quality_inspection(
            line_item_id=line_item_id,
            passed=request.passed,
            notes=request.notes
        )
        service.commit()
        return ReceivingLineItemResponse.from_orm(line_item)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))