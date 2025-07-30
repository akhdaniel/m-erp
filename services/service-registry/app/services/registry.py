"""
Service registry business logic.
"""

import uuid
import httpx
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.core.redis import redis_client
from app.schemas.service import (
    ServiceInstance, 
    ServiceRegistration, 
    ServiceUpdate,
    ServiceHealthCheck,
    ServiceDiscoveryResponse,
    HeartbeatRequest,
    RegistryStats
)


class ServiceRegistryService:
    """Service registry business logic."""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=10.0)
    
    async def register_service(self, registration: ServiceRegistration) -> ServiceInstance:
        """Register a new service instance."""
        
        # Generate unique service ID
        service_id = f"{registration.name}-{uuid.uuid4().hex[:8]}"
        
        # Create service instance
        service_instance = ServiceInstance(
            id=service_id,
            name=registration.name,
            host=registration.host,
            port=registration.port,
            health_endpoint=registration.health_endpoint,
            version=registration.version,
            tags=registration.tags,
            metadata=registration.metadata,
            status="unknown",
            last_heartbeat=datetime.utcnow(),
            registered_at=datetime.utcnow()
        )
        
        # Store in Redis
        service_data = service_instance.dict()
        service_data['last_heartbeat'] = service_data['last_heartbeat'].isoformat()
        service_data['registered_at'] = service_data['registered_at'].isoformat()
        
        success = redis_client.register_service(service_id, service_data)
        
        if not success:
            raise RuntimeError(f"Failed to register service {service_id}")
        
        # Perform initial health check
        await self._check_service_health(service_instance)
        
        return service_instance
    
    async def deregister_service(self, service_id: str) -> bool:
        """Deregister a service instance."""
        return redis_client.deregister_service(service_id)
    
    async def get_service(self, service_id: str) -> Optional[ServiceInstance]:
        """Get service by ID."""
        service_data = redis_client.get_service(service_id)
        
        if service_data:
            # Convert datetime strings back to datetime objects
            if 'last_heartbeat' in service_data and service_data['last_heartbeat']:
                service_data['last_heartbeat'] = datetime.fromisoformat(service_data['last_heartbeat'])
            if 'registered_at' in service_data and service_data['registered_at']:
                service_data['registered_at'] = datetime.fromisoformat(service_data['registered_at'])
            
            return ServiceInstance(**service_data)
        
        return None
    
    async def get_all_services(self) -> ServiceDiscoveryResponse:
        """Get all registered services with statistics."""
        services_data = redis_client.get_all_services()
        services = []
        
        healthy_count = 0
        unhealthy_count = 0
        unknown_count = 0
        
        for service_data in services_data:
            # Convert datetime strings
            if 'last_heartbeat' in service_data and service_data['last_heartbeat']:
                service_data['last_heartbeat'] = datetime.fromisoformat(service_data['last_heartbeat'])
            if 'registered_at' in service_data and service_data['registered_at']:
                service_data['registered_at'] = datetime.fromisoformat(service_data['registered_at'])
            
            service = ServiceInstance(**service_data)
            services.append(service)
            
            # Count by status
            if service.status == "healthy":
                healthy_count += 1
            elif service.status == "unhealthy":
                unhealthy_count += 1
            else:
                unknown_count += 1
        
        return ServiceDiscoveryResponse(
            services=services,
            total=len(services),
            healthy_count=healthy_count,
            unhealthy_count=unhealthy_count,
            unknown_count=unknown_count
        )
    
    async def get_services_by_name(self, service_name: str) -> List[ServiceInstance]:
        """Get all instances of a service by name."""
        services_data = redis_client.get_services_by_name(service_name)
        services = []
        
        for service_data in services_data:
            # Convert datetime strings
            if 'last_heartbeat' in service_data and service_data['last_heartbeat']:
                service_data['last_heartbeat'] = datetime.fromisoformat(service_data['last_heartbeat'])
            if 'registered_at' in service_data and service_data['registered_at']:
                service_data['registered_at'] = datetime.fromisoformat(service_data['registered_at'])
            
            services.append(ServiceInstance(**service_data))
        
        return services
    
    async def update_service(self, service_id: str, update: ServiceUpdate) -> Optional[ServiceInstance]:
        """Update service information."""
        service = await self.get_service(service_id)
        
        if not service:
            return None
        
        # Update fields
        if update.status is not None:
            service.status = update.status
        if update.tags is not None:
            service.tags = update.tags
        if update.metadata is not None:
            service.metadata.update(update.metadata)
        
        # Store updated service
        service_data = service.dict()
        service_data['last_heartbeat'] = service_data['last_heartbeat'].isoformat()
        service_data['registered_at'] = service_data['registered_at'].isoformat()
        
        success = redis_client.register_service(service_id, service_data)
        
        return service if success else None
    
    async def heartbeat(self, heartbeat: HeartbeatRequest) -> bool:
        """Process service heartbeat."""
        service = await self.get_service(heartbeat.service_id)
        
        if not service:
            return False
        
        # Update heartbeat timestamp and status
        service.last_heartbeat = datetime.utcnow()
        if heartbeat.status:
            service.status = heartbeat.status
        if heartbeat.metadata:
            service.metadata.update(heartbeat.metadata)
        
        # Store updated service
        service_data = service.dict()
        service_data['last_heartbeat'] = service_data['last_heartbeat'].isoformat()
        service_data['registered_at'] = service_data['registered_at'].isoformat()
        
        return redis_client.register_service(heartbeat.service_id, service_data)
    
    async def check_all_services_health(self) -> List[ServiceHealthCheck]:
        """Check health of all registered services."""
        services_response = await self.get_all_services()
        health_checks = []
        
        # Create tasks for concurrent health checks
        tasks = []
        for service in services_response.services:
            tasks.append(self._check_service_health(service))
        
        # Execute health checks concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Get updated service statuses
        services_response = await self.get_all_services()
        for service in services_response.services:
            health_check = ServiceHealthCheck(
                service_id=service.id,
                status=service.status,
                last_checked=datetime.utcnow(),
                health_data=service.metadata.get('health_data', {})
            )
            health_checks.append(health_check)
        
        return health_checks
    
    async def _check_service_health(self, service: ServiceInstance) -> None:
        """Check health of a single service."""
        try:
            health_url = f"http://{service.host}:{service.port}{service.health_endpoint}"
            
            start_time = datetime.utcnow()
            response = await self.http_client.get(health_url)
            end_time = datetime.utcnow()
            
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                status = "healthy"
                health_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            else:
                status = "unhealthy"
                health_data = {"error": f"HTTP {response.status_code}"}
            
            # Update service status
            service.status = status
            service.metadata['health_data'] = health_data
            service.metadata['response_time_ms'] = response_time_ms
            
        except Exception as e:
            service.status = "unhealthy"
            service.metadata['health_data'] = {"error": str(e)}
        
        # Store updated service status
        service_data = service.dict()
        service_data['last_heartbeat'] = service_data['last_heartbeat'].isoformat()
        service_data['registered_at'] = service_data['registered_at'].isoformat()
        
        redis_client.register_service(service.id, service_data)
    
    async def get_registry_stats(self) -> RegistryStats:
        """Get service registry statistics."""
        services_response = await self.get_all_services()
        
        # Count services by name
        services_by_name = {}
        for service in services_response.services:
            services_by_name[service.name] = services_by_name.get(service.name, 0) + 1
        
        return RegistryStats(
            total_services=services_response.total,
            healthy_services=services_response.healthy_count,
            unhealthy_services=services_response.unhealthy_count,
            unknown_services=services_response.unknown_count,
            services_by_name=services_by_name,
            last_cleanup=None,  # Will be implemented with cleanup task
            registry_uptime=None  # Will be implemented with startup tracking
        )
    
    async def cleanup_expired_services(self) -> int:
        """Remove expired services."""
        return redis_client.cleanup_expired_services()
    
    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()


# Global service registry instance
registry_service = ServiceRegistryService()