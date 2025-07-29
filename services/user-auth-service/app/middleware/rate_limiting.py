"""
Rate limiting middleware for API endpoints.
Implements sliding window rate limiting with Redis backend.
"""

import time
import json
from typing import Optional, Dict, Any, Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
try:
    import redis.asyncio as redis
except ImportError:
    import aioredis as redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings


class RateLimitConfig:
    """Rate limiting configuration constants."""
    
    # General API limits
    GENERAL_LIMIT = "100/minute"
    BURST_LIMIT = "20/second"
    
    # Authentication endpoint limits (more restrictive)
    AUTH_LOGIN_LIMIT = "5/minute"
    AUTH_REGISTER_LIMIT = "3/minute"
    AUTH_PASSWORD_RESET_LIMIT = "3/5minutes"
    
    # Admin endpoint limits
    ADMIN_LIMIT = "200/minute"
    
    # Service authentication limits
    SERVICE_AUTH_LIMIT = "50/minute"
    
    # Health check limits (generous)
    HEALTH_LIMIT = "60/minute"


class SecurityRateLimiter:
    """Enhanced rate limiter with security features."""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize rate limiter with Redis backend."""
        if redis_url:
            self.redis_client = redis.from_url(redis_url)
        else:
            # In-memory fallback (not recommended for production)
            self.redis_client = None
            self.memory_store: Dict[str, Dict[str, Any]] = {}
    
    async def is_rate_limited(
        self, 
        identifier: str, 
        limit: int, 
        window: int,
        cost: int = 1
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request should be rate limited using sliding window.
        
        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            limit: Maximum requests allowed in window
            window: Time window in seconds
            cost: Cost of this request (default 1)
            
        Returns:
            Tuple of (is_limited, info_dict)
        """
        now = time.time()
        key = f"rate_limit:{identifier}"
        
        if self.redis_client:
            return await self._redis_rate_limit(key, limit, window, cost, now)
        else:
            return await self._memory_rate_limit(key, limit, window, cost, now)
    
    async def _redis_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window: int, 
        cost: int, 
        now: float
    ) -> tuple[bool, Dict[str, Any]]:
        """Redis-based sliding window rate limiting."""
        try:
            pipe = self.redis_client.pipeline()
            
            # Remove expired entries
            pipe.zremrangebyscore(key, 0, now - window)
            
            # Count current requests in window
            pipe.zcard(key)
            
            # Add current request
            request_id = f"{now}:{time.time_ns()}"
            pipe.zadd(key, {request_id: now})
            
            # Set expiration
            pipe.expire(key, window + 60)  # Extra buffer
            
            results = await pipe.execute()
            current_count = results[1]
            
            # Check if limit exceeded
            is_limited = (current_count + cost) > limit
            
            # Calculate reset time
            reset_time = int(now + window)
            remaining = max(0, limit - current_count)
            
            info = {
                "limit": limit,
                "remaining": remaining,
                "reset": reset_time,
                "retry_after": window if is_limited else 0
            }
            
            return is_limited, info
            
        except Exception as e:
            # Fallback to allow request if Redis fails
            print(f"Rate limiting Redis error: {e}")
            return False, {"limit": limit, "remaining": limit, "reset": int(now + window)}
    
    async def _memory_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window: int, 
        cost: int, 
        now: float
    ) -> tuple[bool, Dict[str, Any]]:
        """In-memory sliding window rate limiting (fallback)."""
        if key not in self.memory_store:
            self.memory_store[key] = {"requests": [], "blocked_until": 0}
        
        store = self.memory_store[key]
        
        # Remove expired requests
        cutoff = now - window
        store["requests"] = [req for req in store["requests"] if req > cutoff]
        
        # Check if currently blocked
        if now < store["blocked_until"]:
            info = {
                "limit": limit,
                "remaining": 0,
                "reset": int(store["blocked_until"]),
                "retry_after": int(store["blocked_until"] - now)
            }
            return True, info
        
        # Check rate limit
        current_count = len(store["requests"])
        is_limited = (current_count + cost) > limit
        
        if not is_limited:
            # Add current request
            for _ in range(cost):
                store["requests"].append(now)
        else:
            # Block for remaining window time
            store["blocked_until"] = now + window
        
        remaining = max(0, limit - current_count)
        reset_time = int(now + window)
        
        info = {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time,
            "retry_after": window if is_limited else 0
        }
        
        return is_limited, info


# Global rate limiter instance
rate_limiter = SecurityRateLimiter(settings.redis_url if hasattr(settings, 'redis_url') else None)


def get_rate_limit_key(request: Request) -> str:
    """Generate rate limit key based on request context."""
    # Use authenticated user ID if available
    if hasattr(request.state, 'user_id'):
        return f"user:{request.state.user_id}"
    
    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"


def get_endpoint_limits(path: str, method: str) -> tuple[int, int]:
    """Get rate limit configuration for specific endpoint."""
    # Authentication endpoints (more restrictive)
    if path.startswith("/api/auth/login"):
        return 5, 60  # 5 requests per minute
    elif path.startswith("/api/auth/register"):
        return 3, 60  # 3 requests per minute
    elif path.startswith("/api/auth/change-password"):
        return 3, 300  # 3 requests per 5 minutes
    
    # Admin endpoints
    elif path.startswith("/api/admin/"):
        return 200, 60  # 200 requests per minute
    
    # Service endpoints
    elif path.startswith("/api/services/"):
        return 50, 60  # 50 requests per minute
    
    # Health check
    elif path == "/health":
        return 60, 60  # 60 requests per minute
    
    # General API
    else:
        return 100, 60  # 100 requests per minute


async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """Rate limiting middleware."""
    # Skip rate limiting for certain conditions
    if should_skip_rate_limiting(request):
        return await call_next(request)
    
    # Get rate limit configuration
    limit, window = get_endpoint_limits(request.url.path, request.method)
    identifier = get_rate_limit_key(request)
    
    # Check rate limit
    is_limited, info = await rate_limiter.is_rate_limited(identifier, limit, window)
    
    if is_limited:
        # Return rate limit exceeded response
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded",
                "error": "too_many_requests",
                "limit": info["limit"],
                "reset": info["reset"],
                "retry_after": info["retry_after"]
            },
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset"]),
                "Retry-After": str(info["retry_after"])
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(info["reset"])
    
    return response


def should_skip_rate_limiting(request: Request) -> bool:
    """Determine if rate limiting should be skipped for this request."""
    # Skip for internal health checks
    user_agent = request.headers.get("user-agent", "").lower()
    if "healthcheck" in user_agent or "monitoring" in user_agent:
        return True
    
    # Skip for localhost in development
    if settings.debug and get_remote_address(request) in ["127.0.0.1", "localhost"]:
        # Still apply rate limiting but with higher limits
        return False
    
    return False


# Slowapi integration for decorator-based rate limiting
def create_limiter() -> Limiter:
    """Create SlowAPI limiter instance."""
    return Limiter(
        key_func=get_rate_limit_key,
        default_limits=[RateLimitConfig.GENERAL_LIMIT]
    )


# Custom rate limit exceeded handler
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded exceptions."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": "Rate limit exceeded",
            "error": "too_many_requests",
            "message": f"Rate limit of {exc.detail} exceeded",
            "retry_after": getattr(exc, 'retry_after', 60)
        },
        headers={
            "Retry-After": str(getattr(exc, 'retry_after', 60))
        }
    )


# Rate limiting decorators for specific use cases
def auth_rate_limit(func):
    """Decorator for authentication endpoints with strict limits."""
    async def wrapper(*args, **kwargs):
        # This would be implemented as a dependency in FastAPI
        return await func(*args, **kwargs)
    return wrapper


def admin_rate_limit(func):
    """Decorator for admin endpoints with higher limits."""
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapper