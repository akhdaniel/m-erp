"""
Approval Service for managing purchase order approval workflows.

This service handles the creation, management, and processing of
approval workflows for purchase orders and other business objects.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from purchasing_module.models.approval_workflow import (
    ApprovalWorkflow,
    ApprovalStep,
    ApprovalStatus,
    ApprovalStepStatus,
    ApprovalStepType
)

logger = logging.getLogger(__name__)


class ApprovalService:
    """
    Service class for managing approval workflows.
    
    Handles the complete approval lifecycle including workflow creation,
    step management, escalation, delegation, and notifications.
    """
    
    def __init__(self, db_session=None):
        """
        Initialize the Approval Service.
        
        Args:
            db_session: Database session (in production, injected via DI)
        """
        self.db_session = db_session
    
    def create_approval_workflow(
        self,
        purchase_order_id: int,
        submitted_by_user_id: int,
        workflow_config: Dict[str, Any],
        submission_notes: Optional[str] = None,
        expiration_hours: int = 168  # 7 days
    ) -> Optional[ApprovalWorkflow]:
        """
        Create a new approval workflow for a purchase order.
        
        Args:
            purchase_order_id: ID of purchase order requiring approval
            submitted_by_user_id: ID of user submitting for approval
            workflow_config: Configuration dictionary for workflow steps
            submission_notes: Optional submission notes
            expiration_hours: Hours until workflow expires
            
        Returns:
            ApprovalWorkflow: Created workflow or None if failed
        """
        try:
            # Create approval workflow
            workflow = ApprovalWorkflow(
                company_id=self._get_po_company_id(purchase_order_id),  # In production, get from PO
                purchase_order_id=purchase_order_id,
                workflow_name=workflow_config.get("name", "Standard Approval"),
                workflow_version=workflow_config.get("version", "1.0"),
                submitted_by_user_id=submitted_by_user_id,
                submission_notes=submission_notes
            )
            
            # Initialize workflow with configuration
            workflow.initialize_workflow(workflow_config, expiration_hours)
            
            # Save workflow
            workflow.save(self.db_session, submitted_by_user_id)
            
            # Create approval steps
            self._create_approval_steps(workflow, workflow_config.get("steps", []))
            
            # Start the workflow
            if workflow.start_workflow():
                logger.info(f"Created and started approval workflow for PO {purchase_order_id}")
                
                # Publish workflow creation event
                workflow.publish_event("approval_workflow.created", {
                    "workflow_id": workflow.id,
                    "purchase_order_id": purchase_order_id,
                    "workflow_name": workflow.workflow_name,
                    "total_steps": workflow.total_steps,
                    "submitted_by_user_id": submitted_by_user_id
                })
                
                return workflow
            else:
                logger.error(f"Failed to start approval workflow for PO {purchase_order_id}")
                return None
            
        except Exception as e:
            logger.error(f"Failed to create approval workflow: {e}")
            return None
    
    def _get_po_company_id(self, purchase_order_id: int) -> int:
        """
        Get company ID from purchase order.
        In production, would query the PurchaseOrder model.
        """
        # Mock implementation
        return 1
    
    def _create_approval_steps(
        self,
        workflow: ApprovalWorkflow,
        steps_config: List[Dict[str, Any]]
    ) -> List[ApprovalStep]:
        """
        Create approval steps for a workflow.
        
        Args:
            workflow: Parent approval workflow
            steps_config: List of step configurations
            
        Returns:
            List[ApprovalStep]: Created approval steps
        """
        try:
            steps = []
            
            for i, step_config in enumerate(steps_config, 1):
                step = ApprovalStep(
                    workflow_id=workflow.id,
                    step_number=i,
                    step_name=step_config.get("name", f"Step {i}"),
                    step_type=self._parse_step_type(step_config.get("type", "manager")),
                    description=step_config.get("description", ""),
                    is_required=step_config.get("required", True),
                    approver_role=step_config.get("approver_role"),
                    amount_limit=step_config.get("amount_limit"),
                    step_configuration=step_config
                )
                
                # Save step
                step.save(self.db_session)
                steps.append(step)
                
                logger.info(f"Created approval step {i}: {step.step_name}")
            
            return steps
            
        except Exception as e:
            logger.error(f"Failed to create approval steps: {e}")
            return []
    
    def _parse_step_type(self, step_type_str: str) -> ApprovalStepType:
        """Parse step type string to enum."""
        type_mapping = {
            "manager": ApprovalStepType.MANAGER,
            "director": ApprovalStepType.DIRECTOR,
            "finance": ApprovalStepType.FINANCE,
            "legal": ApprovalStepType.LEGAL,
            "board": ApprovalStepType.BOARD,
            "executive": ApprovalStepType.DIRECTOR,  # Map executive to director
            "custom": ApprovalStepType.CUSTOM
        }
        
        return type_mapping.get(step_type_str.lower(), ApprovalStepType.MANAGER)
    
    def approve_workflow_step(
        self,
        workflow_id: int,
        approver_user_id: int,
        approval_notes: Optional[str] = None
    ) -> bool:
        """
        Approve the current step in a workflow.
        
        Args:
            workflow_id: ID of approval workflow
            approver_user_id: ID of user approving
            approval_notes: Optional approval notes
            
        Returns:
            bool: True if approved successfully
        """
        try:
            # In production, would load from database
            workflow = self._get_mock_workflow(workflow_id)
            
            if not workflow:
                logger.error(f"Approval workflow {workflow_id} not found")
                return False
            
            if not workflow.is_pending:
                logger.error(f"Workflow {workflow_id} is not pending approval")
                return False
            
            # Validate approver has permission for current step
            if not self._validate_approver_permission(workflow, approver_user_id):
                logger.error(f"User {approver_user_id} not authorized to approve current step")
                return False
            
            # Approve current step
            success = workflow.approve_current_step(approver_user_id, approval_notes)
            
            if success:
                # Save workflow changes
                workflow.save(self.db_session, approver_user_id)
                
                # Send notifications for next step or completion
                if workflow.is_completed:
                    self._send_completion_notifications(workflow)
                else:
                    self._send_step_assignment_notifications(workflow)
                
                logger.info(f"Approved step {workflow.current_step_number - 1} in workflow {workflow_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to approve workflow step: {e}")
            return False
    
    def reject_workflow_step(
        self,
        workflow_id: int,
        rejector_user_id: int,
        rejection_notes: str
    ) -> bool:
        """
        Reject the current step in a workflow.
        
        Args:
            workflow_id: ID of approval workflow
            rejector_user_id: ID of user rejecting
            rejection_notes: Reason for rejection
            
        Returns:
            bool: True if rejected successfully
        """
        try:
            # In production, would load from database
            workflow = self._get_mock_workflow(workflow_id)
            
            if not workflow:
                logger.error(f"Approval workflow {workflow_id} not found")
                return False
            
            if not workflow.is_pending:
                logger.error(f"Workflow {workflow_id} is not pending approval")
                return False
            
            # Validate rejector has permission
            if not self._validate_approver_permission(workflow, rejector_user_id):
                logger.error(f"User {rejector_user_id} not authorized to reject current step")
                return False
            
            # Reject current step
            success = workflow.reject_current_step(rejector_user_id, rejection_notes)
            
            if success:
                # Save workflow changes
                workflow.save(self.db_session, rejector_user_id)
                
                # Send rejection notifications
                self._send_rejection_notifications(workflow, rejection_notes)
                
                logger.info(f"Rejected workflow {workflow_id} at step {workflow.current_step_number}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to reject workflow step: {e}")
            return False
    
    def delegate_workflow_step(
        self,
        workflow_id: int,
        delegator_user_id: int,
        delegate_user_id: int,
        delegation_notes: Optional[str] = None
    ) -> bool:
        """
        Delegate the current workflow step to another user.
        
        Args:
            workflow_id: ID of approval workflow
            delegator_user_id: ID of user delegating
            delegate_user_id: ID of user receiving delegation
            delegation_notes: Optional delegation notes
            
        Returns:
            bool: True if delegated successfully
        """
        try:
            # In production, would load from database
            workflow = self._get_mock_workflow(workflow_id)
            
            if not workflow:
                logger.error(f"Approval workflow {workflow_id} not found")
                return False
            
            if not workflow.is_pending:
                logger.error(f"Workflow {workflow_id} is not pending approval")
                return False
            
            # Validate delegator has permission
            if not self._validate_approver_permission(workflow, delegator_user_id):
                logger.error(f"User {delegator_user_id} not authorized to delegate current step")
                return False
            
            # Validate delegate user exists and has appropriate permissions
            if not self._validate_delegate_user(delegate_user_id):
                logger.error(f"Invalid delegate user {delegate_user_id}")
                return False
            
            # Delegate current step
            success = workflow.delegate_current_step(delegator_user_id, delegate_user_id, delegation_notes)
            
            if success:
                # Save workflow changes
                workflow.save(self.db_session, delegator_user_id)
                
                # Send delegation notifications
                self._send_delegation_notifications(workflow, delegator_user_id, delegate_user_id)
                
                logger.info(f"Delegated workflow {workflow_id} step {workflow.current_step_number}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delegate workflow step: {e}")
            return False
    
    def escalate_workflow(
        self,
        workflow_id: int,
        escalation_user_id: int,
        escalation_reason: str = "Automatic escalation due to timeout"
    ) -> bool:
        """
        Escalate a workflow due to timeout or manual request.
        
        Args:
            workflow_id: ID of approval workflow
            escalation_user_id: ID of user to escalate to
            escalation_reason: Reason for escalation
            
        Returns:
            bool: True if escalated successfully
        """
        try:
            # In production, would load from database
            workflow = self._get_mock_workflow(workflow_id)
            
            if not workflow:
                logger.error(f"Approval workflow {workflow_id} not found")
                return False
            
            if not workflow.needs_escalation:
                logger.error(f"Workflow {workflow_id} does not need escalation")
                return False
            
            # Escalate current step
            success = workflow.escalate_current_step(escalation_user_id)
            
            if success:
                # Save workflow changes
                workflow.save(self.db_session)
                
                # Send escalation notifications
                self._send_escalation_notifications(workflow, escalation_reason)
                
                logger.info(f"Escalated workflow {workflow_id} step {workflow.current_step_number}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to escalate workflow: {e}")
            return False
    
    def cancel_workflow(
        self,
        workflow_id: int,
        cancelled_by_user_id: int,
        cancellation_reason: str
    ) -> bool:
        """
        Cancel an approval workflow.
        
        Args:
            workflow_id: ID of approval workflow
            cancelled_by_user_id: ID of user cancelling
            cancellation_reason: Reason for cancellation
            
        Returns:
            bool: True if cancelled successfully
        """
        try:
            # In production, would load from database
            workflow = self._get_mock_workflow(workflow_id)
            
            if not workflow:
                logger.error(f"Approval workflow {workflow_id} not found")
                return False
            
            if workflow.is_completed:
                logger.error(f"Cannot cancel completed workflow {workflow_id}")
                return False
            
            # Cancel workflow
            success = workflow.cancel_workflow(cancelled_by_user_id, cancellation_reason)
            
            if success:
                # Save workflow changes
                workflow.save(self.db_session, cancelled_by_user_id)
                
                # Send cancellation notifications
                self._send_cancellation_notifications(workflow, cancellation_reason)
                
                logger.info(f"Cancelled workflow {workflow_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow: {e}")
            return False
    
    def get_pending_approvals(
        self,
        user_id: int,
        company_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get pending approvals for a user.
        
        Args:
            user_id: ID of user to get approvals for
            company_id: Company ID for data isolation
            limit: Maximum number of approvals to return
            
        Returns:
            List[dict]: List of pending approvals
        """
        try:
            # In production, would query database for pending approvals
            # assigned to the user
            
            # Mock pending approvals
            pending_approvals = []
            
            for i in range(1, min(limit + 1, 6)):  # Generate up to 5 mock approvals
                approval = {
                    "workflow_id": i,
                    "purchase_order_id": i + 100,
                    "po_number": f"PO-{company_id}-20250801-{i:03d}",
                    "supplier_name": f"Supplier {i}",
                    "total_amount": 1000.00 + i * 500,
                    "currency_code": "USD",
                    "current_step": {
                        "step_number": 1 + (i % 3),
                        "step_name": ["Manager Approval", "Director Approval", "Executive Approval"][i % 3],
                        "step_type": ["manager", "director", "executive"][i % 3],
                        "assigned_at": (datetime.utcnow() - timedelta(hours=i * 6)).isoformat(),
                        "due_at": (datetime.utcnow() + timedelta(hours=48 - i * 6)).isoformat()
                    },
                    "submitted_by": f"User {i + 10}",
                    "submitted_at": (datetime.utcnow() - timedelta(hours=i * 8)).isoformat(),
                    "submission_notes": f"Please approve purchase order {i}",
                    "urgency": "high" if i <= 2 else "medium" if i <= 4 else "low",
                    "time_remaining_hours": 48 - i * 6
                }
                
                pending_approvals.append(approval)
            
            return pending_approvals
            
        except Exception as e:
            logger.error(f"Failed to get pending approvals: {e}")
            return []
    
    def get_workflow_history(
        self,
        purchase_order_id: Optional[int] = None,
        company_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get approval workflow history.
        
        Args:
            purchase_order_id: Optional PO ID to filter by
            company_id: Optional company ID to filter by
            limit: Maximum number of workflows to return
            
        Returns:
            List[dict]: List of workflow history records
        """
        try:
            # In production, would query database with proper filters
            
            # Mock workflow history
            history = []
            
            for i in range(1, min(limit + 1, 11)):  # Generate up to 10 mock workflows
                workflow = {
                    "workflow_id": i,
                    "purchase_order_id": i + 100,
                    "po_number": f"PO-1-20250801-{i:03d}",
                    "workflow_name": "Standard Approval",
                    "status": ["approved", "rejected", "cancelled"][i % 3],
                    "total_steps": 2 + (i % 2),
                    "completed_steps": 2 + (i % 2) if i % 3 == 0 else i % 3,
                    "submitted_by": f"User {i + 10}",
                    "submitted_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                    "completed_at": (datetime.utcnow() - timedelta(days=i, hours=-8)).isoformat() if i % 3 != 1 else None,
                    "final_decision_by": f"User {i + 20}" if i % 3 != 1 else None,
                    "processing_time_hours": (8 + i * 2) if i % 3 != 1 else None
                }
                
                history.append(workflow)
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get workflow history: {e}")
            return []
    
    def _validate_approver_permission(self, workflow: ApprovalWorkflow, user_id: int) -> bool:
        """
        Validate that a user has permission to approve the current step.
        
        Args:
            workflow: Approval workflow
            user_id: ID of user to validate
            
        Returns:
            bool: True if user has permission
        """
        # In production, this would check:
        # 1. User is assigned to current step
        # 2. User has appropriate role/permissions
        # 3. User is in the same company
        # 4. Delegation chain is valid
        
        # Mock validation
        return user_id > 0 and workflow.company_id > 0
    
    def _validate_delegate_user(self, user_id: int) -> bool:
        """
        Validate that a user can receive delegated approvals.
        
        Args:
            user_id: ID of user to validate
            
        Returns:
            bool: True if user is valid delegate
        """
        # In production, would check user exists, is active, and has appropriate permissions
        return user_id > 0
    
    def _send_step_assignment_notifications(self, workflow: ApprovalWorkflow) -> None:
        """Send notifications for new step assignment."""
        # In production, would integrate with notification service
        logger.info(f"Sending step assignment notification for workflow {workflow.id}")
    
    def _send_completion_notifications(self, workflow: ApprovalWorkflow) -> None:
        """Send notifications for workflow completion."""
        # In production, would notify submitter and other stakeholders
        logger.info(f"Sending completion notification for workflow {workflow.id}")
    
    def _send_rejection_notifications(self, workflow: ApprovalWorkflow, rejection_notes: str) -> None:
        """Send notifications for workflow rejection."""
        # In production, would notify submitter with rejection details
        logger.info(f"Sending rejection notification for workflow {workflow.id}")
    
    def _send_delegation_notifications(
        self,
        workflow: ApprovalWorkflow,
        delegator_user_id: int,
        delegate_user_id: int
    ) -> None:
        """Send notifications for step delegation."""
        # In production, would notify both delegator and delegate
        logger.info(f"Sending delegation notification for workflow {workflow.id}")
    
    def _send_escalation_notifications(self, workflow: ApprovalWorkflow, reason: str) -> None:
        """Send notifications for workflow escalation."""
        # In production, would notify escalation user and management
        logger.info(f"Sending escalation notification for workflow {workflow.id}")
    
    def _send_cancellation_notifications(self, workflow: ApprovalWorkflow, reason: str) -> None:
        """Send notifications for workflow cancellation."""
        # In production, would notify all stakeholders
        logger.info(f"Sending cancellation notification for workflow {workflow.id}")
    
    def get_approval_statistics(self, company_id: int) -> Dict[str, Any]:
        """
        Get approval workflow statistics for a company.
        
        Args:
            company_id: Company ID for data isolation
            
        Returns:
            dict: Approval statistics
        """
        try:
            # In production, would calculate from database
            return {
                "total_workflows": 145,
                "pending_approvals": 12,
                "completed_this_month": 28,
                "average_approval_time_hours": 18.5,
                "status_breakdown": {
                    "pending": 12,
                    "approved": 98,
                    "rejected": 15,
                    "cancelled": 8,
                    "expired": 2
                },
                "approval_efficiency": {
                    "on_time_approvals": 85.2,
                    "escalated_approvals": 8.3,
                    "expired_approvals": 1.4
                },
                "step_performance": {
                    "manager_avg_hours": 12.3,
                    "director_avg_hours": 24.6,
                    "executive_avg_hours": 36.8
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get approval statistics: {e}")
            return {}
    
    def _get_mock_workflow(self, workflow_id: int) -> Optional[ApprovalWorkflow]:
        """
        Mock method to simulate loading a workflow from database.
        In production, this would be a proper database query.
        """
        # Create mock workflow for testing
        workflow = ApprovalWorkflow(
            id=workflow_id,
            company_id=1,
            purchase_order_id=workflow_id + 100,
            workflow_name="Standard Approval",
            status=ApprovalStatus.IN_PROGRESS,
            current_step_number=1,
            total_steps=2,
            required_approvals=2,
            submitted_by_user_id=1
        )
        
        return workflow