"""
Service registry API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from app.schemas.service import (
    ServiceInstance,
    ServiceRegistration,
    ServiceUpdate,
    ServiceDiscoveryResponse,
    ServiceHealthCheck,
    HeartbeatRequest,
    RegistryStats
)
from app.services.registry import registry_service

router = APIRouter(prefix="/services", tags=["services"])


@router.post("/register", response_model=ServiceInstance, status_code=status.HTTP_201_CREATED)
async def register_service(registration: ServiceRegistration):
    """
    Register a new service instance.
    
    This endpoint allows services to register themselves in the service registry.
    The service will be assigned a unique ID and will be available for discovery.
    """
    try:
        service_instance = await registry_service.register_service(registration)
        return service_instance
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register service: {str(e)}"
        )


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deregister_service(service_id: str):
    """
    Deregister a service instance.
    
    Removes the service from the registry. The service will no longer be
    discoverable by other services.
    """
    success = await registry_service.deregister_service(service_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )


@router.get("/{service_id}", response_model=ServiceInstance)
async def get_service(service_id: str):
    """
    Get service instance by ID.
    
    Returns detailed information about a specific service instance.
    """
    service = await registry_service.get_service(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return service


@router.get("/", response_model=ServiceDiscoveryResponse)
async def discover_services(
    name: Optional[str] = Query(None, description="Filter by service name")
):
    """
    Discover all registered services.
    
    Returns a list of all registered services with their health status
    and statistics. Can be filtered by service name.
    """
    if name:
        services = await registry_service.get_services_by_name(name)
        healthy_count = sum(1 for s in services if s.status == "healthy")
        unhealthy_count = sum(1 for s in services if s.status == "unhealthy")
        unknown_count = sum(1 for s in services if s.status == "unknown")
        
        return ServiceDiscoveryResponse(
            services=services,
            total=len(services),
            healthy_count=healthy_count,
            unhealthy_count=unhealthy_count,
            unknown_count=unknown_count
        )
    else:
        return await registry_service.get_all_services()


@router.put("/{service_id}", response_model=ServiceInstance)
async def update_service(service_id: str, update: ServiceUpdate):
    """
    Update service instance information.
    
    Allows updating service metadata, tags, and status.
    """
    service = await registry_service.update_service(service_id, update)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return service


@router.post("/heartbeat", status_code=status.HTTP_200_OK)
async def service_heartbeat(heartbeat: HeartbeatRequest):
    """
    Service heartbeat endpoint.
    
    Services should call this endpoint periodically to indicate they are alive.
    This helps the registry track service availability and remove stale entries.
    """
    success = await registry_service.heartbeat(heartbeat)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return {"message": "Heartbeat received"}


@router.get("/health/check-all", response_model=List[ServiceHealthCheck])
async def check_all_services_health():
    """
    Check health of all registered services.
    
    Performs health checks on all registered services and returns their status.
    This is useful for monitoring and debugging service availability.
    """
    return await registry_service.check_all_services_health()


@router.get("/stats", response_model=RegistryStats)
async def get_registry_stats():
    """
    Get service registry statistics.
    
    Returns overall statistics about the service registry including
    service counts, health status distribution, and other metrics.
    """
    return await registry_service.get_registry_stats()


@router.post("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_expired_services():
    """
    Clean up expired services.
    
    Removes services that haven't sent heartbeats within the configured TTL.
    This endpoint can be called manually or by automated cleanup tasks.
    """
    removed_count = await registry_service.cleanup_expired_services()
    return {"message": f"Removed {removed_count} expired services"}