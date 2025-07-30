"""
Authentication middleware for inter-service communication.
"""

import httpx
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()


class AuthClient:
    """Client for authentication service communication."""
    
    def __init__(self):
        self.auth_service_url = settings.auth_service_url
        self.service_token = None
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a JWT token with the auth service."""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post(
                f"{self.auth_service_url}/auth/validate-token",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.warning("Token validation failed: Invalid or expired token")
                return None
            else:
                logger.error(f"Auth service error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return None
    
    async def get_service_token(self) -> Optional[str]:
        """Get a service-to-service authentication token."""
        try:
            if self.service_token:
                # TODO: Check if token is still valid before reusing
                return self.service_token
            
            auth_data = {
                "service_name": "menu-access-service",
                "service_key": settings.service_key
            }
            
            response = await self.client.post(
                f"{self.auth_service_url}/services/auth",
                json=auth_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.service_token = data.get("access_token")
                logger.info("Service token obtained successfully")
                return self.service_token
            else:
                logger.error(f"Failed to get service token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting service token: {str(e)}")
            return None
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global auth client instance
auth_client = AuthClient()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = security
) -> Dict[str, Any]:
    """
    Dependency to get the current user from JWT token.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_data = await auth_client.validate_token(credentials.credentials)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data


async def get_current_active_user(
    current_user: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Dependency to get the current active user.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    return current_user


def require_permission(permission_code: str):
    """
    Decorator factory to require specific permission for endpoint access.
    """
    def permission_checker(current_user: Dict[str, Any]) -> Dict[str, Any]:
        user_permissions = current_user.get("permissions", [])
        if permission_code not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_code}' required"
            )
        return current_user
    
    return permission_checker


def require_role_level(min_level: int):
    """
    Decorator factory to require minimum role level for endpoint access.
    """
    def role_level_checker(current_user: Dict[str, Any]) -> Dict[str, Any]:
        user_role_level = current_user.get("role_level", 999)  # Default to lowest level
        if user_role_level > min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role level {min_level} or higher required"
            )
        return current_user
    
    return role_level_checker