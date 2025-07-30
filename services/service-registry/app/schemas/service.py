"""
Service registry schemas for request/response models.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ServiceInstance(BaseModel):
    """Service instance registration data."""
    
    id: str = Field(..., description="Unique service instance ID")
    name: str = Field(..., description="Service name")
    host: str = Field(..., description="Service host/IP")
    port: int = Field(..., description="Service port")
    health_endpoint: str = Field(default="/health", description="Health check endpoint path")
    version: str = Field(default="1.0.0", description="Service version")
    status: str = Field(default="unknown", description="Service health status")
    tags: List[str] = Field(default_factory=list, description="Service tags for categorization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional service metadata")
    last_heartbeat: Optional[datetime] = Field(default=None, description="Last heartbeat timestamp")
    registered_at: Optional[datetime] = Field(default=None, description="Registration timestamp")


class ServiceRegistration(BaseModel):
    """Service registration request."""
    
    name: str = Field(..., description="Service name")
    host: str = Field(..., description="Service host/IP")
    port: int = Field(..., description="Service port")
    health_endpoint: str = Field(default="/health", description="Health check endpoint path")
    version: str = Field(default="1.0.0", description="Service version")
    tags: List[str] = Field(default_factory=list, description="Service tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Service metadata")


class ServiceUpdate(BaseModel):
    """Service update request."""
    
    status: Optional[str] = Field(default=None, description="Service status")
    tags: Optional[List[str]] = Field(default=None, description="Service tags")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Service metadata")


class ServiceHealthCheck(BaseModel):
    """Service health check result."""
    
    service_id: str
    status: str  # healthy, unhealthy, unknown
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    last_checked: datetime
    health_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ServiceDiscoveryResponse(BaseModel):
    """Service discovery response."""
    
    services: List[ServiceInstance]
    total: int
    healthy_count: int
    unhealthy_count: int
    unknown_count: int


class HeartbeatRequest(BaseModel):
    """Heartbeat request from service."""
    
    service_id: str
    status: Optional[str] = Field(default="healthy", description="Current service status")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Updated metadata")


class RegistryStats(BaseModel):
    """Service registry statistics."""
    
    total_services: int
    healthy_services: int
    unhealthy_services: int
    unknown_services: int
    services_by_name: Dict[str, int]
    last_cleanup: Optional[datetime]
    registry_uptime: Optional[str]