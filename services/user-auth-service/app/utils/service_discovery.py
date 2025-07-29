"""
Service discovery and registration utilities.
Helper functions for microservices to register with the auth service.
"""

import httpx
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ServiceDiscoveryClient:
    """
    Client for registering and authenticating with the auth service.
    This can be used by other microservices in the ERP system.
    """
    
    def __init__(
        self,
        auth_service_url: str,
        service_name: str,
        service_secret: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        Initialize service discovery client.
        
        Args:
            auth_service_url: Base URL of the auth service
            service_name: Name of this service
            service_secret: Service secret (if already registered)
            timeout: Request timeout in seconds
        """
        self.auth_service_url = auth_service_url.rstrip('/')
        self.service_name = service_name
        self.service_secret = service_secret
        self.timeout = timeout
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
    async def register_service(
        self,
        service_description: str,
        allowed_scopes: List[str],
        admin_token: str
    ) -> str:
        """
        Register this service with the auth service.
        
        Args:
            service_description: Description of this service
            allowed_scopes: List of scopes this service should be allowed
            admin_token: Admin token for service registration
            
        Returns:
            str: Service secret for future authentication
            
        Raises:
            httpx.HTTPError: If registration fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.auth_service_url}/api/services/register",
                json={
                    "service_name": self.service_name,
                    "service_description": service_description,
                    "allowed_scopes": allowed_scopes
                },
                headers={
                    "Authorization": f"Bearer {admin_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                self.service_secret = data["service_secret"]
                logger.info(f"Service '{self.service_name}' registered successfully")
                return self.service_secret
            else:
                error_detail = response.json().get("detail", "Unknown error")
                logger.error(f"Failed to register service: {error_detail}")
                response.raise_for_status()
    
    async def authenticate(self, requested_scopes: Optional[List[str]] = None) -> str:
        """
        Authenticate with the auth service and get access token.
        
        Args:
            requested_scopes: Specific scopes to request (optional)
            
        Returns:
            str: Access token
            
        Raises:
            ValueError: If service is not registered or authentication fails
            httpx.HTTPError: If request fails
        """
        if not self.service_secret:
            raise ValueError("Service secret not set. Register service first.")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.auth_service_url}/api/services/token",
                json={
                    "service_name": self.service_name,
                    "service_secret": self.service_secret,
                    "scopes": requested_scopes
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                expires_in = data["expires_in"]
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                
                logger.info(f"Service '{self.service_name}' authenticated successfully")
                return self.access_token
            else:
                error_detail = response.json().get("detail", "Unknown error")
                logger.error(f"Failed to authenticate service: {error_detail}")
                response.raise_for_status()
    
    async def get_valid_token(self, requested_scopes: Optional[List[str]] = None) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Args:
            requested_scopes: Specific scopes to request (optional)
            
        Returns:
            str: Valid access token
        """
        # Check if we have a valid token
        if (self.access_token and self.token_expires_at and 
            datetime.utcnow() < self.token_expires_at - timedelta(minutes=5)):
            return self.access_token
        
        # Authenticate to get new token
        return await self.authenticate(requested_scopes)
    
    async def validate_user_token(
        self,
        user_token: str,
        required_permissions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate a user token using the auth service.
        
        Args:
            user_token: User access token to validate
            required_permissions: Required permissions for the operation
            
        Returns:
            Dict containing validation result and user info
            
        Raises:
            httpx.HTTPError: If validation request fails
        """
        service_token = await self.get_valid_token(["validate:tokens"])
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.auth_service_url}/api/validate/user-token",
                json={
                    "token": user_token,
                    "required_permissions": required_permissions
                },
                headers={
                    "Authorization": f"Bearer {service_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
    
    async def get_user_info(
        self,
        user_id: int,
        include_roles: bool = False
    ) -> Dict[str, Any]:
        """
        Get user information from the auth service.
        
        Args:
            user_id: ID of the user to retrieve
            include_roles: Whether to include role information
            
        Returns:
            Dict containing user information
            
        Raises:
            httpx.HTTPError: If request fails
        """
        service_token = await self.get_valid_token(["validate:tokens"])
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.auth_service_url}/api/validate/user-info",
                json={
                    "user_id": user_id,
                    "include_roles": include_roles
                },
                headers={
                    "Authorization": f"Bearer {service_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
    
    async def get_user_permissions(self, user_id: int) -> List[str]:
        """
        Get permissions for a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of user permissions
            
        Raises:
            httpx.HTTPError: If request fails
        """
        service_token = await self.get_valid_token(["validate:tokens"])
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.auth_service_url}/api/validate/permissions/{user_id}",
                headers={"Authorization": f"Bearer {service_token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
    
    async def health_check(self) -> bool:
        """
        Check if the auth service is healthy.
        
        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.auth_service_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False


# Convenience function for creating a configured client
def create_service_client(
    auth_service_url: str,
    service_name: str,
    service_secret: Optional[str] = None
) -> ServiceDiscoveryClient:
    """
    Create a configured service discovery client.
    
    Args:
        auth_service_url: Base URL of the auth service
        service_name: Name of this service
        service_secret: Service secret (if already registered)
        
    Returns:
        ServiceDiscoveryClient: Configured client instance
    """
    return ServiceDiscoveryClient(
        auth_service_url=auth_service_url,
        service_name=service_name,
        service_secret=service_secret
    )


# Example usage for other microservices
async def example_service_setup():
    """
    Example of how other microservices would use this client.
    """
    # Create client
    client = create_service_client(
        auth_service_url="http://auth-service:8000",
        service_name="inventory-service"
    )
    
    # Register service (one-time setup with admin token)
    try:
        secret = await client.register_service(
            service_description="Inventory management service",
            allowed_scopes=["read:users", "validate:tokens"],
            admin_token="admin-token-here"
        )
        print(f"Service registered with secret: {secret}")
    except Exception as e:
        print(f"Registration failed: {e}")
    
    # Authenticate and get service token
    try:
        token = await client.authenticate()
        print(f"Service authenticated with token: {token[:20]}...")
    except Exception as e:
        print(f"Authentication failed: {e}")
    
    # Validate a user token
    try:
        result = await client.validate_user_token(
            user_token="user-token-here",
            required_permissions=["read"]
        )
        print(f"User token validation result: {result}")
    except Exception as e:
        print(f"Token validation failed: {e}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_service_setup())