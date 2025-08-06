"""
Order API endpoints for sales order management.

Provides REST API endpoints for order lifecycle including creation,
confirmation, fulfillment, shipping, invoicing, and payment processing
with full inventory integration.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from sales_module.models import (
    SalesOrder, SalesOrderLineItem, OrderShipment, OrderInvoice,
    OrderStatus, PaymentStatus, ShipmentStatus, InvoiceStatus
)
from sales_module.services import OrderService
from sales_module.framework.database import get_db_session
from sales_module.framework.auth import get_current_user_id, get_current_company_id

router = APIRouter(prefix="/orders", tags=["orders"])


# Pydantic schemas for request/response models
class OrderLineItemCreate(BaseModel):
    product_id: Optional[int] = None
    product_variant_id: Optional[int] = None
    item_code: Optional[str] = Field(None, max_length=100)
    item_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    quantity: Decimal = Field(..., gt=0)
    unit_of_measure: str = Field(default="each", max_length=50)
    unit_price: Decimal = Field(..., ge=0)
    list_price: Optional[Decimal] = Field(None, ge=0)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Decimal = Field(default=0.0, ge=0, le=100)
    discount_amount: Decimal = Field(default=0.0, ge=0)
    tax_percentage: Decimal = Field(default=0.0, ge=0, le=100)
    tax_code: Optional[str] = Field(None, max_length=50)
    specifications: Optional[Dict[str, Any]] = None
    custom_options: Optional[Dict[str, Any]] = None
    lead_time_days: Optional[int] = Field(None, ge=0)
    delivery_date: Optional[datetime] = None
    notes: Optional[str] = None


class OrderCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    customer_id: int = Field(..., gt=0)
    opportunity_id: Optional[int] = Field(None, gt=0)
    quote_id: Optional[int] = Field(None, gt=0)
    
    # Order details
    order_date: Optional[datetime] = None
    required_date: Optional[datetime] = None
    sales_rep_user_id: Optional[int] = Field(None, gt=0)
    
    # Financial information
    currency_code: str = Field(default="USD", max_length=3)
    payment_terms_days: int = Field(default=30, ge=0)
    
    # Addresses
    billing_address: Optional[Dict[str, Any]] = None
    shipping_address: Optional[Dict[str, Any]] = None
    
    # Priority and preferences
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    shipping_method: Optional[str] = Field(None, max_length=100)
    delivery_instructions: Optional[str] = None
    
    # Additional information
    internal_notes: Optional[str] = None
    customer_po_number: Optional[str] = Field(None, max_length=100)
    terms_and_conditions: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    # Line items
    line_items: Optional[List[OrderLineItemCreate]] = None


class OrderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    required_date: Optional[datetime] = None
    sales_rep_user_id: Optional[int] = Field(None, gt=0)
    
    # Addresses can be updated
    billing_address: Optional[Dict[str, Any]] = None
    shipping_address: Optional[Dict[str, Any]] = None
    
    # Priority and preferences
    priority: Optional[str] = Field(None, pattern="^(low|normal|high|urgent)$")
    shipping_method: Optional[str] = Field(None, max_length=100)
    delivery_instructions: Optional[str] = None
    
    # Additional information
    internal_notes: Optional[str] = None
    customer_po_number: Optional[str] = Field(None, max_length=100)
    terms_and_conditions: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class OrderFromQuoteCreate(BaseModel):
    quote_id: int = Field(..., gt=0)
    order_data: Optional[OrderUpdate] = None


class OrderResponse(BaseModel):
    id: int
    order_number: str
    title: str
    description: Optional[str]
    customer_id: int
    opportunity_id: Optional[int]
    quote_id: Optional[int]
    
    # Status and workflow
    status: OrderStatus
    payment_status: PaymentStatus
    
    # Dates
    order_date: datetime
    required_date: Optional[datetime]
    confirmed_date: Optional[datetime]
    shipped_date: Optional[datetime]
    delivered_date: Optional[datetime]
    completed_date: Optional[datetime]
    
    # Financial information
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    currency_code: str
    payment_terms_days: int
    
    # Paid amounts
    paid_amount: Decimal
    outstanding_amount: Decimal
    
    # Fulfillment tracking
    items_shipped: int
    items_remaining: int
    shipment_count: int
    invoice_count: int
    
    # Addresses
    billing_address: Optional[Dict[str, Any]]
    shipping_address: Optional[Dict[str, Any]]
    
    # Priority and preferences
    priority: str
    shipping_method: Optional[str]
    delivery_instructions: Optional[str]
    
    # People
    sales_rep_user_id: Optional[int]
    
    # Additional information
    internal_notes: Optional[str]
    customer_po_number: Optional[str]
    terms_and_conditions: Optional[str]
    custom_fields: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    
    # System fields
    is_active: bool
    hold_status: bool
    hold_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderLineItemResponse(BaseModel):
    id: int
    order_id: int
    line_number: int
    line_type: str
    product_id: Optional[int]
    product_variant_id: Optional[int]
    item_code: Optional[str]
    item_name: str
    description: Optional[str]
    quantity: Decimal
    unit_of_measure: str
    unit_price: Decimal
    list_price: Optional[Decimal]
    unit_cost: Optional[Decimal]
    discount_percentage: Decimal
    discount_amount: Decimal
    line_total: Decimal
    line_cost: Optional[Decimal]
    tax_percentage: Decimal
    tax_amount: Decimal
    tax_code: Optional[str]
    quantity_shipped: Optional[Decimal]
    quantity_invoiced: Optional[Decimal]
    specifications: Optional[Dict[str, Any]]
    custom_options: Optional[Dict[str, Any]]
    lead_time_days: Optional[int]
    delivery_date: Optional[datetime]
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ShipmentCreate(BaseModel):
    tracking_number: Optional[str] = Field(None, max_length=100)
    carrier: Optional[str] = Field(None, max_length=100)
    shipping_method: Optional[str] = Field(None, max_length=100)
    shipped_date: Optional[datetime] = None
    estimated_delivery_date: Optional[datetime] = None
    shipping_address: Optional[Dict[str, Any]] = None
    weight_kg: Optional[Decimal] = Field(None, ge=0)
    dimensions: Optional[Dict[str, Any]] = None
    shipping_cost: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
    line_item_shipments: List[Dict[str, Any]] = Field(..., min_items=1)


class ShipmentResponse(BaseModel):
    id: int
    order_id: int
    shipment_number: str
    status: ShipmentStatus
    tracking_number: Optional[str]
    carrier: Optional[str]
    shipping_method: Optional[str]
    shipped_date: Optional[datetime]
    estimated_delivery_date: Optional[datetime]
    actual_delivery_date: Optional[datetime]
    delivered_to: Optional[str]
    shipping_address: Optional[Dict[str, Any]]
    weight_kg: Optional[Decimal]
    dimensions: Optional[Dict[str, Any]]
    shipping_cost: Optional[Decimal]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    payment_terms_days: Optional[int] = Field(None, ge=0)
    billing_address: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class InvoiceResponse(BaseModel):
    id: int
    order_id: int
    invoice_number: str
    status: InvoiceStatus
    invoice_date: datetime
    due_date: datetime
    sent_date: Optional[datetime]
    payment_terms_days: int
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal
    currency_code: str
    billing_address: Optional[Dict[str, Any]]
    line_items_data: Optional[List[Dict[str, Any]]]
    notes: Optional[str]
    custom_fields: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    payment_amount: Decimal = Field(..., gt=0)
    payment_method: Optional[str] = Field(None, max_length=50)
    payment_reference: Optional[str] = Field(None, max_length=100)
    invoice_id: Optional[int] = Field(None, gt=0)
    notes: Optional[str] = None


class OrderHoldRequest(BaseModel):
    reason: str = Field(..., min_length=1)


# Dependency injection
def get_order_service(
    db: Session = Depends(get_db_session)
) -> OrderService:
    return OrderService(db_session=db)


# Order CRUD endpoints
@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    order_data: OrderCreate,
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Create a new sales order."""
    try:
        # Extract line items
        line_items_data = []
        if order_data.line_items:
            line_items_data = [item.dict() for item in order_data.line_items]
        
        # Remove line_items from order_data for service call
        order_dict = order_data.dict()
        order_dict.pop('line_items', None)
        
        order = order_service.create_order(
            order_data=order_dict,
            line_items=line_items_data,
            user_id=user_id,
            company_id=company_id
        )
        order_service.commit()
        
        return OrderResponse.from_orm(order)
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/from-quote", response_model=OrderResponse, status_code=201)
async def create_order_from_quote(
    request_data: OrderFromQuoteCreate,
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Create a sales order from an accepted quote."""
    try:
        order_data = request_data.order_data.dict() if request_data.order_data else {}
        
        order = order_service.create_order_from_quote(
            quote_id=request_data.quote_id,
            order_data=order_data,
            user_id=user_id,
            company_id=company_id
        )
        order_service.commit()
        
        return OrderResponse.from_orm(order)
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    sales_rep_id: Optional[int] = Query(None, description="Filter by sales rep ID"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    date_from: Optional[datetime] = Query(None, description="Filter orders from date"),
    date_to: Optional[datetime] = Query(None, description="Filter orders to date"),
    limit: int = Query(100, ge=1, le=1000, description="Number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip"),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """List sales orders with filtering options."""
    filters = {}
    if status:
        filters['status'] = status
    if customer_id:
        filters['customer_id'] = customer_id
    if sales_rep_id:
        filters['sales_rep_user_id'] = sales_rep_id
    if priority:
        filters['priority'] = priority
    if date_from:
        filters['order_date_from'] = date_from
    if date_to:
        filters['order_date_to'] = date_to
    
    orders = order_service.get_all(
        company_id=company_id,
        filters=filters,
        limit=limit,
        offset=offset
    )
    
    return [OrderResponse.from_orm(order) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int = Path(..., description="Order ID"),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Get order by ID."""
    order = order_service.get_by_id_or_raise(SalesOrder, order_id, company_id)
    return OrderResponse.from_orm(order)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int = Path(..., description="Order ID"),
    order_data: OrderUpdate = ...,
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Update order details."""
    try:
        order = order_service.get_by_id_or_raise(SalesOrder, order_id, company_id)
        updated_order = order_service.update(order, order_data.dict(exclude_unset=True), user_id)
        order_service.commit()
        
        return OrderResponse.from_orm(updated_order)
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Order lifecycle endpoints
@router.put("/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(
    order_id: int = Path(..., description="Order ID"),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Confirm order and reserve inventory."""
    try:
        order = order_service.confirm_order(order_id, user_id, company_id)
        order_service.commit()
        
        return OrderResponse.from_orm(order)
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{order_id}/hold", response_model=OrderResponse)
async def put_order_on_hold(
    order_id: int = Path(..., description="Order ID"),
    hold_request: OrderHoldRequest = ...,
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Put order on hold."""
    try:
        order = order_service.put_order_on_hold(order_id, hold_request.reason, user_id, company_id)
        order_service.commit()
        
        return OrderResponse.from_orm(order)
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{order_id}/release-hold", response_model=OrderResponse)
async def release_order_hold(
    order_id: int = Path(..., description="Order ID"),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Release order from hold."""
    try:
        order = order_service.release_order_hold(order_id, user_id, company_id)
        order_service.commit()
        
        return OrderResponse.from_orm(order)
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int = Path(..., description="Order ID"),
    cancellation_reason: str = Body(..., embed=True, min_length=1),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Cancel order and release inventory."""
    try:
        order = order_service.cancel_order(order_id, cancellation_reason, user_id, company_id)
        order_service.commit()
        
        return OrderResponse.from_orm(order)
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Inventory integration endpoints
@router.get("/{order_id}/inventory-availability", response_model=Dict[str, Any])
async def check_order_inventory_availability(
    order_id: int = Path(..., description="Order ID"),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Check inventory availability for all items in order."""
    try:
        availability = order_service.check_inventory_availability(order_id, company_id)
        return availability
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{order_id}/release-inventory", response_model=Dict[str, Any])
async def release_order_inventory(
    order_id: int = Path(..., description="Order ID"),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Release inventory reservations for order."""
    try:
        success = order_service.release_order_inventory(order_id, user_id, company_id)
        order_service.commit()
        
        return {"success": success, "message": "Inventory reservations released"}
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Fulfillment endpoints
@router.get("/{order_id}/fulfillment-status", response_model=Dict[str, Any])
async def get_order_fulfillment_status(
    order_id: int = Path(..., description="Order ID"),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Get comprehensive order fulfillment status."""
    status = order_service.get_order_fulfillment_status(order_id, company_id)
    if not status:
        raise HTTPException(status_code=404, detail="Order not found")
    return status


@router.get("/{order_id}/line-items", response_model=List[OrderLineItemResponse])
async def get_order_line_items(
    order_id: int = Path(..., description="Order ID"),
    active_only: bool = Query(True, description="Show only active line items"),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Get order line items."""
    order = order_service.get_by_id_or_raise(SalesOrder, order_id, company_id)
    
    line_items = order.line_items
    if active_only:
        line_items = [item for item in line_items if item.is_active]
    
    return [OrderLineItemResponse.from_orm(item) for item in line_items]


@router.post("/{order_id}/line-items", response_model=OrderLineItemResponse, status_code=201)
async def add_order_line_item(
    order_id: int = Path(..., description="Order ID"),
    line_item_data: OrderLineItemCreate = ...,
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Add line item to order."""
    try:
        line_item = order_service.add_line_item(
            order_id=order_id,
            line_item_data=line_item_data.dict(),
            user_id=user_id,
            company_id=company_id
        )
        if not line_item:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order_service.commit()
        return OrderLineItemResponse.from_orm(line_item)
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Shipment endpoints
@router.post("/{order_id}/shipments", response_model=ShipmentResponse, status_code=201)
async def create_shipment(
    order_id: int = Path(..., description="Order ID"),
    shipment_data: ShipmentCreate = ...,
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Create shipment for order items."""
    try:
        # Extract line item shipments
        line_item_shipments = shipment_data.line_item_shipments
        
        # Remove from shipment data for service call
        shipment_dict = shipment_data.dict()
        shipment_dict.pop('line_item_shipments')
        
        shipment = order_service.ship_order_items(
            order_id=order_id,
            shipment_data=shipment_dict,
            line_item_shipments=line_item_shipments,
            user_id=user_id,
            company_id=company_id
        )
        
        if not shipment:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order_service.commit()
        return ShipmentResponse.from_orm(shipment)
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/shipments/{shipment_id}/tracking", response_model=Dict[str, Any])
async def update_shipment_tracking(
    shipment_id: int = Path(..., description="Shipment ID"),
    tracking_number: str = Body(..., embed=True, min_length=1),
    carrier: Optional[str] = Body(None, embed=True),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Update shipment tracking information."""
    try:
        shipment = order_service.update_shipment_tracking(
            shipment_id=shipment_id,
            tracking_number=tracking_number,
            carrier=carrier,
            user_id=user_id,
            company_id=company_id
        )
        order_service.commit()
        
        return {"success": True, "message": "Tracking information updated"}
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/shipments/{shipment_id}/delivered", response_model=Dict[str, Any])
async def mark_shipment_delivered(
    shipment_id: int = Path(..., description="Shipment ID"),
    delivered_to: Optional[str] = Body(None, embed=True),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Mark shipment as delivered."""
    try:
        shipment = order_service.mark_shipment_delivered(
            shipment_id=shipment_id,
            delivered_to=delivered_to,
            user_id=user_id,
            company_id=company_id
        )
        order_service.commit()
        
        return {"success": True, "message": "Shipment marked as delivered"}
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Invoice endpoints
@router.post("/{order_id}/invoices", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    order_id: int = Path(..., description="Order ID"),
    invoice_data: InvoiceCreate = ...,
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Create invoice for order."""
    try:
        invoice = order_service.create_invoice(
            order_id=order_id,
            invoice_data=invoice_data.dict(exclude_unset=True),
            user_id=user_id,
            company_id=company_id
        )
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order_service.commit()
        return InvoiceResponse.from_orm(invoice)
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/invoices/{invoice_id}/send", response_model=Dict[str, Any])
async def send_invoice(
    invoice_id: int = Path(..., description="Invoice ID"),
    email_template: Optional[str] = Body(None, embed=True),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Send invoice to customer."""
    try:
        invoice = order_service.send_invoice(
            invoice_id=invoice_id,
            email_template=email_template,
            user_id=user_id,
            company_id=company_id
        )
        order_service.commit()
        
        return {"success": True, "message": "Invoice sent to customer"}
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Payment endpoints
@router.post("/{order_id}/payments", response_model=OrderResponse)
async def record_payment(
    order_id: int = Path(..., description="Order ID"),
    payment_data: PaymentCreate = ...,
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Record payment against order."""
    try:
        order = order_service.record_payment(
            order_id=order_id,
            payment_amount=payment_data.payment_amount,
            payment_method=payment_data.payment_method,
            invoice_id=payment_data.invoice_id,
            user_id=user_id,
            company_id=company_id
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order_service.commit()
        return OrderResponse.from_orm(order)
        
    except Exception as e:
        order_service.rollback()
        raise HTTPException(status_code=400, detail=str(e))


# Analytics endpoints
@router.get("/analytics/summary", response_model=Dict[str, Any])
async def get_order_analytics(
    date_from: Optional[datetime] = Query(None, description="Analytics from date"),
    date_to: Optional[datetime] = Query(None, description="Analytics to date"),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """Get order analytics and metrics."""
    date_range = {}
    if date_from:
        date_range['from'] = date_from
    if date_to:
        date_range['to'] = date_to
    
    analytics = order_service.get_order_analytics(
        company_id=company_id,
        date_range=date_range if date_range else None
    )
    
    return analytics