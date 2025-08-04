"""
Purchase Orders API endpoints for the Purchasing Module.

Provides REST API endpoints for managing purchase orders including
creation, approval, status updates, and reporting.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field, validator

from purchasing_module.services.purchase_order_service import PurchaseOrderService
from purchasing_module.models.purchase_order import PurchaseOrderStatus

logger = logging.getLogger(__name__)

# Create router for purchase order endpoints
purchase_orders_router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])

# Pydantic models for request/response

class LineItemCreate(BaseModel):
    """Schema for creating a purchase order line item."""
    line_number: int = Field(..., gt=0, description="Line item number")
    product_code: Optional[str] = Field(None, max_length=50, description="Product code")
    product_name: str = Field(..., max_length=255, description="Product name")
    description: Optional[str] = Field("", max_length=1000, description="Item description")
    quantity: Decimal = Field(..., gt=0, description="Quantity ordered")
    unit_price: Decimal = Field(..., ge=0, description="Unit price")
    unit_of_measure: str = Field("each", max_length=20, description="Unit of measure")
    expected_delivery_date: Optional[datetime] = Field(None, description="Expected delivery date")
    notes: Optional[str] = Field(None, max_length=500, description="Line item notes")

class PurchaseOrderCreate(BaseModel):
    """Schema for creating a purchase order."""
    supplier_id: int = Field(..., gt=0, description="Supplier ID")
    line_items: List[LineItemCreate] = Field(..., min_items=1, description="Purchase order line items")
    expected_delivery_date: Optional[datetime] = Field(None, description="Expected delivery date")
    notes: Optional[str] = Field(None, max_length=1000, description="Order notes")
    currency_code: str = Field("USD", max_length=3, description="Currency code")
    
    @validator('line_items')
    def validate_line_items(cls, v):
        if not v:
            raise ValueError('At least one line item is required')
        return v

class PurchaseOrderUpdate(BaseModel):
    """Schema for updating a purchase order."""
    expected_delivery_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=1000)
    delivery_notes: Optional[str] = Field(None, max_length=1000)

class ApprovalRequest(BaseModel):
    """Schema for approval requests."""
    approval_notes: Optional[str] = Field(None, max_length=1000, description="Approval notes")

class RejectionRequest(BaseModel):
    """Schema for rejection requests."""
    rejection_reason: str = Field(..., max_length=1000, description="Reason for rejection")

class StatusUpdateRequest(BaseModel):
    """Schema for status update requests."""
    status: PurchaseOrderStatus = Field(..., description="New status")
    delivery_notes: Optional[str] = Field(None, max_length=1000, description="Delivery notes")

class PurchaseOrderResponse(BaseModel):
    """Schema for purchase order responses."""
    id: int
    po_number: str
    supplier_id: int
    status: str
    total_amount: Decimal
    currency_code: str
    order_date: datetime
    expected_delivery_date: Optional[datetime]
    notes: Optional[str]
    created_by_user_id: int
    submitted_for_approval_at: Optional[datetime]
    approved_at: Optional[datetime]
    rejected_at: Optional[datetime]
    sent_to_supplier_at: Optional[datetime]
    received_at: Optional[datetime]
    completed_at: Optional[datetime]

# Dependency functions

async def get_purchase_order_service() -> PurchaseOrderService:
    """Dependency to get purchase order service instance."""
    # In production, would use proper dependency injection
    return PurchaseOrderService()

async def get_current_user_id() -> int:
    """Dependency to get current user ID from authentication."""
    # In production, would extract from JWT token or session
    return 1

async def get_current_company_id() -> int:
    """Dependency to get current company ID from authentication."""
    # In production, would extract from user context
    return 1

# API Endpoints

@purchase_orders_router.post("/", response_model=Dict[str, Any])
async def create_purchase_order(
    purchase_order: PurchaseOrderCreate,
    service: PurchaseOrderService = Depends(get_purchase_order_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Create a new purchase order with line items.
    
    Creates a purchase order in draft status that can be submitted for approval.
    """
    try:
        # Convert line items to dict format
        line_items_data = [item.dict() for item in purchase_order.line_items]
        
        # Create purchase order
        po = service.create_purchase_order(
            company_id=company_id,
            supplier_id=purchase_order.supplier_id,
            line_items=line_items_data,
            created_by_user_id=user_id,
            delivery_date=purchase_order.expected_delivery_date,
            notes=purchase_order.notes,
            currency_code=purchase_order.currency_code
        )
        
        if not po:
            raise HTTPException(status_code=400, detail="Failed to create purchase order")
        
        return {
            "success": True,
            "message": "Purchase order created successfully",
            "data": {
                "id": po.id,
                "po_number": po.po_number,
                "status": po.status.value,
                "total_amount": float(po.total_amount),
                "currency_code": po.currency_code
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create purchase order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@purchase_orders_router.get("/", response_model=Dict[str, Any])
async def list_purchase_orders(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    service: PurchaseOrderService = Depends(get_purchase_order_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get list of purchase orders for the current company.
    
    Supports filtering by status and pagination.
    """
    try:
        # Parse status filter
        status_filter = None
        if status:
            try:
                status_filter = PurchaseOrderStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        # Get purchase orders
        orders = service.get_purchase_orders_by_company(
            company_id=company_id,
            status_filter=status_filter,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "data": orders,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(orders)  # In production, would get actual count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list purchase orders: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@purchase_orders_router.get("/{purchase_order_id}", response_model=Dict[str, Any])
async def get_purchase_order(
    purchase_order_id: int = Path(..., gt=0, description="Purchase order ID"),
    service: PurchaseOrderService = Depends(get_purchase_order_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get a specific purchase order by ID.
    
    Returns detailed purchase order information including line items.
    """
    try:
        # In production, would load actual PO from database
        # For now, return mock data
        
        if purchase_order_id <= 0:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        # Mock purchase order data
        po_data = {
            "id": purchase_order_id,
            "po_number": f"PO-{company_id}-20250801-{purchase_order_id:03d}",
            "supplier_id": 1,
            "supplier_name": f"Supplier {purchase_order_id}",
            "status": PurchaseOrderStatus.DRAFT.value,
            "total_amount": 1500.00 + purchase_order_id * 100,
            "currency_code": "USD",
            "order_date": datetime.utcnow().isoformat(),
            "expected_delivery_date": None,
            "notes": f"Purchase order {purchase_order_id}",
            "created_by_user_id": 1,
            "line_items": [
                {
                    "line_number": 1,
                    "product_code": f"PROD{purchase_order_id:03d}",
                    "product_name": f"Product {purchase_order_id}",
                    "quantity": 10.0,
                    "unit_price": 100.0 + purchase_order_id * 10,
                    "line_total": 1000.0 + purchase_order_id * 100,
                    "unit_of_measure": "each"
                }
            ]
        }
        
        return {
            "success": True,
            "data": po_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get purchase order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@purchase_orders_router.put("/{purchase_order_id}", response_model=Dict[str, Any])
async def update_purchase_order(
    purchase_order_id: int = Path(..., gt=0, description="Purchase order ID"),
    update_data: PurchaseOrderUpdate = None,
    service: PurchaseOrderService = Depends(get_purchase_order_service),
    user_id: int = Depends(get_current_user_id)
):
    """
    Update a purchase order.
    
    Only draft purchase orders can be updated.
    """
    try:
        # In production, would load PO and validate status
        # For now, simulate update
        
        logger.info(f"Updating purchase order {purchase_order_id}")
        
        return {
            "success": True,
            "message": "Purchase order updated successfully",
            "data": {
                "id": purchase_order_id,
                "updated_fields": update_data.dict(exclude_unset=True) if update_data else {}
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to update purchase order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@purchase_orders_router.post("/{purchase_order_id}/submit", response_model=Dict[str, Any])
async def submit_for_approval(
    purchase_order_id: int = Path(..., gt=0, description="Purchase order ID"),
    approval_request: ApprovalRequest = None,
    service: PurchaseOrderService = Depends(get_purchase_order_service),
    user_id: int = Depends(get_current_user_id)
):
    """
    Submit a purchase order for approval.
    
    Transitions the purchase order from draft to pending approval status
    and creates an approval workflow.
    """
    try:
        approval_notes = approval_request.approval_notes if approval_request else None
        
        success = service.submit_for_approval(
            purchase_order_id=purchase_order_id,
            submitted_by_user_id=user_id,
            approval_notes=approval_notes
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to submit purchase order for approval")
        
        return {
            "success": True,
            "message": "Purchase order submitted for approval successfully",
            "data": {
                "purchase_order_id": purchase_order_id,
                "status": PurchaseOrderStatus.PENDING_APPROVAL.value,
                "submitted_by_user_id": user_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit purchase order for approval: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@purchase_orders_router.post("/{purchase_order_id}/approve", response_model=Dict[str, Any])
async def approve_purchase_order(
    purchase_order_id: int = Path(..., gt=0, description="Purchase order ID"),
    approval_request: ApprovalRequest = None,
    service: PurchaseOrderService = Depends(get_purchase_order_service),
    user_id: int = Depends(get_current_user_id)
):
    """
    Approve a purchase order.
    
    Completes the approval process and transitions the purchase order
    to approved status.
    """
    try:
        approval_notes = approval_request.approval_notes if approval_request else None
        
        success = service.approve_purchase_order(
            purchase_order_id=purchase_order_id,
            approved_by_user_id=user_id,
            approval_notes=approval_notes
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to approve purchase order")
        
        return {
            "success": True,
            "message": "Purchase order approved successfully",
            "data": {
                "purchase_order_id": purchase_order_id,
                "status": PurchaseOrderStatus.APPROVED.value,
                "approved_by_user_id": user_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve purchase order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@purchase_orders_router.post("/{purchase_order_id}/reject", response_model=Dict[str, Any])
async def reject_purchase_order(
    purchase_order_id: int = Path(..., gt=0, description="Purchase order ID"),
    rejection_request: RejectionRequest,
    service: PurchaseOrderService = Depends(get_purchase_order_service),
    user_id: int = Depends(get_current_user_id)
):
    """
    Reject a purchase order.
    
    Rejects the purchase order and provides a rejection reason.
    """
    try:
        success = service.reject_purchase_order(
            purchase_order_id=purchase_order_id,
            rejected_by_user_id=user_id,
            rejection_reason=rejection_request.rejection_reason
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to reject purchase order")
        
        return {
            "success": True,
            "message": "Purchase order rejected successfully",
            "data": {
                "purchase_order_id": purchase_order_id,
                "status": PurchaseOrderStatus.REJECTED.value,
                "rejected_by_user_id": user_id,
                "rejection_reason": rejection_request.rejection_reason
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reject purchase order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@purchase_orders_router.post("/{purchase_order_id}/send", response_model=Dict[str, Any])
async def send_to_supplier(
    purchase_order_id: int = Path(..., gt=0, description="Purchase order ID"),
    delivery_method: str = Query("email", description="Delivery method"),
    service: PurchaseOrderService = Depends(get_purchase_order_service),
    user_id: int = Depends(get_current_user_id)
):
    """
    Send approved purchase order to supplier.
    
    Sends the purchase order to the supplier via the specified delivery method.
    """
    try:
        success = service.send_to_supplier(
            purchase_order_id=purchase_order_id,
            sent_by_user_id=user_id,
            delivery_method=delivery_method
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to send purchase order to supplier")
        
        return {
            "success": True,
            "message": "Purchase order sent to supplier successfully",
            "data": {
                "purchase_order_id": purchase_order_id,
                "status": PurchaseOrderStatus.SENT_TO_SUPPLIER.value,
                "delivery_method": delivery_method
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send purchase order to supplier: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@purchase_orders_router.put("/{purchase_order_id}/status", response_model=Dict[str, Any])
async def update_delivery_status(
    purchase_order_id: int = Path(..., gt=0, description="Purchase order ID"),
    status_update: StatusUpdateRequest,
    service: PurchaseOrderService = Depends(get_purchase_order_service),
    user_id: int = Depends(get_current_user_id)
):
    """
    Update delivery status of purchase order.
    
    Updates the purchase order status for delivery tracking.
    """
    try:
        success = service.update_delivery_status(
            purchase_order_id=purchase_order_id,
            status=status_update.status,
            updated_by_user_id=user_id,
            delivery_notes=status_update.delivery_notes
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update delivery status")
        
        return {
            "success": True,
            "message": "Delivery status updated successfully",
            "data": {
                "purchase_order_id": purchase_order_id,
                "status": status_update.status.value,
                "updated_by_user_id": user_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update delivery status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@purchase_orders_router.get("/statistics/summary", response_model=Dict[str, Any])
async def get_purchase_order_statistics(
    service: PurchaseOrderService = Depends(get_purchase_order_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get purchase order statistics for the current company.
    
    Returns summary statistics including totals, averages, and status breakdown.
    """
    try:
        stats = service.get_purchase_order_statistics(company_id)
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get purchase order statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")