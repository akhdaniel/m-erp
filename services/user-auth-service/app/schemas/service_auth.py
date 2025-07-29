"""
Service authentication schemas for inter-service communication.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ServiceTokenRequest(BaseModel):
    """Request schema for service authentication token."""
    service_name: str = Field(..., min_length=1, max_length=100, description="Name of the requesting service")
    service_secret: str = Field(..., min_length=32, description="Service secret for authentication")
    scopes: Optional[List[str]] = Field(default=None, description="Requested service scopes")


class ServiceTokenResponse(BaseModel):
    """Response schema for service authentication token."""
    access_token: str = Field(..., description="Service access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    scopes: List[str] = Field(..., description="Granted service scopes")


class ServiceValidationRequest(BaseModel):
    """Request schema for validating service tokens."""
    token: str = Field(..., description="Service token to validate")
    required_scopes: Optional[List[str]] = Field(default=None, description="Required scopes for operation")


class ServiceValidationResponse(BaseModel):
    """Response schema for service token validation."""
    valid: bool = Field(..., description="Whether token is valid")
    service_name: str = Field(..., description="Name of the service")
    scopes: List[str] = Field(..., description="Token scopes")
    expires_at: datetime = Field(..., description="Token expiration time")


class ServiceRegistrationRequest(BaseModel):
    """Request schema for registering a new service."""
    service_name: str = Field(..., min_length=1, max_length=100, description="Unique service name")
    service_description: str = Field(..., min_length=1, max_length=500, description="Service description")
    allowed_scopes: List[str] = Field(..., description="Scopes this service is allowed to request")
    callback_urls: Optional[List[str]] = Field(default=None, description="Service callback URLs")


class ServiceRegistrationResponse(BaseModel):
    """Response schema for service registration."""
    service_id: int = Field(..., description="Generated service ID")
    service_name: str = Field(..., description="Service name")
    service_secret: str = Field(..., description="Generated service secret")
    allowed_scopes: List[str] = Field(..., description="Allowed scopes")
    created_at: datetime = Field(..., description="Service registration time")


class ServiceInfo(BaseModel):
    """Schema for service information."""
    service_id: int = Field(..., description="Service ID")
    service_name: str = Field(..., description="Service name")
    service_description: str = Field(..., description="Service description")
    allowed_scopes: List[str] = Field(..., description="Allowed scopes")
    is_active: bool = Field(..., description="Whether service is active")
    created_at: datetime = Field(..., description="Service creation time")
    last_used: Optional[datetime] = Field(default=None, description="Last token request time")


class ServiceListResponse(BaseModel):
    """Response schema for listing services."""
    services: List[ServiceInfo] = Field(..., description="List of registered services")
    total: int = Field(..., description="Total number of services")


class CurrentService(BaseModel):
    """Schema for current authenticated service."""
    service_id: int = Field(..., description="Service ID")
    service_name: str = Field(..., description="Service name")
    scopes: List[str] = Field(..., description="Service scopes")