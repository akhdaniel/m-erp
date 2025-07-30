"""
Service Registry Client Library

This client can be used by other M-ERP services to register themselves
and send heartbeats to the service registry.
"""

import asyncio
import httpx
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List


class ServiceRegistryClient:
    """Client for interacting with the service registry."""
    
    def __init__(
        self,
        registry_url: str = "http://service-registry:8000",
        service_name: str = "",
        service_host: str = "localhost",
        service_port: int = 8000,
        health_endpoint: str = "/health",
        version: str = "1.0.0",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.registry_url = registry_url.rstrip('/')
        self.service_name = service_name
        self.service_host = service_host
        self.service_port = service_port
        self.health_endpoint = health_endpoint
        self.version = version
        self.tags = tags or []
        self.metadata = metadata or {}
        self.service_id: Optional[str] = None
        self.http_client = httpx.AsyncClient(timeout=10.0)
        self.logger = logging.getLogger(f"service-registry-client.{service_name}")
        
        # Background task handles
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def register(self) -> bool:
        """Register this service with the registry."""
        try:
            registration_data = {
                "name": self.service_name,
                "host": self.service_host,
                "port": self.service_port,
                "health_endpoint": self.health_endpoint,
                "version": self.version,
                "tags": self.tags,
                "metadata": self.metadata
            }
            
            response = await self.http_client.post(
                f"{self.registry_url}/api/v1/services/register",
                json=registration_data
            )
            
            if response.status_code == 201:
                service_data = response.json()
                self.service_id = service_data["id"]
                self.logger.info(f"Successfully registered service with ID: {self.service_id}")
                
                # Start heartbeat task
                await self.start_heartbeat()
                return True
            else:
                self.logger.error(f"Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return False
    
    async def deregister(self) -> bool:
        """Deregister this service from the registry."""
        if not self.service_id:
            self.logger.warning("Cannot deregister: service not registered")
            return False
        
        try:
            # Stop heartbeat
            await self.stop_heartbeat()
            
            response = await self.http_client.delete(
                f"{self.registry_url}/api/v1/services/{self.service_id}"
            )
            
            if response.status_code == 204:
                self.logger.info(f"Successfully deregistered service {self.service_id}")
                self.service_id = None
                return True
            else:
                self.logger.error(f"Deregistration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Deregistration error: {e}")
            return False
    
    async def heartbeat(self, status: str = "healthy", updated_metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Send heartbeat to the registry."""
        if not self.service_id:
            self.logger.warning("Cannot send heartbeat: service not registered")
            return False
        
        try:
            heartbeat_data = {
                "service_id": self.service_id,
                "status": status,
                "metadata": updated_metadata or {}
            }
            
            response = await self.http_client.post(
                f"{self.registry_url}/api/v1/services/heartbeat",
                json=heartbeat_data
            )
            
            if response.status_code == 200:
                self.logger.debug(f"Heartbeat sent successfully for {self.service_id}")
                return True
            else:
                self.logger.error(f"Heartbeat failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Heartbeat error: {e}")
            return False
    
    async def discover_services(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Discover services from the registry."""
        try:
            url = f"{self.registry_url}/api/v1/services"
            params = {}
            if service_name:
                params["name"] = service_name
            
            response = await self.http_client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("services", [])
            else:
                self.logger.error(f"Service discovery failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.logger.error(f"Service discovery error: {e}")
            return []
    
    async def get_service_url(self, service_name: str) -> Optional[str]:
        """Get the URL for a healthy service instance."""
        services = await self.discover_services(service_name)
        
        # Find first healthy service
        for service in services:
            if service.get("status") == "healthy":
                host = service.get("host")
                port = service.get("port")
                if host and port:
                    return f"http://{host}:{port}"
        
        self.logger.warning(f"No healthy instances found for service: {service_name}")
        return None
    
    async def start_heartbeat(self, interval: int = 30) -> None:
        """Start periodic heartbeat task."""
        if self._heartbeat_task:
            await self.stop_heartbeat()
        
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop(interval))
        self.logger.info(f"Started heartbeat task with {interval}s interval")
    
    async def stop_heartbeat(self) -> None:
        """Stop heartbeat task."""
        self._running = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None
            self.logger.info("Stopped heartbeat task")
    
    async def _heartbeat_loop(self, interval: int) -> None:
        """Background heartbeat loop."""
        while self._running:
            try:
                await self.heartbeat()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(interval)
    
    async def close(self) -> None:
        """Close the client and cleanup resources."""
        await self.stop_heartbeat()
        await self.http_client.aclose()
        self.logger.info("Service registry client closed")


# Convenience function for FastAPI applications
def create_service_registry_client(
    service_name: str,
    service_host: str = "localhost",
    service_port: int = 8000,
    registry_url: str = "http://service-registry:8000",
    **kwargs
) -> ServiceRegistryClient:
    """Create a service registry client with common defaults."""
    return ServiceRegistryClient(
        registry_url=registry_url,
        service_name=service_name,
        service_host=service_host,
        service_port=service_port,
        **kwargs
    )


# Example usage for FastAPI lifespan
async def register_service_with_lifespan(
    app,
    service_name: str,
    service_host: str,
    service_port: int,
    registry_url: str = "http://service-registry:8000"
):
    """Example lifespan context manager for FastAPI services."""
    client = create_service_registry_client(
        service_name=service_name,
        service_host=service_host,
        service_port=service_port,
        registry_url=registry_url
    )
    
    # Startup
    success = await client.register()
    if success:
        print(f"✓ Service {service_name} registered with service registry")
    else:
        print(f"✗ Failed to register service {service_name}")
    
    try:
        yield
    finally:
        # Shutdown
        await client.deregister()
        await client.close()
        print(f"✓ Service {service_name} deregistered from service registry")