"""
Purchase Order schemas for API request/response validation.

Provides comprehensive validation schemas for all purchase order operations
including creation, updates, line items, and responses.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum

from purchasing_module.models.purchase_order import PurchaseOrderStatus, PurchaseOrderPriority


# Base schemas for common fields
class BasePurchaseOrderSchema(BaseModel):
    """Base schema with common purchase order fields."""
    
    title: str = Field(..., description="Purchase order title", max_length=255)
    description: Optional[str] = Field(None, description="Purchase order description")
    supplier_id: int = Field(..., description="Supplier/partner ID", gt=0)
    currency_code: str = Field("USD", description="Currency code", max_length=3)
    
    class Config:
        from_attributes = True
        use_enum_values = True


# Line item schemas
class PurchaseOrderLineItemBase(BaseModel):
    """Base schema for purchase order line items."""
    
    product_code: Optional[str] = Field(None, description="Product code/SKU", max_length=100)
    description: str = Field(..., description="Item description")
    unit_of_measure: str = Field("each", description="Unit of measure", max_length=20)
    quantity_ordered: Decimal = Field(..., description="Quantity to order", gt=0)
    unit_price: Decimal = Field(..., description="Unit price", ge=0)
    required_date: Optional[datetime] = Field(None, description="Required delivery date")
    promised_date: Optional[datetime] = Field(None, description="Supplier promised date")
    notes: Optional[str] = Field(None, description="Line item notes")
    supplier_part_number: Optional[str] = Field(None, description="Supplier's part number", max_length=100)
    
    @validator('quantity_ordered', 'unit_price')
    def validate_decimals(cls, v):
        """Ensure proper decimal precision."""
        if v is not None:
            # Round to appropriate decimal places
            if isinstance(v, Decimal):
                return v.quantize(Decimal('0.01'))
        return v
    
    @validator('promised_date')
    def validate_dates(cls, v, values):
        """Ensure promised date is after or equal to required date if both are provided."""
        if v and 'required_date' in values and values['required_date']:
            if v < values['required_date']:
                raise ValueError('Promised date cannot be before required date')
        return v
    
    class Config:
        from_attributes = True


class PurchaseOrderLineItemCreate(PurchaseOrderLineItemBase):
    """Schema for creating purchase order line items."""
    pass


class PurchaseOrderLineItemUpdate(BaseModel):
    """Schema for updating purchase order line items."""
    
    product_code: Optional[str] = Field(None, description="Product code/SKU", max_length=100)
    description: Optional[str] = Field(None, description="Item description")
    unit_of_measure: Optional[str] = Field(None, description="Unit of measure", max_length=20)
    quantity_ordered: Optional[Decimal] = Field(None, description="Quantity to order", gt=0)
    unit_price: Optional[Decimal] = Field(None, description="Unit price", ge=0)
    required_date: Optional[datetime] = Field(None, description="Required delivery date")
    promised_date: Optional[datetime] = Field(None, description="Supplier promised date")
    notes: Optional[str] = Field(None, description="Line item notes")
    supplier_part_number: Optional[str] = Field(None, description="Supplier's part number", max_length=100)
    
    class Config:
        from_attributes = True


class PurchaseOrderLineItemResponse(PurchaseOrderLineItemBase):
    """Schema for purchase order line item responses."""
    
    id: int
    purchase_order_id: int
    line_number: int
    quantity_received: Decimal = Field(default=0, description="Quantity received")
    line_total: Decimal = Field(..., description="Line total amount")
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Purchase Order schemas
class PurchaseOrderCreate(BasePurchaseOrderSchema):
    """Schema for creating new purchase orders."""
    
    po_number: Optional[str] = Field(None, description="PO number (auto-generated if empty)", max_length=50)
    supplier_contact_id: Optional[int] = Field(None, description="Supplier contact ID", gt=0)
    
    # Financial information
    exchange_rate: Optional[Decimal] = Field(1.0, description="Exchange rate", gt=0)
    shipping_amount: Optional[Decimal] = Field(0, description="Shipping amount", ge=0)
    discount_amount: Optional[Decimal] = Field(0, description="Discount amount", ge=0)
    
    # Status and priority
    priority: Optional[PurchaseOrderPriority] = Field(PurchaseOrderPriority.NORMAL, description="Order priority")
    
    # Dates
    order_date: Optional[datetime] = Field(None, description="Order date (defaults to now)")
    required_date: Optional[datetime] = Field(None, description="Required delivery date")
    
    # Additional information
    terms_and_conditions: Optional[str] = Field(None, description="Terms and conditions")
    notes: Optional[str] = Field(None, description="External notes for supplier")
    internal_notes: Optional[str] = Field(None, description="Internal notes")
    reference_number: Optional[str] = Field(None, description="Reference number", max_length=100)
    
    # Delivery information
    delivery_address: Optional[str] = Field(None, description="Delivery address")
    delivery_contact: Optional[str] = Field(None, description="Delivery contact name", max_length=255)
    delivery_phone: Optional[str] = Field(None, description="Delivery contact phone", max_length=50)
    delivery_instructions: Optional[str] = Field(None, description="Delivery instructions")
    
    # Line items
    items: Optional[List[PurchaseOrderLineItemCreate]] = Field(None, description="Line items")
    
    @validator('required_date')
    def validate_required_date(cls, v, values):
        """Ensure required date is in the future."""
        if v and 'order_date' in values:
            order_date = values['order_date'] or datetime.utcnow()
            if v < order_date:
                raise ValueError('Required date must be after order date')
        return v


class PurchaseOrderUpdate(BaseModel):
    """Schema for updating existing purchase orders."""
    
    title: Optional[str] = Field(None, description="Purchase order title", max_length=255)
    description: Optional[str] = Field(None, description="Purchase order description")
    supplier_contact_id: Optional[int] = Field(None, description="Supplier contact ID", gt=0)
    
    # Financial information
    shipping_amount: Optional[Decimal] = Field(None, description="Shipping amount", ge=0)
    discount_amount: Optional[Decimal] = Field(None, description="Discount amount", ge=0)
    
    # Priority
    priority: Optional[PurchaseOrderPriority] = Field(None, description="Order priority")
    
    # Dates
    required_date: Optional[datetime] = Field(None, description="Required delivery date")
    promised_date: Optional[datetime] = Field(None, description="Supplier promised date")
    
    # Additional information
    terms_and_conditions: Optional[str] = Field(None, description="Terms and conditions")
    notes: Optional[str] = Field(None, description="External notes for supplier")
    internal_notes: Optional[str] = Field(None, description="Internal notes")
    reference_number: Optional[str] = Field(None, description="Reference number", max_length=100)
    
    # Delivery information
    delivery_address: Optional[str] = Field(None, description="Delivery address")
    delivery_contact: Optional[str] = Field(None, description="Delivery contact name", max_length=255)
    delivery_phone: Optional[str] = Field(None, description="Delivery contact phone", max_length=50)
    delivery_instructions: Optional[str] = Field(None, description="Delivery instructions")
    
    # Line items (for bulk update)
    items: Optional[List[PurchaseOrderLineItemCreate]] = Field(None, description="Replace all line items")
    
    class Config:
        from_attributes = True
        use_enum_values = True


class PurchaseOrderResponse(BasePurchaseOrderSchema):
    """Schema for complete purchase order responses."""
    
    # Primary fields
    id: int
    po_number: str
    supplier_contact_id: Optional[int]
    
    # Financial information
    exchange_rate: Decimal
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    
    # Status and workflow
    status: PurchaseOrderStatus
    priority: PurchaseOrderPriority
    
    # Dates
    order_date: datetime
    required_date: Optional[datetime]
    promised_date: Optional[datetime]
    approved_date: Optional[datetime]
    sent_date: Optional[datetime]
    
    # Approval information
    approved_by_user_id: Optional[int]
    approval_notes: Optional[str]
    
    # Additional information
    terms_and_conditions: Optional[str]
    notes: Optional[str]
    internal_notes: Optional[str]
    reference_number: Optional[str]
    
    # Delivery information
    delivery_address: Optional[str]
    delivery_contact: Optional[str]
    delivery_phone: Optional[str]
    delivery_instructions: Optional[str]
    
    # Tracking
    is_active: bool
    company_id: int
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Related data
    line_items: Optional[List[PurchaseOrderLineItemResponse]] = None
    
    # Computed properties
    is_approved: Optional[bool] = None
    is_editable: Optional[bool] = None
    can_be_cancelled: Optional[bool] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True
        
    def __init__(self, **data):
        super().__init__(**data)
        # Set computed properties if source object is available
        if 'is_approved' not in data and 'status' in data:
            self.is_approved = data['status'] in [
                PurchaseOrderStatus.APPROVED,
                PurchaseOrderStatus.SENT_TO_SUPPLIER,
                PurchaseOrderStatus.ACKNOWLEDGED,
                PurchaseOrderStatus.PARTIALLY_RECEIVED,
                PurchaseOrderStatus.RECEIVED,
                PurchaseOrderStatus.INVOICED,
                PurchaseOrderStatus.COMPLETED
            ]
        if 'is_editable' not in data and 'status' in data:
            self.is_editable = data['status'] in [
                PurchaseOrderStatus.DRAFT,
                PurchaseOrderStatus.REJECTED
            ]
        if 'can_be_cancelled' not in data and 'status' in data:
            self.can_be_cancelled = data['status'] not in [
                PurchaseOrderStatus.RECEIVED,
                PurchaseOrderStatus.INVOICED,
                PurchaseOrderStatus.COMPLETED,
                PurchaseOrderStatus.CANCELLED
            ]


class PurchaseOrderListResponse(BaseModel):
    """Schema for paginated purchase order list responses."""
    
    data: List[PurchaseOrderResponse]  # Standardized to use 'data' key
    total_count: int
    page: int
    page_size: int
    total_pages: int


class PurchaseOrderApprovalRequest(BaseModel):
    """Schema for approving/rejecting purchase orders."""
    
    action: str = Field(..., description="Action to take", pattern="^(approve|reject)$")
    notes: Optional[str] = Field(None, description="Approval/rejection notes", max_length=1000)
    
    @validator('action')
    def validate_action(cls, v):
        if v not in ['approve', 'reject']:
            raise ValueError('Action must be either "approve" or "reject"')
        return v


class PurchaseOrderStatusUpdate(BaseModel):
    """Schema for updating purchase order status."""
    
    status: PurchaseOrderStatus = Field(..., description="New status")
    notes: Optional[str] = Field(None, description="Status change notes", max_length=1000)
    
    class Config:
        use_enum_values = True


class PurchaseOrderSendRequest(BaseModel):
    """Schema for sending purchase order to supplier."""
    
    send_method: str = Field("email", description="Method to send PO", pattern="^(email|fax|api)$")
    email_to: Optional[str] = Field(None, description="Email address to send to")
    email_cc: Optional[List[str]] = Field(None, description="CC email addresses")
    message: Optional[str] = Field(None, description="Message to include", max_length=2000)
    
    @validator('email_to')
    def validate_email(cls, v, values):
        if values.get('send_method') == 'email' and not v:
            raise ValueError('Email address is required when send_method is "email"')
        return v