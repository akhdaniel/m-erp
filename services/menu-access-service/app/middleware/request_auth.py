"""Request authentication middleware."""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import httpx

from app.middleware.auth import auth_client
from app.middleware.simple_auth import get_user_from_token
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and validate user authentication from requests."""
    
    # Paths that don't require authentication
    PUBLIC_PATHS = ["/", "/health", "/docs", "/openapi.json", "/redoc"]
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and extract user information."""
        # Initialize request state
        request.state.user = None
        request.state.is_authenticated = False
        
        # Skip authentication for public paths
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            try:
                # First try to validate as user token
                user_data = await auth_client.validate_token(token)
                if user_data:
                    # Set user data on request state
                    request.state.user = user_data
                    request.state.is_authenticated = True
                    logger.debug(f"Authenticated user: {user_data.get('email')}")
                else:
                    # If user token validation fails, try to validate as service token
                    logger.debug("User token validation failed, trying service token validation")
                    service_data = await self._validate_service_token(token)
                    if service_data:
                        # Set service data on request state (treat as admin user)
                        request.state.user = {
                            "user_id": 0,
                            "email": f"service@{service_data.get('service_name', 'unknown')}.local",
                            "permissions": ["admin:all"],  # Services have admin permissions
                            "is_active": True,
                            "role_level": 0  # Highest level
                        }
                        request.state.is_authenticated = True
                        logger.debug(f"Authenticated service: {service_data.get('service_name')}")
                    else:
                        logger.warning("Invalid or expired token provided")
            except Exception as e:
                logger.error(f"Error validating token: {str(e)}")
        
        # Continue processing the request
        response = await call_next(request)
        return response
    
    async def _validate_service_token(self, token: str) -> dict:
        """Validate a service token with the auth service."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.auth_service_url}/api/services/validate",
                    json={"token": token}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Service token validation failed: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error validating service token: {str(e)}")
            return None