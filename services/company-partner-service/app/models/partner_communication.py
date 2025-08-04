"""
Partner Communication model for tracking all partner interactions.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import BaseModel


class PartnerCommunication(BaseModel):
    """
    Partner Communication model for tracking interactions and correspondence.
    
    This model stores a comprehensive log of all communications with partners
    including emails, phone calls, meetings, and other interactions with
    timestamps, participants, and outcome tracking.
    """
    
    __tablename__ = "partner_communications"
    
    # Foreign key to partner
    partner_id = Column(
        Integer,
        ForeignKey("partners.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Optional link to specific contact
    partner_contact_id = Column(
        Integer,
        ForeignKey("partner_contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Communication details
    communication_type = Column(String(50), nullable=False, default="email", index=True)
    subject = Column(String(500), nullable=False)
    content = Column(Text)
    direction = Column(String(20), nullable=False, default="outbound", index=True)
    
    # Participants and scheduling
    initiated_by = Column(String(255))  # User who initiated the communication
    participants = Column(Text)  # JSON or comma-separated list of participants
    scheduled_at = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    
    # Status and outcomes
    status = Column(String(20), nullable=False, default="pending", index=True)
    priority = Column(String(20), nullable=False, default="normal", index=True)
    outcome = Column(String(100))
    follow_up_required = Column(Boolean, default=False, nullable=False)
    follow_up_date = Column(DateTime, nullable=True, index=True)
    
    # Metadata
    tags = Column(Text)  # JSON or comma-separated tags for categorization
    attachments_count = Column(Integer, default=0, nullable=False)
    external_reference = Column(String(255))  # Reference to external system
    
    # Relationships
    partner = relationship("Partner", back_populates="communications")
    partner_contact = relationship("PartnerContact", back_populates="communications")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "communication_type IN ('email', 'phone', 'meeting', 'video_call', 'letter', 'fax', 'text', 'other')",
            name="partner_communications_type_check"
        ),
        CheckConstraint(
            "direction IN ('inbound', 'outbound')",
            name="partner_communications_direction_check"
        ),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'cancelled', 'failed')",
            name="partner_communications_status_check"
        ),
        CheckConstraint(
            "priority IN ('low', 'normal', 'high', 'urgent')",
            name="partner_communications_priority_check"
        ),
        CheckConstraint("LENGTH(subject) >= 1", name="partner_communications_subject_check"),
        {'extend_existing': True}
    )
    
    def __str__(self):
        """String representation of the partner communication."""
        return f"PartnerCommunication(type='{self.communication_type}', subject='{self.subject[:50]}...')"
    
    def __repr__(self):
        """Detailed representation of the partner communication."""
        return (
            f"PartnerCommunication(id={self.id}, partner_id={self.partner_id}, "
            f"type='{self.communication_type}', status='{self.status}')"
        )
    
    @property
    def is_completed(self):
        """Check if communication is completed."""
        return self.status == "completed"
    
    @property
    def is_pending(self):
        """Check if communication is pending."""
        return self.status == "pending"
    
    @property
    def is_overdue(self):
        """Check if scheduled communication is overdue."""
        if self.scheduled_at and not self.is_completed:
            return datetime.utcnow() > self.scheduled_at
        return False
    
    @property
    def needs_follow_up(self):
        """Check if communication needs follow-up."""
        if not self.follow_up_required:
            return False
        if self.follow_up_date:
            return datetime.utcnow() >= self.follow_up_date
        return True
    
    def mark_completed(self, outcome=None):
        """Mark communication as completed with optional outcome."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        if outcome:
            self.outcome = outcome
    
    def schedule_follow_up(self, follow_up_date, required=True):
        """Schedule a follow-up for this communication."""
        self.follow_up_required = required
        self.follow_up_date = follow_up_date
    
    def get_duration_minutes(self):
        """Calculate communication duration in minutes."""
        if self.completed_at and self.scheduled_at:
            delta = self.completed_at - self.scheduled_at
            return int(delta.total_seconds() / 60)
        return None
    
    def is_inbound(self):
        """Check if communication is inbound."""
        return self.direction == "inbound"
    
    def is_high_priority(self):
        """Check if communication is high priority."""
        return self.priority in ("high", "urgent")