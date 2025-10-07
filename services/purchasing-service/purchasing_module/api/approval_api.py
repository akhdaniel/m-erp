"""
Approval API endpoints for purchasing module.

Provides REST API for approval workflow management including
pending approvals, approval actions, and delegation.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status, Body
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1/approvals", tags=["approvals"])

# In-memory storage for demo purposes
mock_approvals_db = []
next_approval_id = 1

# Dependencies
def get_current_user_id() -> int:
    """Get current user ID from authentication."""
    return 1

def get_current_company_id() -> int:
    """Get current company ID from context."""
    return 1


@router.get("/")
async def list_approvals(
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: int = Depends(get_current_user_id)
):
    """
    List all approvals for the current user.
    """
    try:
        # Filter approvals
        filtered = mock_approvals_db
        if status:
            filtered = [a for a in filtered if a["status"] == status]
        
        # Pagination
        total_count = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        items = filtered[start:end]
        
        return {
            "data": items,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }
    except Exception as e:
        logger.error(f"Error listing approvals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/pending")
async def get_pending_approvals(
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get pending approvals for current user.
    
    Returns list of purchase orders pending approval by the current user.
    """
    try:
        # Import here to avoid circular dependency
        from purchasing_module.api.purchase_order_api import mock_purchase_orders_db
        
        pending = []
        for po in mock_purchase_orders_db:
            if (po.get('company_id') == company_id and 
                po.get('approval_status') == 'requires_approval'):
                
                # Check if user has authority to approve based on amount
                amount = float(po.get('total_amount', 0))
                approval_level = po.get('approval_level', 'manager')
                
                # Simplified approval logic - in production would check actual roles
                can_approve = True  # For demo, any user can approve
                
                if can_approve:
                    pending.append({
                        "id": po['id'],
                        "po_number": po['po_number'],
                        "supplier_name": po.get('supplier_name'),
                        "total_amount": po['total_amount'],
                        "currency_code": po.get('currency_code', 'USD'),
                        "order_date": po['order_date'],
                        "approval_level": approval_level,
                        "requested_by": po.get('created_by'),
                        "urgency": "normal"
                    })
        
        return {
            "pending_count": len(pending),
            "approvals": pending
        }
        
    except Exception as e:
        logger.error(f"Error getting pending approvals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/history")
async def get_approval_history(
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get approval history for current user.
    
    Returns list of approvals/rejections made by the current user.
    """
    try:
        # Import here to avoid circular dependency
        from purchasing_module.api.purchase_order_api import mock_purchase_orders_db
        
        history = []
        for po in mock_purchase_orders_db:
            if po.get('company_id') == company_id:
                if po.get('approved_by') == user_id:
                    history.append({
                        "id": po['id'],
                        "po_number": po['po_number'],
                        "action": "approved",
                        "date": po.get('approved_at'),
                        "amount": po['total_amount'],
                        "supplier": po.get('supplier_name'),
                        "notes": po.get('approval_notes')
                    })
                elif po.get('rejected_by') == user_id:
                    history.append({
                        "id": po['id'],
                        "po_number": po['po_number'],
                        "action": "rejected",
                        "date": po.get('rejected_at'),
                        "amount": po['total_amount'],
                        "supplier": po.get('supplier_name'),
                        "reason": po.get('rejection_reason')
                    })
        
        # Sort by date (most recent first)
        history.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return {
            "total_count": len(history),
            "history": history
        }
        
    except Exception as e:
        logger.error(f"Error getting approval history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/delegate")
async def delegate_approval(
    request: Dict[str, Any] = Body(...),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Delegate approval authority to another user.
    
    Allows temporary delegation of approval rights.
    """
    try:
        global next_approval_id
        
        delegation = {
            "id": next_approval_id,
            "from_user": user_id,
            "to_user": request.get('to_user'),
            "start_date": request.get('start_date', datetime.utcnow().isoformat()),
            "end_date": request.get('end_date'),
            "approval_limit": request.get('approval_limit'),
            "reason": request.get('reason'),
            "status": "active",
            "company_id": company_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        next_approval_id += 1
        mock_approvals_db.append(delegation)
        
        return {
            "message": "Approval delegation created successfully",
            "delegation": delegation
        }
        
    except Exception as e:
        logger.error(f"Error delegating approval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/workflows")
async def get_approval_workflows(
    company_id: int = Depends(get_current_company_id)
):
    """
    Get configured approval workflows.
    
    Returns the approval workflow configuration for the company.
    """
    try:
        # Return sample workflow configuration
        return {
            "workflows": [
                {
                    "id": 1,
                    "name": "Standard Purchase Approval",
                    "description": "Standard approval workflow for purchase orders",
                    "levels": [
                        {
                            "level": 1,
                            "name": "Direct Approval",
                            "min_amount": 0,
                            "max_amount": 5000,
                            "approvers": ["manager"],
                            "auto_approve": False
                        },
                        {
                            "level": 2,
                            "name": "Manager Approval",
                            "min_amount": 5000,
                            "max_amount": 10000,
                            "approvers": ["senior_manager", "director"],
                            "auto_approve": False
                        },
                        {
                            "level": 3,
                            "name": "Executive Approval",
                            "min_amount": 10000,
                            "max_amount": None,
                            "approvers": ["cfo", "ceo"],
                            "auto_approve": False
                        }
                    ],
                    "escalation_hours": 48,
                    "status": "active"
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting workflows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats")
async def get_approval_stats(
    company_id: int = Depends(get_current_company_id)
):
    """Get approval statistics."""
    try:
        # Import here to avoid circular dependency
        from purchasing_module.api.purchase_order_api import mock_purchase_orders_db
        
        company_orders = [po for po in mock_purchase_orders_db if po.get('company_id') == company_id]
        
        pending = len([po for po in company_orders if po.get('approval_status') == 'requires_approval'])
        approved = len([po for po in company_orders if po.get('approval_status') == 'approved'])
        rejected = len([po for po in company_orders if po.get('approval_status') == 'rejected'])
        auto_approved = len([po for po in company_orders if po.get('approval_status') == 'auto_approved'])
        
        return {
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "auto_approved": auto_approved,
            "approval_rate": (approved / (approved + rejected) * 100) if (approved + rejected) > 0 else 0,
            "average_approval_time": "24 hours"  # Would calculate from actual data
        }
        
    except Exception as e:
        logger.error(f"Error getting approval stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )