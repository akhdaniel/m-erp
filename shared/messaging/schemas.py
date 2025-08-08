"""
Message schemas for XERPIUM messaging system.
"""
from datetime import datetime
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field
from .events import MessageType, EventType, CommandType, NotificationType


class BaseMessage(BaseModel):
    """Base message schema with common fields."""
    id: str = Field(..., description="Unique message identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message creation timestamp")
    source_service: str = Field(..., description="Service that sent the message")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracking related messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Message(BaseMessage):
    """Generic message for all communication types."""
    type: MessageType = Field(..., description="Type of message (event, command, notification)")
    subject: str = Field(..., description="Subject/topic of the message")
    payload: Dict[str, Any] = Field(..., description="Message payload data")
    target_service: Optional[str] = Field(None, description="Target service (for commands)")
    reply_to: Optional[str] = Field(None, description="Reply channel for response messages")


class Event(BaseMessage):
    """Business event message."""
    type: MessageType = Field(default=MessageType.EVENT, description="Message type (always 'event')")
    event_type: EventType = Field(..., description="Specific event type")
    entity_type: str = Field(..., description="Type of entity (user, company, partner, etc.)")
    entity_id: Union[str, int] = Field(..., description="ID of the affected entity")
    company_id: Optional[Union[str, int]] = Field(None, description="Company context for multi-tenant operations")
    user_id: Optional[Union[str, int]] = Field(None, description="User who triggered the event")
    before_data: Optional[Dict[str, Any]] = Field(None, description="Entity state before the event")
    after_data: Optional[Dict[str, Any]] = Field(None, description="Entity state after the event")
    changes: Optional[Dict[str, Any]] = Field(None, description="Changed fields and their new values")


class Command(BaseMessage):
    """Inter-service command message."""
    type: MessageType = Field(default=MessageType.COMMAND, description="Message type (always 'command')")
    command_type: CommandType = Field(..., description="Specific command type")
    target_service: str = Field(..., description="Service that should execute the command")
    payload: Dict[str, Any] = Field(..., description="Command parameters")
    reply_to: Optional[str] = Field(None, description="Channel to send response to")
    timeout: Optional[int] = Field(30, description="Command timeout in seconds")


class Notification(BaseMessage):
    """UI notification message."""
    type: MessageType = Field(default=MessageType.NOTIFICATION, description="Message type (always 'notification')")
    notification_type: NotificationType = Field(..., description="Specific notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    target_user_id: Optional[Union[str, int]] = Field(None, description="Specific user to notify")
    target_company_id: Optional[Union[str, int]] = Field(None, description="Company users to notify")
    channel: str = Field(default="general", description="Notification channel")
    priority: int = Field(default=1, description="Priority level (1=low, 2=medium, 3=high)")
    expires_at: Optional[datetime] = Field(None, description="When notification expires")


class CommandResponse(BaseModel):
    """Response to a command message."""
    command_id: str = Field(..., description="ID of the original command")
    success: bool = Field(..., description="Whether command was successful")
    result: Optional[Dict[str, Any]] = Field(None, description="Command result data")
    error: Optional[str] = Field(None, description="Error message if command failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    execution_time_ms: Optional[int] = Field(None, description="Command execution time in milliseconds")


class HealthCheckMessage(BaseModel):
    """Health check message for service monitoring."""
    service_name: str = Field(..., description="Name of the service")
    status: str = Field(..., description="Service status (healthy, unhealthy, unknown)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional health details")
    uptime_seconds: Optional[int] = Field(None, description="Service uptime in seconds")
    version: Optional[str] = Field(None, description="Service version")