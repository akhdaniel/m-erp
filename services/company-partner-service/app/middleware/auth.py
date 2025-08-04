"""
Authentication middleware for inter-service communication.
"""

import httpx
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request, Depends
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
                f"{self.auth_service_url}/api/auth/validate-token",
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
                "service_name": "company-partner-service",
                "service_secret": settings.service_key
            }
            
            response = await self.client.post(
                f"{self.auth_service_url}/api/services/token",
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
    credentials: HTTPAuthorizationCredentials = Depends(security)
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
    current_user: Dict[str, Any] = Depends(get_current_user)
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


def require_company_access(company_id: int, user_data: Dict[str, Any]) -> bool:
    """
    Check if user has access to a specific company.
    TODO: This is a placeholder - implement proper company access control
    based on user-company relationships from the database.
    """
    # For now, allow all authenticated users access to all companies
    # This should be replaced with proper company access control
    return True


async def verify_company_access(
    company_id: int,
    current_user: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Dependency to verify user has access to a specific company.
    """
    if not require_company_access(company_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )
    
    return current_user


async def get_current_user_company(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> int:
    """
    Dependency to get the current user's company ID.
    TODO: This should be replaced with proper multi-company logic
    that gets the company based on user's selection or default company.
    """
    # For now, return a default company ID (1)
    # This should be replaced with logic to get the user's current/selected company
    company_id = current_user.get("company_id", 1)
    return company_id