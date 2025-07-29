"""
Security headers middleware for enhanced security.
Implements security headers following OWASP best practices.
"""

from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.core.config import settings


class SecurityHeaders:
    """Security headers configuration and constants."""
    
    # Content Security Policy
    CSP_POLICY = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    
    # Permissions Policy (Feature Policy)
    PERMISSIONS_POLICY = (
        "accelerometer=(), "
        "camera=(), "
        "geolocation=(), "
        "gyroscope=(), "
        "magnetometer=(), "
        "microphone=(), "
        "payment=(), "
        "usb=()"
    )


async def security_headers_middleware(request: Request, call_next: Callable) -> Response:
    """
    Add security headers to all responses.
    Implements OWASP security header recommendations.
    """
    response = await call_next(request)
    
    # Security headers for all responses
    security_headers = {
        # Prevent MIME sniffing
        "X-Content-Type-Options": "nosniff",
        
        # Enable XSS protection
        "X-XSS-Protection": "1; mode=block",
        
        # Prevent clickjacking
        "X-Frame-Options": "DENY",
        
        # Referrer policy
        "Referrer-Policy": "strict-origin-when-cross-origin",
        
        # Permissions policy
        "Permissions-Policy": SecurityHeaders.PERMISSIONS_POLICY,
        
        # Remove server information
        "Server": "UserAuthService/1.0",
        
        # Cache control for security
        "Cache-Control": "no-store, no-cache, must-revalidate, private",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    
    # HTTPS-only headers (only in production or when using HTTPS)
    if not settings.debug or request.url.scheme == "https":
        security_headers.update({
            # HTTP Strict Transport Security
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Content Security Policy
            "Content-Security-Policy": SecurityHeaders.CSP_POLICY,
        })
    
    # API-specific headers
    if request.url.path.startswith("/api/"):
        security_headers.update({
            # API versioning
            "API-Version": "1.0",
            
            # Rate limiting info (will be overridden by rate limiting middleware)
            "X-RateLimit-Policy": "applied",
        })
    
    # Documentation-specific headers
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        # Relax CSP for documentation pages
        if "Content-Security-Policy" in security_headers:
            security_headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self'"
            )
    
    # Add all security headers to response
    for header, value in security_headers.items():
        response.headers[header] = value
    
    return response


def add_cors_security_headers(response: Response) -> Response:
    """
    Add CORS security headers to response.
    Called by CORS middleware for additional security.
    """
    # Prevent credential theft
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    # Limit exposed headers
    response.headers["Access-Control-Expose-Headers"] = (
        "X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, "
        "API-Version, X-Request-ID"
    )
    
    # Control preflight cache
    response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
    
    return response


async def request_id_middleware(request: Request, call_next: Callable) -> Response:
    """
    Add unique request ID for tracking and security monitoring.
    """
    import uuid
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # Add to request state for logging
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response


async def security_monitoring_middleware(request: Request, call_next: Callable) -> Response:
    """
    Security monitoring middleware for detecting suspicious activity.
    """
    import time
    
    start_time = time.time()
    
    # Log security-relevant request info
    security_context = {
        "ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", ""),
        "method": request.method,
        "path": request.url.path,
        "timestamp": start_time
    }
    
    # Check for suspicious patterns
    suspicious_patterns = detect_suspicious_activity(request)
    if suspicious_patterns:
        # Log suspicious activity (implement actual logging)
        print(f"Suspicious activity detected: {suspicious_patterns}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    response_time = time.time() - start_time
    response.headers["X-Response-Time"] = f"{response_time:.3f}s"
    
    return response


def detect_suspicious_activity(request: Request) -> list[str]:
    """
    Detect suspicious activity patterns in requests.
    Returns list of detected suspicious patterns.
    """
    patterns = []
    
    # Check user agent
    user_agent = request.headers.get("user-agent", "").lower()
    suspicious_agents = ["sqlmap", "nikto", "dirb", "gobuster", "scanner"]
    if any(agent in user_agent for agent in suspicious_agents):
        patterns.append("suspicious_user_agent")
    
    # Check for common attack patterns in path
    path = request.url.path.lower()
    attack_patterns = ["../", "script>", "select ", "union ", "drop ", "exec("]
    if any(pattern in path for pattern in attack_patterns):
        patterns.append("potential_injection_attempt")
    
    # Check for excessive header size
    total_header_size = sum(len(k) + len(v) for k, v in request.headers.items())
    if total_header_size > 8192:  # 8KB limit
        patterns.append("excessive_header_size")
    
    # Check for missing standard headers
    if not request.headers.get("user-agent"):
        patterns.append("missing_user_agent")
    
    return patterns


class SecurityConfig:
    """Security configuration constants."""
    
    # Maximum request sizes
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_HEADER_SIZE = 8192  # 8KB
    
    # Timeouts
    REQUEST_TIMEOUT = 30  # seconds
    
    # Security headers
    SECURITY_HEADERS_ENABLED = True
    
    # Content type restrictions
    ALLOWED_CONTENT_TYPES = [
        "application/json",
        "application/x-www-form-urlencoded",
        "multipart/form-data"
    ]


async def content_security_middleware(request: Request, call_next: Callable) -> Response:
    """
    Content security middleware for validating request content.
    """
    # Check content length
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > SecurityConfig.MAX_REQUEST_SIZE:
        return JSONResponse(
            status_code=413,
            content={
                "detail": "Request entity too large",
                "max_size": SecurityConfig.MAX_REQUEST_SIZE
            }
        )
    
    # Check content type for POST/PUT requests
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "").split(";")[0]
        if content_type and content_type not in SecurityConfig.ALLOWED_CONTENT_TYPES:
            return JSONResponse(
                status_code=415,
                content={
                    "detail": "Unsupported media type",
                    "allowed_types": SecurityConfig.ALLOWED_CONTENT_TYPES
                }
            )
    
    return await call_next(request)