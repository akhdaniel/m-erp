"""
Audit middleware for automatic security event logging.
Integrates with the audit service to log security-relevant events.
"""

import time
import json
from typing import Callable, Optional, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.audit_service import AuditService
from app.models.audit_log import AuditAction, AuditSeverity
from app.core.database import get_db


class AuditContext:
    """Context manager for audit logging during request processing."""
    
    def __init__(self, request: Request, db: AsyncSession):
        self.request = request
        self.db = db
        self.start_time = time.time()
        self.user_id: Optional[int] = None
        self.service_id: Optional[int] = None
        self.service_name: Optional[str] = None
        self.logged_events: list[str] = []
    
    def set_user_context(self, user_id: int):
        """Set user context for audit logging."""
        self.user_id = user_id
        
    def set_service_context(self, service_id: int, service_name: str):
        """Set service context for audit logging."""
        self.service_id = service_id
        self.service_name = service_name
    
    async def log_event(
        self,
        action: AuditAction,
        description: str,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        severity: Optional[AuditSeverity] = None
    ):
        """Log an audit event with current context."""
        event_key = f"{action.value}:{description}"
        if event_key in self.logged_events:
            return  # Avoid duplicate logging
        
        await AuditService.log_action(
            db=self.db,
            action=action,
            description=description,
            user_id=self.user_id,
            service_id=self.service_id,
            service_name=self.service_name,
            request=self.request,
            success=success,
            error_message=error_message,
            metadata=metadata,
            severity=severity
        )
        
        self.logged_events.append(event_key)


async def audit_middleware(request: Request, call_next: Callable) -> Response:
    """
    Audit middleware for automatic security event logging.
    Logs all security-relevant requests and responses.
    """
    start_time = time.time()
    
    # Get database session
    async for db in get_db():
        # Create audit context
        audit_ctx = AuditContext(request, db)
        request.state.audit_context = audit_ctx
        
        # Determine if this is a security-relevant endpoint
        is_security_endpoint = _is_security_endpoint(request.url.path)
        
        # Log request start for security endpoints
        if is_security_endpoint:
            await _log_request_start(audit_ctx, request)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Log successful response for security endpoints
            if is_security_endpoint:
                await _log_request_success(audit_ctx, request, response, start_time)
            
            # Log specific endpoint actions
            await _log_endpoint_specific_events(audit_ctx, request, response)
            
            return response
            
        except Exception as e:
            # Log request failure
            if is_security_endpoint:
                await _log_request_failure(audit_ctx, request, e, start_time)
            raise
        
        finally:
            await db.close()
        
        break  # Exit the async generator


def _is_security_endpoint(path: str) -> bool:
    """Determine if endpoint is security-relevant and should be audited."""
    security_paths = [
        "/api/auth/",
        "/api/admin/",
        "/api/services/",
        "/api/validate/"
    ]
    return any(path.startswith(sp) for sp in security_paths)


async def _log_request_start(audit_ctx: AuditContext, request: Request):
    """Log the start of a security-relevant request."""
    endpoint = request.url.path
    method = request.method
    
    # Don't log routine operations
    routine_endpoints = ["/health", "/docs", "/openapi.json", "/redoc"]
    if any(endpoint.endswith(re) for re in routine_endpoints):
        return
    
    # Log request initiation for sensitive endpoints
    sensitive_endpoints = [
        "/api/auth/login",
        "/api/auth/register", 
        "/api/auth/change-password",
        "/api/admin/",
        "/api/services/token",
        "/api/services/register"
    ]
    
    if any(endpoint.startswith(se) for se in sensitive_endpoints):
        await audit_ctx.log_event(
            action=AuditAction.ADMIN_ACTION,  # Generic action for request start
            description=f"Security endpoint accessed: {method} {endpoint}",
            severity=AuditSeverity.LOW,
            metadata={
                "endpoint": endpoint,
                "method": method,
                "user_agent": request.headers.get("user-agent"),
                "event_type": "request_start"
            }
        )


async def _log_request_success(
    audit_ctx: AuditContext,
    request: Request,
    response: Response,
    start_time: float
):
    """Log successful completion of security-relevant request."""
    duration = time.time() - start_time
    endpoint = request.url.path
    
    # Log slow requests as potential security concern
    if duration > 5.0:  # 5 seconds
        await audit_ctx.log_event(
            action=AuditAction.SUSPICIOUS_ACTIVITY,
            description=f"Slow request detected: {endpoint} took {duration:.2f}s",
            severity=AuditSeverity.MEDIUM,
            metadata={
                "endpoint": endpoint,
                "duration_seconds": duration,
                "status_code": response.status_code,
                "event_type": "slow_request"
            }
        )


async def _log_request_failure(
    audit_ctx: AuditContext,
    request: Request,
    error: Exception,
    start_time: float
):
    """Log failed security-relevant request."""
    duration = time.time() - start_time
    endpoint = request.url.path
    
    await audit_ctx.log_event(
        action=AuditAction.SUSPICIOUS_ACTIVITY,
        description=f"Request failed: {endpoint} - {str(error)}",
        success=False,
        error_message=str(error),
        severity=AuditSeverity.HIGH,
        metadata={
            "endpoint": endpoint,
            "duration_seconds": duration,
            "error_type": type(error).__name__,
            "event_type": "request_failure"
        }
    )


async def _log_endpoint_specific_events(
    audit_ctx: AuditContext,
    request: Request,
    response: Response
):
    """Log specific events based on endpoint and response."""
    endpoint = request.url.path
    status_code = response.status_code
    
    # Authentication endpoints
    if endpoint == "/api/auth/login":
        if status_code == 200:
            # Login success will be logged by the login endpoint itself
            pass
        elif status_code in [400, 401, 422]:
            # Login failure - extract email from request if possible
            await audit_ctx.log_event(
                action=AuditAction.LOGIN_FAILED,
                description="Login attempt failed",
                success=False,
                severity=AuditSeverity.MEDIUM,
                metadata={
                    "status_code": status_code,
                    "endpoint": endpoint
                }
            )
    
    elif endpoint == "/api/auth/register":
        if status_code == 201:
            await audit_ctx.log_event(
                action=AuditAction.USER_CREATED,
                description="User registration successful",
                severity=AuditSeverity.LOW,
                metadata={"status_code": status_code}
            )
        elif status_code in [400, 422]:
            await audit_ctx.log_event(
                action=AuditAction.USER_CREATED,
                description="User registration failed",
                success=False,
                severity=AuditSeverity.LOW,
                metadata={"status_code": status_code}
            )
    
    elif endpoint == "/api/auth/change-password":
        if status_code == 200:
            await audit_ctx.log_event(
                action=AuditAction.PASSWORD_CHANGE,
                description="Password change successful",
                severity=AuditSeverity.MEDIUM,
                metadata={"status_code": status_code}
            )
        else:
            await audit_ctx.log_event(
                action=AuditAction.PASSWORD_CHANGE,
                description="Password change failed",
                success=False,
                severity=AuditSeverity.MEDIUM,
                metadata={"status_code": status_code}
            )
    
    # Admin endpoints
    elif endpoint.startswith("/api/admin/"):
        if status_code in [200, 201]:
            await audit_ctx.log_event(
                action=AuditAction.ADMIN_ACTION,
                description=f"Admin action completed: {request.method} {endpoint}",
                severity=AuditSeverity.MEDIUM,
                metadata={
                    "status_code": status_code,
                    "method": request.method,
                    "endpoint": endpoint
                }
            )
    
    # Service endpoints
    elif endpoint.startswith("/api/services/"):
        if endpoint == "/api/services/register" and status_code == 201:
            await audit_ctx.log_event(
                action=AuditAction.SERVICE_REGISTERED,
                description="New service registered",
                severity=AuditSeverity.MEDIUM,
                metadata={"status_code": status_code}
            )
        elif endpoint == "/api/services/token" and status_code == 200:
            await audit_ctx.log_event(
                action=AuditAction.SERVICE_TOKEN_ISSUED,
                description="Service token issued",
                severity=AuditSeverity.LOW,
                metadata={"status_code": status_code}
            )
    
    # Unauthorized access attempts
    if status_code == 401:
        await audit_ctx.log_event(
            action=AuditAction.UNAUTHORIZED_ACCESS,
            description=f"Unauthorized access attempt: {endpoint}",
            success=False,
            severity=AuditSeverity.HIGH,
            metadata={
                "status_code": status_code,
                "endpoint": endpoint,
                "method": request.method
            }
        )
    
    # Permission denied
    elif status_code == 403:
        await audit_ctx.log_event(
            action=AuditAction.PERMISSION_DENIED,
            description=f"Permission denied: {endpoint}",
            success=False,
            severity=AuditSeverity.HIGH,
            metadata={
                "status_code": status_code,
                "endpoint": endpoint,
                "method": request.method
            }
        )
    
    # Rate limiting
    elif status_code == 429:
        await audit_ctx.log_event(
            action=AuditAction.RATE_LIMIT_EXCEEDED,
            description=f"Rate limit exceeded: {endpoint}",
            success=False,
            severity=AuditSeverity.HIGH,
            metadata={
                "status_code": status_code,
                "endpoint": endpoint,
                "method": request.method
            }
        )


# Decorator for manual audit logging in endpoints
def audit_action(action: AuditAction, description: str, severity: AuditSeverity = AuditSeverity.LOW):
    """
    Decorator for manual audit logging in endpoints.
    
    Usage:
        @audit_action(AuditAction.USER_CREATED, "User registration")
        async def register_user(...):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request and hasattr(request.state, 'audit_context'):
                audit_ctx = request.state.audit_context
                
                try:
                    result = await func(*args, **kwargs)
                    await audit_ctx.log_event(action, description, severity=severity)
                    return result
                except Exception as e:
                    await audit_ctx.log_event(
                        action, 
                        f"{description} - Failed: {str(e)}", 
                        success=False,
                        error_message=str(e),
                        severity=AuditSeverity.HIGH
                    )
                    raise
            else:
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator