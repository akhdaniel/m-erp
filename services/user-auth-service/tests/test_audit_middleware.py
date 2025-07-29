"""
Tests for audit middleware.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.audit_middleware import (
    AuditContext,
    audit_middleware,
    _is_security_endpoint,
    _log_endpoint_specific_events
)
from app.models.audit_log import AuditAction, AuditSeverity


class TestAuditContext:
    """Test AuditContext functionality."""
    
    @pytest.mark.asyncio
    async def test_audit_context_creation(self, db_session: AsyncSession):
        """Test AuditContext creation and initialization."""
        mock_request = Mock(spec=Request)
        
        ctx = AuditContext(mock_request, db_session)
        
        assert ctx.request == mock_request
        assert ctx.db == db_session
        assert ctx.user_id is None
        assert ctx.service_id is None
        assert ctx.service_name is None
        assert ctx.logged_events == []
    
    def test_set_user_context(self, db_session: AsyncSession):
        """Test setting user context."""
        mock_request = Mock(spec=Request)
        ctx = AuditContext(mock_request, db_session)
        
        ctx.set_user_context(123)
        
        assert ctx.user_id == 123
    
    def test_set_service_context(self, db_session: AsyncSession):
        """Test setting service context."""
        mock_request = Mock(spec=Request)
        ctx = AuditContext(mock_request, db_session)
        
        ctx.set_service_context(456, "test-service")
        
        assert ctx.service_id == 456
        assert ctx.service_name == "test-service"
    
    @pytest.mark.asyncio
    async def test_log_event(self, db_session: AsyncSession):
        """Test logging an event with context."""
        mock_request = Mock(spec=Request)
        mock_request.client.host = "192.168.1.100"
        mock_request.headers = {"user-agent": "test-agent"}
        mock_request.url.path = "/api/test"
        mock_request.method = "POST"
        
        ctx = AuditContext(mock_request, db_session)
        ctx.set_user_context(123)
        
        with patch('app.middleware.audit_middleware.AuditService.log_action') as mock_log:
            mock_log.return_value = Mock()
            
            await ctx.log_event(
                action=AuditAction.LOGIN_SUCCESS,
                description="Test event",
                success=True,
                metadata={"test": "value"}
            )
            
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            
            assert call_args[1]["action"] == AuditAction.LOGIN_SUCCESS
            assert call_args[1]["description"] == "Test event"
            assert call_args[1]["user_id"] == 123
            assert call_args[1]["request"] == mock_request
            assert call_args[1]["success"] is True
            assert call_args[1]["metadata"]["test"] == "value"
    
    @pytest.mark.asyncio
    async def test_log_event_deduplication(self, db_session: AsyncSession):
        """Test that duplicate events are not logged twice."""
        mock_request = Mock(spec=Request)
        ctx = AuditContext(mock_request, db_session)
        
        with patch('app.middleware.audit_middleware.AuditService.log_action') as mock_log:
            mock_log.return_value = Mock()
            
            # Log the same event twice
            await ctx.log_event(
                action=AuditAction.LOGIN_SUCCESS,
                description="Test event"
            )
            await ctx.log_event(
                action=AuditAction.LOGIN_SUCCESS,
                description="Test event"
            )
            
            # Should only be called once due to deduplication
            assert mock_log.call_count == 1


class TestAuditMiddleware:
    """Test audit middleware functionality."""
    
    def test_is_security_endpoint(self):
        """Test security endpoint detection."""
        # Security endpoints
        assert _is_security_endpoint("/api/auth/login") is True
        assert _is_security_endpoint("/api/admin/users") is True
        assert _is_security_endpoint("/api/services/token") is True
        assert _is_security_endpoint("/api/validate/user-token") is True
        
        # Non-security endpoints
        assert _is_security_endpoint("/health") is False
        assert _is_security_endpoint("/docs") is False
        assert _is_security_endpoint("/api/public/info") is False
    
    @pytest.mark.asyncio
    async def test_audit_middleware_flow(self, db_session: AsyncSession):
        """Test complete audit middleware flow."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/auth/login"
        mock_request.method = "POST"
        mock_request.client.host = "192.168.1.100"
        mock_request.headers = {"user-agent": "test-agent"}
        mock_request.state = Mock()
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        
        call_next = AsyncMock(return_value=mock_response)
        
        with patch('app.middleware.audit_middleware.get_db') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = db_session
            mock_get_db.return_value.__aexit__.return_value = None
            
            with patch('app.middleware.audit_middleware._log_request_start') as mock_log_start:
                with patch('app.middleware.audit_middleware._log_request_success') as mock_log_success:
                    with patch('app.middleware.audit_middleware._log_endpoint_specific_events') as mock_log_specific:
                        
                        result = await audit_middleware(mock_request, call_next)
                        
                        # Verify middleware created audit context
                        assert hasattr(mock_request.state, 'audit_context')
                        
                        # Verify all logging functions were called
                        mock_log_start.assert_called_once()
                        mock_log_success.assert_called_once()
                        mock_log_specific.assert_called_once()
                        
                        # Verify response is returned
                        assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_audit_middleware_exception_handling(self, db_session: AsyncSession):
        """Test audit middleware exception handling."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/auth/login"
        mock_request.method = "POST"
        mock_request.client.host = "192.168.1.100"
        mock_request.headers = {"user-agent": "test-agent"}
        mock_request.state = Mock()
        
        # Mock call_next to raise an exception
        test_exception = ValueError("Test error")
        call_next = AsyncMock(side_effect=test_exception)
        
        with patch('app.middleware.audit_middleware.get_db') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = db_session
            mock_get_db.return_value.__aexit__.return_value = None
            
            with patch('app.middleware.audit_middleware._log_request_failure') as mock_log_failure:
                
                with pytest.raises(ValueError):
                    await audit_middleware(mock_request, call_next)
                
                # Verify failure was logged
                mock_log_failure.assert_called_once()
                args = mock_log_failure.call_args[0]
                assert args[2] == test_exception  # The exception should be passed
    
    @pytest.mark.asyncio
    async def test_log_endpoint_specific_events_login_success(self, db_session: AsyncSession):
        """Test endpoint-specific logging for successful login."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/auth/login"
        mock_request.method = "POST"
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        
        mock_audit_ctx = Mock()
        mock_audit_ctx.log_event = AsyncMock()
        
        await _log_endpoint_specific_events(mock_audit_ctx, mock_request, mock_response)
        
        # Login success should not log here (handled by endpoint)
        mock_audit_ctx.log_event.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_log_endpoint_specific_events_login_failure(self, db_session: AsyncSession):
        """Test endpoint-specific logging for failed login."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/auth/login"
        mock_request.method = "POST"
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 401
        
        mock_audit_ctx = Mock()
        mock_audit_ctx.log_event = AsyncMock()
        
        await _log_endpoint_specific_events(mock_audit_ctx, mock_request, mock_response)
        
        # Should log login failure
        mock_audit_ctx.log_event.assert_called_once()
        call_args = mock_audit_ctx.log_event.call_args
        assert call_args[1]["action"] == AuditAction.LOGIN_FAILED
        assert call_args[1]["success"] is False
    
    @pytest.mark.asyncio
    async def test_log_endpoint_specific_events_register_success(self, db_session: AsyncSession):
        """Test endpoint-specific logging for successful registration."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/auth/register"
        mock_request.method = "POST"
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 201
        
        mock_audit_ctx = Mock()
        mock_audit_ctx.log_event = AsyncMock()
        
        await _log_endpoint_specific_events(mock_audit_ctx, mock_request, mock_response)
        
        # Should log user creation
        mock_audit_ctx.log_event.assert_called_once()
        call_args = mock_audit_ctx.log_event.call_args
        assert call_args[1]["action"] == AuditAction.USER_CREATED
        assert call_args[1]["success"] is True
    
    @pytest.mark.asyncio
    async def test_log_endpoint_specific_events_unauthorized(self, db_session: AsyncSession):
        """Test endpoint-specific logging for unauthorized access."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/admin/users"
        mock_request.method = "GET"
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 401
        
        mock_audit_ctx = Mock()
        mock_audit_ctx.log_event = AsyncMock()
        
        await _log_endpoint_specific_events(mock_audit_ctx, mock_request, mock_response)
        
        # Should log unauthorized access
        mock_audit_ctx.log_event.assert_called_once()
        call_args = mock_audit_ctx.log_event.call_args
        assert call_args[1]["action"] == AuditAction.UNAUTHORIZED_ACCESS
        assert call_args[1]["success"] is False
        assert call_args[1]["severity"] == AuditSeverity.HIGH
    
    @pytest.mark.asyncio
    async def test_log_endpoint_specific_events_permission_denied(self, db_session: AsyncSession):
        """Test endpoint-specific logging for permission denied."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/admin/users"
        mock_request.method = "POST"
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 403
        
        mock_audit_ctx = Mock()
        mock_audit_ctx.log_event = AsyncMock()
        
        await _log_endpoint_specific_events(mock_audit_ctx, mock_request, mock_response)
        
        # Should log permission denied
        mock_audit_ctx.log_event.assert_called_once()
        call_args = mock_audit_ctx.log_event.call_args
        assert call_args[1]["action"] == AuditAction.PERMISSION_DENIED
        assert call_args[1]["success"] is False
        assert call_args[1]["severity"] == AuditSeverity.HIGH
    
    @pytest.mark.asyncio
    async def test_log_endpoint_specific_events_rate_limit(self, db_session: AsyncSession):
        """Test endpoint-specific logging for rate limit exceeded."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/auth/login"
        mock_request.method = "POST"
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 429
        
        mock_audit_ctx = Mock()
        mock_audit_ctx.log_event = AsyncMock()
        
        await _log_endpoint_specific_events(mock_audit_ctx, mock_request, mock_response)
        
        # Should log rate limit exceeded
        mock_audit_ctx.log_event.assert_called_once()
        call_args = mock_audit_ctx.log_event.call_args
        assert call_args[1]["action"] == AuditAction.RATE_LIMIT_EXCEEDED
        assert call_args[1]["success"] is False
        assert call_args[1]["severity"] == AuditSeverity.HIGH
    
    @pytest.mark.asyncio
    async def test_log_endpoint_specific_events_password_change(self, db_session: AsyncSession):
        """Test endpoint-specific logging for password change."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/auth/change-password"
        mock_request.method = "POST"
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        
        mock_audit_ctx = Mock()
        mock_audit_ctx.log_event = AsyncMock()
        
        await _log_endpoint_specific_events(mock_audit_ctx, mock_request, mock_response)
        
        # Should log password change
        mock_audit_ctx.log_event.assert_called_once()
        call_args = mock_audit_ctx.log_event.call_args
        assert call_args[1]["action"] == AuditAction.PASSWORD_CHANGE
        assert call_args[1]["success"] is True
        assert call_args[1]["severity"] == AuditSeverity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_log_endpoint_specific_events_admin_action(self, db_session: AsyncSession):
        """Test endpoint-specific logging for admin actions."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/admin/users/123"
        mock_request.method = "PUT"
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        
        mock_audit_ctx = Mock()
        mock_audit_ctx.log_event = AsyncMock()
        
        await _log_endpoint_specific_events(mock_audit_ctx, mock_request, mock_response)
        
        # Should log admin action
        mock_audit_ctx.log_event.assert_called_once()
        call_args = mock_audit_ctx.log_event.call_args
        assert call_args[1]["action"] == AuditAction.ADMIN_ACTION
        assert call_args[1]["severity"] == AuditSeverity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_log_endpoint_specific_events_service_register(self, db_session: AsyncSession):
        """Test endpoint-specific logging for service registration."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/services/register"
        mock_request.method = "POST"
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 201
        
        mock_audit_ctx = Mock()
        mock_audit_ctx.log_event = AsyncMock()
        
        await _log_endpoint_specific_events(mock_audit_ctx, mock_request, mock_response)
        
        # Should log service registration
        mock_audit_ctx.log_event.assert_called_once()
        call_args = mock_audit_ctx.log_event.call_args
        assert call_args[1]["action"] == AuditAction.SERVICE_REGISTERED
        assert call_args[1]["severity"] == AuditSeverity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_log_endpoint_specific_events_service_token(self, db_session: AsyncSession):
        """Test endpoint-specific logging for service token issuance."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/services/token"
        mock_request.method = "POST"
        
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        
        mock_audit_ctx = Mock()
        mock_audit_ctx.log_event = AsyncMock()
        
        await _log_endpoint_specific_events(mock_audit_ctx, mock_request, mock_response)
        
        # Should log service token issuance
        mock_audit_ctx.log_event.assert_called_once()
        call_args = mock_audit_ctx.log_event.call_args
        assert call_args[1]["action"] == AuditAction.SERVICE_TOKEN_ISSUED
        assert call_args[1]["severity"] == AuditSeverity.LOW