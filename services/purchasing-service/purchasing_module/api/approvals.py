"""
Approvals API endpoints for the Purchasing Module.

Provides REST API endpoints for managing approval workflows,
processing approvals, and tracking approval statistics.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field

from purchasing_module.services.approval_service import ApprovalService
from purchasing_module.models.approval_workflow import ApprovalStatus

logger = logging.getLogger(__name__)

# Create router for approval endpoints
approvals_router = APIRouter(prefix="/approvals", tags=["Approvals"])

# Pydantic models for request/response

class ApprovalDecisionRequest(BaseModel):
    """Schema for approval decisions."""
    approval_notes: Optional[str] = Field(None, max_length=1000, description="Approval notes")

class RejectionDecisionRequest(BaseModel):
    """Schema for rejection decisions."""
    rejection_notes: str = Field(..., max_length=1000, description="Rejection notes")

class DelegationRequest(BaseModel):
    """Schema for delegation requests."""
    delegate_user_id: int = Field(..., gt=0, description="User ID to delegate to")
    delegation_notes: Optional[str] = Field(None, max_length=1000, description="Delegation notes")

class EscalationRequest(BaseModel):
    """Schema for escalation requests."""
    escalation_user_id: int = Field(..., gt=0, description="User ID to escalate to")
    escalation_reason: str = Field(..., max_length=1000, description="Reason for escalation")

class CancellationRequest(BaseModel):
    """Schema for workflow cancellation."""
    cancellation_reason: str = Field(..., max_length=1000, description="Reason for cancellation")

class WorkflowResponse(BaseModel):
    """Schema for workflow responses."""
    workflow_id: int
    purchase_order_id: int
    po_number: str
    workflow_name: str
    status: str
    current_step_number: int
    total_steps: int
    submitted_by: str
    submitted_at: str

# Dependency functions

async def get_approval_service() -> ApprovalService:
    """Dependency to get approval service instance."""
    # In production, would use proper dependency injection
    return ApprovalService()

async def get_current_user_id() -> int:
    """Dependency to get current user ID from authentication."""
    # In production, would extract from JWT token or session
    return 1

async def get_current_company_id() -> int:
    """Dependency to get current company ID from authentication."""
    # In production, would extract from user context
    return 1

# API Endpoints

@approvals_router.get("/pending", response_model=Dict[str, Any])
async def get_pending_approvals(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records"),
    service: ApprovalService = Depends(get_approval_service),
    user_id: int = Depends(get_current_user_id),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get pending approvals for the current user.
    
    Returns list of approval workflows waiting for the user's action.
    """
    try:
        pending_approvals = service.get_pending_approvals(
            user_id=user_id,
            company_id=company_id,
            limit=limit
        )
        
        return {
            "success": True,
            "data": {
                "pending_approvals": pending_approvals,
                "total_pending": len(pending_approvals)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get pending approvals: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@approvals_router.get("/workflows/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow_details(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    service: ApprovalService = Depends(get_approval_service)
):
    """
    Get detailed information about a specific approval workflow.
    
    Returns workflow status, steps, and history.
    """
    try:
        # In production, would load actual workflow from database
        # For now, return mock data
        
        workflow_details = {
            "workflow_id": workflow_id,
            "purchase_order_id": workflow_id + 100,
            "po_number": f"PO-1-20250801-{workflow_id:03d}",
            "workflow_name": "Standard Approval",
            "workflow_version": "1.0",
            "status": ApprovalStatus.IN_PROGRESS.value,
            "current_step": {
                "step_number": 1,
                "step_name": "Manager Approval",
                "step_type": "manager",
                "assigned_to_user_id": 1,
                "assigned_at": datetime.utcnow().isoformat(),
                "due_at": (datetime.utcnow()).isoformat(),
                "status": "pending"
            },
            "steps": [
                {
                    "step_number": 1,
                    "step_name": "Manager Approval",
                    "step_type": "manager",  
                    "status": "pending",
                    "is_required": True
                },
                {
                    "step_number": 2,
                    "step_name": "Director Approval",
                    "step_type": "director",
                    "status": "waiting",
                    "is_required": True
                }
            ],
            "submitted_by": "User 1",
            "submitted_at": datetime.utcnow().isoformat(),
            "submission_notes": f"Please approve purchase order {workflow_id}",
            "total_steps": 2,
            "completed_steps": 0,
            "approval_percentage": 0.0,
            "time_remaining_hours": 48.0
        }
        
        return {
            "success": True,
            "data": workflow_details
        }
        
    except Exception as e:
        logger.error(f"Failed to get workflow details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@approvals_router.post("/workflows/{workflow_id}/approve", response_model=Dict[str, Any])
async def approve_workflow_step(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    approval_request: ApprovalDecisionRequest = None,
    service: ApprovalService = Depends(get_approval_service),
    user_id: int = Depends(get_current_user_id)
):
    """
    Approve the current step in an approval workflow.
    
    Advances the workflow to the next step or completes it if this is the final step.
    """
    try:
        approval_notes = approval_request.approval_notes if approval_request else None
        
        success = service.approve_workflow_step(
            workflow_id=workflow_id,
            approver_user_id=user_id,
            approval_notes=approval_notes
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to approve workflow step")
        
        return {
            "success": True,
            "message": "Workflow step approved successfully",
            "data": {
                "workflow_id": workflow_id,
                "approved_by_user_id": user_id,
                "approved_at": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve workflow step: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@approvals_router.post("/workflows/{workflow_id}/reject", response_model=Dict[str, Any])
async def reject_workflow_step(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    rejection_request: RejectionDecisionRequest,
    service: ApprovalService = Depends(get_approval_service),
    user_id: int = Depends(get_current_user_id)
):
    """
    Reject the current step in an approval workflow.
    
    Rejects the workflow and provides rejection notes.
    """
    try:
        success = service.reject_workflow_step(
            workflow_id=workflow_id,
            rejector_user_id=user_id,
            rejection_notes=rejection_request.rejection_notes
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to reject workflow step")
        
        return {
            "success": True,
            "message": "Workflow step rejected successfully",
            "data": {
                "workflow_id": workflow_id,
                "rejected_by_user_id": user_id,
                "rejected_at": datetime.utcnow().isoformat(),
                "rejection_notes": rejection_request.rejection_notes
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reject workflow step: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@approvals_router.post("/workflows/{workflow_id}/delegate", response_model=Dict[str, Any])
async def delegate_workflow_step(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    delegation_request: DelegationRequest,
    service: ApprovalService = Depends(get_approval_service),
    user_id: int = Depends(get_current_user_id)
):
    """
    Delegate the current workflow step to another user.
    
    Transfers approval responsibility to the specified user.
    """
    try:
        success = service.delegate_workflow_step(
            workflow_id=workflow_id,
            delegator_user_id=user_id,
            delegate_user_id=delegation_request.delegate_user_id,
            delegation_notes=delegation_request.delegation_notes
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delegate workflow step")
        
        return {
            "success": True,
            "message": "Workflow step delegated successfully",
            "data": {
                "workflow_id": workflow_id,
                "delegated_by_user_id": user_id,
                "delegated_to_user_id": delegation_request.delegate_user_id,
                "delegated_at": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delegate workflow step: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@approvals_router.post("/workflows/{workflow_id}/escalate", response_model=Dict[str, Any])
async def escalate_workflow(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    escalation_request: EscalationRequest,
    service: ApprovalService = Depends(get_approval_service),
    user_id: int = Depends(get_current_user_id)
):
    """
    Escalate an approval workflow to a higher authority.
    
    Used when normal approval process needs management intervention.
    """
    try:
        success = service.escalate_workflow(
            workflow_id=workflow_id,
            escalation_user_id=escalation_request.escalation_user_id,
            escalation_reason=escalation_request.escalation_reason
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to escalate workflow")
        
        return {
            "success": True,
            "message": "Workflow escalated successfully",
            "data": {
                "workflow_id": workflow_id,
                "escalated_to_user_id": escalation_request.escalation_user_id,
                "escalated_at": datetime.utcnow().isoformat(),
                "escalation_reason": escalation_request.escalation_reason
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to escalate workflow: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@approvals_router.post("/workflows/{workflow_id}/cancel", response_model=Dict[str, Any])
async def cancel_workflow(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    cancellation_request: CancellationRequest,
    service: ApprovalService = Depends(get_approval_service),
    user_id: int = Depends(get_current_user_id)
):
    """
    Cancel an approval workflow.
    
    Cancels the workflow before completion with a specified reason.
    """
    try:
        success = service.cancel_workflow(
            workflow_id=workflow_id,
            cancelled_by_user_id=user_id,
            cancellation_reason=cancellation_request.cancellation_reason
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to cancel workflow")
        
        return {
            "success": True,
            "message": "Workflow cancelled successfully",
            "data": {
                "workflow_id": workflow_id,
                "cancelled_by_user_id": user_id,
                "cancelled_at": datetime.utcnow().isoformat(),
                "cancellation_reason": cancellation_request.cancellation_reason
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel workflow: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@approvals_router.get("/workflows/history", response_model=Dict[str, Any])
async def get_workflow_history(
    purchase_order_id: Optional[int] = Query(None, description="Filter by purchase order ID"),
    status: Optional[str] = Query(None, description="Filter by workflow status"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records"),
    service: ApprovalService = Depends(get_approval_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get approval workflow history.
    
    Returns list of completed and active workflows with optional filtering.
    """
    try:
        # Validate status filter if provided
        if status:
            try:
                ApprovalStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        workflow_history = service.get_workflow_history(
            purchase_order_id=purchase_order_id,
            company_id=company_id,
            limit=limit
        )
        
        # Apply status filter if provided
        if status:
            workflow_history = [
                workflow for workflow in workflow_history 
                if workflow.get("status") == status
            ]
        
        return {
            "success": True,
            "data": {
                "workflows": workflow_history,
                "total_workflows": len(workflow_history),
                "filters": {
                    "purchase_order_id": purchase_order_id,
                    "status": status
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@approvals_router.get("/statistics/summary", response_model=Dict[str, Any])
async def get_approval_statistics(
    service: ApprovalService = Depends(get_approval_service),
    company_id: int = Depends(get_current_company_id)
):
    """
    Get approval workflow statistics.
    
    Returns summary statistics including processing times, success rates, and efficiency metrics.
    """
    try:
        stats = service.get_approval_statistics(company_id)
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get approval statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@approvals_router.get("/my-actions", response_model=Dict[str, Any])
async def get_my_approval_actions(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    service: ApprovalService = Depends(get_approval_service),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get approval actions taken by the current user.
    
    Returns history of approvals, rejections, and delegations by the user.
    """
    try:
        # In production, would query database for user's approval actions
        # For now, return mock data
        
        my_actions = {
            "user_id": user_id,
            "period_days": days,
            "summary": {
                "total_actions": 15,
                "approved": 12,
                "rejected": 2,
                "delegated": 1,
                "average_response_time_hours": 8.5
            },
            "recent_actions": [
                {
                    "workflow_id": 1,
                    "purchase_order_id": 101,
                    "po_number": "PO-1-20250801-001",
                    "action": "approved",
                    "action_date": (datetime.utcnow()).isoformat(),
                    "notes": "Approved - within budget",
                    "response_time_hours": 6.5
                },
                {
                    "workflow_id": 2,
                    "purchase_order_id": 102,
                    "po_number": "PO-1-20250801-002",
                    "action": "rejected",
                    "action_date": (datetime.utcnow()).isoformat(),
                    "notes": "Rejected - insufficient justification",
                    "response_time_hours": 12.3
                }
            ]
        }
        
        return {
            "success": True,
            "data": my_actions
        }
        
    except Exception as e:
        logger.error(f"Failed to get user approval actions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@approvals_router.get("/workflows/{workflow_id}/timeline", response_model=Dict[str, Any])
async def get_workflow_timeline(
    workflow_id: int = Path(..., gt=0, description="Workflow ID"),
    service: ApprovalService = Depends(get_approval_service)
):
    """
    Get detailed timeline for a specific workflow.
    
    Returns chronological history of all workflow events and actions.
    """
    try:
        # In production, would load actual workflow timeline from database
        # For now, return mock timeline data
        
        timeline = {
            "workflow_id": workflow_id,
            "events": [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_type": "workflow_created",
                    "description": "Workflow created and submitted for approval",
                    "user_id": 1,
                    "user_name": "John Doe",
                    "details": {
                        "workflow_name": "Standard Approval",
                        "total_steps": 2
                    }
                },
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_type": "step_assigned",
                    "description": "Step 1 assigned to Manager",
                    "user_id": 2,
                    "user_name": "Jane Manager",
                    "details": {
                        "step_number": 1,
                        "step_name": "Manager Approval"
                    }
                }
            ],
            "current_status": "in_progress",
            "total_processing_time_hours": 12.5
        }
        
        return {
            "success": True,
            "data": timeline
        }
        
    except Exception as e:
        logger.error(f"Failed to get workflow timeline: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")