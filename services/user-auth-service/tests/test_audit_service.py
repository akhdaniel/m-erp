"""
Tests for audit logging service.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.audit_service import AuditService, audit_login_success, audit_login_failure
from app.models.audit_log import AuditAction, AuditSeverity, AuditLog


class TestAuditService:
    """Test cases for AuditService."""
    
    @pytest.mark.asyncio
    async def test_log_action_basic(self, db_session: AsyncSession):
        """Test basic audit log creation."""
        audit_log = await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_SUCCESS,
            description="User login successful",
            user_id=1,
            success=True
        )
        
        assert audit_log.id is not None
        assert audit_log.action == AuditAction.LOGIN_SUCCESS.value
        assert audit_log.description == "User login successful"
        assert audit_log.user_id == 1
        assert audit_log.success is True
        assert audit_log.severity == AuditSeverity.LOW.value
    
    @pytest.mark.asyncio
    async def test_log_action_with_request(self, db_session: AsyncSession):
        """Test audit log creation with request context."""
        # Mock request object
        mock_request = Mock(spec=Request)
        mock_request.client.host = "192.168.1.100"
        mock_request.headers = {"user-agent": "Mozilla/5.0"}
        mock_request.url.path = "/api/auth/login"
        mock_request.method = "POST"
        mock_request.state.session_id = "session123"
        mock_request.state.request_id = "req456"
        
        audit_log = await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_FAILED,
            description="Invalid credentials",
            request=mock_request,
            success=False,
            error_message="Wrong password"
        )
        
        assert audit_log.ip_address == "192.168.1.100"
        assert audit_log.user_agent == "Mozilla/5.0"
        assert audit_log.endpoint == "/api/auth/login"
        assert audit_log.http_method == "POST"
        assert audit_log.session_id == "session123"
        assert audit_log.request_id == "req456"
        assert audit_log.success is False
        assert audit_log.error_message == "Wrong password"
    
    @pytest.mark.asyncio
    async def test_log_authentication_success(self, db_session: AsyncSession):
        """Test logging successful authentication."""
        audit_log = await AuditService.log_authentication_success(
            db=db_session,
            user_id=123,
            login_method="password"
        )
        
        assert audit_log.action == AuditAction.LOGIN_SUCCESS.value
        assert audit_log.user_id == 123
        assert audit_log.success is True
        assert audit_log.severity == AuditSeverity.LOW.value
        assert "password" in audit_log.description
        assert audit_log.metadata["login_method"] == "password"
        assert "authentication" in audit_log.tags
        assert "success" in audit_log.tags
    
    @pytest.mark.asyncio
    async def test_log_authentication_failure(self, db_session: AsyncSession):
        """Test logging failed authentication."""
        audit_log = await AuditService.log_authentication_failure(
            db=db_session,
            email="test@example.com",
            reason="Invalid password",
            attempt_count=3
        )
        
        assert audit_log.action == AuditAction.LOGIN_FAILED.value
        assert audit_log.success is False
        assert audit_log.severity == AuditSeverity.HIGH.value  # High due to attempt_count >= 3
        assert "test@example.com" in audit_log.description
        assert audit_log.error_message == "Invalid password"
        assert audit_log.metadata["email"] == "test@example.com"
        assert audit_log.metadata["attempt_count"] == 3
    
    @pytest.mark.asyncio
    async def test_log_suspicious_activity(self, db_session: AsyncSession):
        """Test logging suspicious activity."""
        audit_log = await AuditService.log_suspicious_activity(
            db=db_session,
            activity_type="multiple_failed_logins",
            description="Too many failed login attempts",
            user_id=456,
            metadata={"ip": "192.168.1.100", "count": 5}
        )
        
        assert audit_log.action == AuditAction.SUSPICIOUS_ACTIVITY.value
        assert audit_log.severity == AuditSeverity.CRITICAL.value
        assert audit_log.success is False
        assert audit_log.user_id == 456
        assert "suspicious" in audit_log.tags
        assert audit_log.metadata["activity_type"] == "multiple_failed_logins"
        assert audit_log.metadata["ip"] == "192.168.1.100"
    
    @pytest.mark.asyncio
    async def test_log_rate_limit_exceeded(self, db_session: AsyncSession):
        """Test logging rate limit exceeded."""
        audit_log = await AuditService.log_rate_limit_exceeded(
            db=db_session,
            identifier="user:123",
            endpoint="/api/auth/login",
            limit=5
        )
        
        assert audit_log.action == AuditAction.RATE_LIMIT_EXCEEDED.value
        assert audit_log.severity == AuditSeverity.HIGH.value
        assert audit_log.success is False
        assert audit_log.metadata["identifier"] == "user:123"
        assert audit_log.metadata["endpoint"] == "/api/auth/login"
        assert audit_log.metadata["limit"] == 5
        assert "rate_limiting" in audit_log.tags
    
    @pytest.mark.asyncio
    async def test_log_admin_action(self, db_session: AsyncSession):
        """Test logging admin actions."""
        audit_log = await AuditService.log_admin_action(
            db=db_session,
            admin_user_id=1,
            action_type="user_creation",
            description="Created new user account",
            target_user_id=789,
            metadata={"role": "user", "department": "engineering"}
        )
        
        assert audit_log.action == AuditAction.ADMIN_ACTION.value
        assert audit_log.severity == AuditSeverity.MEDIUM.value
        assert audit_log.user_id == 1
        assert audit_log.target_user_id == 789
        assert audit_log.success is True
        assert audit_log.metadata["action_type"] == "user_creation"
        assert "admin" in audit_log.tags
        assert "management" in audit_log.tags
    
    @pytest.mark.asyncio
    async def test_log_service_action(self, db_session: AsyncSession):
        """Test logging service actions."""
        audit_log = await AuditService.log_service_action(
            db=db_session,
            service_id=1,
            service_name="inventory-service",
            action=AuditAction.SERVICE_TOKEN_ISSUED,
            description="Token issued for inventory service",
            success=True,
            metadata={"token_type": "access", "scopes": ["inventory:read"]}
        )
        
        assert audit_log.action == AuditAction.SERVICE_TOKEN_ISSUED.value
        assert audit_log.service_id == 1
        assert audit_log.service_name == "inventory-service"
        assert audit_log.success is True
        assert audit_log.severity == AuditSeverity.LOW.value
        assert "service" in audit_log.tags
        assert "inter_service" in audit_log.tags
    
    @pytest.mark.asyncio
    async def test_get_audit_logs_filtering(self, db_session: AsyncSession):
        """Test audit log filtering and querying."""
        # Create test logs
        await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_SUCCESS,
            description="Login 1",
            user_id=1,
            success=True
        )
        
        await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_FAILED,
            description="Login 2",
            user_id=2,
            success=False
        )
        
        await AuditService.log_action(
            db=db_session,
            action=AuditAction.ADMIN_ACTION,
            description="Admin action",
            user_id=1,
            success=True
        )
        
        # Test filtering by user_id
        logs = await AuditService.get_audit_logs(db=db_session, user_id=1)
        assert len(logs) == 2
        assert all(log.user_id == 1 for log in logs)
        
        # Test filtering by action
        logs = await AuditService.get_audit_logs(
            db=db_session, 
            action=AuditAction.LOGIN_FAILED.value
        )
        assert len(logs) == 1
        assert logs[0].action == AuditAction.LOGIN_FAILED.value
        
        # Test filtering by success
        logs = await AuditService.get_audit_logs(db=db_session, success=False)
        assert len(logs) == 1
        assert logs[0].success is False
        
        # Test limit and offset
        logs = await AuditService.get_audit_logs(db=db_session, limit=2, offset=0)
        assert len(logs) == 2
        
        logs = await AuditService.get_audit_logs(db=db_session, limit=2, offset=2)
        assert len(logs) == 1
    
    @pytest.mark.asyncio
    async def test_get_security_summary(self, db_session: AsyncSession):
        """Test security summary generation."""
        # Create test security events
        await AuditService.log_authentication_failure(
            db=db_session,
            email="test1@example.com",
            reason="Invalid password"
        )
        
        await AuditService.log_authentication_failure(
            db=db_session,
            email="test2@example.com",
            reason="Account not found"
        )
        
        await AuditService.log_suspicious_activity(
            db=db_session,
            activity_type="brute_force",
            description="Brute force attempt detected"
        )
        
        await AuditService.log_rate_limit_exceeded(
            db=db_session,
            identifier="ip:192.168.1.100",
            endpoint="/api/auth/login",
            limit=5
        )
        
        # Get security summary
        summary = await AuditService.get_security_summary(db=db_session, hours=24)
        
        assert summary["total_events"] == 4
        assert summary["failed_authentications"] == 2
        assert summary["suspicious_activities"] == 1
        assert summary["rate_limit_violations"] == 1
        assert summary["period_hours"] == 24
        assert "generated_at" in summary
    
    @pytest.mark.asyncio
    async def test_data_sanitization(self, db_session: AsyncSession):
        """Test sensitive data sanitization."""
        request_data = {
            "email": "test@example.com",
            "password": "secret123",
            "current_password": "oldpass",
            "token": "jwt-token",
            "service_secret": "secret-key",
            "normal_field": "normal_value"
        }
        
        audit_log = await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_FAILED,
            description="Login failed",
            request_data=request_data,
            success=False
        )
        
        # Check that sensitive fields are redacted
        assert audit_log.request_data["email"] == "test@example.com"
        assert audit_log.request_data["password"] == "[REDACTED]"
        assert audit_log.request_data["current_password"] == "[REDACTED]"
        assert audit_log.request_data["token"] == "[REDACTED]"
        assert audit_log.request_data["service_secret"] == "[REDACTED]"
        assert audit_log.request_data["normal_field"] == "normal_value"
    
    @pytest.mark.asyncio
    async def test_severity_auto_determination(self, db_session: AsyncSession):
        """Test automatic severity determination."""
        # Critical action
        log1 = await AuditService.log_action(
            db=db_session,
            action=AuditAction.SUSPICIOUS_ACTIVITY,
            description="Suspicious activity",
            success=False
        )
        assert log1.severity == AuditSeverity.CRITICAL.value
        
        # High severity action
        log2 = await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_FAILED,
            description="Login failed",
            success=False
        )
        assert log2.severity == AuditSeverity.HIGH.value
        
        # Medium severity action
        log3 = await AuditService.log_action(
            db=db_session,
            action=AuditAction.PASSWORD_CHANGE,
            description="Password changed",
            success=True
        )
        assert log3.severity == AuditSeverity.MEDIUM.value
        
        # Low severity action
        log4 = await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_SUCCESS,
            description="Login successful",
            success=True
        )
        assert log4.severity == AuditSeverity.LOW.value


class TestConvenienceFunctions:
    """Test convenience functions for audit logging."""
    
    @pytest.mark.asyncio
    async def test_audit_login_success(self, db_session: AsyncSession):
        """Test audit_login_success convenience function."""
        audit_log = await audit_login_success(
            db=db_session,
            user_id=123,
            login_method="oauth"
        )
        
        assert audit_log.action == AuditAction.LOGIN_SUCCESS.value
        assert audit_log.user_id == 123
        assert audit_log.metadata["login_method"] == "oauth"
        assert audit_log.success is True
    
    @pytest.mark.asyncio
    async def test_audit_login_failure(self, db_session: AsyncSession):
        """Test audit_login_failure convenience function."""
        audit_log = await audit_login_failure(
            db=db_session,
            email="test@example.com",
            reason="Account locked",
            attempt_count=5
        )
        
        assert audit_log.action == AuditAction.LOGIN_FAILED.value
        assert audit_log.metadata["email"] == "test@example.com"
        assert audit_log.error_message == "Account locked"
        assert audit_log.success is False


class TestAuditLogModel:
    """Test AuditLog model methods."""
    
    def test_create_log_class_method(self):
        """Test AuditLog.create_log class method."""
        audit_log = AuditLog.create_log(
            action=AuditAction.USER_CREATED,
            description="New user created",
            user_id=123,
            success=True,
            metadata={"department": "engineering"}
        )
        
        assert audit_log.action == AuditAction.USER_CREATED.value
        assert audit_log.description == "New user created"
        assert audit_log.user_id == 123
        assert audit_log.success is True
        assert audit_log.metadata["department"] == "engineering"
    
    def test_to_dict_method(self):
        """Test AuditLog.to_dict method."""
        audit_log = AuditLog.create_log(
            action=AuditAction.LOGIN_SUCCESS,
            description="Login successful",
            user_id=123,
            ip_address="192.168.1.100",
            success=True
        )
        
        data = audit_log.to_dict()
        
        assert data["action"] == AuditAction.LOGIN_SUCCESS.value
        assert data["description"] == "Login successful"
        assert data["user_id"] == 123
        assert data["ip_address"] == "192.168.1.100"
        assert data["success"] is True
        assert "id" in data
        assert "created_at" in data
    
    def test_sanitize_request_data(self):
        """Test _sanitize_request_data static method."""
        data = {
            "username": "test",
            "password": "secret",
            "nested": {
                "token": "jwt-token",
                "value": "normal"
            }
        }
        
        sanitized = AuditLog._sanitize_request_data(data)
        
        assert sanitized["username"] == "test"
        assert sanitized["password"] == "[REDACTED]"
        assert sanitized["nested"]["token"] == "[REDACTED]"
        assert sanitized["nested"]["value"] == "normal"
    
    def test_determine_severity(self):
        """Test _determine_severity static method."""
        # Critical actions
        assert AuditLog._determine_severity(
            AuditAction.SUSPICIOUS_ACTIVITY, True
        ) == AuditSeverity.CRITICAL
        
        # High actions
        assert AuditLog._determine_severity(
            AuditAction.LOGIN_FAILED, False
        ) == AuditSeverity.HIGH
        
        # Medium actions
        assert AuditLog._determine_severity(
            AuditAction.PASSWORD_CHANGE, True
        ) == AuditSeverity.MEDIUM
        
        # Low actions
        assert AuditLog._determine_severity(
            AuditAction.LOGIN_SUCCESS, True
        ) == AuditSeverity.LOW
        
        # Failed medium action becomes high
        assert AuditLog._determine_severity(
            AuditAction.PASSWORD_CHANGE, False
        ) == AuditSeverity.HIGH