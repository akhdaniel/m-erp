"""
Quote-related Pydantic schemas for API request/response validation.

Provides comprehensive validation schemas for all quote operations
including creation, updates, line items, approvals, and responses.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum

from sales_module.models import QuoteStatus, ApprovalStatus


# Base schemas for common fields
class BaseQuoteSchema(BaseModel):
    """Base schema with common quote fields."""
    
    title: str = Field(..., description="Quote title", max_length=200)
    description: Optional[str] = Field(None, description="Quote description", max_length=1000)
    customer_id: int = Field(..., description="Customer/partner ID", gt=0)
    currency_code: str = Field("USD", description="Currency code", max_length=3)
    
    class Config:
        from_attributes = True


# Request schemas
class QuoteCreateRequest(BaseQuoteSchema):
    """Schema for creating new quotes."""
    
    quote_number: Optional[str] = Field(None, description="Quote number (auto-generated if empty)", max_length=50)
    contact_person: Optional[str] = Field(None, description="Customer contact person", max_length=100)
    contact_email: Optional[str] = Field(None, description="Customer contact email", max_length=255)
    contact_phone: Optional[str] = Field(None, description="Customer contact phone", max_length=50)
    
    # Validity dates
    valid_from: Optional[datetime] = Field(None, description="Quote valid from date")
    valid_until: Optional[datetime] = Field(None, description="Quote valid until date")
    
    # Terms and conditions
    payment_terms: Optional[str] = Field(None, description="Payment terms", max_length=200)
    delivery_terms: Optional[str] = Field(None, description="Delivery terms", max_length=200)
    special_instructions: Optional[str] = Field(None, description="Special instructions", max_length=1000)
    
    # Pricing settings
    requires_approval: bool = Field(False, description="Whether quote requires approval")
    is_template: bool = Field(False, description="Whether this is a template quote")
    
    @validator('valid_until')
    def validate_dates(cls, v, values):
        if v and 'valid_from' in values and values['valid_from']:
            if v <= values['valid_from']:
                raise ValueError('Valid until date must be after valid from date')
        return v


class QuoteUpdateRequest(BaseModel):
    """Schema for updating existing quotes."""
    
    title: Optional[str] = Field(None, description="Quote title", max_length=200)
    description: Optional[str] = Field(None, description="Quote description", max_length=1000)
    contact_person: Optional[str] = Field(None, description="Customer contact person", max_length=100)
    contact_email: Optional[str] = Field(None, description="Customer contact email", max_length=255)
    contact_phone: Optional[str] = Field(None, description="Customer contact phone", max_length=50)
    
    valid_until: Optional[datetime] = Field(None, description="Quote valid until date")
    payment_terms: Optional[str] = Field(None, description="Payment terms", max_length=200)
    delivery_terms: Optional[str] = Field(None, description="Delivery terms", max_length=200)
    special_instructions: Optional[str] = Field(None, description="Special instructions", max_length=1000)
    
    class Config:
        from_attributes = True


# Line item schemas
class QuoteLineItemCreateRequest(BaseModel):
    """Schema for creating quote line items."""
    
    product_id: Optional[int] = Field(None, description="Product ID from inventory", gt=0)
    item_name: str = Field(..., description="Item name", max_length=200)
    item_code: Optional[str] = Field(None, description="Item code/SKU", max_length=100)
    description: Optional[str] = Field(None, description="Item description", max_length=1000)
    
    quantity: Decimal = Field(..., description="Quantity", gt=0)
    unit_of_measure: str = Field("each", description="Unit of measure", max_length=50)
    unit_price: Decimal = Field(..., description="Unit price", ge=0)
    unit_cost: Optional[Decimal] = Field(None, description="Unit cost", ge=0)
    
    discount_percentage: Optional[Decimal] = Field(None, description="Line discount percentage", ge=0, le=100)
    tax_percentage: Optional[Decimal] = Field(None, description="Tax percentage", ge=0, le=100)
    
    line_number: Optional[int] = Field(None, description="Line number (auto-assigned if empty)", gt=0)
    
    @validator('quantity', 'unit_price')
    def validate_decimals(cls, v):
        if v < 0:
            raise ValueError('Values must be non-negative')
        return v


class QuoteLineItemUpdateRequest(BaseModel):
    """Schema for updating quote line items."""
    
    quantity: Optional[Decimal] = Field(None, description="Quantity", gt=0)
    unit_price: Optional[Decimal] = Field(None, description="Unit price", ge=0)
    discount_percentage: Optional[Decimal] = Field(None, description="Line discount percentage", ge=0, le=100)
    description: Optional[str] = Field(None, description="Item description", max_length=1000)
    
    class Config:
        from_attributes = True


# Approval schemas
class QuoteApprovalRequest(BaseModel):
    """Schema for requesting quote approval."""
    
    approval_level: int = Field(1, description="Approval level required", ge=1, le=5)
    request_reason: Optional[str] = Field(None, description="Reason for approval request", max_length=500)
    urgency: str = Field("normal", description="Urgency level")
    
    @validator('urgency')
    def validate_urgency(cls, v):
        valid_urgencies = ['low', 'normal', 'high', 'urgent']
        if v not in valid_urgencies:
            raise ValueError(f'Urgency must be one of: {", ".join(valid_urgencies)}')
        return v


class QuoteApprovalAction(BaseModel):
    """Schema for approval actions."""
    
    action: str = Field(..., description="Approval action")
    notes: Optional[str] = Field(None, description="Approval notes", max_length=1000)
    escalate_to_user_id: Optional[int] = Field(None, description="User ID to escalate to", gt=0)
    
    @validator('action')
    def validate_action(cls, v):
        valid_actions = ['approve', 'reject', 'escalate']
        if v not in valid_actions:
            raise ValueError(f'Action must be one of: {", ".join(valid_actions)}')
        return v


# Other operation schemas
class QuoteDiscountRequest(BaseModel):
    """Schema for applying overall quote discount."""
    
    discount_percentage: Decimal = Field(..., description="Discount percentage", ge=0, le=100)
    reason: Optional[str] = Field(None, description="Reason for discount", max_length=500)


class QuoteSendRequest(BaseModel):
    """Schema for sending quote to customer."""
    
    email_template: Optional[str] = Field(None, description="Email template to use", max_length=100)
    send_copy_to: Optional[List[str]] = Field(None, description="Additional email addresses for copies")
    custom_message: Optional[str] = Field(None, description="Custom message", max_length=1000)


class QuoteVersionRequest(BaseModel):
    """Schema for creating quote version."""
    
    reason: Optional[str] = Field(None, description="Reason for new version", max_length=500)


class QuoteConversionRequest(BaseModel):
    """Schema for converting quote to order."""
    
    order_data: Optional[Dict[str, Any]] = Field(None, description="Additional order data")
    delivery_date: Optional[datetime] = Field(None, description="Requested delivery date")
    special_instructions: Optional[str] = Field(None, description="Special order instructions", max_length=1000)


class ValidityExtensionRequest(BaseModel):
    """Schema for extending quote validity."""
    
    additional_days: int = Field(..., description="Additional days to extend", gt=0, le=365)
    reason: Optional[str] = Field(None, description="Reason for extension", max_length=500)


# Response schemas
class QuoteLineItemResponse(BaseModel):
    """Schema for quote line item responses."""
    
    id: int
    line_number: int
    product_id: Optional[int]
    item_name: str
    item_code: Optional[str]
    description: Optional[str]
    
    quantity: Decimal
    unit_of_measure: str
    unit_price: Decimal
    unit_cost: Optional[Decimal]
    
    discount_percentage: Optional[Decimal]
    discount_amount: Optional[Decimal]
    tax_percentage: Optional[Decimal]
    tax_amount: Optional[Decimal]
    line_total: Decimal
    
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class QuoteVersionResponse(BaseModel):
    """Schema for quote version responses."""
    
    id: int
    version_number: int
    created_by_user_id: int
    created_at: datetime
    reason: Optional[str]
    
    # Snapshot data
    subtotal: Decimal
    total_amount: Decimal
    margin_percentage: Optional[Decimal]
    
    class Config:
        from_attributes = True


class QuoteApprovalResponse(BaseModel):
    """Schema for quote approval responses."""
    
    id: int
    approval_level: int
    status: str
    requested_by_user_id: int
    assigned_to_user_id: int
    
    request_reason: Optional[str]
    urgency_level: str
    
    discount_percentage: Optional[Decimal]
    quote_total: Decimal
    margin_percentage: Optional[Decimal]
    
    due_date: datetime
    approved_at: Optional[datetime]
    approved_by_user_id: Optional[int]
    approver_notes: Optional[str]
    
    escalated_to_user_id: Optional[int]
    escalation_reason: Optional[str]
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuoteResponse(BaseModel):
    """Schema for complete quote responses."""
    
    id: int
    quote_number: str
    title: str
    description: Optional[str]
    status: str
    
    customer_id: int
    contact_person: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    
    # Dates
    valid_from: datetime
    valid_until: datetime
    quote_date: datetime
    
    # Financial data
    subtotal: Decimal
    tax_amount: Optional[Decimal]
    shipping_amount: Optional[Decimal]
    overall_discount_percentage: Optional[Decimal]
    overall_discount_amount: Optional[Decimal]
    total_amount: Decimal
    
    total_cost: Optional[Decimal]
    margin_amount: Optional[Decimal]
    margin_percentage: Optional[Decimal]
    
    currency_code: str
    
    # Terms
    payment_terms: Optional[str]
    delivery_terms: Optional[str]
    special_instructions: Optional[str]
    
    # Workflow fields
    requires_approval: bool
    is_template: bool
    sent_to_customer: bool
    sent_at: Optional[datetime]
    
    # System fields
    prepared_by_user_id: int
    approved_by_user_id: Optional[int]
    company_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Related data
    line_items: Optional[List[QuoteLineItemResponse]] = None
    versions: Optional[List[QuoteVersionResponse]] = None
    approvals: Optional[List[QuoteApprovalResponse]] = None
    
    class Config:
        from_attributes = True


class QuoteListResponse(BaseModel):
    """Schema for paginated quote list responses."""
    
    quotes: List[QuoteResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class QuoteAnalyticsResponse(BaseModel):
    """Schema for quote analytics responses."""
    
    summary: Dict[str, int]
    conversion_metrics: Dict[str, float]
    by_status: Dict[str, int]
    approval_metrics: Dict[str, float]
    top_quotes: List[Dict[str, Any]]
    quote_trends: List[Dict[str, Any]]


class InventoryValidationResponse(BaseModel):
    """Schema for inventory validation responses."""
    
    valid: bool
    line_items: List[Dict[str, Any]]
    issues: List[str]


class InventoryReservationResponse(BaseModel):
    """Schema for inventory reservation responses."""
    
    success: bool
    reservations: List[Dict[str, Any]]
    failed_reservations: List[Dict[str, Any]]
    quote_id: int


class QuoteConversionResponse(BaseModel):
    """Schema for quote conversion responses."""
    
    success: bool
    order_id: Optional[int]
    quote_id: int
    message: str
    error: Optional[str] = None


# Utility schemas
class PendingApprovalsResponse(BaseModel):
    """Schema for pending approvals responses."""
    
    approvals: List[Dict[str, Any]]
    total_count: int


class APIResponse(BaseModel):
    """Generic API response wrapper."""
    
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None
    errors: Optional[List[str]] = None


# Query parameter schemas
class QuoteQueryParams(BaseModel):
    """Schema for quote list query parameters."""
    
    page: int = Field(1, description="Page number", ge=1)
    page_size: int = Field(20, description="Items per page", ge=1, le=100)
    status: Optional[str] = Field(None, description="Filter by status")
    customer_id: Optional[int] = Field(None, description="Filter by customer", gt=0)
    search: Optional[str] = Field(None, description="Search in title/description", max_length=100)
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", description="Sort order")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v