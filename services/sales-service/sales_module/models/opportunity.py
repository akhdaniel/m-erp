"""
Sales opportunity models for pipeline management and tracking.

Provides comprehensive sales opportunity management including
pipeline stages, activities, forecasting, and win/loss analysis.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
import enum

from sales_module.framework.base import CompanyBusinessObject, BaseModel


class OpportunitySource(str, enum.Enum):
    """Opportunity source enumeration"""
    WEBSITE = "website"  # Website inquiry
    REFERRAL = "referral"  # Customer referral
    COLD_CALL = "cold_call"  # Cold calling
    EMAIL_CAMPAIGN = "email_campaign"  # Email marketing
    TRADE_SHOW = "trade_show"  # Trade show lead
    SOCIAL_MEDIA = "social_media"  # Social media
    PARTNER = "partner"  # Partner referral
    EXISTING_CUSTOMER = "existing_customer"  # Existing customer expansion
    OTHER = "other"  # Other source


class OpportunityPriority(str, enum.Enum):
    """Opportunity priority enumeration"""
    LOW = "low"  # Low priority
    MEDIUM = "medium"  # Medium priority
    HIGH = "high"  # High priority
    URGENT = "urgent"  # Urgent priority


class ActivityType(str, enum.Enum):
    """Activity type enumeration"""
    CALL = "call"  # Phone call
    EMAIL = "email"  # Email communication
    MEETING = "meeting"  # In-person or virtual meeting
    DEMO = "demo"  # Product demonstration
    PROPOSAL = "proposal"  # Proposal sent
    FOLLOW_UP = "follow_up"  # Follow-up activity
    NEGOTIATION = "negotiation"  # Negotiation activity
    CONTRACT = "contract"  # Contract discussion
    NOTE = "note"  # Internal note
    TASK = "task"  # Task or reminder


class ActivityOutcome(str, enum.Enum):
    """Activity outcome enumeration"""
    COMPLETED = "completed"  # Successfully completed
    NO_ANSWER = "no_answer"  # No answer/response
    VOICEMAIL = "voicemail"  # Left voicemail
    CALLBACK_REQUESTED = "callback_requested"  # Callback requested
    MEETING_SCHEDULED = "meeting_scheduled"  # Meeting scheduled
    PROPOSAL_REQUESTED = "proposal_requested"  # Proposal requested
    NOT_INTERESTED = "not_interested"  # Not interested
    POSITIVE = "positive"  # Positive response
    NEGATIVE = "negative"  # Negative response


class OpportunityStage(CompanyBusinessObject):
    """
    Opportunity Stage model for sales pipeline configuration.
    
    Defines configurable sales pipeline stages with
    probability percentages and business rules.
    """
    
    __tablename__ = "opportunity_stages"
    
    # Stage information
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    
    # Stage ordering and display
    sequence_order = Column(Integer, nullable=False, index=True)
    color = Column(String(7))  # Hex color code for UI
    icon = Column(String(100))  # Icon identifier for UI
    
    # Stage configuration
    probability_percentage = Column(Numeric(5, 2), nullable=False, default=0.0)
    is_active_stage = Column(Boolean, nullable=False, default=True)
    is_closed_won = Column(Boolean, nullable=False, default=False)
    is_closed_lost = Column(Boolean, nullable=False, default=False)
    
    # Stage requirements and rules
    required_activities = Column(JSON)  # Array of required activity types
    minimum_days_in_stage = Column(Integer, nullable=True)
    maximum_days_in_stage = Column(Integer, nullable=True)
    
    # Automation settings
    auto_create_activities = Column(JSON)  # Activities to auto-create when entering stage
    notification_settings = Column(JSON)  # Notification configuration
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    # opportunities = relationship("SalesOpportunity", back_populates="stage")
    
    def __str__(self):
        """String representation of opportunity stage."""
        return f"{self.name} ({self.probability_percentage}%)"
    
    def __repr__(self):
        """Detailed representation of opportunity stage."""
        return (
            f"OpportunityStage(id={self.id}, name='{self.name}', code='{self.code}', "
            f"sequence={self.sequence_order}, probability={self.probability_percentage}%)"
        )
    
    @property
    def is_open_stage(self) -> bool:
        """Check if this is an open (active) stage."""
        return not (self.is_closed_won or self.is_closed_lost)
    
    @property
    def is_closed_stage(self) -> bool:
        """Check if this is a closed stage."""
        return self.is_closed_won or self.is_closed_lost
    
    def get_next_stage(self) -> Optional['OpportunityStage']:
        """Get the next stage in sequence."""
        # In production, would query database for next stage
        return None  # Simplified for demo
    
    def get_previous_stage(self) -> Optional['OpportunityStage']:
        """Get the previous stage in sequence."""
        # In production, would query database for previous stage
        return None  # Simplified for demo


class SalesOpportunity(CompanyBusinessObject):
    """
    Sales Opportunity model for tracking potential sales.
    
    Comprehensive opportunity management including pipeline tracking,
    forecasting, activities, and competitive analysis.
    """
    
    __tablename__ = "sales_opportunities"
    
    # Basic opportunity information
    name = Column(String(255), nullable=False, index=True)
    opportunity_number = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # Customer reference
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Opportunity classification
    source = Column(Enum(OpportunitySource), nullable=False, index=True)
    priority = Column(Enum(OpportunityPriority), nullable=False, default=OpportunityPriority.MEDIUM, index=True)
    
    # Pipeline management
    stage_id = Column(
        Integer,
        ForeignKey("opportunity_stages.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    probability_percentage = Column(Numeric(5, 2), nullable=False, default=0.0)
    
    # Financial information
    estimated_value = Column(Numeric(15, 2), nullable=False)
    weighted_value = Column(Numeric(15, 2), nullable=False, default=0.0)  # estimated_value * probability
    actual_value = Column(Numeric(15, 2), nullable=True)
    currency_code = Column(String(3), nullable=False, default="USD")
    
    # Timeline
    expected_close_date = Column(DateTime, nullable=False, index=True)
    actual_close_date = Column(DateTime, nullable=True, index=True)
    first_contact_date = Column(DateTime, nullable=True)
    last_activity_date = Column(DateTime, nullable=True)
    
    # Assignment and ownership
    sales_rep_user_id = Column(Integer, nullable=False, index=True)
    team_members = Column(JSON)  # Array of user IDs involved in opportunity
    
    # Lead information
    lead_qualification_score = Column(Integer, nullable=True)  # 0-100 score
    budget_confirmed = Column(Boolean, nullable=False, default=False)
    authority_confirmed = Column(Boolean, nullable=False, default=False)
    need_confirmed = Column(Boolean, nullable=False, default=False)
    timeline_confirmed = Column(Boolean, nullable=False, default=False)
    
    # Competitive information
    competitors = Column(JSON)  # Array of competitor names/info
    competitive_position = Column(String(50), nullable=True)  # "leading", "competitive", "behind"
    
    # Sales process tracking
    proposal_sent_date = Column(DateTime, nullable=True)
    contract_sent_date = Column(DateTime, nullable=True)
    decision_date = Column(DateTime, nullable=True)
    
    # Products and services
    products_interested = Column(JSON)  # Array of product IDs or names
    solution_requirements = Column(Text)
    
    # Closure information
    close_reason = Column(String(255), nullable=True)
    competitor_won = Column(String(255), nullable=True)
    lessons_learned = Column(Text)
    
    # Status and flags
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_archived = Column(Boolean, default=False, nullable=False)
    
    # Additional attributes
    tags = Column(JSON)  # Array of string tags
    custom_attributes = Column(JSON)
    
    # Relationships
    # customer = relationship("Customer", back_populates="opportunities")
    # stage = relationship("OpportunityStage", back_populates="opportunities")
    # activities = relationship("OpportunityActivity", back_populates="opportunity", cascade="all, delete-orphan")
    # quotes = relationship("SalesQuote", back_populates="opportunity")
    # orders = relationship("SalesOrder", back_populates="opportunity")
    
    def __str__(self):
        """String representation of sales opportunity."""
        return f"{self.name} ({self.opportunity_number})"
    
    def __repr__(self):
        """Detailed representation of sales opportunity."""
        return (
            f"SalesOpportunity(id={self.id}, name='{self.name}', "
            f"number='{self.opportunity_number}', value={self.estimated_value})"
        )
    
    @property
    def display_identifier(self) -> str:
        """Get display identifier with opportunity number."""
        return f"{self.name} ({self.opportunity_number})"
    
    @property
    def is_overdue(self) -> bool:
        """Check if opportunity is past expected close date."""
        if not self.expected_close_date or self.actual_close_date:
            return False
        return datetime.utcnow() > self.expected_close_date
    
    @property
    def days_until_close(self) -> Optional[int]:
        """Calculate days until expected close date."""
        if not self.expected_close_date or self.actual_close_date:
            return None
        delta = self.expected_close_date - datetime.utcnow()
        return delta.days
    
    @property
    def days_in_current_stage(self) -> int:
        """Calculate days in current stage."""
        # In production, would track stage entry date
        return 0  # Simplified for demo
    
    @property
    def sales_cycle_days(self) -> Optional[int]:
        """Calculate total sales cycle length."""
        if not self.first_contact_date:
            return None
        
        end_date = self.actual_close_date or datetime.utcnow()
        return (end_date - self.first_contact_date).days
    
    @property
    def bant_score(self) -> int:
        """Calculate BANT (Budget, Authority, Need, Timeline) qualification score."""
        score = 0
        if self.budget_confirmed:
            score += 25
        if self.authority_confirmed:
            score += 25
        if self.need_confirmed:
            score += 25
        if self.timeline_confirmed:
            score += 25
        return score
    
    @property
    def is_qualified_lead(self) -> bool:
        """Check if opportunity is a qualified lead (BANT score >= 75)."""
        return self.bant_score >= 75
    
    def generate_opportunity_number(self, prefix: str = "OPP") -> str:
        """Generate opportunity number if not provided."""
        # In production, would use company settings and sequence numbers
        import time
        timestamp = int(time.time())
        return f"{prefix}{timestamp:08d}"
    
    def update_weighted_value(self) -> None:
        """Update weighted value based on estimated value and probability."""
        self.weighted_value = (self.estimated_value * self.probability_percentage) / 100
    
    def advance_stage(self, new_stage_id: int, user_id: int = None) -> None:
        """Advance opportunity to next stage."""
        old_stage_id = self.stage_id
        self.stage_id = new_stage_id
        
        # Update probability based on new stage (would get from stage record)
        # self.probability_percentage = new_stage.probability_percentage
        self.update_weighted_value()
        
        # Log audit trail
        self.log_audit_trail("stage_advanced", user_id, {
            "old_stage_id": old_stage_id,
            "new_stage_id": new_stage_id
        })
        
        # Publish event
        self.publish_event("opportunity.stage_changed", {
            "opportunity_id": self.id,
            "opportunity_number": self.opportunity_number,
            "old_stage_id": old_stage_id,
            "new_stage_id": new_stage_id
        })
    
    def mark_won(self, actual_value: Decimal, close_reason: str = None, user_id: int = None) -> None:
        """Mark opportunity as won."""
        self.actual_close_date = datetime.utcnow()
        self.actual_value = actual_value
        self.probability_percentage = Decimal('100.00')
        self.close_reason = close_reason or "Won"
        self.update_weighted_value()
        
        # Log audit trail
        self.log_audit_trail("opportunity_won", user_id, {
            "actual_value": float(actual_value),
            "close_reason": close_reason
        })
        
        # Publish event
        self.publish_event("opportunity.won", {
            "opportunity_id": self.id,
            "opportunity_number": self.opportunity_number,
            "actual_value": float(actual_value),
            "customer_id": self.customer_id
        })
    
    def mark_lost(self, close_reason: str, competitor_won: str = None, user_id: int = None) -> None:
        """Mark opportunity as lost."""
        self.actual_close_date = datetime.utcnow()
        self.probability_percentage = Decimal('0.00')
        self.close_reason = close_reason
        self.competitor_won = competitor_won
        self.update_weighted_value()
        
        # Log audit trail
        self.log_audit_trail("opportunity_lost", user_id, {
            "close_reason": close_reason,
            "competitor_won": competitor_won
        })
        
        # Publish event
        self.publish_event("opportunity.lost", {
            "opportunity_id": self.id,
            "opportunity_number": self.opportunity_number,
            "close_reason": close_reason,
            "competitor_won": competitor_won,
            "customer_id": self.customer_id
        })
    
    def calculate_forecast_category(self) -> str:
        """Calculate forecast category based on probability and timeline."""
        if self.actual_close_date:
            return "closed"
        
        if self.probability_percentage >= 90:
            return "commit"
        elif self.probability_percentage >= 70:
            return "best_case"
        elif self.probability_percentage >= 50:
            return "pipeline"
        else:
            return "upside"


class OpportunityActivity(CompanyBusinessObject):
    """
    Opportunity Activity model for tracking sales interactions.
    
    Comprehensive activity logging including calls, meetings,
    emails, and other sales interactions with outcomes.
    """
    
    __tablename__ = "opportunity_activities"
    
    # Opportunity reference
    opportunity_id = Column(
        Integer,
        ForeignKey("sales_opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Activity information
    subject = Column(String(255), nullable=False)
    activity_type = Column(Enum(ActivityType), nullable=False, index=True)
    description = Column(Text)
    
    # Activity timing
    activity_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=True)
    scheduled_date = Column(DateTime, nullable=True, index=True)
    
    # Activity outcome and results
    outcome = Column(Enum(ActivityOutcome), nullable=True, index=True)
    outcome_description = Column(Text)
    
    # Participants
    created_by_user_id = Column(Integer, nullable=False, index=True)
    attendees = Column(JSON)  # Array of user IDs and external contacts
    
    # Follow-up information
    follow_up_required = Column(Boolean, nullable=False, default=False)
    follow_up_date = Column(DateTime, nullable=True, index=True)
    follow_up_notes = Column(Text)
    
    # Activity content
    attachments = Column(JSON)  # Array of document references
    recording_url = Column(String(500), nullable=True)  # For recorded calls/meetings
    
    # Integration data
    external_activity_id = Column(String(255), nullable=True, index=True)  # For calendar/email integration
    external_system = Column(String(100), nullable=True)  # Source system
    
    # Status
    is_completed = Column(Boolean, nullable=False, default=True, index=True)
    is_billable = Column(Boolean, nullable=False, default=False)
    
    # Additional metadata
    tags = Column(JSON)  # Array of string tags
    custom_attributes = Column(JSON)
    
    # Relationships
    # opportunity = relationship("SalesOpportunity", back_populates="activities")
    
    def __str__(self):
        """String representation of opportunity activity."""
        return f"{self.activity_type.value}: {self.subject}"
    
    def __repr__(self):
        """Detailed representation of opportunity activity."""
        return (
            f"OpportunityActivity(id={self.id}, type='{self.activity_type.value}', "
            f"subject='{self.subject}', opportunity_id={self.opportunity_id})"
        )
    
    @property
    def is_overdue(self) -> bool:
        """Check if scheduled activity is overdue."""
        if not self.scheduled_date or self.is_completed:
            return False
        return datetime.utcnow() > self.scheduled_date
    
    @property
    def duration_hours(self) -> Optional[float]:
        """Get duration in hours."""
        if not self.duration_minutes:
            return None
        return self.duration_minutes / 60.0
    
    @property
    def is_scheduled(self) -> bool:
        """Check if activity is scheduled for the future."""
        return self.scheduled_date is not None and not self.is_completed
    
    @property
    def is_follow_up_due(self) -> bool:
        """Check if follow-up is due."""
        if not self.follow_up_required or not self.follow_up_date:
            return False
        return datetime.utcnow() >= self.follow_up_date
    
    def mark_completed(self, outcome: ActivityOutcome = None, 
                      outcome_description: str = None, user_id: int = None) -> None:
        """Mark activity as completed."""
        self.is_completed = True
        self.activity_date = datetime.utcnow()
        
        if outcome:
            self.outcome = outcome
        if outcome_description:
            self.outcome_description = outcome_description
        
        # Log audit trail
        self.log_audit_trail("activity_completed", user_id, {
            "activity_type": self.activity_type.value,
            "outcome": outcome.value if outcome else None
        })
        
        # Publish event
        self.publish_event("opportunity_activity.completed", {
            "activity_id": self.id,
            "opportunity_id": self.opportunity_id,
            "activity_type": self.activity_type.value,
            "outcome": outcome.value if outcome else None
        })
    
    def schedule_follow_up(self, follow_up_date: datetime, notes: str = None) -> None:
        """Schedule follow-up for this activity."""
        self.follow_up_required = True
        self.follow_up_date = follow_up_date
        if notes:
            self.follow_up_notes = notes
        
        # Publish event for follow-up scheduling
        self.publish_event("opportunity_activity.follow_up_scheduled", {
            "activity_id": self.id,
            "opportunity_id": self.opportunity_id,
            "follow_up_date": follow_up_date.isoformat()
        })
    
    def create_follow_up_activity(self, subject: str, activity_type: ActivityType,
                                 scheduled_date: datetime, user_id: int) -> 'OpportunityActivity':
        """Create a follow-up activity."""
        follow_up = OpportunityActivity(
            company_id=self.company_id,
            opportunity_id=self.opportunity_id,
            subject=subject,
            activity_type=activity_type,
            scheduled_date=scheduled_date,
            created_by_user_id=user_id,
            is_completed=False,
            description=f"Follow-up to: {self.subject}"
        )
        
        # Mark this activity's follow-up as completed
        self.follow_up_required = False
        
        return follow_up