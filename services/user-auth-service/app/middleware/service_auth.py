"""
Service authentication middleware for inter-service communication.
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List, Optional

from app.core.database import get_db
from app.services.service_auth import ServiceAuthService
from app.schemas.service_auth import CurrentService


security = HTTPBearer()


async def get_current_service(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> CurrentService:
    """
    Dependency to extract and validate current service from service token.
    """
    token = credentials.credentials
    
    # Validate service token
    is_valid, payload = await ServiceAuthService.validate_service_token(db, token)
    
    if not is_valid or payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired service token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if service is still active
    service = await ServiceAuthService.get_service_by_id(db, payload["service_id"])
    if not service or not service.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Service not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return CurrentService(
        service_id=payload["service_id"],
        service_name=payload["service_name"],
        scopes=payload["scopes"]
    )


def require_service_scopes(required_scopes: List[str]):
    """
    Decorator factory to create a dependency that requires specific service scopes.
    
    Args:
        required_scopes: List of required service scopes
        
    Returns:
        Dependency function that validates service has required scopes
    """
    async def check_service_scopes(
        current_service: Annotated[CurrentService, Depends(get_current_service)]
    ) -> CurrentService:
        """Check if current service has required scopes."""
        missing_scopes = [scope for scope in required_scopes 
                         if scope not in current_service.scopes]
        
        if missing_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scopes: {', '.join(missing_scopes)}"
            )
        
        return current_service
    
    return check_service_scopes


def require_service_scope(required_scope: str):
    """
    Convenience function for requiring a single service scope.
    
    Args:
        required_scope: Single required service scope
        
    Returns:
        Dependency function that validates service has required scope
    """
    return require_service_scopes([required_scope])


# Pre-defined scope dependencies for common operations
require_read_users = require_service_scope("read:users")
require_write_users = require_service_scope("write:users")
require_read_roles = require_service_scope("read:roles")
require_write_roles = require_service_scope("write:roles")
require_validate_tokens = require_service_scope("validate:tokens")
require_admin_users = require_service_scope("admin:users")
require_admin_services = require_service_scope("admin:services")


async def validate_service_token_endpoint(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
    required_scopes: Optional[List[str]] = None
) -> dict:
    """
    Endpoint helper for validating service tokens with optional scope checking.
    This can be used by other services to validate tokens they receive.
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
        required_scopes: Optional list of required scopes
        
    Returns:
        dict: Token validation result with service info
        
    Raises:
        HTTPException: If token is invalid or missing required scopes
    """
    token = credentials.credentials
    
    # Validate token
    is_valid, payload = await ServiceAuthService.validate_service_token(
        db, token, required_scopes
    )
    
    if not is_valid or payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service token or insufficient scopes",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get service info
    service = await ServiceAuthService.get_service_by_id(db, payload["service_id"])
    if not service or not service.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Service not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "valid": True,
        "service_id": payload["service_id"],
        "service_name": payload["service_name"],
        "scopes": payload["scopes"],
        "expires_at": payload.get("exp")
    }