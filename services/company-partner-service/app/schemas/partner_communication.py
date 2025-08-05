"""
Partner Communication schemas for API request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class PartnerCommunicationBase(BaseModel):
    """Base schema for partner communication data."""
    partner_contact_id: Optional[int] = None
    communication_type: str = Field(default="email", max_length=50)
    subject: str = Field(..., min_length=1, max_length=500)
    content: Optional[str] = None
    direction: str = Field(default="outbound", max_length=20)
    initiated_by: Optional[str] = Field(None, max_length=255)
    participants: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: str = Field(default="pending", max_length=20)
    priority: str = Field(default="normal", max_length=20)
    outcome: Optional[str] = Field(None, max_length=100)
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    tags: Optional[str] = None
    attachments_count: int = Field(default=0, ge=0)
    external_reference: Optional[str] = Field(None, max_length=255)

    @validator('communication_type')
    def validate_communication_type(cls, v):
        valid_types = ['email', 'phone', 'meeting', 'video_call', 'letter', 'fax', 'text', 'other']
        if v not in valid_types:
            raise ValueError(f'Communication type must be one of: {", ".join(valid_types)}')
        return v

    @validator('direction')
    def validate_direction(cls, v):
        valid_directions = ['inbound', 'outbound']
        if v not in valid_directions:
            raise ValueError(f'Direction must be one of: {", ".join(valid_directions)}')
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'failed']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v

    @validator('subject')
    def validate_subject(cls, v):
        if v and len(v.strip()) < 1:
            raise ValueError('Subject cannot be empty')
        return v.strip() if v else v


class PartnerCommunicationCreate(PartnerCommunicationBase):
    """Schema for creating a new partner communication."""
    partner_id: int = Field(..., gt=0)


class PartnerCommunicationUpdate(BaseModel):
    """Schema for updating a partner communication."""
    partner_contact_id: Optional[int] = None
    communication_type: Optional[str] = Field(None, max_length=50)
    subject: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    direction: Optional[str] = Field(None, max_length=20)
    initiated_by: Optional[str] = Field(None, max_length=255)
    participants: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=20)
    priority: Optional[str] = Field(None, max_length=20)
    outcome: Optional[str] = Field(None, max_length=100)
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None
    tags: Optional[str] = None
    attachments_count: Optional[int] = Field(None, ge=0)
    external_reference: Optional[str] = Field(None, max_length=255)

    @validator('communication_type')
    def validate_communication_type(cls, v):
        if v:
            valid_types = ['email', 'phone', 'meeting', 'video_call', 'letter', 'fax', 'text', 'other']
            if v not in valid_types:
                raise ValueError(f'Communication type must be one of: {", ".join(valid_types)}')
        return v

    @validator('direction')
    def validate_direction(cls, v):
        if v:
            valid_directions = ['inbound', 'outbound']
            if v not in valid_directions:
                raise ValueError(f'Direction must be one of: {", ".join(valid_directions)}')
        return v

    @validator('status')
    def validate_status(cls, v):
        if v:
            valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'failed']
            if v not in valid_statuses:
                raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        if v:
            valid_priorities = ['low', 'normal', 'high', 'urgent']
            if v not in valid_priorities:
                raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v

    @validator('subject')
    def validate_subject(cls, v):
        if v and len(v.strip()) < 1:
            raise ValueError('Subject cannot be empty')
        return v.strip() if v else v


class PartnerCommunicationResponse(PartnerCommunicationBase):
    """Schema for partner communication response."""
    id: int
    partner_id: int
    is_completed: bool
    is_pending: bool
    is_overdue: bool
    needs_follow_up: bool
    duration_minutes: Optional[int]
    is_inbound: bool
    is_high_priority: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PartnerCommunicationListResponse(BaseModel):
    """Schema for partner communication list response."""
    communications: List[PartnerCommunicationResponse]
    total: int
    page: int
    per_page: int
    pages: int


class PartnerCommunicationStatsResponse(BaseModel):
    """Schema for partner communication statistics response."""
    total_communications: int
    pending_communications: int
    completed_communications: int
    overdue_communications: int
    follow_ups_required: int
    communications_by_type: dict
    communications_by_priority: dict
    recent_activity: List[dict]


class PartnerCommunicationBulkActionRequest(BaseModel):
    """Schema for bulk actions on partner communications."""
    communication_ids: List[int] = Field(..., min_items=1)
    action: str = Field(..., pattern=r'^(complete|cancel|delete|update_status)$')
    data: Optional[dict] = None  # Additional data for the action