"""
Tests for audit API endpoints.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.audit_log import AuditAction, AuditSeverity
from app.services.audit_service import AuditService
from tests.conftest import create_test_user, create_test_role, get_test_token


class TestAuditEndpoints:
    """Test audit API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_get_audit_logs_unauthorized(self, client: TestClient, db_session: AsyncSession):
        """Test getting audit logs without proper permissions."""
        response = client.get("/api/audit/logs")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_audit_logs_forbidden(self, client: TestClient, db_session: AsyncSession):
        """Test getting audit logs with insufficient permissions."""
        # Create user without audit permissions
        user = await create_test_user(db_session, email="user@example.com")
        token = get_test_token(user.id)
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/audit/logs", headers=headers)
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_audit_logs_success(self, client: TestClient, db_session: AsyncSession):
        """Test getting audit logs with proper permissions."""
        # Create admin user with audit permissions
        admin_role = await create_test_role(db_session, name="admin", permissions=["audit:read"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        token = get_test_token(admin_user.id)
        
        # Create test audit logs
        await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_SUCCESS,
            description="Test login success",
            user_id=admin_user.id,
            success=True
        )
        
        await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_FAILED,
            description="Test login failure",
            success=False
        )
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/audit/logs", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert "has_more" in data
        
        assert len(data["logs"]) == 2
        assert data["total"] == 2
        assert data["limit"] == 100
        assert data["offset"] == 0
        assert data["has_more"] is False
    
    @pytest.mark.asyncio
    async def test_get_audit_logs_with_filters(self, client: TestClient, db_session: AsyncSession):
        """Test getting audit logs with various filters."""
        # Create admin user with audit permissions
        admin_role = await create_test_role(db_session, name="admin", permissions=["audit:read"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        token = get_test_token(admin_user.id)
        
        # Create test audit logs with different properties
        await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_SUCCESS,
            description="User 1 login",
            user_id=1,
            success=True
        )
        
        await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_FAILED,
            description="User 2 login failure",
            user_id=2,
            success=False,
            severity=AuditSeverity.HIGH
        )
        
        await AuditService.log_action(
            db=db_session,
            action=AuditAction.ADMIN_ACTION,
            description="Admin action",
            user_id=1,
            success=True
        )
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test filter by user_id
        response = client.get("/api/audit/logs?user_id=1", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["logs"]) == 2
        assert all(log["user_id"] == 1 for log in data["logs"])
        
        # Test filter by action
        response = client.get(
            f"/api/audit/logs?action={AuditAction.LOGIN_FAILED.value}", 
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["logs"]) == 1
        assert data["logs"][0]["action"] == AuditAction.LOGIN_FAILED.value
        
        # Test filter by severity
        response = client.get(
            f"/api/audit/logs?severity={AuditSeverity.HIGH.value}", 
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["logs"]) == 1
        assert data["logs"][0]["severity"] == AuditSeverity.HIGH.value
        
        # Test filter by success
        response = client.get("/api/audit/logs?success=false", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["logs"]) == 1
        assert data["logs"][0]["success"] is False
        
        # Test pagination
        response = client.get("/api/audit/logs?limit=2&offset=0", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["logs"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0
    
    @pytest.mark.asyncio
    async def test_get_audit_logs_invalid_filters(self, client: TestClient, db_session: AsyncSession):
        """Test getting audit logs with invalid filters."""
        # Create admin user with audit permissions
        admin_role = await create_test_role(db_session, name="admin", permissions=["audit:read"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        token = get_test_token(admin_user.id)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test invalid action
        response = client.get("/api/audit/logs?action=invalid_action", headers=headers)
        assert response.status_code == 400
        assert "Invalid action type" in response.json()["detail"]
        
        # Test invalid severity
        response = client.get("/api/audit/logs?severity=invalid_severity", headers=headers)
        assert response.status_code == 400
        assert "Invalid severity level" in response.json()["detail"]
        
        # Test invalid date range
        start_date = "2023-12-01T00:00:00"
        end_date = "2023-11-01T00:00:00"  # End before start
        response = client.get(
            f"/api/audit/logs?start_date={start_date}&end_date={end_date}", 
            headers=headers
        )
        assert response.status_code == 400
        assert "Start date must be before end date" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_security_summary(self, client: TestClient, db_session: AsyncSession):
        """Test getting security summary."""
        # Create admin user with audit permissions
        admin_role = await create_test_role(db_session, name="admin", permissions=["audit:read"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        token = get_test_token(admin_user.id)
        
        # Create test security events
        await AuditService.log_authentication_failure(
            db=db_session,
            email="test1@example.com",
            reason="Invalid password"
        )
        
        await AuditService.log_suspicious_activity(
            db=db_session,
            activity_type="brute_force",
            description="Brute force detected"
        )
        
        await AuditService.log_rate_limit_exceeded(
            db=db_session,
            identifier="ip:192.168.1.100",
            endpoint="/api/auth/login",
            limit=5
        )
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/audit/security-summary", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "period_hours" in data
        assert "total_events" in data
        assert "failed_authentications" in data
        assert "suspicious_activities" in data
        assert "rate_limit_violations" in data
        assert "top_failing_ips" in data
        assert "generated_at" in data
        
        assert data["period_hours"] == 24
        assert data["total_events"] >= 3
        assert data["failed_authentications"] >= 1
        assert data["suspicious_activities"] >= 1
        assert data["rate_limit_violations"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_security_summary_custom_hours(self, client: TestClient, db_session: AsyncSession):
        """Test getting security summary with custom time period."""
        # Create admin user with audit permissions
        admin_role = await create_test_role(db_session, name="admin", permissions=["audit:read"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        token = get_test_token(admin_user.id)
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/audit/security-summary?hours=48", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["period_hours"] == 48
    
    @pytest.mark.asyncio
    async def test_get_audit_actions(self, client: TestClient, db_session: AsyncSession):
        """Test getting available audit actions."""
        # Create admin user with audit permissions
        admin_role = await create_test_role(db_session, name="admin", permissions=["audit:read"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        token = get_test_token(admin_user.id)
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/audit/actions", headers=headers)
        
        assert response.status_code == 200
        actions = response.json()
        
        assert isinstance(actions, list)
        assert len(actions) > 0
        assert AuditAction.LOGIN_SUCCESS.value in actions
        assert AuditAction.LOGIN_FAILED.value in actions
        assert AuditAction.SUSPICIOUS_ACTIVITY.value in actions
    
    @pytest.mark.asyncio
    async def test_get_audit_severities(self, client: TestClient, db_session: AsyncSession):
        """Test getting available audit severities."""
        # Create admin user with audit permissions
        admin_role = await create_test_role(db_session, name="admin", permissions=["audit:read"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        token = get_test_token(admin_user.id)
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/audit/severities", headers=headers)
        
        assert response.status_code == 200
        severities = response.json()
        
        assert isinstance(severities, list)
        assert len(severities) == 4
        assert AuditSeverity.LOW.value in severities
        assert AuditSeverity.MEDIUM.value in severities
        assert AuditSeverity.HIGH.value in severities
        assert AuditSeverity.CRITICAL.value in severities
    
    @pytest.mark.asyncio
    async def test_get_user_recent_audit_logs(self, client: TestClient, db_session: AsyncSession):
        """Test getting recent audit logs for a specific user."""
        # Create admin user with audit permissions
        admin_role = await create_test_role(db_session, name="admin", permissions=["audit:read"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        token = get_test_token(admin_user.id)
        
        # Create audit logs for different users
        await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_SUCCESS,
            description="User 123 login",
            user_id=123,
            success=True
        )
        
        await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_SUCCESS,
            description="User 456 login",
            user_id=456,
            success=True
        )
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/audit/user/123/recent", headers=headers)
        
        assert response.status_code == 200
        logs = response.json()
        
        assert isinstance(logs, list)
        assert len(logs) == 1
        assert logs[0]["user_id"] == 123
        assert logs[0]["description"] == "User 123 login"
    
    @pytest.mark.asyncio
    async def test_get_failed_login_attempts(self, client: TestClient, db_session: AsyncSession):
        """Test getting failed login attempts."""
        # Create admin user with audit permissions
        admin_role = await create_test_role(db_session, name="admin", permissions=["audit:read"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        token = get_test_token(admin_user.id)
        
        # Create mixed audit logs
        await AuditService.log_authentication_success(
            db=db_session,
            user_id=123
        )
        
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
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/audit/failed-logins", headers=headers)
        
        assert response.status_code == 200
        logs = response.json()
        
        assert isinstance(logs, list)
        assert len(logs) == 2
        assert all(log["action"] == AuditAction.LOGIN_FAILED.value for log in logs)
        assert all(log["success"] is False for log in logs)
    
    @pytest.mark.asyncio
    async def test_get_failed_login_attempts_with_ip_filter(self, client: TestClient, db_session: AsyncSession):
        """Test getting failed login attempts filtered by IP."""
        # Create admin user with audit permissions
        admin_role = await create_test_role(db_session, name="admin", permissions=["audit:read"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        token = get_test_token(admin_user.id)
        
        # Create audit logs with different IPs
        await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_FAILED,
            description="Failed login from IP 1",
            ip_address="192.168.1.100",
            success=False
        )
        
        await AuditService.log_action(
            db=db_session,
            action=AuditAction.LOGIN_FAILED,
            description="Failed login from IP 2",
            ip_address="192.168.1.200",
            success=False
        )
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(
            "/api/audit/failed-logins?ip_address=192.168.1.100", 
            headers=headers
        )
        
        assert response.status_code == 200
        logs = response.json()
        
        assert isinstance(logs, list)
        assert len(logs) == 1
        assert logs[0]["ip_address"] == "192.168.1.100"
    
    @pytest.mark.asyncio
    async def test_get_suspicious_activities(self, client: TestClient, db_session: AsyncSession):
        """Test getting suspicious activities."""
        # Create admin user with audit permissions
        admin_role = await create_test_role(db_session, name="admin", permissions=["audit:read"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        token = get_test_token(admin_user.id)
        
        # Create mixed audit logs
        await AuditService.log_authentication_success(
            db=db_session,
            user_id=123
        )
        
        await AuditService.log_suspicious_activity(
            db=db_session,
            activity_type="brute_force",
            description="Brute force attack detected",
            metadata={"ip": "192.168.1.100"}
        )
        
        await AuditService.log_suspicious_activity(
            db=db_session,
            activity_type="sql_injection",
            description="SQL injection attempt",
            metadata={"payload": "' OR 1=1 --"}
        )
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/audit/suspicious-activity", headers=headers)
        
        assert response.status_code == 200
        logs = response.json()
        
        assert isinstance(logs, list)
        assert len(logs) == 2
        assert all(log["action"] == AuditAction.SUSPICIOUS_ACTIVITY.value for log in logs)
        assert all(log["severity"] == AuditSeverity.CRITICAL.value for log in logs)
    
    @pytest.mark.asyncio
    async def test_get_suspicious_activities_with_severity_filter(self, client: TestClient, db_session: AsyncSession):
        """Test getting suspicious activities with severity filter."""
        # Create admin user with audit permissions
        admin_role = await create_test_role(db_session, name="admin", permissions=["audit:read"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        token = get_test_token(admin_user.id)
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(
            f"/api/audit/suspicious-activity?severity={AuditSeverity.CRITICAL.value}", 
            headers=headers
        )
        
        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)
    
    @pytest.mark.asyncio
    async def test_get_suspicious_activities_invalid_severity(self, client: TestClient, db_session: AsyncSession):
        """Test getting suspicious activities with invalid severity filter."""
        # Create admin user with audit permissions
        admin_role = await create_test_role(db_session, name="admin", permissions=["audit:read"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        token = get_test_token(admin_user.id)
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(
            "/api/audit/suspicious-activity?severity=invalid_severity", 
            headers=headers
        )
        
        assert response.status_code == 400
        assert "Invalid severity level" in response.json()["detail"]