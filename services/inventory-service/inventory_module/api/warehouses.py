"""
Warehouse API endpoints for inventory management.

Provides REST API endpoints for warehouse and location operations including
warehouse management, location hierarchy, and capacity optimization.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from datetime import datetime

from inventory_module.models import Warehouse, WarehouseLocation, WarehouseType, LocationType
from inventory_module.services import WarehouseService, WarehouseLocationService

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


# Pydantic schemas
class WarehouseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    warehouse_type: WarehouseType = WarehouseType.MAIN
    address_line_1: Optional[str] = Field(None, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country_code: str = Field(default="US", max_length=3)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    timezone: str = Field(default="UTC", max_length=50)
    operating_hours: Optional[Dict[str, Dict[str, str]]] = None
    currency_code: str = Field(default="USD", max_length=3)
    capabilities: Optional[List[str]] = None
    total_area_sqm: Optional[Decimal] = Field(None, ge=0)
    storage_area_sqm: Optional[Decimal] = Field(None, ge=0)
    ceiling_height_m: Optional[Decimal] = Field(None, ge=0)
    dock_doors_count: Optional[int] = Field(None, ge=0)
    default_cost_center: Optional[str] = Field(None, max_length=50)
    labor_cost_per_hour: Optional[Decimal] = Field(None, ge=0)
    storage_cost_per_sqm: Optional[Decimal] = Field(None, ge=0)
    allow_negative_stock: bool = False
    require_location_tracking: bool = True
    enable_cycle_counting: bool = True
    warehouse_manager_user_id: Optional[int] = None
    create_default_locations: bool = True


class WarehouseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    address_line_1: Optional[str] = Field(None, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country_code: Optional[str] = Field(None, max_length=3)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    timezone: Optional[str] = Field(None, max_length=50)
    operating_hours: Optional[Dict[str, Dict[str, str]]] = None
    currency_code: Optional[str] = Field(None, max_length=3)
    total_area_sqm: Optional[Decimal] = Field(None, ge=0)
    storage_area_sqm: Optional[Decimal] = Field(None, ge=0)
    ceiling_height_m: Optional[Decimal] = Field(None, ge=0)
    dock_doors_count: Optional[int] = Field(None, ge=0)
    default_cost_center: Optional[str] = Field(None, max_length=50)
    labor_cost_per_hour: Optional[Decimal] = Field(None, ge=0)
    storage_cost_per_sqm: Optional[Decimal] = Field(None, ge=0)
    allow_negative_stock: Optional[bool] = None
    require_location_tracking: Optional[bool] = None
    enable_cycle_counting: Optional[bool] = None
    warehouse_manager_user_id: Optional[int] = None


class WarehouseResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    warehouse_type: WarehouseType
    address_line_1: Optional[str]
    address_line_2: Optional[str]
    city: Optional[str]
    state_province: Optional[str]
    postal_code: Optional[str]
    country_code: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    contact_person: Optional[str]
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    timezone: Optional[str]
    operating_hours: Optional[Dict[str, Dict[str, str]]]
    currency_code: Optional[str]
    capabilities: Optional[List[str]]
    total_area_sqm: Optional[Decimal]
    storage_area_sqm: Optional[Decimal]
    ceiling_height_m: Optional[Decimal]
    dock_doors_count: Optional[int]
    default_cost_center: Optional[str]
    labor_cost_per_hour: Optional[Decimal]
    storage_cost_per_sqm: Optional[Decimal]
    allow_negative_stock: bool
    require_location_tracking: bool
    enable_cycle_counting: bool
    default_receiving_location_id: Optional[int]
    default_shipping_location_id: Optional[int]
    is_active: bool
    is_primary: bool
    warehouse_manager_user_id: Optional[int]
    last_cycle_count_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LocationCreate(BaseModel):
    warehouse_id: int
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    parent_location_id: Optional[int] = None
    location_type: LocationType
    position_x: Optional[Decimal] = None
    position_y: Optional[Decimal] = None
    position_z: Optional[Decimal] = None
    max_weight_kg: Optional[Decimal] = Field(None, ge=0)
    max_volume_cbm: Optional[Decimal] = Field(None, ge=0)
    max_items: Optional[int] = Field(None, ge=0)
    allow_mixed_products: bool = True
    allow_mixed_batches: bool = True
    require_picking_confirmation: bool = False
    climate_controlled: bool = False
    temperature_min: Optional[Decimal] = None
    temperature_max: Optional[Decimal] = None
    humidity_min: Optional[Decimal] = Field(None, ge=0, le=100)
    humidity_max: Optional[Decimal] = Field(None, ge=0, le=100)
    pick_sequence: int = 0
    putaway_sequence: int = 0
    abc_classification: Optional[str] = Field(None, pattern="^[ABC]$")
    restricted_access: bool = False
    access_permissions: Optional[Dict[str, Any]] = None
    hazmat_approved: bool = False
    inspection_frequency_days: int = 90
    notes: Optional[str] = None
    custom_attributes: Optional[Dict[str, Any]] = None


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    barcode: Optional[str] = Field(None, max_length=100)
    position_x: Optional[Decimal] = None
    position_y: Optional[Decimal] = None
    position_z: Optional[Decimal] = None
    max_weight_kg: Optional[Decimal] = Field(None, ge=0)
    max_volume_cbm: Optional[Decimal] = Field(None, ge=0)
    max_items: Optional[int] = Field(None, ge=0)
    allow_mixed_products: Optional[bool] = None
    allow_mixed_batches: Optional[bool] = None
    require_picking_confirmation: Optional[bool] = None
    climate_controlled: Optional[bool] = None
    temperature_min: Optional[Decimal] = None
    temperature_max: Optional[Decimal] = None
    humidity_min: Optional[Decimal] = Field(None, ge=0, le=100)
    humidity_max: Optional[Decimal] = Field(None, ge=0, le=100)
    pick_sequence: Optional[int] = None
    putaway_sequence: Optional[int] = None
    abc_classification: Optional[str] = Field(None, pattern="^[ABC]$")
    restricted_access: Optional[bool] = None
    access_permissions: Optional[Dict[str, Any]] = None
    hazmat_approved: Optional[bool] = None
    inspection_frequency_days: Optional[int] = Field(None, ge=1)
    notes: Optional[str] = None
    custom_attributes: Optional[Dict[str, Any]] = None


class LocationResponse(BaseModel):
    id: int
    warehouse_id: int
    name: str
    code: str
    barcode: Optional[str]
    parent_location_id: Optional[int]
    location_type: LocationType
    level: int
    position_x: Optional[Decimal]
    position_y: Optional[Decimal]
    position_z: Optional[Decimal]
    max_weight_kg: Optional[Decimal]
    max_volume_cbm: Optional[Decimal]
    max_items: Optional[int]
    current_weight_kg: Optional[Decimal]
    current_volume_cbm: Optional[Decimal]
    current_items: Optional[int]
    allow_mixed_products: bool
    allow_mixed_batches: bool
    require_picking_confirmation: bool
    climate_controlled: bool
    temperature_min: Optional[Decimal]
    temperature_max: Optional[Decimal]
    humidity_min: Optional[Decimal]
    humidity_max: Optional[Decimal]
    pick_sequence: Optional[int]
    putaway_sequence: Optional[int]
    abc_classification: Optional[str]
    restricted_access: bool
    access_permissions: Optional[Dict[str, Any]]
    hazmat_approved: bool
    last_inspected_date: Optional[datetime]
    next_inspection_date: Optional[datetime]
    inspection_frequency_days: Optional[int]
    is_active: bool
    is_blocked: bool
    blocked_reason: Optional[str]
    blocked_until: Optional[datetime]
    notes: Optional[str]
    custom_attributes: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LocationBlockRequest(BaseModel):
    reason: str = Field(..., min_length=1)
    blocked_until: Optional[datetime] = None


class PutawayOptimizationRequest(BaseModel):
    product_id: int
    quantity: Decimal = Field(..., gt=0)
    weight_kg: Optional[Decimal] = Field(None, ge=0)
    volume_cbm: Optional[Decimal] = Field(None, ge=0)


# Dependency injection
def get_warehouse_service() -> WarehouseService:
    return WarehouseService(db_session=None, user_id=1, company_id=1)


def get_location_service() -> WarehouseLocationService:
    return WarehouseLocationService(db_session=None, user_id=1, company_id=1)


# Warehouse endpoints
@router.post("/", response_model=WarehouseResponse, status_code=201)
async def create_warehouse(
    warehouse_data: WarehouseCreate,
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Create a new warehouse."""
    try:
        warehouse = service.create_warehouse(**warehouse_data.dict())
        service.commit()
        return WarehouseResponse.from_orm(warehouse)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[WarehouseResponse])
async def list_warehouses(
    active_only: bool = Query(True, description="Filter active warehouses only"),
    service: WarehouseService = Depends(get_warehouse_service)
):
    """List all warehouses."""
    warehouses = service.get_company_warehouses(active_only=active_only)
    return [WarehouseResponse.from_orm(warehouse) for warehouse in warehouses]


@router.get("/primary", response_model=Optional[WarehouseResponse])
async def get_primary_warehouse(
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Get the primary warehouse."""
    warehouse = service.get_primary_warehouse()
    return WarehouseResponse.from_orm(warehouse) if warehouse else None


@router.get("/by-capability/{capability}", response_model=List[WarehouseResponse])
async def get_warehouses_by_capability(
    capability: str = Path(..., description="Capability name"),
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Get warehouses that have a specific capability."""
    warehouses = service.get_warehouses_by_capability(capability)
    return [WarehouseResponse.from_orm(warehouse) for warehouse in warehouses]


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: int = Path(..., description="Warehouse ID"),
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Get warehouse by ID."""
    warehouse = service.get_by_id_or_raise(Warehouse, warehouse_id)
    return WarehouseResponse.from_orm(warehouse)


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: int = Path(..., description="Warehouse ID"),
    warehouse_data: WarehouseUpdate = ...,
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Update warehouse."""
    try:
        warehouse = service.get_by_id_or_raise(Warehouse, warehouse_id)
        updated_warehouse = service.update(warehouse, warehouse_data.dict(exclude_unset=True))
        service.commit()
        return WarehouseResponse.from_orm(updated_warehouse)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{warehouse_id}/set-primary", response_model=WarehouseResponse)
async def set_primary_warehouse(
    warehouse_id: int = Path(..., description="Warehouse ID"),
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Set warehouse as primary."""
    try:
        warehouse = service.set_primary_warehouse(warehouse_id)
        service.commit()
        return WarehouseResponse.from_orm(warehouse)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{warehouse_id}/capabilities", response_model=WarehouseResponse)
async def update_warehouse_capabilities(
    warehouse_id: int = Path(..., description="Warehouse ID"),
    capabilities: List[str] = ...,
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Update warehouse capabilities."""
    try:
        warehouse = service.update_warehouse_capabilities(warehouse_id, capabilities)
        service.commit()
        return WarehouseResponse.from_orm(warehouse)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{warehouse_id}/utilization", response_model=Dict[str, Any])
async def get_warehouse_utilization(
    warehouse_id: int = Path(..., description="Warehouse ID"),
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Get warehouse utilization statistics."""
    return service.get_warehouse_utilization(warehouse_id)


@router.get("/{warehouse_id}/costs", response_model=Dict[str, Any])
async def calculate_warehouse_costs(
    warehouse_id: int = Path(..., description="Warehouse ID"),
    period_days: int = Query(30, ge=1, le=365, description="Cost calculation period in days"),
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Calculate warehouse operational costs."""
    return service.calculate_warehouse_costs(warehouse_id, period_days)


@router.delete("/{warehouse_id}", status_code=204)
async def delete_warehouse(
    warehouse_id: int = Path(..., description="Warehouse ID"),
    hard_delete: bool = Query(False, description="Perform hard delete instead of soft delete"),
    service: WarehouseService = Depends(get_warehouse_service)
):
    """Delete warehouse."""
    try:
        warehouse = service.get_by_id_or_raise(Warehouse, warehouse_id)
        service.delete(warehouse, soft_delete=not hard_delete)
        service.commit()
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Location endpoints
@router.post("/{warehouse_id}/locations", response_model=LocationResponse, status_code=201)
async def create_location(
    warehouse_id: int = Path(..., description="Warehouse ID"),
    location_data: LocationCreate = ...,
    service: WarehouseLocationService = Depends(get_location_service)
):
    """Create a new warehouse location."""
    try:
        location_data_dict = location_data.dict()
        location_data_dict['warehouse_id'] = warehouse_id
        location = service.create_location(**location_data_dict)
        service.commit()
        return LocationResponse.from_orm(location)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{warehouse_id}/locations", response_model=List[LocationResponse])
async def list_warehouse_locations(
    warehouse_id: int = Path(..., description="Warehouse ID"),
    active_only: bool = Query(True, description="Filter active locations only"),
    location_type: Optional[LocationType] = Query(None, description="Filter by location type"),
    service: WarehouseLocationService = Depends(get_location_service)
):
    """List locations for a warehouse."""
    locations = service.get_warehouse_locations(
        warehouse_id=warehouse_id,
        active_only=active_only,
        location_type=location_type
    )
    return [LocationResponse.from_orm(location) for location in locations]


@router.get("/{warehouse_id}/locations/hierarchy", response_model=List[Dict[str, Any]])
async def get_location_hierarchy(
    warehouse_id: int = Path(..., description="Warehouse ID"),
    service: WarehouseLocationService = Depends(get_location_service)
):
    """Get hierarchical location structure for warehouse."""
    return service.get_location_hierarchy(warehouse_id)


@router.get("/{warehouse_id}/locations/available", response_model=List[LocationResponse])
async def get_available_locations(
    warehouse_id: int = Path(..., description="Warehouse ID"),
    weight_kg: Optional[Decimal] = Query(None, ge=0, description="Required weight capacity"),
    volume_cbm: Optional[Decimal] = Query(None, ge=0, description="Required volume capacity"),
    items: Optional[int] = Query(None, ge=0, description="Required item capacity"),
    location_type: Optional[LocationType] = Query(None, description="Filter by location type"),
    service: WarehouseLocationService = Depends(get_location_service)
):
    """Get locations that can accommodate specified requirements."""
    locations = service.get_available_locations(
        warehouse_id=warehouse_id,
        weight_kg=weight_kg,
        volume_cbm=volume_cbm,
        items=items,
        location_type=location_type
    )
    return [LocationResponse.from_orm(location) for location in locations]


@router.get("/{warehouse_id}/locations/at-capacity", response_model=List[LocationResponse])
async def get_locations_at_capacity(
    warehouse_id: int = Path(..., description="Warehouse ID"),
    threshold_percentage: float = Query(95.0, ge=0, le=100, description="Capacity threshold percentage"),
    service: WarehouseLocationService = Depends(get_location_service)
):
    """Get locations at or near capacity."""
    locations = service.get_locations_at_capacity(warehouse_id, threshold_percentage)
    return [LocationResponse.from_orm(location) for location in locations]


@router.post("/{warehouse_id}/locations/optimize-putaway", response_model=List[Dict[str, Any]])
async def optimize_putaway_locations(
    warehouse_id: int = Path(..., description="Warehouse ID"),
    request: PutawayOptimizationRequest = ...,
    service: WarehouseLocationService = Depends(get_location_service)
):
    """Get optimized putaway location suggestions."""
    return service.optimize_putaway_locations(
        warehouse_id=warehouse_id,
        product_id=request.product_id,
        quantity=request.quantity,
        weight_kg=request.weight_kg,
        volume_cbm=request.volume_cbm
    )


@router.get("/locations/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: int = Path(..., description="Location ID"),
    service: WarehouseLocationService = Depends(get_location_service)
):
    """Get location by ID."""
    location = service.get_by_id_or_raise(WarehouseLocation, location_id)
    return LocationResponse.from_orm(location)


@router.put("/locations/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int = Path(..., description="Location ID"),
    location_data: LocationUpdate = ...,
    service: WarehouseLocationService = Depends(get_location_service)
):
    """Update location."""
    try:
        location = service.get_by_id_or_raise(WarehouseLocation, location_id)
        updated_location = service.update(location, location_data.dict(exclude_unset=True))
        service.commit()
        return LocationResponse.from_orm(updated_location)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/locations/{location_id}/capacity", response_model=LocationResponse)
async def update_location_capacity(
    location_id: int = Path(..., description="Location ID"),
    max_weight_kg: Optional[Decimal] = Query(None, ge=0),
    max_volume_cbm: Optional[Decimal] = Query(None, ge=0),
    max_items: Optional[int] = Query(None, ge=0),
    service: WarehouseLocationService = Depends(get_location_service)
):
    """Update location capacity limits."""
    try:
        location = service.update_location_capacity(
            location_id=location_id,
            max_weight_kg=max_weight_kg,
            max_volume_cbm=max_volume_cbm,
            max_items=max_items
        )
        service.commit()
        return LocationResponse.from_orm(location)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/locations/{location_id}/move", response_model=LocationResponse)
async def move_location(
    location_id: int = Path(..., description="Location ID"),
    new_parent_id: Optional[int] = Query(None, description="New parent location ID (null for root)"),
    service: WarehouseLocationService = Depends(get_location_service)
):
    """Move location to a new parent."""
    try:
        location = service.move_location(location_id, new_parent_id)
        service.commit()
        return LocationResponse.from_orm(location)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/locations/{location_id}/block", response_model=LocationResponse)
async def block_location(
    location_id: int = Path(..., description="Location ID"),
    request: LocationBlockRequest = ...,
    service: WarehouseLocationService = Depends(get_location_service)
):
    """Block a location from use."""
    try:
        location = service.block_location(
            location_id=location_id,
            reason=request.reason,
            blocked_until=request.blocked_until
        )
        service.commit()
        return LocationResponse.from_orm(location)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/locations/{location_id}/unblock", response_model=LocationResponse)
async def unblock_location(
    location_id: int = Path(..., description="Location ID"),
    service: WarehouseLocationService = Depends(get_location_service)
):
    """Unblock a location."""
    try:
        location = service.unblock_location(location_id)
        service.commit()
        return LocationResponse.from_orm(location)
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/locations/{location_id}", status_code=204)
async def delete_location(
    location_id: int = Path(..., description="Location ID"),
    hard_delete: bool = Query(False, description="Perform hard delete instead of soft delete"),
    service: WarehouseLocationService = Depends(get_location_service)
):
    """Delete location."""
    try:
        location = service.get_by_id_or_raise(WarehouseLocation, location_id)
        service.delete(location, soft_delete=not hard_delete)
        service.commit()
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))