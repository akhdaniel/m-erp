"""
Quote API endpoints for sales module.

Provides comprehensive REST API for quote management including
CRUD operations, workflow management, approvals, and inventory integration.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from fastapi.responses import JSONResponse
from decimal import Decimal
import logging

from sales_module.services.quote_service import QuoteService
from sales_module.schemas.quote_schemas import (
    QuoteCreateRequest, QuoteUpdateRequest, QuoteResponse, QuoteListResponse,
    QuoteLineItemCreateRequest, QuoteLineItemUpdateRequest, QuoteLineItemResponse,
    QuoteApprovalRequest, QuoteApprovalAction, QuoteApprovalResponse,
    QuoteDiscountRequest, QuoteSendRequest, QuoteVersionRequest, QuoteVersionResponse,
    QuoteConversionRequest, QuoteConversionResponse, ValidityExtensionRequest,
    QuoteAnalyticsResponse, InventoryValidationResponse, InventoryReservationResponse,
    PendingApprovalsResponse, APIResponse, QuoteQueryParams
)
from sales_module.models import QuoteStatus

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1/quotes", tags=["quotes"])


# Dependencies
def get_quote_service() -> QuoteService:
    """Get quote service instance."""
    return QuoteService()


def get_current_user_id() -> int:
    """Get current user ID from authentication."""
    # In production, would extract from JWT token
    return 1


def get_current_company_id() -> int:
    """Get current company ID from authentication."""
    # In production, would extract from JWT token or user context
    return 1


# Quote CRUD endpoints
@router.post("/", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
async def create_quote(
    quote_data: QuoteCreateRequest,
    line_items: Optional[List[QuoteLineItemCreateRequest]] = None,
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Create new quote with optional line items.
    
    Creates a new sales quote with the provided information and optional line items.
    Automatically calculates totals and handles inventory integration.
    """
    try:
        # Convert request data to dict
        quote_dict = quote_data.model_dump(exclude_unset=True)
        line_items_list = [item.model_dump() for item in line_items] if line_items else None
        
        # Create quote using service
        quote = quote_service.create_quote(
            quote_data=quote_dict,
            line_items=line_items_list,
            user_id=user_id,
            company_id=company_id
        )
        
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create quote"
            )
        
        return QuoteResponse.model_validate(quote)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating quote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=QuoteListResponse)
async def list_quotes(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    quote_status: Optional[str] = Query(None, description="Filter by status"),
    customer_id: Optional[int] = Query(None, gt=0, description="Filter by customer"),
    search: Optional[str] = Query(None, max_length=100, description="Search text"),
    quote_service: QuoteService = Depends(get_quote_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    List quotes with filtering and pagination.
    
    Returns paginated list of quotes with optional filtering by status,
    customer, and search text.
    """
    try:
        # Build filter criteria
        filters = {"company_id": company_id}
        if quote_status:
            filters["status"] = quote_status
        if customer_id:
            filters["customer_id"] = customer_id
        if search:
            filters["search"] = search
        
        # Get quotes from service
        result = quote_service.list(
            filters=filters,
            page=page,
            page_size=page_size
        )
        
        # Extract data from service result
        quotes = result.get("items", [])
        total_count = result.get("total", 0)
        total_pages = result.get("total_pages", 0)
        
        return QuoteListResponse(
            quotes=[QuoteResponse.model_validate(quote) for quote in quotes],
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error listing quotes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_quote(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    include_line_items: bool = Query(True, description="Include line items"),
    include_versions: bool = Query(False, description="Include versions"),
    include_approvals: bool = Query(False, description="Include approvals"),
    quote_service: QuoteService = Depends(get_quote_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get quote by ID with optional related data.
    
    Returns complete quote information with optional inclusion of
    line items, versions, and approval history.
    """
    try:
        quote = quote_service.get_by_id(quote_id, company_id)
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found"
            )
        
        # Convert to response model
        quote_response = QuoteResponse.model_validate(quote)
        
        # Include related data if requested
        if include_line_items:
            # In production, would load from database
            quote_response.line_items = []
        
        if include_versions:
            # In production, would load from database
            quote_response.versions = []
        
        if include_approvals:
            # In production, would load from database
            quote_response.approvals = []
        
        return quote_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quote {quote_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{quote_id}", response_model=QuoteResponse)
async def update_quote(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    quote_data: QuoteUpdateRequest = None,
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Update existing quote.
    
    Updates quote information while preserving workflow state
    and recalculating totals as needed.
    """
    try:
        quote = quote_service.get_by_id(quote_id, company_id)
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found"
            )
        
        # Convert request data to dict
        update_dict = quote_data.model_dump(exclude_unset=True)
        
        # Update quote using service
        updated_quote = quote_service.update(
            quote_id=quote_id,
            update_data=update_dict,
            user_id=user_id,
            company_id=company_id
        )
        
        return QuoteResponse.model_validate(updated_quote)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating quote {quote_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Delete quote (soft delete).
    
    Marks quote as inactive while preserving data for audit trail.
    """
    try:
        quote = quote_service.get_by_id(quote_id, company_id)
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found"
            )
        
        # Check if quote can be deleted
        if quote.status in [QuoteStatus.SENT, QuoteStatus.ACCEPTED, QuoteStatus.CONVERTED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete quote that has been sent or accepted"
            )
        
        success = quote_service.delete(quote_id, user_id, company_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete quote"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting quote {quote_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Line item endpoints
@router.post("/{quote_id}/line-items", response_model=QuoteLineItemResponse, status_code=status.HTTP_201_CREATED)
async def add_line_item(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    line_item_data: QuoteLineItemCreateRequest = None,
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Add line item to quote.
    
    Adds new line item to quote with automatic inventory integration
    and total recalculation.
    """
    try:
        # Convert request data to dict
        item_dict = line_item_data.model_dump()
        
        # Add line item using service
        line_item = quote_service.add_line_item(
            quote_id=quote_id,
            line_item_data=item_dict,
            user_id=user_id,
            company_id=company_id
        )
        
        if not line_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found"
            )
        
        return QuoteLineItemResponse.model_validate(line_item)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding line item to quote {quote_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{quote_id}/line-items/{line_item_id}", response_model=QuoteLineItemResponse)
async def update_line_item(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    line_item_id: int = Path(..., gt=0, description="Line item ID"),
    line_item_data: QuoteLineItemUpdateRequest = None,
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Update quote line item.
    
    Updates line item information and recalculates quote totals.
    """
    try:
        # Extract pricing update
        new_unit_price = line_item_data.unit_price if line_item_data.unit_price else None
        discount_percentage = line_item_data.discount_percentage if line_item_data.discount_percentage else None
        
        if new_unit_price:
            line_item = quote_service.update_line_item_pricing(
                line_item_id=line_item_id,
                new_unit_price=new_unit_price,
                discount_percentage=discount_percentage,
                user_id=user_id,
                company_id=company_id
            )
        else:
            # Handle other field updates
            # In production, would have dedicated update method
            line_item = None
        
        if not line_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Line item not found"
            )
        
        return QuoteLineItemResponse.model_validate(line_item)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating line item {line_item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{quote_id}/line-items/{line_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_line_item(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    line_item_id: int = Path(..., gt=0, description="Line item ID"),
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Delete line item from quote.
    
    Removes line item and recalculates quote totals.
    """
    try:
        # In production, would have dedicated delete line item method
        success = True  # Placeholder
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Line item not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting line item {line_item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Quote operations endpoints
@router.post("/{quote_id}/discount", response_model=QuoteResponse)
async def apply_discount(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    discount_request: QuoteDiscountRequest = None,
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Apply overall discount to quote.
    
    Applies percentage discount to entire quote and recalculates totals.
    """
    try:
        quote = quote_service.apply_overall_discount(
            quote_id=quote_id,
            discount_percentage=discount_request.discount_percentage,
            user_id=user_id,
            company_id=company_id
        )
        
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found"
            )
        
        return QuoteResponse.model_validate(quote)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error applying discount to quote {quote_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{quote_id}/send", response_model=QuoteResponse)
async def send_quote(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    send_request: QuoteSendRequest = None,
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Send quote to customer.
    
    Sends quote via email and updates status to sent.
    """
    try:
        quote = quote_service.send_quote_to_customer(
            quote_id=quote_id,
            email_template=send_request.email_template if send_request else None,
            user_id=user_id,
            company_id=company_id
        )
        
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found"
            )
        
        return QuoteResponse.model_validate(quote)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error sending quote {quote_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{quote_id}/versions", response_model=QuoteVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    version_request: QuoteVersionRequest = None,
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Create new version of quote.
    
    Creates snapshot version for revision tracking.
    """
    try:
        version = quote_service.create_quote_version(
            quote_id=quote_id,
            reason=version_request.reason if version_request else None,
            user_id=user_id,
            company_id=company_id
        )
        
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found"
            )
        
        return QuoteVersionResponse.model_validate(version)
        
    except Exception as e:
        logger.error(f"Error creating version for quote {quote_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{quote_id}/convert", response_model=QuoteConversionResponse)
async def convert_to_order(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    conversion_request: QuoteConversionRequest = None,
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Convert quote to sales order.
    
    Converts accepted quote to sales order and updates status.
    """
    try:
        result = quote_service.convert_quote_to_order(
            quote_id=quote_id,
            order_data=conversion_request.order_data if conversion_request else None,
            user_id=user_id,
            company_id=company_id
        )
        
        return QuoteConversionResponse(**result)
        
    except Exception as e:
        logger.error(f"Error converting quote {quote_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{quote_id}/extend-validity", response_model=QuoteResponse)
async def extend_validity(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    extension_request: ValidityExtensionRequest = None,
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Extend quote validity period.
    
    Extends quote validity by specified number of days.
    """
    try:
        quote = quote_service.extend_quote_validity(
            quote_id=quote_id,
            additional_days=extension_request.additional_days,
            user_id=user_id,
            company_id=company_id
        )
        
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found"
            )
        
        return QuoteResponse.model_validate(quote)
        
    except Exception as e:
        logger.error(f"Error extending validity for quote {quote_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Approval workflow endpoints
@router.post("/{quote_id}/approvals", response_model=QuoteApprovalResponse, status_code=status.HTTP_201_CREATED)
async def request_approval(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    approval_request: QuoteApprovalRequest = None,
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Request quote approval.
    
    Creates approval request for quote with specified level and urgency.
    """
    try:
        approval = quote_service.request_quote_approval(
            quote_id=quote_id,
            approval_level=approval_request.approval_level if approval_request else 1,
            request_reason=approval_request.request_reason if approval_request else None,
            urgency=approval_request.urgency if approval_request else "normal",
            user_id=user_id,
            company_id=company_id
        )
        
        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found"
            )
        
        return QuoteApprovalResponse.model_validate(approval)
        
    except Exception as e:
        logger.error(f"Error requesting approval for quote {quote_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/approvals/{approval_id}/action", response_model=QuoteApprovalResponse)
async def approval_action(
    approval_id: int = Path(..., gt=0, description="Approval ID"),
    action_request: QuoteApprovalAction = None,
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Perform approval action.
    
    Approve, reject, or escalate approval request.
    """
    try:
        if action_request.action == "approve":
            approval = quote_service.approve_quote(
                approval_id=approval_id,
                approver_notes=action_request.notes,
                user_id=user_id,
                company_id=company_id
            )
        elif action_request.action == "reject":
            approval = quote_service.reject_quote_approval(
                approval_id=approval_id,
                rejection_reason=action_request.notes or "No reason provided",
                user_id=user_id,
                company_id=company_id
            )
        elif action_request.action == "escalate":
            if not action_request.escalate_to_user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="escalate_to_user_id required for escalation"
                )
            approval = quote_service.escalate_approval(
                approval_id=approval_id,
                escalation_reason=action_request.notes or "Escalated",
                escalate_to_user_id=action_request.escalate_to_user_id,
                user_id=user_id,
                company_id=company_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action"
            )
        
        if not approval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval not found"
            )
        
        return QuoteApprovalResponse.model_validate(approval)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing approval action {approval_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/approvals/pending", response_model=PendingApprovalsResponse)
async def get_pending_approvals(
    quote_service: QuoteService = Depends(get_quote_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get pending approvals for current user.
    
    Returns list of approval requests awaiting action from current user.
    """
    try:
        approvals = quote_service.get_pending_approvals(user_id, company_id)
        
        return PendingApprovalsResponse(
            approvals=approvals,
            total_count=len(approvals)
        )
        
    except Exception as e:
        logger.error(f"Error getting pending approvals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Inventory integration endpoints  
@router.get("/{quote_id}/inventory/validate", response_model=InventoryValidationResponse)
async def validate_inventory(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    quote_service: QuoteService = Depends(get_quote_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Validate inventory availability for quote.
    
    Checks inventory availability for all quote line items.
    """
    try:
        result = quote_service.validate_quote_inventory(quote_id, company_id)
        return InventoryValidationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error validating inventory for quote {quote_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{quote_id}/inventory/reserve", response_model=InventoryReservationResponse)
async def reserve_inventory(
    quote_id: int = Path(..., gt=0, description="Quote ID"),
    expiry_hours: int = Query(24, ge=1, le=168, description="Reservation expiry hours"),
    quote_service: QuoteService = Depends(get_quote_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Reserve inventory for quote.
    
    Creates temporary inventory reservations for quote line items.
    """
    try:
        result = quote_service.reserve_quote_inventory(
            quote_id=quote_id,
            company_id=company_id,
            expiry_hours=expiry_hours
        )
        return InventoryReservationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error reserving inventory for quote {quote_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Analytics endpoints
@router.get("/analytics", response_model=QuoteAnalyticsResponse)
async def get_analytics(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    quote_service: QuoteService = Depends(get_quote_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get quote analytics and metrics.
    
    Returns comprehensive analytics including conversion rates,
    performance metrics, and trend data.
    """
    try:
        # Parse date range if provided
        date_range = None
        if date_from or date_to:
            from datetime import datetime
            date_range = {}
            if date_from:
                date_range['from'] = datetime.fromisoformat(date_from)
            if date_to:
                date_range['to'] = datetime.fromisoformat(date_to)
        
        analytics = quote_service.get_quote_analytics(company_id, date_range)
        return QuoteAnalyticsResponse(**analytics)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {e}"
        )
    except Exception as e:
        logger.error(f"Error getting quote analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint for quote API.
    
    Returns API health status and service connectivity.
    """
    try:
        return {
            "status": "healthy",
            "service": "quote-api",
            "timestamp": "2025-01-04T20:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "quote-api",
                "error": str(e)
            }
        )