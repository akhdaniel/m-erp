"""
Audit Log schemas for API requests and responses.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class AuditLogBase(BaseModel):
    """Base audit log schema."""
    event_id: str = Field(..., description="Original event ID from message queue")
    event_type: str = Field(..., description="Type of event")
    entity_type: str = Field(..., description="Type of entity affected")
    entity_id: str = Field(..., description="ID of the affected entity")
    company_id: Optional[int] = Field(None, description="Company context")
    user_id: Optional[int] = Field(None, description="User who triggered the event")
    source_service: str = Field(..., description="Service that generated the event")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracking")
    timestamp: datetime = Field(..., description="When the event occurred")
    before_data: Optional[Dict[str, Any]] = Field(None, description="Entity state before")
    after_data: Optional[Dict[str, Any]] = Field(None, description="Entity state after")
    changes: Optional[Dict[str, Any]] = Field(None, description="Specific changes made")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AuditLogCreate(AuditLogBase):
    """Schema for creating audit log entries."""
    pass


class AuditLogResponse(AuditLogBase):
    """Schema for audit log responses."""
    id: int = Field(..., description="Audit log ID")
    created_at: datetime = Field(..., description="When this audit log was created")
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, audit_log):
        """Create response from ORM model."""
        return cls(
            id=audit_log.id,
            event_id=audit_log.event_id,
            event_type=audit_log.event_type,
            entity_type=audit_log.entity_type,
            entity_id=audit_log.entity_id,
            company_id=audit_log.company_id,
            user_id=audit_log.user_id,
            source_service=audit_log.source_service,
            correlation_id=audit_log.correlation_id,
            timestamp=audit_log.timestamp,
            before_data=audit_log.before_data,
            after_data=audit_log.after_data,
            changes=audit_log.changes,
            metadata=audit_log.event_metadata,
            created_at=audit_log.created_at
        )


class AuditLogSummary(BaseModel):
    """Summary schema for audit log entries."""
    id: int = Field(..., description="Audit log ID")
    event_type: str = Field(..., description="Type of event")
    entity_type: str = Field(..., description="Type of entity affected")
    entity_id: str = Field(..., description="ID of the affected entity")
    timestamp: datetime = Field(..., description="When the event occurred")
    action_description: str = Field(..., description="Human-readable action description")
    summary: str = Field(..., description="One-line summary")
    changes_summary: Optional[str] = Field(None, description="Summary of changes")


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log responses."""
    items: List[AuditLogResponse] = Field(..., description="List of audit log entries")
    total: int = Field(..., description="Total number of entries")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum number of items returned")
    
    @property
    def has_more(self) -> bool:
        """Check if there are more items available."""
        return (self.skip + len(self.items)) < self.total


class AuditStats(BaseModel):
    """Audit statistics schema."""
    total_events: int = Field(..., description="Total number of audit events")
    events_by_type: Dict[str, int] = Field(..., description="Event count by type")
    events_by_service: Dict[str, int] = Field(..., description="Event count by service")
    events_by_entity_type: Dict[str, int] = Field(..., description="Event count by entity type")
    events_last_24h: int = Field(..., description="Events in the last 24 hours")
    events_last_7d: int = Field(..., description="Events in the last 7 days")
    most_active_users: List[Dict[str, Any]] = Field(..., description="Most active users")
    most_active_companies: List[Dict[str, Any]] = Field(..., description="Most active companies")