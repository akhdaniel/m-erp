"""Request authentication middleware."""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.middleware.auth import auth_client
from app.middleware.simple_auth import get_user_from_token

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
                # For development, use simple JWT decoding
                user_data = await get_user_from_token(token)
                if user_data:
                    # Set user data on request state
                    request.state.user = user_data
                    request.state.is_authenticated = True
                    logger.debug(f"Authenticated user: {user_data.get('email')}")
                else:
                    logger.warning("Invalid or expired token provided")
            except Exception as e:
                logger.error(f"Error validating token: {str(e)}")
        
        # Continue processing the request
        response = await call_next(request)
        return response