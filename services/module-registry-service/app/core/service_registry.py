"""
Service registry integration for Module Registry Service
"""
import httpx
import asyncio
import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class ServiceRegistryClient:
    """Client for service registry communication"""
    
    def __init__(self):
        self.service_registry_url = settings.service_registry_url
        self.service_name = settings.service_name
        self.service_host = settings.service_host
        self.service_port = settings.service_port
        self.registration_data = {
            "name": self.service_name,
            "host": self.service_host,
            "port": self.service_port,
            "status": "healthy",
            "metadata": {
                "version": settings.app_version,
                "description": "Module Registry Service for XERPIUM Extension System",
                "endpoints": [
                    f"http://{self.service_host}:{self.service_port}/modules",
                    f"http://{self.service_host}:{self.service_port}/installations",
                    f"http://{self.service_host}:{self.service_port}/health"
                ]
            }
        }
    
    async def register_service(self) -> bool:
        """Register this service with the service registry"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.service_registry_url}/services/register",
                    json=self.registration_data,
                    timeout=5.0
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Successfully registered {self.service_name} with service registry")
                    return True
                else:
                    logger.error(f"Failed to register service: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to service registry: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during service registration: {e}")
            return False
    
    async def unregister_service(self) -> bool:
        """Unregister this service from the service registry"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.service_registry_url}/services/{self.service_name}",
                    timeout=5.0
                )
                
                if response.status_code in [200, 204]:
                    logger.info(f"Successfully unregistered {self.service_name} from service registry")
                    return True
                else:
                    logger.error(f"Failed to unregister service: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to service registry: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during service unregistration: {e}")
            return False
    
    async def update_service_status(self, status: str, metadata: Dict[str, Any] = None) -> bool:
        """Update service status in the registry"""
        try:
            update_data = {
                "status": status,
                "last_heartbeat": None  # Will be set by service registry
            }
            
            if metadata:
                update_data["metadata"] = {**self.registration_data["metadata"], **metadata}
            
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.service_registry_url}/services/{self.service_name}",
                    json=update_data,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    logger.debug(f"Updated {self.service_name} status to {status}")
                    return True
                else:
                    logger.error(f"Failed to update service status: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to service registry: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during status update: {e}")
            return False
    
    async def get_service(self, service_name: str) -> Dict[str, Any] | None:
        """Get service information from registry"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.service_registry_url}/services/{service_name}",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"Service {service_name} not found in registry")
                    return None
                else:
                    logger.error(f"Failed to get service info: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to service registry: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting service info: {e}")
            return None
    
    async def list_services(self) -> list[Dict[str, Any]]:
        """List all services in the registry"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.service_registry_url}/services",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return response.json().get("services", [])
                else:
                    logger.error(f"Failed to list services: {response.status_code} - {response.text}")
                    return []
                    
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to service registry: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing services: {e}")
            return []
    
    async def start_heartbeat(self, interval: int = 30):
        """Start periodic heartbeat to service registry"""
        while True:
            try:
                await self.update_service_status("healthy")
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                logger.info("Heartbeat task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in heartbeat: {e}")
                await asyncio.sleep(interval)


# Global service registry client instance
service_registry_client = ServiceRegistryClient()