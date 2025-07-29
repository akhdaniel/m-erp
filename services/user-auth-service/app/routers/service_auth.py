"""
Service authentication API endpoints for inter-service communication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List, Optional

from app.core.database import get_db
from app.services.service_auth import ServiceAuthService
from app.middleware.service_auth import (
    get_current_service, 
    require_admin_services,
    validate_service_token_endpoint
)
from app.schemas.service_auth import (
    ServiceTokenRequest,
    ServiceTokenResponse,
    ServiceValidationRequest,
    ServiceValidationResponse,
    ServiceRegistrationRequest,
    ServiceRegistrationResponse,
    ServiceInfo,
    ServiceListResponse,
    CurrentService
)
from app.schemas.auth import MessageResponse

router = APIRouter(prefix="/api/services", tags=["Service Authentication"])
security = HTTPBearer()


@router.post(
    "/register",
    response_model=ServiceRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new service",
    description="Register a new microservice for inter-service authentication"
)
async def register_service(
    service_data: ServiceRegistrationRequest,
    current_service: Annotated[CurrentService, Depends(require_admin_services)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Register a new service for inter-service authentication.
    
    Requires admin:services scope.
    
    - **service_name**: Unique service name
    - **service_description**: Description of the service
    - **allowed_scopes**: List of scopes the service can request
    - **callback_urls**: Optional callback URLs for the service
    
    Returns the service information and generated secret.
    """
    try:
        service, service_secret = await ServiceAuthService.register_service(
            db,
            service_data.service_name,
            service_data.service_description,
            service_data.allowed_scopes
        )
        
        return ServiceRegistrationResponse(
            service_id=service.id,
            service_name=service.service_name,
            service_secret=service_secret,
            allowed_scopes=service.allowed_scopes,
            created_at=service.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/token",
    response_model=ServiceTokenResponse,
    summary="Get service access token",
    description="Authenticate service and get access token"
)
async def get_service_token(
    token_request: ServiceTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Authenticate a service and return an access token.
    
    - **service_name**: Name of the service
    - **service_secret**: Service secret for authentication
    - **scopes**: Requested scopes (optional, defaults to all allowed scopes)
    
    Returns access token with granted scopes.
    """
    try:
        service, access_token, granted_scopes = await ServiceAuthService.authenticate_service(
            db,
            token_request.service_name,
            token_request.service_secret,
            token_request.scopes
        )
        
        return ServiceTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ServiceAuthService.SERVICE_TOKEN_EXPIRE_HOURS * 3600,
            scopes=granted_scopes
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/validate",
    response_model=ServiceValidationResponse,
    summary="Validate service token",
    description="Validate a service token and return service information"
)
async def validate_service_token(
    validation_request: ServiceValidationRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Validate a service token and return service information.
    
    This endpoint can be used by other services to validate tokens they receive.
    
    - **token**: Service token to validate
    - **required_scopes**: Required scopes for the operation (optional)
    
    Returns validation result with service information.
    """
    is_valid, payload = await ServiceAuthService.validate_service_token(
        db,
        validation_request.token,
        validation_request.required_scopes
    )
    
    if not is_valid or payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service token or insufficient scopes"
        )
    
    # Convert timestamp to datetime
    from datetime import datetime, timezone
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    
    return ServiceValidationResponse(
        valid=True,
        service_name=payload["service_name"],
        scopes=payload["scopes"],
        expires_at=expires_at
    )


@router.get(
    "/list",
    response_model=ServiceListResponse,
    summary="List registered services",
    description="Get list of all registered services"
)
async def list_services(
    current_service: Annotated[CurrentService, Depends(require_admin_services)],
    db: Annotated[AsyncSession, Depends(get_db)],
    active_only: bool = True
):
    """
    List all registered services.
    
    Requires admin:services scope.
    
    - **active_only**: Whether to return only active services (default: true)
    
    Returns list of service information.
    """
    services = await ServiceAuthService.list_services(db, active_only)
    
    service_infos = []
    for service in services:
        service_infos.append(ServiceInfo(
            service_id=service.id,
            service_name=service.service_name,
            service_description=service.service_description,
            allowed_scopes=service.allowed_scopes,
            is_active=service.is_active,
            created_at=service.created_at,
            last_used=service.last_used
        ))
    
    return ServiceListResponse(
        services=service_infos,
        total=len(service_infos)
    )


@router.get(
    "/{service_id}",
    response_model=ServiceInfo,
    summary="Get service information",
    description="Get detailed information about a specific service"
)
async def get_service_info(
    service_id: int,
    current_service: Annotated[CurrentService, Depends(require_admin_services)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get detailed information about a specific service.
    
    Requires admin:services scope.
    
    - **service_id**: ID of the service to retrieve
    
    Returns service information.
    """
    service = await ServiceAuthService.get_service_by_id(db, service_id)
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return ServiceInfo(
        service_id=service.id,
        service_name=service.service_name,
        service_description=service.service_description,
        allowed_scopes=service.allowed_scopes,
        is_active=service.is_active,
        created_at=service.created_at,
        last_used=service.last_used
    )


@router.post(
    "/{service_id}/status",
    response_model=ServiceInfo,
    summary="Update service status",
    description="Activate or deactivate a service"
)
async def update_service_status(
    service_id: int,
    is_active: bool,
    current_service: Annotated[CurrentService, Depends(require_admin_services)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update service active status.
    
    Requires admin:services scope.
    
    - **service_id**: ID of the service to update
    - **is_active**: New active status
    
    Returns updated service information.
    """
    service = await ServiceAuthService.update_service_status(db, service_id, is_active)
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return ServiceInfo(
        service_id=service.id,
        service_name=service.service_name,
        service_description=service.service_description,
        allowed_scopes=service.allowed_scopes,
        is_active=service.is_active,
        created_at=service.created_at,
        last_used=service.last_used
    )


@router.post(
    "/{service_id}/revoke-tokens",
    response_model=MessageResponse,
    summary="Revoke all service tokens",
    description="Revoke all active tokens for a service"
)
async def revoke_service_tokens(
    service_id: int,
    current_service: Annotated[CurrentService, Depends(require_admin_services)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Revoke all active tokens for a service.
    
    Requires admin:services scope.
    
    - **service_id**: ID of the service whose tokens to revoke
    
    Returns success message with count of revoked tokens.
    """
    service = await ServiceAuthService.get_service_by_id(db, service_id)
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    revoked_count = await ServiceAuthService.revoke_all_service_tokens(db, service_id)
    
    return MessageResponse(
        message=f"Successfully revoked {revoked_count} token(s) for service '{service.service_name}'"
    )


@router.get(
    "/me",
    response_model=ServiceInfo,
    summary="Get current service info",
    description="Get information about the currently authenticated service"
)
async def get_current_service_info(
    current_service: Annotated[CurrentService, Depends(get_current_service)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get information about the currently authenticated service.
    
    Requires valid service token.
    
    Returns current service information.
    """
    service = await ServiceAuthService.get_service_by_id(db, current_service.service_id)
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    return ServiceInfo(
        service_id=service.id,
        service_name=service.service_name,
        service_description=service.service_description,
        allowed_scopes=service.allowed_scopes,
        is_active=service.is_active,
        created_at=service.created_at,
        last_used=service.last_used
    )