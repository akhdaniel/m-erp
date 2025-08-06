"""
Pricing API endpoints for dynamic pricing and discount management.

Provides REST API for pricing rule management, price calculations,
discount application, and integration with product and customer data.
"""

from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime, date
from decimal import Decimal
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from pydantic import BaseModel, Field, validator

from sales_module.services.pricing_rule_service import PricingRuleService
from sales_module.models.pricing_rules import PricingRuleType, DiscountType

# Type variable for generic responses
T = TypeVar('T')

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/pricing", tags=["Pricing"])


# Base Schema Models

class BaseResponseModel(BaseModel):
    """Base response model"""
    pass

class ListResponseModel(BaseModel, Generic[T]):
    """List response model"""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total count")
    page: int = Field(1, description="Current page")
    limit: int = Field(50, description="Items per page")

class StandardCreateRequest(BaseModel):
    """Standard create request model"""
    pass

class StandardUpdateRequest(BaseModel):
    """Standard update request model"""
    pass

# Mock dependency functions
async def get_current_user():
    """Mock current user dependency"""
    return {"user_id": 1, "company_id": 1}

async def get_database():
    """Mock database dependency"""
    return None

# Request/Response Models

class PriceCalculationRequest(BaseModel):
    """Request model for price calculation"""
    product_id: int = Field(..., description="Product ID", gt=0)
    customer_id: Optional[int] = Field(None, description="Customer ID for customer-specific pricing", gt=0)
    quantity: Decimal = Field(Decimal('1.0'), description="Quantity", gt=0)
    base_price: Optional[Decimal] = Field(None, description="Base price (if known)", gt=0)
    product_category_id: Optional[int] = Field(None, description="Product category ID", gt=0)
    company_id: Optional[int] = Field(None, description="Company ID for isolation", gt=0)

    @validator('quantity', pre=True)
    def validate_quantity(cls, v):
        return Decimal(str(v)) if v is not None else Decimal('1.0')

    @validator('base_price', pre=True)
    def validate_base_price(cls, v):
        return Decimal(str(v)) if v is not None else None


class BulkPriceCalculationRequest(BaseModel):
    """Request model for bulk price calculation"""
    items: List[Dict[str, Any]] = Field(..., description="List of items with product_id, quantity, base_price")
    customer_id: Optional[int] = Field(None, description="Customer ID", gt=0)
    company_id: Optional[int] = Field(None, description="Company ID for isolation", gt=0)

    @validator('items')
    def validate_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Items list cannot be empty")
        for item in v:
            if 'product_id' not in item or 'quantity' not in item:
                raise ValueError("Each item must have product_id and quantity")
        return v


class PricingRuleCreateRequest(StandardCreateRequest):
    """Request model for creating pricing rules"""
    name: str = Field(..., description="Rule name", max_length=255)
    description: Optional[str] = Field(None, description="Rule description")
    rule_type: PricingRuleType = Field(..., description="Type of pricing rule")
    priority: int = Field(1, description="Rule priority (lower = higher priority)", ge=1, le=999)
    is_active: bool = Field(True, description="Whether rule is active")
    
    # Customer specific rules
    customer_id: Optional[int] = Field(None, description="Customer ID for customer-specific rules", gt=0)
    
    # Product specific rules
    product_id: Optional[int] = Field(None, description="Product ID for product-specific rules", gt=0)
    product_category_id: Optional[int] = Field(None, description="Product category ID", gt=0)
    
    # Volume discount rules
    min_quantity: Optional[Decimal] = Field(None, description="Minimum quantity", gt=0)
    max_quantity: Optional[Decimal] = Field(None, description="Maximum quantity", gt=0)
    min_amount: Optional[Decimal] = Field(None, description="Minimum amount", gt=0)
    max_amount: Optional[Decimal] = Field(None, description="Maximum amount", gt=0)
    
    # Discount configuration
    discount_type: DiscountType = Field(DiscountType.PERCENTAGE, description="Discount type")
    discount_value: Decimal = Field(..., description="Discount value", ge=0)
    
    # Date range for promotional rules
    start_date: Optional[date] = Field(None, description="Start date for rule validity")
    end_date: Optional[date] = Field(None, description="End date for rule validity")

    @validator('min_quantity', 'max_quantity', pre=True)
    def validate_quantities(cls, v):
        return Decimal(str(v)) if v is not None else None

    @validator('min_amount', 'max_amount', 'discount_value', pre=True)
    def validate_amounts(cls, v):
        return Decimal(str(v)) if v is not None else None


class PricingRuleUpdateRequest(StandardUpdateRequest):
    """Request model for updating pricing rules"""
    name: Optional[str] = Field(None, description="Rule name", max_length=255)
    description: Optional[str] = Field(None, description="Rule description")
    rule_type: Optional[PricingRuleType] = Field(None, description="Type of pricing rule")
    priority: Optional[int] = Field(None, description="Rule priority", ge=1, le=999)
    is_active: Optional[bool] = Field(None, description="Whether rule is active")
    
    # Customer specific rules
    customer_id: Optional[int] = Field(None, description="Customer ID", gt=0)
    
    # Product specific rules
    product_id: Optional[int] = Field(None, description="Product ID", gt=0)
    product_category_id: Optional[int] = Field(None, description="Product category ID", gt=0)
    
    # Volume discount rules
    min_quantity: Optional[Decimal] = Field(None, description="Minimum quantity", gt=0)
    max_quantity: Optional[Decimal] = Field(None, description="Maximum quantity", gt=0)
    min_amount: Optional[Decimal] = Field(None, description="Minimum amount", gt=0)
    max_amount: Optional[Decimal] = Field(None, description="Maximum amount", gt=0)
    
    # Discount configuration
    discount_type: Optional[DiscountType] = Field(None, description="Discount type")
    discount_value: Optional[Decimal] = Field(None, description="Discount value", ge=0)
    
    # Date range for promotional rules
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")

    @validator('min_quantity', 'max_quantity', 'discount_value', 'min_amount', 'max_amount', pre=True)
    def validate_decimals(cls, v):
        return Decimal(str(v)) if v is not None else None


class PricingRuleResponse(BaseResponseModel):
    """Response model for pricing rules"""
    id: int
    name: str
    description: Optional[str]
    rule_type: str
    priority: int
    is_active: bool
    customer_id: Optional[int]
    product_id: Optional[int]
    product_category_id: Optional[int]
    min_quantity: Optional[Decimal]
    max_quantity: Optional[Decimal]
    min_amount: Optional[Decimal]
    max_amount: Optional[Decimal]
    discount_type: str
    discount_value: Decimal
    start_date: Optional[date]
    end_date: Optional[date]
    created_by: Optional[int]
    is_valid: bool
    days_until_expiry: Optional[int]


# API Endpoints

@router.post("/calculate", summary="Calculate Product Price", response_model=Dict[str, Any])
async def calculate_product_price(
    request: PriceCalculationRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Calculate final product price with all applicable pricing rules.
    
    Returns detailed pricing information including base price, final price,
    discount amount, and all applicable pricing rules.
    """
    try:
        service = PricingRuleService(db)
        
        result = service.calculate_product_price(
            product_id=request.product_id,
            customer_id=request.customer_id,
            quantity=request.quantity,
            base_price=request.base_price,
            product_category_id=request.product_category_id,
            company_id=request.company_id or current_user.get('company_id')
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Price calculated successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating product price: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/calculate-bulk", summary="Calculate Bulk Pricing", response_model=Dict[str, Any])
async def calculate_bulk_pricing(
    request: BulkPriceCalculationRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Calculate pricing for multiple items at once.
    
    Useful for quote line items and order calculations.
    Returns pricing for each item plus summary totals.
    """
    try:
        service = PricingRuleService(db)
        
        result = service.calculate_bulk_pricing(
            items=request.items,
            customer_id=request.customer_id,
            company_id=request.company_id or current_user.get('company_id')
        )
        
        return {
            "success": True,
            "data": result,
            "message": f"Bulk pricing calculated for {len(request.items)} items"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating bulk pricing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/rules", summary="List Pricing Rules", response_model=ListResponseModel[PricingRuleResponse])
async def list_pricing_rules(
    rule_type: Optional[PricingRuleType] = Query(None, description="Filter by rule type"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID", gt=0),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get list of pricing rules with optional filtering.
    
    Supports filtering by rule type, customer, and active status.
    Results are paginated and sorted by priority.
    """
    try:
        service = PricingRuleService(db)
        
        filters = {}
        if rule_type:
            filters['rule_type'] = rule_type.value
        if customer_id:
            filters['customer_id'] = customer_id
        if is_active is not None:
            filters['is_active'] = is_active
        
        # Add company filter
        filters['company_id'] = current_user.get('company_id')
        
        result = service.list(
            filters=filters,
            page=page,
            limit=limit,
            sort_by='priority'
        )
        
        # Convert to response format
        items = []
        for rule in result.get('items', []):
            rule_dict = rule.to_dict() if hasattr(rule, 'to_dict') else rule
            rule_dict['is_valid'] = rule.is_valid if hasattr(rule, 'is_valid') else True
            rule_dict['days_until_expiry'] = rule.days_until_expiry if hasattr(rule, 'days_until_expiry') else None
            items.append(PricingRuleResponse(**rule_dict))
        
        return ListResponseModel[PricingRuleResponse](
            items=items,
            total=result.get('total', 0),
            page=page,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error listing pricing rules: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/rules", summary="Create Pricing Rule", response_model=PricingRuleResponse)
async def create_pricing_rule(
    request: PricingRuleCreateRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Create a new pricing rule.
    
    Validates rule data and creates pricing rule with proper audit trail.
    Automatically assigns company_id and created_by from current user.
    """
    try:
        service = PricingRuleService(db)
        
        rule_data = request.dict(exclude_none=True)
        
        pricing_rule = service.create_pricing_rule(
            rule_data=rule_data,
            user_id=current_user.get('user_id'),
            company_id=current_user.get('company_id')
        )
        
        # Convert to response format
        rule_dict = pricing_rule.to_dict() if hasattr(pricing_rule, 'to_dict') else pricing_rule.__dict__
        rule_dict['is_valid'] = pricing_rule.is_valid
        rule_dict['days_until_expiry'] = pricing_rule.days_until_expiry
        
        return PricingRuleResponse(**rule_dict)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating pricing rule: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/rules/{rule_id}", summary="Get Pricing Rule", response_model=PricingRuleResponse)
async def get_pricing_rule(
    rule_id: int = Path(..., description="Pricing rule ID", gt=0),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get pricing rule by ID.
    
    Returns detailed information about the pricing rule including
    validity status and expiry information.
    """
    try:
        service = PricingRuleService(db)
        
        pricing_rule = service.get_by_id(rule_id, current_user.get('company_id'))
        if not pricing_rule:
            raise HTTPException(status_code=404, detail="Pricing rule not found")
        
        # Convert to response format
        rule_dict = pricing_rule.to_dict() if hasattr(pricing_rule, 'to_dict') else pricing_rule.__dict__
        rule_dict['is_valid'] = pricing_rule.is_valid
        rule_dict['days_until_expiry'] = pricing_rule.days_until_expiry
        
        return PricingRuleResponse(**rule_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pricing rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/rules/{rule_id}", summary="Update Pricing Rule", response_model=PricingRuleResponse)
async def update_pricing_rule(
    rule_id: int = Path(..., description="Pricing rule ID", gt=0),
    request: PricingRuleUpdateRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Update existing pricing rule.
    
    Validates updated data and maintains audit trail.
    Only provided fields are updated.
    """
    try:
        service = PricingRuleService(db)
        
        # Check if rule exists
        existing_rule = service.get_by_id(rule_id, current_user.get('company_id'))
        if not existing_rule:
            raise HTTPException(status_code=404, detail="Pricing rule not found")
        
        rule_data = request.dict(exclude_none=True)
        
        pricing_rule = service.update_pricing_rule(
            rule_id=rule_id,
            rule_data=rule_data,
            user_id=current_user.get('user_id'),
            company_id=current_user.get('company_id')
        )
        
        # Convert to response format
        rule_dict = pricing_rule.to_dict() if hasattr(pricing_rule, 'to_dict') else pricing_rule.__dict__
        rule_dict['is_valid'] = pricing_rule.is_valid
        rule_dict['days_until_expiry'] = pricing_rule.days_until_expiry
        
        return PricingRuleResponse(**rule_dict)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating pricing rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/rules/{rule_id}", summary="Delete Pricing Rule")
async def delete_pricing_rule(
    rule_id: int = Path(..., description="Pricing rule ID", gt=0),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Delete pricing rule.
    
    Permanently removes the pricing rule from the system.
    This action cannot be undone.
    """
    try:
        service = PricingRuleService(db)
        
        # Check if rule exists
        existing_rule = service.get_by_id(rule_id, current_user.get('company_id'))
        if not existing_rule:
            raise HTTPException(status_code=404, detail="Pricing rule not found")
        
        service.delete(rule_id, current_user.get('company_id'))
        
        return {"message": "Pricing rule deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting pricing rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/rules/{rule_id}/activate", summary="Activate Pricing Rule", response_model=PricingRuleResponse)
async def activate_pricing_rule(
    rule_id: int = Path(..., description="Pricing rule ID", gt=0),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Activate pricing rule.
    
    Sets the rule as active and available for price calculations.
    """
    try:
        service = PricingRuleService(db)
        
        pricing_rule = service.activate_rule(
            rule_id=rule_id,
            user_id=current_user.get('user_id'),
            company_id=current_user.get('company_id')
        )
        
        # Convert to response format
        rule_dict = pricing_rule.to_dict() if hasattr(pricing_rule, 'to_dict') else pricing_rule.__dict__
        rule_dict['is_valid'] = pricing_rule.is_valid
        rule_dict['days_until_expiry'] = pricing_rule.days_until_expiry
        
        return PricingRuleResponse(**rule_dict)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error activating pricing rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/rules/{rule_id}/deactivate", summary="Deactivate Pricing Rule", response_model=PricingRuleResponse)
async def deactivate_pricing_rule(
    rule_id: int = Path(..., description="Pricing rule ID", gt=0),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Deactivate pricing rule.
    
    Sets the rule as inactive and excludes it from price calculations.
    """
    try:
        service = PricingRuleService(db)
        
        pricing_rule = service.deactivate_rule(
            rule_id=rule_id,
            user_id=current_user.get('user_id'),
            company_id=current_user.get('company_id')
        )
        
        # Convert to response format
        rule_dict = pricing_rule.to_dict() if hasattr(pricing_rule, 'to_dict') else pricing_rule.__dict__
        rule_dict['is_valid'] = pricing_rule.is_valid
        rule_dict['days_until_expiry'] = pricing_rule.days_until_expiry
        
        return PricingRuleResponse(**rule_dict)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deactivating pricing rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/rules/customer/{customer_id}", summary="Get Customer Pricing Rules", response_model=ListResponseModel[PricingRuleResponse])
async def get_customer_pricing_rules(
    customer_id: int = Path(..., description="Customer ID", gt=0),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get all pricing rules applicable to specific customer.
    
    Returns rules that either apply to all customers or are
    specifically created for the given customer.
    """
    try:
        service = PricingRuleService(db)
        
        rules = service.get_customer_rules(
            customer_id=customer_id,
            company_id=current_user.get('company_id')
        )
        
        # Convert to response format
        items = []
        for rule in rules:
            rule_dict = rule.to_dict() if hasattr(rule, 'to_dict') else rule.__dict__
            rule_dict['is_valid'] = rule.is_valid
            rule_dict['days_until_expiry'] = rule.days_until_expiry
            items.append(PricingRuleResponse(**rule_dict))
        
        return ListResponseModel[PricingRuleResponse](
            items=items,
            total=len(items),
            page=1,
            limit=len(items)
        )
        
    except Exception as e:
        logger.error(f"Error getting customer pricing rules for {customer_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/rules/types", summary="Get Pricing Rule Types")
async def get_pricing_rule_types():
    """
    Get available pricing rule types and discount types.
    
    Returns enumeration values for use in UI dropdowns.
    """
    return {
        "pricing_rule_types": [
            {"value": rule_type.value, "label": rule_type.value.replace('_', ' ').title()}
            for rule_type in PricingRuleType
        ],
        "discount_types": [
            {"value": discount_type.value, "label": discount_type.value.replace('_', ' ').title()}
            for discount_type in DiscountType
        ]
    }


@router.get("/health", summary="Pricing API Health Check")
async def health_check():
    """Health check endpoint for pricing API."""
    return {
        "status": "healthy",
        "service": "pricing-api",
        "timestamp": datetime.utcnow().isoformat()
    }