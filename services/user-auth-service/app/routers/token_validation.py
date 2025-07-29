"""
Token validation endpoints for inter-service communication.
These endpoints allow other microservices to validate user tokens.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated, List, Optional
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.user import User
from app.services.jwt_service import JWTService
from app.middleware.service_auth import get_current_service, require_validate_tokens
from app.schemas.service_auth import CurrentService

router = APIRouter(prefix="/api/validate", tags=["Token Validation"])
security = HTTPBearer()


class UserTokenValidationRequest(BaseModel):
    """Request schema for validating user tokens."""
    token: str = Field(..., description="User access token to validate")
    required_permissions: Optional[List[str]] = Field(default=None, description="Required permissions")


class UserTokenValidationResponse(BaseModel):
    """Response schema for user token validation."""
    valid: bool = Field(..., description="Whether token is valid")
    user_id: int = Field(..., description="User ID from token")
    email: str = Field(..., description="User email address")
    permissions: List[str] = Field(..., description="User permissions")
    is_active: bool = Field(..., description="Whether user is active")


class UserInfoRequest(BaseModel):
    """Request schema for getting user information."""
    user_id: int = Field(..., description="User ID to retrieve")
    include_roles: bool = Field(default=False, description="Include role information")


class UserInfoResponse(BaseModel):
    """Response schema for user information."""
    user_id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    is_active: bool = Field(..., description="Whether user is active")
    is_verified: bool = Field(..., description="Whether user is verified")
    permissions: List[str] = Field(..., description="User permissions")
    roles: Optional[List[str]] = Field(default=None, description="User role names")


@router.post(
    "/user-token",
    response_model=UserTokenValidationResponse,
    summary="Validate user access token",
    description="Validate a user access token and return user information"
)
async def validate_user_token(
    validation_request: UserTokenValidationRequest,
    current_service: Annotated[CurrentService, Depends(require_validate_tokens)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Validate a user access token and return user information.
    
    This endpoint allows other microservices to validate user tokens
    they receive and get basic user information.
    
    Requires validate:tokens scope.
    
    - **token**: User access token to validate
    - **required_permissions**: Required permissions (optional)
    
    Returns validation result with user information.
    """
    # Verify the user access token
    payload = JWTService.verify_access_token(validation_request.token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired user token"
        )
    
    user_id = payload.get("user_id")
    token_permissions = payload.get("permissions", [])
    
    # Check required permissions if specified
    if validation_request.required_permissions:
        missing_permissions = [
            perm for perm in validation_request.required_permissions
            if perm not in token_permissions
        ]
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(missing_permissions)}"
            )
    
    # Get user from database to verify existence and status
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserTokenValidationResponse(
        valid=True,
        user_id=user.id,
        email=user.email,
        permissions=token_permissions,
        is_active=user.is_active
    )


@router.post(
    "/user-info",
    response_model=UserInfoResponse,
    summary="Get user information",
    description="Get detailed user information by user ID"
)
async def get_user_info(
    user_request: UserInfoRequest,
    current_service: Annotated[CurrentService, Depends(require_validate_tokens)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get detailed user information by user ID.
    
    This endpoint allows other microservices to get user details
    for users they need to work with.
    
    Requires validate:tokens scope.
    
    - **user_id**: ID of the user to retrieve
    - **include_roles**: Whether to include role names
    
    Returns detailed user information.
    """
    # Get user from database
    stmt = select(User).where(User.id == user_request.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user permissions
    permissions = await user.get_permissions(db)
    
    # Get user roles if requested
    roles = None
    if user_request.include_roles:
        from app.models.role import Role, UserRole
        role_stmt = select(Role.name).join(UserRole).where(UserRole.user_id == user.id)
        role_result = await db.execute(role_stmt)
        roles = [row[0] for row in role_result.fetchall()]
    
    return UserInfoResponse(
        user_id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        permissions=permissions,
        roles=roles
    )


@router.get(
    "/permissions/{user_id}",
    response_model=List[str],
    summary="Get user permissions",
    description="Get permissions for a specific user"
)
async def get_user_permissions(
    user_id: int,
    current_service: Annotated[CurrentService, Depends(require_validate_tokens)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get permissions for a specific user.
    
    This is a convenience endpoint for quickly checking user permissions.
    
    Requires validate:tokens scope.
    
    - **user_id**: ID of the user
    
    Returns list of user permissions.
    """
    # Get user from database
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    # Get and return user permissions
    permissions = await user.get_permissions(db)
    return permissions


@router.get(
    "/health",
    summary="Service health check",
    description="Health check endpoint for service monitoring"
)
async def health_check():
    """
    Health check endpoint for monitoring service availability.
    
    This endpoint can be called without authentication to check
    if the token validation service is operational.
    """
    return {
        "status": "healthy",
        "service": "token-validation",
        "available_endpoints": [
            "/api/validate/user-token",
            "/api/validate/user-info", 
            "/api/validate/permissions/{user_id}"
        ]
    }