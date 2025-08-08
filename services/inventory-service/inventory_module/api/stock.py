"""
Stock API endpoints for inventory management.

Provides REST API endpoints for stock operations including
stock levels, movements, reservations, and stock adjustments.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from inventory_module.models import StockLevel, StockMovement, StockMovementType
from inventory_module.services import StockService, StockMovementService
from inventory_module.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stock", tags=["stock"])


# Pydantic schemas
class StockAdjustmentRequest(BaseModel):
    product_id: int
    location_id: int
    quantity_change: Decimal = Field(..., description="Positive for increase, negative for decrease")
    movement_type: StockMovementType
    product_variant_id: Optional[int] = None
    reason: Optional[str] = None
    unit_cost: Optional[Decimal] = Field(None, ge=0)


class StockReservationRequest(BaseModel):
    product_id: int
    location_id: int
    quantity: Decimal = Field(..., gt=0)
    product_variant_id: Optional[int] = None
    reason: Optional[str] = None


class StockAvailabilityRequest(BaseModel):
    product_id: int
    quantity: Decimal = Field(..., gt=0)
    location_id: Optional[int] = None
    product_variant_id: Optional[int] = None


class StockLevelResponse(BaseModel):
    id: int
    product_id: int
    product_variant_id: Optional[int]
    warehouse_location_id: int
    quantity_on_hand: Decimal
    quantity_reserved: Decimal
    quantity_available: Decimal
    quantity_incoming: Decimal
    batch_number: Optional[str]
    serial_numbers: Optional[List[str]]
    expiration_date: Optional[datetime]
    unit_cost: Optional[Decimal]
    total_cost: Optional[Decimal]
    cost_method: Optional[str]
    last_movement_date: Optional[datetime]
    last_movement_type: Optional[StockMovementType]
    last_count_date: Optional[datetime]
    is_active: bool
    negative_stock_allowed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    product_variant_id: Optional[int]
    warehouse_location_id: int
    from_location_id: Optional[int]
    to_location_id: Optional[int]
    movement_type: StockMovementType
    movement_date: datetime
    quantity: Decimal
    unit_cost: Optional[Decimal]
    total_cost: Optional[Decimal]
    batch_number: Optional[str]
    serial_numbers: Optional[List[str]]
    expiration_date: Optional[datetime]
    source_document_type: Optional[str]
    source_document_id: Optional[int]
    source_document_number: Optional[str]
    created_by_user_id: int
    approved_by_user_id: Optional[int]
    approved_at: Optional[datetime]
    reference_number: Optional[str]
    notes: Optional[str]
    reason_code: Optional[str]
    quality_check_required: bool
    quality_check_passed: Optional[bool]
    quality_notes: Optional[str]
    inspected_by_user_id: Optional[int]
    inspected_at: Optional[datetime]
    quantity_before: Optional[Decimal]
    quantity_after: Optional[Decimal]
    is_reversed: bool
    reversed_by_movement_id: Optional[int]
    reversed_at: Optional[datetime]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockAvailabilityResponse(BaseModel):
    available: bool
    quantity_available: Decimal
    shortage: Decimal
    locations: List[Dict[str, Any]]


class StockSummaryResponse(BaseModel):
    on_hand: Decimal
    reserved: Decimal
    available: Decimal
    incoming: Decimal


# Dependency injection
def get_stock_service(db: Session = Depends(get_db)) -> StockService:
    return StockService(db_session=db, user_id=1, company_id=1)


def get_movement_service(db: Session = Depends(get_db)) -> StockMovementService:
    return StockMovementService(db_session=db, user_id=1, company_id=1)


# Stock level endpoints
@router.get("/levels", response_model=List[StockLevelResponse])
async def list_stock_levels(
    location_id: Optional[int] = Query(None, description="Filter by location ID"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    active_only: bool = Query(True, description="Filter active stock levels only"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    service: StockService = Depends(get_stock_service)
):
    """List stock levels with filtering."""
    if location_id:
        stock_levels = service.get_location_stock_levels(location_id, active_only)
    else:
        stock_levels = service.list_all(
            StockLevel,
            active_only=active_only,
            limit=limit,
            offset=offset,
            order_by="warehouse_location_id"
        )
    
    # Apply product filter if specified
    if product_id:
        stock_levels = [sl for sl in stock_levels if sl.product_id == product_id]
    
    return [StockLevelResponse.from_orm(sl) for sl in stock_levels[:limit]]


@router.get("/levels/{stock_level_id}", response_model=StockLevelResponse)
async def get_stock_level(
    stock_level_id: int = Path(..., description="Stock level ID"),
    service: StockService = Depends(get_stock_service)
):
    """Get stock level by ID."""
    stock_level = service.get_by_id_or_raise(StockLevel, stock_level_id)
    return StockLevelResponse.from_orm(stock_level)


@router.get("/levels/product/{product_id}/location/{location_id}", response_model=Optional[StockLevelResponse])
async def get_product_location_stock(
    product_id: int = Path(..., description="Product ID"),
    location_id: int = Path(..., description="Location ID"),
    product_variant_id: Optional[int] = Query(None, description="Product variant ID"),
    service: StockService = Depends(get_stock_service)
):
    """Get stock level for specific product at location."""
    stock_level = service.get_stock_level(product_id, location_id, product_variant_id)
    return StockLevelResponse.from_orm(stock_level) if stock_level else None


@router.get("/summary/product/{product_id}", response_model=StockSummaryResponse)
async def get_product_stock_summary(
    product_id: int = Path(..., description="Product ID"),
    product_variant_id: Optional[int] = Query(None, description="Product variant ID"),
    service: StockService = Depends(get_stock_service)
):
    """Get total stock summary for a product across all locations."""
    totals = service.get_product_total_stock(product_id, product_variant_id)
    return StockSummaryResponse(**totals)


@router.post("/availability/check", response_model=StockAvailabilityResponse)
async def check_stock_availability(
    request: StockAvailabilityRequest,
    service: StockService = Depends(get_stock_service)
):
    """Check stock availability for a product."""
    availability = service.check_stock_availability(
        product_id=request.product_id,
        quantity=request.quantity,
        location_id=request.location_id,
        product_variant_id=request.product_variant_id
    )
    return StockAvailabilityResponse(**availability)


@router.get("/stats", response_model=Dict[str, Any])
async def get_stock_stats(
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse ID"),
    service: StockService = Depends(get_stock_service)
):
    """Get stock statistics for dashboard."""
    try:
        # Get total stock value
        value_data = service.calculate_stock_value(location_id=warehouse_id)
        total_value = value_data.get("total_value", 0)
        
        # Get low stock count
        low_stock_items = service.get_low_stock_items(warehouse_id=warehouse_id, limit=1000)
        low_stock_count = len(low_stock_items) if low_stock_items else 0
        
        return {
            "total_value": total_value,
            "low_stock_count": low_stock_count,
            "warehouses": 5,  # Placeholder for now
            "total_items": 100  # Placeholder for now
        }
    except Exception as e:
        logger.error(f"Error getting stock stats: {e}")
        return {
            "total_value": 0,
            "low_stock_count": 0,
            "warehouses": 0,
            "total_items": 0
        }


@router.get("/low-stock", response_model=List[Dict[str, Any]])
async def get_low_stock_items(
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse ID"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of items"),
    service: StockService = Depends(get_stock_service)
):
    """Get items with low stock levels."""
    return service.get_low_stock_items(warehouse_id=warehouse_id, limit=limit)


@router.get("/value", response_model=Dict[str, Any])
async def calculate_stock_value(
    location_id: Optional[int] = Query(None, description="Filter by location ID"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    service: StockService = Depends(get_stock_service)
):
    """Calculate total stock value."""
    return service.calculate_stock_value(location_id=location_id, product_id=product_id)


# Stock adjustment endpoints
@router.post("/adjust", response_model=StockLevelResponse)
async def adjust_stock(
    request: StockAdjustmentRequest,
    service: StockService = Depends(get_stock_service)
):
    """Adjust stock level for a product at location."""
    try:
        stock_level = service.adjust_stock(
            product_id=request.product_id,
            quantity_change=request.quantity_change,
            location_id=request.location_id,
            movement_type=request.movement_type,
            product_variant_id=request.product_variant_id,
            reason=request.reason,
            unit_cost=request.unit_cost
        )
        service.commit()
        return StockLevelResponse.from_orm(stock_level)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Stock reservation endpoints
@router.post("/reserve", response_model=Dict[str, str])
async def reserve_stock(
    request: StockReservationRequest,
    service: StockService = Depends(get_stock_service)
):
    """Reserve stock for allocation."""
    try:
        success = service.reserve_stock(
            product_id=request.product_id,
            quantity=request.quantity,
            location_id=request.location_id,
            product_variant_id=request.product_variant_id,
            reason=request.reason
        )
        service.commit()
        return {"message": "Stock reserved successfully" if success else "Failed to reserve stock"}
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/release-reservation", response_model=Dict[str, str])
async def release_reservation(
    request: StockReservationRequest,
    service: StockService = Depends(get_stock_service)
):
    """Release reserved stock."""
    try:
        success = service.release_reservation(
            product_id=request.product_id,
            quantity=request.quantity,
            location_id=request.location_id,
            product_variant_id=request.product_variant_id
        )
        service.commit()
        return {"message": "Reservation released successfully" if success else "Failed to release reservation"}
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Stock movement endpoints
@router.get("/movements/recent", response_model=List[Dict[str, Any]])
async def get_recent_movements(
    limit: int = Query(10, ge=1, le=100, description="Number of recent movements to return"),
    service: StockService = Depends(get_stock_service)
):
    """Get recent stock movements for dashboard."""
    try:
        movements = service.get_recent_movements(limit=limit)
        return [
            {
                "product": m.product.name if hasattr(m, 'product') and m.product else "Unknown Product",
                "type": m.movement_type if hasattr(m, 'movement_type') else "Unknown",
                "quantity": m.quantity if hasattr(m, 'quantity') else 0,
                "warehouse": m.location.warehouse.name if hasattr(m, 'location') and m.location and hasattr(m.location, 'warehouse') else "Unknown",
                "time": m.created_at.isoformat() if hasattr(m, 'created_at') else datetime.utcnow().isoformat()
            }
            for m in movements
        ] if movements else []
    except Exception as e:
        logger.error(f"Error getting recent movements: {e}")
        return []


@router.get("/movements", response_model=List[StockMovementResponse])
async def list_stock_movements(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    movement_type: Optional[StockMovementType] = Query(None, description="Filter by movement type"),
    location_id: Optional[int] = Query(None, description="Filter by location ID"),
    days_back: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of movements"),
    service: StockMovementService = Depends(get_movement_service)
):
    """List stock movements with filtering."""
    if product_id:
        movements = service.get_product_movements(
            product_id=product_id,
            location_id=location_id,
            days_back=days_back,
            limit=limit
        )
    elif movement_type:
        movements = service.get_movements_by_type(
            movement_type=movement_type,
            days_back=days_back,
            limit=limit
        )
    else:
        movements = service.list_all(
            StockMovement,
            limit=limit,
            order_by="movement_date",
            order_desc=True
        )
    
    return [StockMovementResponse.from_orm(movement) for movement in movements]


@router.get("/movements/{movement_id}", response_model=StockMovementResponse)
async def get_stock_movement(
    movement_id: int = Path(..., description="Movement ID"),
    service: StockMovementService = Depends(get_movement_service)
):
    """Get stock movement by ID."""
    movement = service.get_by_id_or_raise(StockMovement, movement_id)
    return StockMovementResponse.from_orm(movement)


@router.get("/movements/pending-approvals", response_model=List[StockMovementResponse])
async def get_pending_approvals(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of movements"),
    service: StockMovementService = Depends(get_movement_service)
):
    """Get movements pending approval."""
    movements = service.get_pending_approvals(limit=limit)
    return [StockMovementResponse.from_orm(movement) for movement in movements]


@router.put("/movements/{movement_id}/approve", response_model=StockMovementResponse)
async def approve_movement(
    movement_id: int = Path(..., description="Movement ID"),
    service: StockMovementService = Depends(get_movement_service)
):
    """Approve a stock movement."""
    try:
        # In production, would get approver user ID from auth context
        movement = service.approve_movement(movement_id, approver_user_id=1)
        service.commit()
        return StockMovementResponse.from_orm(movement)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/movements/{movement_id}/reverse", response_model=StockMovementResponse)
async def reverse_movement(
    movement_id: int = Path(..., description="Movement ID"),
    reason: str = Query(..., min_length=1, description="Reason for reversal"),
    service: StockMovementService = Depends(get_movement_service)
):
    """Create a reversal movement."""
    try:
        # In production, would get user ID from auth context
        reversal_movement = service.create_reversal(movement_id, user_id=1, reason=reason)
        service.commit()
        return StockMovementResponse.from_orm(reversal_movement)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/movements/statistics", response_model=Dict[str, Any])
async def get_movement_statistics(
    days_back: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    service: StockMovementService = Depends(get_movement_service)
):
    """Get stock movement statistics for reporting."""
    return service.calculate_movement_statistics(days_back=days_back)