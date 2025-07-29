"""
Audit logging service for security and compliance tracking.
Provides centralized audit logging functionality for the application.
"""

import asyncio
from typing import Optional, Dict, Any, List
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from datetime import datetime, timedelta

from app.models.audit_log import AuditLog, AuditAction, AuditSeverity
from app.core.database import get_db


class AuditService:
    """Service for managing audit logs and security monitoring."""
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        action: AuditAction,
        description: str,
        user_id: Optional[int] = None,
        target_user_id: Optional[int] = None,
        service_id: Optional[int] = None,
        service_name: Optional[str] = None,
        request: Optional[Request] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_status: Optional[int] = None,
        severity: Optional[AuditSeverity] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> AuditLog:
        """
        Create and save an audit log entry.
        
        Args:
            db: Database session
            action: Type of action being logged
            description: Human-readable description
            user_id: ID of user performing action
            target_user_id: ID of user being acted upon
            service_id: ID of service performing action
            service_name: Name of service performing action
            request: FastAPI request object
            request_data: Request data to log (will be sanitized)
            response_status: HTTP response status
            severity: Log severity level
            success: Whether action succeeded
            error_message: Error message if action failed
            metadata: Additional metadata
            tags: Tags for categorization
            
        Returns:
            Created AuditLog instance
        """
        # Extract request context if provided
        ip_address = None
        user_agent = None
        endpoint = None
        http_method = None
        session_id = None
        request_id = None
        
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            endpoint = str(request.url.path)
            http_method = request.method
            session_id = getattr(request.state, 'session_id', None)
            request_id = getattr(request.state, 'request_id', None)
        
        # Create audit log entry
        audit_log = AuditLog.create_log(
            action=action,
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
            severity=severity or AuditSeverity.LOW,
            success=success,
            error_message=error_message,
            metadata=metadata,
            tags=tags,
            session_id=session_id,
            request_id=request_id
        )
        
        # Save to database
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        
        # Check for suspicious patterns asynchronously
        asyncio.create_task(AuditService._check_suspicious_patterns(audit_log))
        
        return audit_log
    
    @staticmethod
    async def log_authentication_success(
        db: AsyncSession,
        user_id: int,
        request: Optional[Request] = None,
        login_method: str = "password"
    ) -> AuditLog:
        """Log successful authentication."""
        return await AuditService.log_action(
            db=db,
            action=AuditAction.LOGIN_SUCCESS,
            description=f"User successfully authenticated using {login_method}",
            user_id=user_id,
            request=request,
            severity=AuditSeverity.LOW,
            success=True,
            metadata={"login_method": login_method},
            tags=["authentication", "success"]
        )
    
    @staticmethod
    async def log_authentication_failure(
        db: AsyncSession,
        email: str,
        reason: str,
        request: Optional[Request] = None,
        attempt_count: Optional[int] = None
    ) -> AuditLog:
        """Log failed authentication attempt."""
        severity = AuditSeverity.HIGH if attempt_count and attempt_count >= 3 else AuditSeverity.MEDIUM
        
        return await AuditService.log_action(
            db=db,
            action=AuditAction.LOGIN_FAILED,
            description=f"Authentication failed for {email}: {reason}",
            request=request,
            severity=severity,
            success=False,
            error_message=reason,
            metadata={"email": email, "reason": reason, "attempt_count": attempt_count},
            tags=["authentication", "failure"]
        )
    
    @staticmethod
    async def log_suspicious_activity(
        db: AsyncSession,
        activity_type: str,
        description: str,
        request: Optional[Request] = None,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log suspicious activity detection."""
        return await AuditService.log_action(
            db=db,
            action=AuditAction.SUSPICIOUS_ACTIVITY,
            description=f"Suspicious activity detected: {description}",
            user_id=user_id,
            request=request,
            severity=AuditSeverity.CRITICAL,
            success=False,
            metadata={
                **(metadata or {}),
                "activity_type": activity_type
            },
            tags=["security", "suspicious", activity_type]
        )
    
    @staticmethod
    async def log_rate_limit_exceeded(
        db: AsyncSession,
        identifier: str,
        endpoint: str,
        limit: int,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log rate limit exceeded event."""
        return await AuditService.log_action(
            db=db,
            action=AuditAction.RATE_LIMIT_EXCEEDED,
            description=f"Rate limit exceeded for {identifier} on {endpoint}",
            request=request,
            severity=AuditSeverity.HIGH,
            success=False,
            metadata={
                "identifier": identifier,
                "endpoint": endpoint,
                "limit": limit
            },
            tags=["rate_limiting", "security"]
        )
    
    @staticmethod
    async def log_admin_action(
        db: AsyncSession,
        admin_user_id: int,
        action_type: str,
        description: str,
        target_user_id: Optional[int] = None,
        request: Optional[Request] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log administrative actions."""
        return await AuditService.log_action(
            db=db,
            action=AuditAction.ADMIN_ACTION,
            description=f"Admin action: {description}",
            user_id=admin_user_id,
            target_user_id=target_user_id,
            request=request,
            severity=AuditSeverity.MEDIUM,
            success=True,
            metadata={
                **(metadata or {}),
                "action_type": action_type
            },
            tags=["admin", "management", action_type]
        )
    
    @staticmethod
    async def log_service_action(
        db: AsyncSession,
        service_id: int,
        service_name: str,
        action: AuditAction,
        description: str,
        request: Optional[Request] = None,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log service-to-service actions."""
        return await AuditService.log_action(
            db=db,
            action=action,
            description=description,
            service_id=service_id,
            service_name=service_name,
            request=request,
            severity=AuditSeverity.LOW,
            success=success,
            metadata=metadata,
            tags=["service", "inter_service"]
        )
    
    @staticmethod
    async def get_audit_logs(
        db: AsyncSession,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        severity: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        success: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Query audit logs with filtering options.
        
        Args:
            db: Database session
            user_id: Filter by user ID
            action: Filter by action type
            severity: Filter by severity level
            start_date: Filter by start date
            end_date: Filter by end date
            ip_address: Filter by IP address
            success: Filter by success status
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of matching audit logs
        """
        query = select(AuditLog)
        conditions = []
        
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if action:
            conditions.append(AuditLog.action == action)
        if severity:
            conditions.append(AuditLog.severity == severity)
        if start_date:
            conditions.append(AuditLog.created_at >= start_date)
        if end_date:
            conditions.append(AuditLog.created_at <= end_date)
        if ip_address:
            conditions.append(AuditLog.ip_address == ip_address)
        if success is not None:
            conditions.append(AuditLog.success == success)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(AuditLog.created_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_security_summary(
        db: AsyncSession,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get security summary for the specified time period.
        
        Args:
            db: Database session
            hours: Number of hours to look back
            
        Returns:
            Dictionary containing security metrics
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Total events
        total_query = select(func.count(AuditLog.id)).where(AuditLog.created_at >= since)
        total_result = await db.execute(total_query)
        total_events = total_result.scalar()
        
        # Failed authentication attempts
        failed_auth_query = select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.created_at >= since,
                AuditLog.action == AuditAction.LOGIN_FAILED.value
            )
        )
        failed_auth_result = await db.execute(failed_auth_query)
        failed_auth = failed_auth_result.scalar()
        
        # Suspicious activities
        suspicious_query = select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.created_at >= since,
                AuditLog.action == AuditAction.SUSPICIOUS_ACTIVITY.value
            )
        )
        suspicious_result = await db.execute(suspicious_query)
        suspicious_activities = suspicious_result.scalar()
        
        # Rate limit violations
        rate_limit_query = select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.created_at >= since,
                AuditLog.action == AuditAction.RATE_LIMIT_EXCEEDED.value
            )
        )
        rate_limit_result = await db.execute(rate_limit_query)
        rate_limit_violations = rate_limit_result.scalar()
        
        # Top IPs by failed attempts
        top_ips_query = select(
            AuditLog.ip_address,
            func.count(AuditLog.id).label('count')
        ).where(
            and_(
                AuditLog.created_at >= since,
                AuditLog.success == False,
                AuditLog.ip_address.isnot(None)
            )
        ).group_by(AuditLog.ip_address).order_by(desc('count')).limit(10)
        
        top_ips_result = await db.execute(top_ips_query)
        top_ips = [{"ip": row.ip_address, "failed_attempts": row.count} 
                   for row in top_ips_result]
        
        return {
            "period_hours": hours,
            "total_events": total_events,
            "failed_authentications": failed_auth,
            "suspicious_activities": suspicious_activities,
            "rate_limit_violations": rate_limit_violations,
            "top_failing_ips": top_ips,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def _check_suspicious_patterns(audit_log: AuditLog):
        """
        Asynchronously check for suspicious patterns and create alerts.
        This runs in the background to avoid blocking the main request.
        """
        try:
            # Get new database session for background task
            async for db in get_db():
                # Check for multiple failed logins from same IP
                if (audit_log.action == AuditAction.LOGIN_FAILED.value and 
                    audit_log.ip_address):
                    
                    recent_failures = await AuditService._count_recent_failures(
                        db, audit_log.ip_address, minutes=15
                    )
                    
                    if recent_failures >= 5:
                        await AuditService.log_suspicious_activity(
                            db=db,
                            activity_type="multiple_failed_logins",
                            description=f"Multiple failed login attempts from IP {audit_log.ip_address}",
                            metadata={
                                "ip_address": audit_log.ip_address,
                                "failure_count": recent_failures,
                                "time_window_minutes": 15
                            }
                        )
                break
        except Exception as e:
            # Log error but don't raise to avoid affecting main request
            print(f"Error in suspicious pattern check: {e}")
    
    @staticmethod
    async def _count_recent_failures(
        db: AsyncSession,
        ip_address: str,
        minutes: int = 15
    ) -> int:
        """Count recent authentication failures from specific IP."""
        since = datetime.utcnow() - timedelta(minutes=minutes)
        
        query = select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.created_at >= since,
                AuditLog.ip_address == ip_address,
                AuditLog.action == AuditAction.LOGIN_FAILED.value
            )
        )
        
        result = await db.execute(query)
        return result.scalar() or 0


# Convenience functions for common audit actions
async def audit_login_success(
    db: AsyncSession,
    user_id: int,
    request: Optional[Request] = None,
    login_method: str = "password"
) -> AuditLog:
    """Convenience function for logging successful login."""
    return await AuditService.log_authentication_success(
        db, user_id, request, login_method
    )


async def audit_login_failure(
    db: AsyncSession,
    email: str,
    reason: str,
    request: Optional[Request] = None,
    attempt_count: Optional[int] = None
) -> AuditLog:
    """Convenience function for logging failed login."""
    return await AuditService.log_authentication_failure(
        db, email, reason, request, attempt_count
    )


async def audit_admin_action(
    db: AsyncSession,
    admin_user_id: int,
    action_type: str,
    description: str,
    target_user_id: Optional[int] = None,
    request: Optional[Request] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """Convenience function for logging admin actions."""
    return await AuditService.log_admin_action(
        db, admin_user_id, action_type, description, target_user_id, request, metadata
    )