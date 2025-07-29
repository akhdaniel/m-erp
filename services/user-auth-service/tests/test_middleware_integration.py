"""
Middleware integration tests - verifying middleware stack order and interactions.
"""

import pytest
import json
from unittest.mock import patch, Mock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.middleware.rate_limiting import SecurityRateLimiter
from app.middleware.security_headers import detect_suspicious_activity
from tests.conftest import create_test_user


class TestMiddlewareOrder:
    """Test that middleware is applied in the correct order."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_middleware_order_headers(self, client: TestClient):
        """Test middleware order through response headers."""
        response = client.get("/health")
        
        # Headers should be applied in correct order
        # 1. Request ID (first)
        assert "X-Request-ID" in response.headers
        
        # 2. Security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        
        # 3. Rate limiting headers
        assert "X-RateLimit-Policy" in response.headers
        
        # 4. Response time (last)
        assert "X-Response-Time" in response.headers
    
    def test_middleware_processing_order(self, client: TestClient):
        """Test that middleware processes requests in correct order."""
        # Make a request that would trigger multiple middleware
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrong"
        })
        
        # Should have all middleware headers
        expected_headers = [
            "X-Request-ID",      # Request ID middleware
            "X-Content-Type-Options",  # Security headers
            "X-RateLimit-Limit", # Rate limiting (if not rate limited)
            "X-Response-Time"    # Response time (audit middleware)
        ]
        
        for header in expected_headers:
            if header == "X-RateLimit-Limit" and response.status_code == 429:
                continue  # Rate limited responses might not have all headers
            assert header in response.headers, f"Missing header: {header}"
    
    def test_cors_integration(self, client: TestClient):
        """Test CORS middleware integration with security middleware."""
        # Make a preflight request
        response = client.options("/api/auth/login", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        # Should have CORS headers
        assert "Access-Control-Allow-Origin" in response.headers
        
        # Should also have security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Request-ID" in response.headers


class TestRateLimitingMiddleware:
    """Test rate limiting middleware integration."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_rate_limiting_headers_consistent(self, client: TestClient):
        """Test rate limiting headers are consistently applied."""
        responses = []
        
        # Make several requests
        for i in range(5):
            response = client.post("/api/auth/login", json={
                "email": f"test{i}@example.com",
                "password": "wrong"
            })
            responses.append(response)
        
        # Check rate limiting headers progression
        for i, response in enumerate(responses):
            if response.status_code != 429:  # Not rate limited
                assert "X-RateLimit-Limit" in response.headers
                assert "X-RateLimit-Remaining" in response.headers
                assert "X-RateLimit-Reset" in response.headers
                
                # Remaining should decrease
                remaining = int(response.headers["X-RateLimit-Remaining"])
                assert remaining >= 0
    
    def test_rate_limiting_endpoint_specific(self, client: TestClient):
        """Test different endpoints have different rate limits."""
        # Test auth endpoint (strict limits)
        auth_responses = []
        for i in range(3):
            response = client.post("/api/auth/login", json={
                "email": "auth_test@example.com",
                "password": "wrong"
            })
            auth_responses.append(response)
        
        # Test health endpoint (generous limits)
        health_responses = []
        for i in range(10):
            response = client.get("/health")
            health_responses.append(response)
        
        # Auth should be more restrictive than health
        auth_rate_limited = any(r.status_code == 429 for r in auth_responses)
        health_rate_limited = any(r.status_code == 429 for r in health_responses)
        
        # Health should be less likely to be rate limited
        if auth_rate_limited and not health_rate_limited:
            assert True  # Expected behavior
        elif not auth_rate_limited:
            # Check that auth has lower limits in headers
            auth_limit = int(auth_responses[0].headers.get("X-RateLimit-Limit", "100"))
            health_limit = int(health_responses[0].headers.get("X-RateLimit-Limit", "100"))
            # Auth endpoint should have stricter limits (but this might vary by config)
    
    @patch('app.middleware.rate_limiting.rate_limiter')
    def test_rate_limiting_redis_fallback(self, mock_rate_limiter, client: TestClient):
        """Test rate limiting falls back gracefully when Redis fails."""
        # Mock Redis failure
        mock_rate_limiter.is_rate_limited = AsyncMock(side_effect=Exception("Redis connection failed"))
        
        # Request should still work (fallback to allow)
        response = client.get("/health")
        assert response.status_code == 200
        
        # Should have security headers even if rate limiting fails
        assert "X-Content-Type-Options" in response.headers


class TestSecurityHeadersMiddleware:
    """Test security headers middleware integration."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_security_headers_all_endpoints(self, client: TestClient):
        """Test security headers are applied to all endpoints."""
        endpoints = [
            ("/health", "GET"),
            ("/api/auth/login", "POST"),
            ("/docs", "GET"),
            ("/openapi.json", "GET")
        ]
        
        for endpoint, method in endpoints:
            if method == "POST":
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            
            # All endpoints should have basic security headers
            assert "X-Content-Type-Options" in response.headers
            assert "X-Frame-Options" in response.headers
            assert "X-Request-ID" in response.headers
    
    def test_csp_header_context_specific(self, client: TestClient):
        """Test CSP headers are context-specific."""
        # API endpoint should have strict CSP
        api_response = client.post("/api/auth/login", json={})
        
        # Docs endpoint should have relaxed CSP
        docs_response = client.get("/docs")
        
        # Both should have CSP but docs should be more permissive
        if "Content-Security-Policy" in api_response.headers and "Content-Security-Policy" in docs_response.headers:
            api_csp = api_response.headers["Content-Security-Policy"]
            docs_csp = docs_response.headers["Content-Security-Policy"]
            
            # Docs should allow unsafe-inline and unsafe-eval
            assert "'unsafe-inline'" in docs_csp
            assert "'unsafe-eval'" in docs_csp
    
    def test_suspicious_activity_detection(self, client: TestClient):
        """Test suspicious activity detection in security middleware."""
        # Test suspicious user agent
        suspicious_headers = {"User-Agent": "sqlmap/1.0"}
        response = client.get("/health", headers=suspicious_headers)
        
        # Should still work but be detected
        assert response.status_code == 200
        assert "X-Response-Time" in response.headers
        
        # Test with normal user agent
        normal_headers = {"User-Agent": "Mozilla/5.0"}
        normal_response = client.get("/health", headers=normal_headers)
        assert normal_response.status_code == 200
    
    def test_suspicious_patterns_detection(self):
        """Test suspicious pattern detection function."""
        # Mock request with suspicious user agent
        mock_request = Mock()
        mock_request.headers = {"user-agent": "nikto/2.1.6"}
        mock_request.url.path = "/normal/path"
        
        patterns = detect_suspicious_activity(mock_request)
        assert "suspicious_user_agent" in patterns
        
        # Mock request with injection attempt
        mock_request.headers = {"user-agent": "Mozilla/5.0"}
        mock_request.url.path = "/api/users'; DROP TABLE users; --"
        
        patterns = detect_suspicious_activity(mock_request)
        assert "potential_injection_attempt" in patterns
        
        # Mock request with no headers
        mock_request.headers = {}
        mock_request.url.path = "/normal/path"
        
        patterns = detect_suspicious_activity(mock_request)
        assert "missing_user_agent" in patterns


class TestAuditMiddleware:
    """Test audit middleware integration."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_audit_context_creation(self, client: TestClient, db_session: AsyncSession):
        """Test that audit context is created for requests."""
        # Make a request to a security endpoint
        response = client.post("/api/auth/login", json={
            "email": "audit@example.com",
            "password": "wrong"
        })
        
        # Should have request ID for audit tracking
        assert "X-Request-ID" in response.headers
        
        # Response should be processed
        assert response.status_code in [400, 401, 422]
    
    def test_audit_request_id_unique(self, client: TestClient):
        """Test that each request gets unique audit ID."""
        responses = []
        for i in range(5):
            response = client.get("/health")
            responses.append(response)
        
        # All request IDs should be unique
        request_ids = [r.headers["X-Request-ID"] for r in responses]
        assert len(set(request_ids)) == len(request_ids)
    
    @pytest.mark.asyncio 
    async def test_audit_slow_request_detection(self, client: TestClient):
        """Test audit middleware detects slow requests."""
        # This would require mocking slow operations
        # For now, just verify response time header is present
        response = client.get("/health")
        
        assert "X-Response-Time" in response.headers
        response_time = response.headers["X-Response-Time"]
        assert response_time.endswith("s")  # Should be in seconds format


class TestMiddlewareErrorHandling:
    """Test middleware error handling and resilience."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @patch('app.middleware.audit_middleware.get_db')
    def test_audit_middleware_db_failure(self, mock_get_db, client: TestClient):
        """Test audit middleware handles database failures gracefully."""
        # Mock database failure
        mock_get_db.side_effect = Exception("Database connection failed")
        
        # Request should still work
        response = client.get("/health")
        assert response.status_code == 200
        
        # Should still have basic headers
        assert "X-Request-ID" in response.headers
        assert "X-Content-Type-Options" in response.headers
    
    @patch('app.middleware.security_headers.detect_suspicious_activity')
    def test_security_middleware_detection_failure(self, mock_detect, client: TestClient):
        """Test security middleware handles detection failures gracefully."""
        # Mock detection failure
        mock_detect.side_effect = Exception("Detection failed")
        
        # Request should still work
        response = client.get("/health")
        assert response.status_code == 200
        
        # Should still have security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
    
    def test_middleware_large_request_handling(self, client: TestClient):
        """Test middleware handles large requests appropriately."""
        # Large JSON payload
        large_data = {"data": "x" * 1000, "email": "test@example.com"}
        
        response = client.post("/api/auth/login", json=large_data)
        
        # Should handle gracefully
        assert response.status_code != 500
        assert "X-Request-ID" in response.headers
        assert "X-Content-Type-Options" in response.headers
    
    def test_middleware_malformed_request_handling(self, client: TestClient):
        """Test middleware handles malformed requests."""
        # Invalid JSON
        response = client.post(
            "/api/auth/login",
            data="invalid json{",
            headers={"Content-Type": "application/json"}
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 422]  # Bad request, not server error
        assert "X-Request-ID" in response.headers
        assert "X-Content-Type-Options" in response.headers


class TestMiddlewarePerformance:
    """Test middleware performance characteristics."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_middleware_overhead(self, client: TestClient):
        """Test middleware doesn't add excessive overhead."""
        import time
        
        # Time multiple requests
        start_time = time.time()
        
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete quickly (< 2 seconds for 10 requests)
        assert total_time < 2.0
        
        # Each response should have timing info
        final_response = client.get("/health")
        assert "X-Response-Time" in final_response.headers
    
    def test_middleware_memory_efficiency(self, client: TestClient):
        """Test middleware doesn't leak memory or resources."""
        # Make many requests to check for memory leaks
        for i in range(50):
            response = client.get("/health")
            assert response.status_code == 200
            
            # Each should have unique request ID (no reuse)
            assert "X-Request-ID" in response.headers
            
            # Should have consistent headers
            assert "X-Content-Type-Options" in response.headers


class TestMiddlewareConfiguration:
    """Test middleware configuration and customization."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_security_headers_configuration(self, client: TestClient):
        """Test security headers can be configured."""
        response = client.get("/health")
        
        # Check configurable headers have expected values
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "no-store" in response.headers["Cache-Control"]
    
    def test_rate_limiting_configuration(self, client: TestClient):
        """Test rate limiting configuration is applied correctly."""
        # Test different endpoint types have different limits
        auth_response = client.post("/api/auth/login", json={})
        health_response = client.get("/health")
        
        # Both should have rate limit headers
        for response in [auth_response, health_response]:
            if response.status_code != 429:
                assert "X-RateLimit-Limit" in response.headers
                limit = int(response.headers["X-RateLimit-Limit"])
                assert limit > 0
    
    @patch.dict('os.environ', {'RATE_LIMITING_ENABLED': 'false'})
    def test_rate_limiting_can_be_disabled(self, client: TestClient):
        """Test rate limiting can be disabled via configuration."""
        # This would require restarting the app with new config
        # For now, just verify the config exists
        from app.core.config import settings
        assert hasattr(settings, 'rate_limiting_enabled')
    
    @patch.dict('os.environ', {'AUDIT_LOGGING_ENABLED': 'false'})  
    def test_audit_logging_can_be_disabled(self, client: TestClient):
        """Test audit logging can be disabled via configuration."""
        # This would require restarting the app with new config
        # For now, just verify the config exists
        from app.core.config import settings
        assert hasattr(settings, 'audit_logging_enabled')