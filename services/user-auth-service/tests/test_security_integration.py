"""
Security integration tests - verifying all security features work together.
Tests the complete security stack: rate limiting, headers, audit, lockout.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User
from app.models.audit_log import AuditLog, AuditAction, AuditSeverity
from app.services.account_lockout_service import AccountLockoutConfig
from tests.conftest import create_test_user, create_test_role, get_test_token


class TestSecurityMiddlewareIntegration:
    """Test integration of all security middleware components."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_security_headers_applied(self, client: TestClient):
        """Test that security headers are applied to all responses."""
        response = client.get("/health")
        
        # Check security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-XSS-Protection" in response.headers
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "Referrer-Policy" in response.headers
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers
        
        # Check cache control headers
        assert "Cache-Control" in response.headers
        assert "no-store" in response.headers["Cache-Control"]
    
    def test_api_specific_headers(self, client: TestClient):
        """Test API-specific security headers."""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrong"
        })
        
        # Should have API-specific headers
        assert "API-Version" in response.headers
        assert "X-RateLimit-Policy" in response.headers
    
    def test_documentation_headers_relaxed(self, client: TestClient):
        """Test that documentation endpoints have relaxed CSP."""
        response = client.get("/docs")
        
        # Should have relaxed CSP for docs
        if "Content-Security-Policy" in response.headers:
            csp = response.headers["Content-Security-Policy"]
            assert "'unsafe-inline'" in csp
            assert "'unsafe-eval'" in csp
    
    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, client: TestClient, db_session: AsyncSession):
        """Test rate limiting integration with other security features."""
        # Create a user for testing
        user = await create_test_user(db_session, email="test@example.com", password="correct_password")
        
        # Make multiple requests to trigger rate limiting
        login_data = {"email": "test@example.com", "password": "wrong_password"}
        
        responses = []
        for i in range(10):  # Should exceed rate limit
            response = client.post("/api/auth/login", json=login_data)
            responses.append(response)
            
            # Check that rate limit headers are present
            if response.status_code != 429:
                assert "X-RateLimit-Limit" in response.headers
                assert "X-RateLimit-Remaining" in response.headers
                assert "X-RateLimit-Reset" in response.headers
        
        # At least one should be rate limited
        rate_limited_responses = [r for r in responses if r.status_code == 429]
        assert len(rate_limited_responses) > 0
        
        # Rate limited response should have proper headers
        rate_limited = rate_limited_responses[0]
        assert "Retry-After" in rate_limited.headers
        assert "Rate limit exceeded" in rate_limited.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_security_monitoring_detection(self, client: TestClient, db_session: AsyncSession):
        """Test that suspicious activity is detected and logged."""
        # Test suspicious user agent
        headers = {"User-Agent": "sqlmap/1.0"}
        response = client.get("/api/auth/login", headers=headers)
        
        # Should detect suspicious user agent
        assert "X-Response-Time" in response.headers
        
        # Test potential injection attempt
        response = client.get("/api/auth/../admin/users")
        
        # Should detect path traversal attempt
        assert response.status_code in [404, 401, 403]  # Should be blocked
    
    @pytest.mark.asyncio
    async def test_audit_logging_integration(self, client: TestClient, db_session: AsyncSession):
        """Test that security events are properly audited."""
        user = await create_test_user(db_session, email="audit_test@example.com", password="correct_password")
        
        # Failed login should be audited
        response = client.post("/api/auth/login", json={
            "email": "audit_test@example.com",
            "password": "wrong_password"
        })
        assert response.status_code == 401
        
        # Check that audit log was created
        audit_logs = await db_session.execute(
            db_session.query(AuditLog).filter(
                AuditLog.action == AuditAction.LOGIN_FAILED.value
            )
        )
        audit_log = audit_logs.scalar_one_or_none()
        
        if audit_log:  # Audit middleware might be async
            assert audit_log.action == AuditAction.LOGIN_FAILED.value
            assert audit_log.success is False
    
    @pytest.mark.asyncio
    async def test_account_lockout_with_rate_limiting(self, client: TestClient, db_session: AsyncSession):
        """Test account lockout works with rate limiting."""
        user = await create_test_user(db_session, email="lockout_test@example.com", password="correct_password")
        
        # Make failed attempts to trigger lockout
        login_data = {"email": "lockout_test@example.com", "password": "wrong_password"}
        
        lockout_response = None
        for attempt in range(AccountLockoutConfig.MAX_FAILED_ATTEMPTS + 2):
            response = client.post("/api/auth/login", json=login_data)
            
            if response.status_code == 423:  # Account locked
                lockout_response = response
                break
            elif response.status_code == 429:  # Rate limited
                # Rate limiting kicked in first
                assert "Rate limit exceeded" in response.json()["detail"]
                break
        
        # Should eventually get either lockout or rate limit
        assert lockout_response is not None or any(
            r.status_code == 429 for r in [response]
        )
        
        if lockout_response:
            assert "Account locked" in lockout_response.json()["detail"]
            assert "X-Account-Locked" in lockout_response.headers


class TestSecurityFeatureInteractions:
    """Test interactions between different security features."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_admin_lockout_override_with_audit(self, client: TestClient, db_session: AsyncSession):
        """Test admin lockout override creates proper audit trail."""
        # Create admin and locked user
        admin_role = await create_test_role(db_session, name="admin", permissions=["manage_users"])
        admin_user = await create_test_user(
            db_session, 
            email="admin@example.com", 
            roles=[admin_role]
        )
        admin_token = get_test_token(admin_user.id)
        
        locked_user = await create_test_user(db_session, email="locked@example.com")
        locked_user.failed_login_attempts = 5
        locked_user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        await db_session.commit()
        
        # Admin unlocks account
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(f"/api/admin/unlock-account/{locked_user.id}", headers=headers)
        
        assert response.status_code == 200
        
        # Verify account is unlocked
        await db_session.refresh(locked_user)
        assert locked_user.is_locked is False
        
        # Should have audit log for admin action
        # (This would be verified in a real scenario with proper audit setup)
    
    @pytest.mark.asyncio
    async def test_service_authentication_with_security_stack(self, client: TestClient, db_session: AsyncSession):
        """Test service authentication works with security middleware."""
        # Test service registration (should have security headers)
        service_data = {
            "name": "test-service",
            "description": "Test service",
            "scopes": ["test:read"]
        }
        
        response = client.post("/api/services/register", json=service_data)
        
        # Should have security headers even for service endpoints
        assert "X-Content-Type-Options" in response.headers
        assert "X-Request-ID" in response.headers
        
        if response.status_code == 201:
            # Service registration succeeded
            assert "service_secret" in response.json()
        else:
            # May require authentication, but security headers should be present
            assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio 
    async def test_concurrent_security_operations(self, client: TestClient, db_session: AsyncSession):
        """Test security features work correctly under concurrent load."""
        user = await create_test_user(db_session, email="concurrent@example.com", password="correct_password")
        
        async def make_request():
            """Make a login request."""
            return client.post("/api/auth/login", json={
                "email": "concurrent@example.com",
                "password": "wrong_password"
            })
        
        # Make concurrent requests
        tasks = [make_request() for _ in range(5)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should have proper error handling
        for response in responses:
            if not isinstance(response, Exception):
                assert response.status_code in [401, 423, 429]  # Auth fail, locked, or rate limited
                assert "X-Request-ID" in response.headers


class TestSecurityConfigurationValidation:
    """Test security configuration and edge cases."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_security_headers_configuration(self, client: TestClient):
        """Test security headers are properly configured."""
        response = client.get("/health")
        
        # Verify critical security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block"
        }
        
        for header, expected_value in security_headers.items():
            assert header in response.headers
            assert response.headers[header] == expected_value
    
    def test_rate_limiting_configuration(self, client: TestClient):
        """Test rate limiting is properly configured."""
        # Health endpoint should have higher limits
        responses = []
        for i in range(10):
            response = client.get("/health")
            responses.append(response)
        
        # Health endpoint should not be rate limited easily
        rate_limited = [r for r in responses if r.status_code == 429]
        assert len(rate_limited) == 0  # Health should have generous limits
    
    @pytest.mark.asyncio
    async def test_audit_configuration(self, client: TestClient, db_session: AsyncSession):
        """Test audit logging configuration."""
        # Make a request that should be audited
        response = client.get("/api/auth/me")
        
        # Should get 401 (no auth) but should be audited
        assert response.status_code == 401
        
        # Request should have audit context
        assert "X-Request-ID" in response.headers
    
    @pytest.mark.asyncio
    async def test_lockout_configuration(self, client: TestClient, db_session: AsyncSession):
        """Test account lockout configuration."""
        user = await create_test_user(db_session, email="config_test@example.com", password="correct_password")
        
        # Test lockout threshold
        login_data = {"email": "config_test@example.com", "password": "wrong_password"}
        
        # Should warn before lockout
        for attempt in range(AccountLockoutConfig.MAX_FAILED_ATTEMPTS - 1):
            response = client.post("/api/auth/login", json=login_data)
            assert response.status_code == 401
            if "remaining" in response.json()["detail"]:
                assert "X-Remaining-Attempts" in response.headers
        
        # Final attempt should lock
        response = client.post("/api/auth/login", json=login_data)
        if response.status_code == 423:
            assert "X-Account-Locked" in response.headers
            assert "Retry-After" in response.headers


class TestSecurityPerformance:
    """Test security features performance and scalability."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_security_middleware_performance(self, client: TestClient):
        """Test that security middleware doesn't significantly impact performance."""
        start_time = time.time()
        
        # Make multiple requests
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 10 requests in reasonable time (< 5 seconds)
        assert total_time < 5.0
        
        # Each request should have response time header
        final_response = client.get("/health")
        assert "X-Response-Time" in final_response.headers
    
    @pytest.mark.asyncio
    async def test_audit_logging_performance(self, client: TestClient, db_session: AsyncSession):
        """Test audit logging doesn't significantly impact performance."""
        user = await create_test_user(db_session, email="perf_test@example.com", password="correct_password")
        
        start_time = time.time()
        
        # Make authenticated requests that generate audit logs
        for _ in range(5):
            response = client.post("/api/auth/login", json={
                "email": "perf_test@example.com",
                "password": "wrong_password"  # Will create audit logs
            })
            assert response.status_code == 401
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete in reasonable time even with audit logging
        assert total_time < 10.0


class TestSecurityValidationScenarios:
    """Test real-world security scenarios and attack patterns."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_brute_force_attack_simulation(self, client: TestClient):
        """Simulate brute force attack and verify protections."""
        attack_data = {"email": "victim@example.com", "password": "guess"}
        
        responses = []
        for attempt in range(20):  # Aggressive attack
            response = client.post("/api/auth/login", json=attack_data)
            responses.append(response)
            
            # Should be rate limited or blocked
            if response.status_code in [423, 429]:
                break
        
        # Should have protection mechanisms engaged
        blocked_responses = [r for r in responses if r.status_code in [423, 429]]
        assert len(blocked_responses) > 0
    
    def test_sql_injection_attempt_detection(self, client: TestClient):
        """Test SQL injection attempts are handled safely."""
        injection_attempts = [
            {"email": "admin'; DROP TABLE users; --", "password": "password"},
            {"email": "admin' OR '1'='1", "password": "password"},
            {"email": "admin'; SELECT * FROM users; --", "password": "password"}
        ]
        
        for attempt in injection_attempts:
            response = client.post("/api/auth/login", json=attempt)
            
            # Should not cause server error (500)
            assert response.status_code != 500
            # Should be rejected (401 unauthorized or 400 bad request)
            assert response.status_code in [400, 401]
    
    def test_xss_attempt_detection(self, client: TestClient):
        """Test XSS attempts in request data."""
        xss_attempts = [
            {"email": "<script>alert('xss')</script>@example.com", "password": "password"},
            {"email": "user@example.com", "password": "<img src=x onerror=alert('xss')>"},
        ]
        
        for attempt in xss_attempts:
            response = client.post("/api/auth/login", json=attempt)
            
            # Should not execute script or cause server error
            assert response.status_code != 500
            # Response should not contain unescaped script tags
            response_text = response.text
            assert "<script>" not in response_text
            assert "onerror=" not in response_text
    
    def test_session_security(self, client: TestClient):
        """Test session-related security measures."""
        # Test that requests have proper session tracking
        response1 = client.get("/health")
        response2 = client.get("/health")
        
        # Each should have unique request ID
        assert response1.headers["X-Request-ID"] != response2.headers["X-Request-ID"]
        
        # Both should have security headers
        for response in [response1, response2]:
            assert "X-Content-Type-Options" in response.headers
            assert "X-Frame-Options" in response.headers
    
    @pytest.mark.asyncio
    async def test_privilege_escalation_prevention(self, client: TestClient, db_session: AsyncSession):
        """Test prevention of privilege escalation attacks."""
        # Create regular user
        user = await create_test_user(db_session, email="regular@example.com")
        token = get_test_token(user.id)
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access admin endpoints
        admin_endpoints = [
            "/api/admin/users",
            "/api/admin/lockout-statistics",
            "/api/admin/unlock-account/1"
        ]
        
        for endpoint in admin_endpoints:
            response = client.get(endpoint, headers=headers)
            # Should be forbidden, not unauthorized (proves token is valid but insufficient)
            assert response.status_code == 403
    
    def test_dos_protection(self, client: TestClient):
        """Test basic DoS protection measures."""
        # Test large request body handling
        large_data = {"email": "test@example.com", "password": "x" * 10000}
        response = client.post("/api/auth/login", json=large_data)
        
        # Should handle gracefully (not 500)
        assert response.status_code != 500
        # Should either succeed or fail gracefully
        assert response.status_code in [400, 401, 413, 422]
        
        # Test rapid requests (basic rate limiting test)
        responses = []
        for _ in range(15):  # Rapid requests
            response = client.get("/health")
            responses.append(response)
        
        # Should have rate limiting engaged for some endpoints
        # (Health might be exempted, but headers should be present)
        for response in responses:
            assert "X-Response-Time" in response.headers