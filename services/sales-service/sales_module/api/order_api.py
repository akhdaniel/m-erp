"""
Order API endpoints for sales order management.

Provides REST API endpoints for order lifecycle including creation,
confirmation, fulfillment, shipping, invoicing, and payment processing
with full inventory integration.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
import logging
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from sales_module.models import (
    SalesOrder, SalesOrderLineItem, OrderShipment, OrderInvoice,
    OrderStatus, PaymentStatus, ShipmentStatus, InvoiceStatus
)
from sales_module.services import OrderService
from sales_module.framework.database import get_db_session
from sales_module.framework.auth import get_current_user_id, get_current_company_id

logger = logging.getLogger(__name__)
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


# Analytics endpoints (must be defined before /{order_id} to avoid route conflicts)
@router.get("/stats", response_model=Dict[str, Any])
async def get_order_stats(
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get order statistics for dashboard widgets.
    
    Returns key order metrics including pending orders count,
    status distribution, and other KPI data.
    """
    try:
        # Get comprehensive order analytics
        analytics = order_service.get_order_analytics(company_id=company_id)
        
        # Return focused stats for dashboard widgets
        stats = {
            "pending_orders": analytics.get("pending_orders_count", 0),
            "total_orders": analytics.get("total_orders", 0),
            "confirmed_orders": analytics.get("confirmed_orders", 0),
            "shipped_orders": analytics.get("shipped_orders", 0),
            "completed_orders": analytics.get("completed_orders", 0),
            "cancelled_orders": analytics.get("cancelled_orders", 0),
            "total_revenue": float(analytics.get("total_revenue", 0)),
            "average_order_value": float(analytics.get("average_order_value", 0)),
            "orders_this_month": analytics.get("orders_this_month", 0),
            "revenue_this_month": float(analytics.get("revenue_this_month", 0)),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting order stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve order statistics"
        )


@router.get("/analytics/revenue-trend", response_model=Dict[str, Any])
async def get_revenue_trend(
    period: Optional[str] = Query("last_30_days", description="Time period: last_7_days, last_30_days, last_90_days"),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get revenue trend data for chart widgets.
    
    Returns time-series revenue data for trend analysis and charts.
    """
    try:
        # Calculate date range based on period
        today = date.today()
        if period == "last_7_days":
            start_date = today - timedelta(days=7)
            granularity = "daily"
        elif period == "last_30_days":
            start_date = today - timedelta(days=30)
            granularity = "daily"
        elif period == "last_90_days":
            start_date = today - timedelta(days=90)
            granularity = "weekly"
        else:
            start_date = today - timedelta(days=30)
            granularity = "daily"

        # Generate sample trend data with realistic patterns
        trend_data = []
        current_date = start_date
        
        while current_date <= today:
            # Generate sample revenue data with business patterns
            base_revenue = 4000 + (current_date.day * 150) + ((current_date.weekday() + 1) * 180)
            
            # Weekend effect (lower sales)
            if current_date.weekday() >= 5:
                base_revenue *= 0.6
            
            # Month-end spike
            if current_date.day >= 28:
                base_revenue *= 1.3
                
            trend_data.append({
                "date": current_date.isoformat(),
                "revenue": round(float(base_revenue), 2),
                "orders_count": max(1, int(base_revenue / 280)),
                "average_order_value": 280.0
            })
            
            if granularity == "daily":
                current_date += timedelta(days=1)
            else:  # weekly
                current_date += timedelta(weeks=1)

        return {
            "data": trend_data,
            "period": period,
            "granularity": granularity,
            "summary": {
                "total_revenue": sum(d["revenue"] for d in trend_data),
                "total_orders": sum(d["orders_count"] for d in trend_data),
                "average_order_value": 280.0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting revenue trend: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve revenue trend data"
        )


@router.get("/analytics/top-customers", response_model=Dict[str, Any])
async def get_top_customers(
    limit: int = Query(10, ge=1, le=100, description="Number of top customers to return"),
    period: Optional[str] = Query("all_time", description="Time period: last_30_days, last_90_days, all_time"),
    company_id: int = Depends(get_current_company_id),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get top customers by revenue for analytics.
    
    Returns customer rankings with order counts and revenue metrics.
    """
    try:
        # Generate sample top customers data
        top_customers = []
        customer_names = [
            "Acme Corporation", "Global Industries", "Tech Solutions Inc",
            "Future Systems", "Digital Dynamics", "Enterprise Partners",
            "Innovation Labs", "Business Solutions Co", "Strategic Ventures",
            "Market Leaders Inc", "Growth Partners", "Success Industries"
        ]
        
        for i, name in enumerate(customer_names[:limit]):
            revenue = (12 - i) * 8500 + ((i + 1) * 1200)
            order_count = max(5, 30 - (i * 2))
            
            top_customers.append({
                "customer_id": 1000 + i,
                "customer_name": name,
                "order_count": order_count,
                "total_revenue": float(revenue),
                "average_order_value": float(revenue / order_count),
                "last_order_date": (date.today() - timedelta(days=i * 3)).isoformat()
            })
        
        return {
            "data": top_customers,
            "period": period,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting top customers: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve top customers data"
        )


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


# Analytics endpoints moved to before /{order_id} route to fix routing conflicts


# Duplicate /stats endpoint removed - now defined before /{order_id} route


# @router.get("/analytics/revenue-trend", response_model=Dict[str, Any])
# async def get_revenue_trend(
#     period: Optional[str] = Query("last_30_days", description="Time period: last_7_days, last_30_days, last_90_days"),
#     company_id: int = Depends(get_current_company_id),
#     order_service: OrderService = Depends(get_order_service)
# ):
#     """
#     Get revenue trend data for chart widgets.
#     
#     Returns time-series revenue data for trend analysis and charts.
#     """
#     try:
#         # Calculate date range based on period
#         today = date.today()
#         if period == "last_7_days":
#             start_date = today - timedelta(days=7)
#             granularity = "daily"
#         elif period == "last_30_days":
#             start_date = today - timedelta(days=30)
#             granularity = "daily"
#         elif period == "last_90_days":
#             start_date = today - timedelta(days=90)
#             granularity = "weekly"
#         else:
#             start_date = today - timedelta(days=30)
#             granularity = "daily"
# 
#         # Generate sample trend data with realistic patterns
#         trend_data = []
#         current_date = start_date
#         
#         while current_date <= today:
#             # Generate sample revenue data with business patterns
#             base_revenue = 4000 + (current_date.day * 150) + ((current_date.weekday() + 1) * 180)
#             
#             # Weekend effect (lower sales)
#             if current_date.weekday() >= 5:
#                 base_revenue *= 0.6
#             
#             # Month-end spike
#             if current_date.day >= 28:
#                 base_revenue *= 1.3
#                 
#             trend_data.append({
#                 "date": current_date.isoformat(),
#                 "revenue": round(float(base_revenue), 2),
#                 "orders_count": max(1, int(base_revenue / 280)),
#                 "average_order_value": 280.0
#             })
#             
#             if granularity == "daily":
#                 current_date += timedelta(days=1)
#             else:  # weekly
#                 current_date += timedelta(weeks=1)
# 
#         return {
#             "data": trend_data,
#             "period": period,
#             "granularity": granularity,
#             "total_revenue": sum(item["revenue"] for item in trend_data),
#             "total_orders": sum(item["orders_count"] for item in trend_data),
#             "period_growth": 12.5,  # Sample growth percentage
#             "chart_config": {
#                 "type": "line",
#                 "x_field": "date",
#                 "y_field": "revenue",
#                 "title": f"Revenue Trend ({period.replace('_', ' ').title()})",
#                 "color": "#10B981"
#             },
#             "last_updated": datetime.utcnow().isoformat()
#         }
#         
#     except Exception as e:
#         logger.error(f"Error getting revenue trend: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve revenue trend data"
#         )
# 
# 
# @router.get("/analytics/top-customers", response_model=Dict[str, Any])
# async def get_top_customers_orders(
#     limit: int = Query(5, ge=1, le=20, description="Number of top customers to return"),
#     period: Optional[str] = Query("current_month", description="Time period for analysis"),
#     company_id: int = Depends(get_current_company_id),
#     order_service: OrderService = Depends(get_order_service)
# ):
#     """
#     Get top customers by order revenue for analytics widgets.
#     
#     Returns customer performance data ranked by total order revenue.
#     """
#     try:
#         # Get analytics from service
#         analytics = order_service.get_order_analytics(
#             company_id=company_id,
#             period=period
#         )
# 
#         # Generate sample top customers data with realistic business patterns
#         top_customers = [
#             {
#                 "customer_name": "TechCorp Solutions", 
#                 "customer_id": 1,
#                 "order_count": 12,
#                 "total_revenue": 34500.0,
#                 "average_order": 2875.0,
#                 "last_order_date": "2025-01-07",
#                 "growth_rate": 18.3,
#                 "payment_status": "excellent"
#             },
#             {
#                 "customer_name": "Global Manufacturing Ltd",
#                 "customer_id": 2, 
#                 "order_count": 8,
#                 "total_revenue": 28900.0,
#                 "average_order": 3612.5,
#                 "last_order_date": "2025-01-06",
#                 "growth_rate": 25.7,
#                 "payment_status": "good"
#             },
#             {
#                 "customer_name": "Innovation Systems Inc",
#                 "customer_id": 3,
#                 "order_count": 15,
#                 "total_revenue": 22750.0,
#                 "average_order": 1516.67,
#                 "last_order_date": "2025-01-08",
#                 "growth_rate": 8.9,
#                 "payment_status": "good"
#             },
#             {
#                 "customer_name": "Metro Retail Group",
#                 "customer_id": 4,
#                 "order_count": 6,
#                 "total_revenue": 19200.0,
#                 "average_order": 3200.0,
#                 "last_order_date": "2025-01-05", 
#                 "growth_rate": -3.2,
#                 "payment_status": "fair"
#             },
#             {
#                 "customer_name": "Digital Ventures Co",
#                 "customer_id": 5,
#                 "order_count": 10,
#                 "total_revenue": 16800.0,
#                 "average_order": 1680.0,
#                 "last_order_date": "2025-01-04",
#                 "growth_rate": 14.1,
#                 "payment_status": "excellent"
#             }
#         ]
# 
#         return {
#             "data": top_customers[:limit],
#             "period": period,
#             "total_customers": len(top_customers),
#             "total_revenue": sum(customer["total_revenue"] for customer in top_customers[:limit]),
#             "total_orders": sum(customer["order_count"] for customer in top_customers[:limit]),
#             "config": {
#                 "title": f"Top Customers by Revenue ({period.replace('_', ' ').title()})",
#                 "columns": ["customer_name", "order_count", "total_revenue", "average_order"],
#                 "sortable": True,
#                 "link_pattern": "/sales/customers/{customer_id}"
#             },
#             "last_updated": datetime.utcnow().isoformat()
#         }
#         
#     except Exception as e:
#         logger.error(f"Error getting top customers: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to retrieve top customers data"
#         )