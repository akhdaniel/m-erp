"""
Approval Workflow models for purchase order approval processes
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from purchasing_module.framework.base import CompanyBusinessObject, BaseModel


class ApprovalStatus(str, enum.Enum):
    """Approval workflow status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ApprovalStepStatus(str, enum.Enum):
    """Individual approval step status"""
    WAITING = "waiting"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELEGATED = "delegated"
    ESCALATED = "escalated"
    SKIPPED = "skipped"


class ApprovalStepType(str, enum.Enum):
    """Types of approval steps"""
    MANAGER = "manager"
    DIRECTOR = "director"
    FINANCE = "finance"
    LEGAL = "legal"
    BOARD = "board"
    CUSTOM = "custom"


class ApprovalWorkflow(CompanyBusinessObject):
    """
    Approval Workflow model for purchase order approvals.
    
    Manages the approval process for purchase orders with configurable
    approval steps, escalation, and delegation capabilities.
    """
    
    __tablename__ = "approval_workflows"
    
    # Purchase order reference
    purchase_order_id = Column(
        Integer,
        ForeignKey("purchase_orders.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Workflow configuration
    workflow_name = Column(String(100), nullable=False)
    workflow_version = Column(String(20), nullable=False, default="1.0")
    
    # Workflow status
    status = Column(Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING, index=True)
    current_step_number = Column(Integer, nullable=False, default=1)
    
    # Timing
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Workflow metadata
    total_steps = Column(Integer, nullable=False)
    required_approvals = Column(Integer, nullable=False)
    received_approvals = Column(Integer, nullable=False, default=0)
    
    # Escalation settings
    escalation_enabled = Column(Boolean, nullable=False, default=True)
    escalation_hours = Column(Integer, nullable=False, default=48)
    reminder_hours = Column(Integer, nullable=False, default=24)
    
    # Submitter information
    submitted_by_user_id = Column(Integer, nullable=False, index=True)
    submission_notes = Column(Text)
    
    # Final decision
    final_decision = Column(String(20))  # 'approved' or 'rejected'
    final_decision_by_user_id = Column(Integer, nullable=True)
    final_decision_at = Column(DateTime, nullable=True)
    final_decision_notes = Column(Text)
    
    # Configuration
    configuration = Column(JSON)  # Workflow configuration data
    
    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    # purchase_order = relationship("PurchaseOrder", back_populates="approval_workflow")
    # approval_steps = relationship("ApprovalStep", back_populates="workflow", cascade="all, delete-orphan", order_by="ApprovalStep.step_number")
    
    def __str__(self):
        """String representation of approval workflow."""
        return f"Approval Workflow for PO {self.purchase_order_id}: {self.status.value} - Step {self.current_step_number}/{self.total_steps}"
    
    def __repr__(self):
        """Detailed representation of approval workflow."""
        return (
            f"ApprovalWorkflow(id={self.id}, po_id={self.purchase_order_id}, "
            f"status='{self.status.value}', step={self.current_step_number}/{self.total_steps})"
        )
    
    @property
    def is_completed(self) -> bool:
        """Check if workflow is completed (approved or rejected)."""
        return self.status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]
    
    @property
    def is_pending(self) -> bool:
        """Check if workflow is pending approval."""
        return self.status in [ApprovalStatus.PENDING, ApprovalStatus.IN_PROGRESS]
    
    @property
    def is_expired(self) -> bool:
        """Check if workflow has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def approval_percentage(self) -> float:
        """Get approval completion percentage."""
        if self.total_steps == 0:
            return 0.0
        return (self.received_approvals / self.required_approvals) * 100
    
    @property
    def time_remaining_hours(self) -> Optional[float]:
        """Get remaining hours before expiration."""
        if not self.expires_at:
            return None
        
        remaining = self.expires_at - datetime.utcnow()
        return max(0, remaining.total_seconds() / 3600)
    
    @property
    def needs_escalation(self) -> bool:
        """Check if workflow needs escalation."""
        if not self.escalation_enabled or self.is_completed:
            return False
        
        # Check if current step has been pending too long
        current_step = self.get_current_step()
        if not current_step:
            return False
        
        escalation_time = current_step.assigned_at + timedelta(hours=self.escalation_hours)
        return datetime.utcnow() > escalation_time and current_step.status == ApprovalStepStatus.PENDING
    
    @property
    def needs_reminder(self) -> bool:
        """Check if workflow needs reminder notification."""
        if self.is_completed:
            return False
        
        current_step = self.get_current_step()
        if not current_step:
            return False
        
        reminder_time = current_step.assigned_at + timedelta(hours=self.reminder_hours)
        return datetime.utcnow() > reminder_time and current_step.status == ApprovalStepStatus.PENDING
    
    def get_current_step(self):
        """
        Get the current approval step.
        
        In production, this would return the actual ApprovalStep object.
        For now, returning None as placeholder.
        """
        # return next((step for step in self.approval_steps if step.step_number == self.current_step_number), None)
        return None
    
    def initialize_workflow(
        self,
        workflow_config: Dict[str, Any],
        expiration_hours: int = 168  # 7 days default
    ) -> None:
        """
        Initialize the approval workflow with configuration.
        
        Args:
            workflow_config: Configuration dictionary with approval steps
            expiration_hours: Hours until workflow expires
        """
        self.configuration = workflow_config
        self.total_steps = len(workflow_config.get('steps', []))
        self.required_approvals = sum(1 for step in workflow_config.get('steps', []) if step.get('required', True))
        
        if expiration_hours > 0:
            self.expires_at = datetime.utcnow() + timedelta(hours=expiration_hours)
        
        self.status = ApprovalStatus.PENDING
        
        # Create approval steps (simulated)
        self._create_approval_steps(workflow_config.get('steps', []))
    
    def _create_approval_steps(self, steps_config: List[Dict[str, Any]]) -> None:
        """
        Create approval steps from configuration.
        
        Args:
            steps_config: List of step configurations
        """
        # In production, this would create ApprovalStep objects
        # For now, just log the creation
        for i, step_config in enumerate(steps_config, 1):
            print(f"Creating approval step {i}: {step_config.get('name', f'Step {i}')}")
    
    def start_workflow(self) -> bool:
        """
        Start the approval workflow.
        
        Returns:
            bool: True if started successfully
        """
        if self.status != ApprovalStatus.PENDING:
            return False
        
        self.status = ApprovalStatus.IN_PROGRESS
        self.submitted_at = datetime.utcnow()
        
        # Assign first step
        return self._assign_current_step()
    
    def _assign_current_step(self) -> bool:
        """
        Assign the current approval step to appropriate approver.
        
        Returns:
            bool: True if assignment successful
        """
        current_step = self.get_current_step()
        if not current_step:
            return False
        
        # In production, this would:
        # 1. Determine approver based on step configuration
        # 2. Send notification to approver
        # 3. Set step status to PENDING
        # 4. Record assignment timestamp
        
        print(f"Assigning approval step {self.current_step_number} to approver")
        return True
    
    def approve_current_step(
        self,
        approver_user_id: int,
        notes: Optional[str] = None,
        delegation_user_id: Optional[int] = None
    ) -> bool:
        """
        Approve the current workflow step.
        
        Args:
            approver_user_id: ID of user approving
            notes: Optional approval notes
            delegation_user_id: Optional user to delegate to
            
        Returns:
            bool: True if approval successful
        """
        if not self.is_pending:
            return False
        
        current_step = self.get_current_step()
        if not current_step:
            return False
        
        # Record approval (simulated)
        print(f"Step {self.current_step_number} approved by user {approver_user_id}")
        if notes:
            print(f"Approval notes: {notes}")
        
        self.received_approvals += 1
        
        # Check if workflow is complete
        if self.current_step_number >= self.total_steps:
            return self._complete_workflow(True, approver_user_id, notes)
        
        # Move to next step
        self.current_step_number += 1
        return self._assign_current_step()
    
    def reject_current_step(
        self,
        rejector_user_id: int,
        notes: Optional[str] = None
    ) -> bool:
        """
        Reject the current workflow step.
        
        Args:
            rejector_user_id: ID of user rejecting
            notes: Optional rejection notes
            
        Returns:
            bool: True if rejection successful
        """
        if not self.is_pending:
            return False
        
        # Record rejection (simulated)
        print(f"Step {self.current_step_number} rejected by user {rejector_user_id}")
        if notes:
            print(f"Rejection notes: {notes}")
        
        return self._complete_workflow(False, rejector_user_id, notes)
    
    def _complete_workflow(
        self,
        approved: bool,
        decision_user_id: int,
        notes: Optional[str] = None
    ) -> bool:
        """
        Complete the approval workflow.
        
        Args:
            approved: Whether workflow was approved
            decision_user_id: ID of user making final decision
            notes: Optional decision notes
            
        Returns:
            bool: True if completion successful
        """
        self.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        self.final_decision = "approved" if approved else "rejected"
        self.final_decision_by_user_id = decision_user_id
        self.final_decision_at = datetime.utcnow()
        self.completed_at = datetime.utcnow()
        
        if notes:
            self.final_decision_notes = notes
        
        # Publish event for workflow completion
        event_type = f"approval_workflow.{self.final_decision}"
        self.publish_event(event_type, {
            "workflow_id": self.id,
            "purchase_order_id": self.purchase_order_id,
            "decision_user_id": decision_user_id,
            "total_steps": self.total_steps,
            "received_approvals": self.received_approvals
        })
        
        return True
    
    def escalate_current_step(self, escalation_user_id: int) -> bool:
        """
        Escalate the current approval step.
        
        Args:
            escalation_user_id: ID of user to escalate to
            
        Returns:
            bool: True if escalation successful
        """
        if not self.is_pending or not self.needs_escalation:
            return False
        
        current_step = self.get_current_step()
        if not current_step:
            return False
        
        # Record escalation (simulated)
        print(f"Step {self.current_step_number} escalated to user {escalation_user_id}")
        
        # In production, this would:
        # 1. Update current step with escalation info
        # 2. Assign to escalation user
        # 3. Send escalation notifications
        # 4. Log escalation in audit trail
        
        return True
    
    def delegate_current_step(
        self,
        delegator_user_id: int,
        delegate_user_id: int,
        notes: Optional[str] = None
    ) -> bool:
        """
        Delegate the current approval step to another user.
        
        Args:
            delegator_user_id: ID of user delegating
            delegate_user_id: ID of user receiving delegation
            notes: Optional delegation notes
            
        Returns:
            bool: True if delegation successful
        """
        if not self.is_pending:
            return False
        
        current_step = self.get_current_step()
        if not current_step:
            return False
        
        # Record delegation (simulated)
        print(f"Step {self.current_step_number} delegated from user {delegator_user_id} to user {delegate_user_id}")
        if notes:
            print(f"Delegation notes: {notes}")
        
        # In production, this would:
        # 1. Update current step with delegation info
        # 2. Assign to delegate user
        # 3. Send delegation notifications
        # 4. Log delegation in audit trail
        
        return True
    
    def cancel_workflow(self, cancelled_by_user_id: int, reason: str) -> bool:
        """
        Cancel the approval workflow.
        
        Args:
            cancelled_by_user_id: ID of user cancelling
            reason: Reason for cancellation
            
        Returns:
            bool: True if cancellation successful
        """
        if self.is_completed:
            return False
        
        self.status = ApprovalStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        self.final_decision = "cancelled"
        self.final_decision_by_user_id = cancelled_by_user_id
        self.final_decision_notes = f"Cancelled: {reason}"
        
        # Publish cancellation event
        self.publish_event("approval_workflow.cancelled", {
            "workflow_id": self.id,
            "purchase_order_id": self.purchase_order_id,
            "cancelled_by_user_id": cancelled_by_user_id,
            "reason": reason
        })
        
        return True


class ApprovalStep(BaseModel):
    """
    Individual approval step within a workflow.
    
    Represents a single approval step with approver assignment,
    timing, and decision tracking.
    """
    
    __tablename__ = "approval_steps"
    
    # Workflow reference
    workflow_id = Column(
        Integer,
        ForeignKey("approval_workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Step configuration
    step_number = Column(Integer, nullable=False)
    step_name = Column(String(100), nullable=False)
    step_type = Column(Enum(ApprovalStepType), nullable=False)
    description = Column(Text)
    
    # Approval requirements
    is_required = Column(Boolean, nullable=False, default=True)
    approver_role = Column(String(100))
    approver_user_id = Column(Integer, nullable=True, index=True)
    amount_limit = Column(Numeric(15, 2), nullable=True)
    
    # Step status
    status = Column(Enum(ApprovalStepStatus), nullable=False, default=ApprovalStepStatus.WAITING, index=True)
    
    # Timing
    assigned_at = Column(DateTime, nullable=True)
    due_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Decision
    decision = Column(String(20))  # 'approved', 'rejected', 'delegated', etc.
    decision_notes = Column(Text)
    decision_by_user_id = Column(Integer, nullable=True)
    
    # Escalation and delegation
    escalated_to_user_id = Column(Integer, nullable=True)
    escalated_at = Column(DateTime, nullable=True)
    delegated_to_user_id = Column(Integer, nullable=True)
    delegated_by_user_id = Column(Integer, nullable=True)
    delegated_at = Column(DateTime, nullable=True)
    delegation_notes = Column(Text)
    
    # Notifications
    reminder_sent_at = Column(DateTime, nullable=True)
    reminder_count = Column(Integer, nullable=False, default=0)
    
    # Configuration
    step_configuration = Column(JSON)
    
    # Relationships
    # workflow = relationship("ApprovalWorkflow", back_populates="approval_steps")
    
    def __str__(self):
        """String representation of approval step."""
        return f"Step {self.step_number}: {self.step_name} - {self.status.value}"
    
    def __repr__(self):
        """Detailed representation of approval step."""
        return (
            f"ApprovalStep(id={self.id}, workflow_id={self.workflow_id}, "
            f"step={self.step_number}, name='{self.step_name}', status='{self.status.value}')"
        )
    
    @property
    def is_completed(self) -> bool:
        """Check if step is completed."""
        return self.status in [
            ApprovalStepStatus.APPROVED,
            ApprovalStepStatus.REJECTED,
            ApprovalStepStatus.SKIPPED
        ]
    
    @property
    def is_pending(self) -> bool:
        """Check if step is pending approval."""
        return self.status == ApprovalStepStatus.PENDING
    
    @property
    def is_overdue(self) -> bool:
        """Check if step is overdue."""
        if not self.due_at or self.is_completed:
            return False
        return datetime.utcnow() > self.due_at
    
    @property
    def hours_remaining(self) -> Optional[float]:
        """Get hours remaining until due."""
        if not self.due_at:
            return None
        
        remaining = self.due_at - datetime.utcnow()
        return max(0, remaining.total_seconds() / 3600)
    
    def assign_to_user(
        self,
        user_id: int,
        due_hours: int = 48
    ) -> None:
        """
        Assign step to a specific user.
        
        Args:
            user_id: ID of user to assign to
            due_hours: Hours until step is due
        """
        self.approver_user_id = user_id
        self.assigned_at = datetime.utcnow()
        self.due_at = datetime.utcnow() + timedelta(hours=due_hours)
        self.status = ApprovalStepStatus.PENDING
    
    def approve(self, approver_user_id: int, notes: Optional[str] = None) -> bool:
        """
        Approve this step.
        
        Args:
            approver_user_id: ID of approving user
            notes: Optional approval notes
            
        Returns:
            bool: True if approved successfully
        """
        if not self.is_pending:
            return False
        
        self.status = ApprovalStepStatus.APPROVED
        self.decision = "approved"
        self.decision_by_user_id = approver_user_id
        self.completed_at = datetime.utcnow()
        
        if notes:
            self.decision_notes = notes
        
        return True
    
    def reject(self, rejector_user_id: int, notes: Optional[str] = None) -> bool:
        """
        Reject this step.
        
        Args:
            rejector_user_id: ID of rejecting user
            notes: Optional rejection notes
            
        Returns:
            bool: True if rejected successfully
        """
        if not self.is_pending:
            return False
        
        self.status = ApprovalStepStatus.REJECTED
        self.decision = "rejected"
        self.decision_by_user_id = rejector_user_id
        self.completed_at = datetime.utcnow()
        
        if notes:
            self.decision_notes = notes
        
        return True
    
    def delegate(
        self,
        delegator_user_id: int,
        delegate_user_id: int,
        notes: Optional[str] = None
    ) -> bool:
        """
        Delegate this step to another user.
        
        Args:
            delegator_user_id: ID of user delegating
            delegate_user_id: ID of user receiving delegation
            notes: Optional delegation notes
            
        Returns:
            bool: True if delegated successfully
        """
        if not self.is_pending:
            return False
        
        self.status = ApprovalStepStatus.DELEGATED
        self.delegated_by_user_id = delegator_user_id
        self.delegated_to_user_id = delegate_user_id
        self.delegated_at = datetime.utcnow()
        
        if notes:
            self.delegation_notes = notes
        
        # Reassign to delegate
        self.approver_user_id = delegate_user_id
        self.status = ApprovalStepStatus.PENDING
        
        return True
    
    def escalate(self, escalation_user_id: int) -> bool:
        """
        Escalate this step to a higher authority.
        
        Args:
            escalation_user_id: ID of user to escalate to
            
        Returns:
            bool: True if escalated successfully
        """
        if not self.is_pending:
            return False
        
        self.status = ApprovalStepStatus.ESCALATED
        self.escalated_to_user_id = escalation_user_id
        self.escalated_at = datetime.utcnow()
        
        # Reassign to escalation user
        self.approver_user_id = escalation_user_id
        self.status = ApprovalStepStatus.PENDING
        
        return True