"""
Audit logging model for security and compliance tracking.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Index
from sqlalchemy.sql import func
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum

from app.core.database import Base


class AuditAction(str, Enum):
    """Audit action types for categorization."""
    
    # Authentication actions
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    PASSWORD_CHANGE = "password_change"
    EMAIL_CHANGE = "email_change"
    
    # User management actions
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ACTIVATED = "user_activated"
    USER_DEACTIVATED = "user_deactivated"
    
    # Role and permission actions
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    
    # Service management actions
    SERVICE_REGISTERED = "service_registered"
    SERVICE_TOKEN_ISSUED = "service_token_issued"
    SERVICE_TOKEN_REVOKED = "service_token_revoked"
    SERVICE_ACTIVATED = "service_activated"
    SERVICE_DEACTIVATED = "service_deactivated"
    
    # Security events
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_DENIED = "permission_denied"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    
    # Admin actions
    ADMIN_ACTION = "admin_action"
    BULK_OPERATION = "bulk_operation"
    SYSTEM_CONFIG_CHANGE = "system_config_change"


class AuditSeverity(str, Enum):
    """Audit log severity levels."""
    
    LOW = "low"           # Normal operations
    MEDIUM = "medium"     # Important changes
    HIGH = "high"         # Security events
    CRITICAL = "critical" # Security breaches


class AuditLog(Base):
    """
    Audit log model for tracking all security-relevant actions.
    Implements comprehensive logging for compliance and security monitoring.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Core audit information
    action = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default=AuditSeverity.LOW, index=True)
    description = Column(String(500), nullable=False)
    
    # User and session context
    user_id = Column(Integer, nullable=True, index=True)  # User performing action
    target_user_id = Column(Integer, nullable=True, index=True)  # User being acted upon
    session_id = Column(String(255), nullable=True, index=True)
    request_id = Column(String(255), nullable=True, index=True)
    
    # Service context (for service-to-service actions)
    service_id = Column(Integer, nullable=True, index=True)
    service_name = Column(String(100), nullable=True)
    
    # Network and client information
    ip_address = Column(String(45), nullable=True, index=True)  # Supports IPv6
    user_agent = Column(Text, nullable=True)
    client_info = Column(JSON, nullable=True)  # Additional client metadata
    
    # Request context
    endpoint = Column(String(255), nullable=True, index=True)
    http_method = Column(String(10), nullable=True)
    request_data = Column(JSON, nullable=True)  # Sanitized request data
    response_status = Column(Integer, nullable=True)
    
    # Additional metadata
    additional_data = Column(JSON, nullable=True)  # Flexible additional data
    tags = Column(JSON, nullable=True)  # For categorization and searching
    
    # Outcome and impact
    success = Column(Boolean, nullable=False, default=True, index=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_ip_created', 'ip_address', 'created_at'),
        Index('idx_audit_severity_created', 'severity', 'created_at'),
        Index('idx_audit_action_created', 'action', 'created_at'),
        Index('idx_audit_success_created', 'success', 'created_at'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id}, created_at={self.created_at})>"

    @classmethod
    def create_log(
        cls,
        action: AuditAction,
        description: str,
        user_id: Optional[int] = None,
        target_user_id: Optional[int] = None,
        service_id: Optional[int] = None,
        service_name: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_status: Optional[int] = None,
        severity: AuditSeverity = AuditSeverity.LOW,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> 'AuditLog':
        """
        Create a new audit log entry with comprehensive context.
        
        Args:
            action: Type of action being logged
            description: Human-readable description
            user_id: ID of user performing action
            target_user_id: ID of user being acted upon (if different)
            service_id: ID of service performing action (for service actions)
            service_name: Name of service performing action
            ip_address: Client IP address
            user_agent: Client user agent
            endpoint: API endpoint accessed
            http_method: HTTP method used
            request_data: Sanitized request data
            response_status: HTTP response status
            severity: Log severity level
            success: Whether action succeeded
            error_message: Error message if action failed
            metadata: Additional metadata
            tags: Tags for categorization
            session_id: Session identifier
            request_id: Request identifier
            
        Returns:
            AuditLog instance
        """
        # Sanitize sensitive data from request_data
        if request_data:
            request_data = cls._sanitize_request_data(request_data)
        
        # Auto-determine severity based on action if not specified
        if severity == AuditSeverity.LOW:
            severity = cls._determine_severity(action, success)
        
        return cls(
            action=action.value,
            severity=severity.value,
            description=description,
            user_id=user_id,
            target_user_id=target_user_id,
            service_id=service_id,
            service_name=service_name,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            http_method=http_method,
            request_data=request_data,
            response_status=response_status,
            success=success,
            error_message=error_message,
            metadata=metadata,
            tags=tags,
            session_id=session_id,
            request_id=request_id
        )
    
    @staticmethod
    def _sanitize_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from request data."""
        sensitive_keys = [
            'password', 'token', 'secret', 'key', 'authorization',
            'current_password', 'new_password', 'service_secret'
        ]
        
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = AuditLog._sanitize_request_data(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def _determine_severity(action: AuditAction, success: bool) -> AuditSeverity:
        """Auto-determine severity based on action type and success."""
        # Critical severity actions
        critical_actions = [
            AuditAction.UNAUTHORIZED_ACCESS,
            AuditAction.SUSPICIOUS_ACTIVITY,
            AuditAction.ACCOUNT_LOCKED
        ]
        
        # High severity actions
        high_actions = [
            AuditAction.LOGIN_FAILED,
            AuditAction.PERMISSION_DENIED,
            AuditAction.RATE_LIMIT_EXCEEDED,
            AuditAction.SERVICE_TOKEN_REVOKED,
            AuditAction.USER_DELETED,
            AuditAction.SYSTEM_CONFIG_CHANGE
        ]
        
        # Medium severity actions
        medium_actions = [
            AuditAction.PASSWORD_CHANGE,
            AuditAction.EMAIL_CHANGE,
            AuditAction.ROLE_ASSIGNED,
            AuditAction.ROLE_REMOVED,
            AuditAction.USER_DEACTIVATED,
            AuditAction.SERVICE_REGISTERED,
            AuditAction.ADMIN_ACTION
        ]
        
        if action in critical_actions or (not success and action in high_actions):
            return AuditSeverity.CRITICAL
        elif action in high_actions or (not success and action in medium_actions):
            return AuditSeverity.HIGH
        elif action in medium_actions:
            return AuditSeverity.MEDIUM
        else:
            return AuditSeverity.LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "action": self.action,
            "severity": self.severity,
            "description": self.description,
            "user_id": self.user_id,
            "target_user_id": self.target_user_id,
            "service_id": self.service_id,
            "service_name": self.service_name,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "endpoint": self.endpoint,
            "http_method": self.http_method,
            "response_status": self.response_status,
            "success": self.success,
            "error_message": self.error_message,
            "metadata": self.metadata,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }