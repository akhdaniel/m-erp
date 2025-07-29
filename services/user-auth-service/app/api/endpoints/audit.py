"""
Audit log API endpoints for security monitoring and compliance.
Provides read-only access to audit logs for administrators.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.routers.auth import get_current_user, get_admin_user
from app.models.user import User
from app.models.audit_log import AuditLog, AuditAction, AuditSeverity
from app.services.audit_service import AuditService


router = APIRouter()


class AuditLogResponse(BaseModel):
    """Audit log response model."""
    id: int
    action: str
    severity: str
    description: str
    user_id: Optional[int]
    target_user_id: Optional[int]
    service_id: Optional[int]
    service_name: Optional[str]
    ip_address: Optional[str]
    endpoint: Optional[str]
    http_method: Optional[str]
    response_status: Optional[int]
    success: bool
    error_message: Optional[str]
    metadata: Optional[dict]
    tags: Optional[List[str]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SecuritySummaryResponse(BaseModel):
    """Security summary response model."""
    period_hours: int
    total_events: int
    failed_authentications: int
    suspicious_activities: int
    rate_limit_violations: int
    top_failing_ips: List[dict]
    generated_at: str


class AuditLogListResponse(BaseModel):
    """Paginated audit log list response."""
    logs: List[AuditLogResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


@router.get(
    "/logs",
    response_model=AuditLogListResponse,
    summary="Get audit logs",
    description="Retrieve audit logs with filtering and pagination options"
)
async def get_audit_logs(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    success: Optional[bool] = Query(None, description="Filter by success status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get audit logs with filtering options.
    Requires 'audit:read' permission.
    """
    # Validate date range
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    # Validate action enum
    if action:
        try:
            AuditAction(action)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action type: {action}"
            )
    
    # Validate severity enum
    if severity:
        try:
            AuditSeverity(severity)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid severity level: {severity}"
            )
    
    # Get logs
    logs = await AuditService.get_audit_logs(
        db=db,
        user_id=user_id,
        action=action,
        severity=severity,
        start_date=start_date,
        end_date=end_date,
        ip_address=ip_address,
        success=success,
        limit=limit + 1,  # Get one extra to check if there are more
        offset=offset
    )
    
    # Check if there are more results
    has_more = len(logs) > limit
    if has_more:
        logs = logs[:limit]  # Remove the extra log
    
    # Convert to response models
    log_responses = [
        AuditLogResponse(
            id=log.id,
            action=log.action,
            severity=log.severity,
            description=log.description,
            user_id=log.user_id,
            target_user_id=log.target_user_id,
            service_id=log.service_id,
            service_name=log.service_name,
            ip_address=log.ip_address,
            endpoint=log.endpoint,
            http_method=log.http_method,
            response_status=log.response_status,
            success=log.success,
            error_message=log.error_message,
            metadata=log.metadata,
            tags=log.tags,
            created_at=log.created_at
        )
        for log in logs
    ]
    
    return AuditLogListResponse(
        logs=log_responses,
        total=len(log_responses),
        limit=limit,
        offset=offset,
        has_more=has_more
    )


@router.get(
    "/security-summary",
    response_model=SecuritySummaryResponse,
    summary="Get security summary",
    description="Get security metrics and summary for specified time period"
)
async def get_security_summary(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze (max 7 days)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get security summary for the specified time period.
    Requires 'audit:read' permission.
    """
    summary = await AuditService.get_security_summary(db=db, hours=hours)
    
    return SecuritySummaryResponse(**summary)


@router.get(
    "/actions",
    response_model=List[str],
    summary="Get available audit actions",
    description="Get list of all available audit action types"
)
async def get_audit_actions(
    current_user: User = Depends(get_admin_user)
):
    """
    Get list of all available audit action types.
    Requires 'audit:read' permission.
    """
    return [action.value for action in AuditAction]


@router.get(
    "/severities",
    response_model=List[str],
    summary="Get available severity levels",
    description="Get list of all available audit severity levels"
)
async def get_audit_severities(
    current_user: User = Depends(get_admin_user)
):
    """
    Get list of all available audit severity levels.
    Requires 'audit:read' permission.
    """
    return [severity.value for severity in AuditSeverity]


@router.get(
    "/user/{user_id}/recent",
    response_model=List[AuditLogResponse],
    summary="Get recent audit logs for user",
    description="Get recent audit logs for a specific user"
)
async def get_user_recent_audit_logs(
    user_id: int,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get recent audit logs for a specific user.
    Requires 'audit:read' permission.
    """
    start_date = datetime.utcnow() - timedelta(hours=hours)
    
    logs = await AuditService.get_audit_logs(
        db=db,
        user_id=user_id,
        start_date=start_date,
        limit=limit,
        offset=0
    )
    
    return [
        AuditLogResponse(
            id=log.id,
            action=log.action,
            severity=log.severity,
            description=log.description,
            user_id=log.user_id,
            target_user_id=log.target_user_id,
            service_id=log.service_id,
            service_name=log.service_name,
            ip_address=log.ip_address,
            endpoint=log.endpoint,
            http_method=log.http_method,
            response_status=log.response_status,
            success=log.success,
            error_message=log.error_message,
            metadata=log.metadata,
            tags=log.tags,
            created_at=log.created_at
        )
        for log in logs
    ]


@router.get(
    "/failed-logins",
    response_model=List[AuditLogResponse],
    summary="Get failed login attempts",
    description="Get recent failed login attempts for security monitoring"
)
async def get_failed_login_attempts(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get recent failed login attempts for security monitoring.
    Requires 'audit:read' permission.
    """
    start_date = datetime.utcnow() - timedelta(hours=hours)
    
    logs = await AuditService.get_audit_logs(
        db=db,
        action=AuditAction.LOGIN_FAILED.value,
        start_date=start_date,
        ip_address=ip_address,
        success=False,
        limit=limit,
        offset=0
    )
    
    return [
        AuditLogResponse(
            id=log.id,
            action=log.action,
            severity=log.severity,
            description=log.description,
            user_id=log.user_id,
            target_user_id=log.target_user_id,
            service_id=log.service_id,
            service_name=log.service_name,
            ip_address=log.ip_address,
            endpoint=log.endpoint,
            http_method=log.http_method,
            response_status=log.response_status,
            success=log.success,
            error_message=log.error_message,
            metadata=log.metadata,
            tags=log.tags,
            created_at=log.created_at
        )
        for log in logs
    ]


@router.get(
    "/suspicious-activity",
    response_model=List[AuditLogResponse],
    summary="Get suspicious activities",
    description="Get recent suspicious activities detected by the system"
)
async def get_suspicious_activities(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Get recent suspicious activities detected by the system.
    Requires 'audit:read' permission.
    """
    # Validate severity if provided
    if severity:
        try:
            AuditSeverity(severity)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid severity level: {severity}"
            )
    
    start_date = datetime.utcnow() - timedelta(hours=hours)
    
    logs = await AuditService.get_audit_logs(
        db=db,
        action=AuditAction.SUSPICIOUS_ACTIVITY.value,
        start_date=start_date,
        severity=severity,
        limit=limit,
        offset=0
    )
    
    return [
        AuditLogResponse(
            id=log.id,
            action=log.action,
            severity=log.severity,
            description=log.description,
            user_id=log.user_id,
            target_user_id=log.target_user_id,
            service_id=log.service_id,
            service_name=log.service_name,
            ip_address=log.ip_address,
            endpoint=log.endpoint,
            http_method=log.http_method,
            response_status=log.response_status,
            success=log.success,
            error_message=log.error_message,
            metadata=log.metadata,
            tags=log.tags,
            created_at=log.created_at
        )
        for log in logs
    ]