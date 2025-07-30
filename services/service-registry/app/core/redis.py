"""
Redis connection and utilities for service registry.
"""

import json
import redis
from typing import Optional, Dict, Any, List
from app.core.config import settings


class RedisClient:
    """Redis client for service registry operations."""
    
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )
    
    async def ping(self) -> bool:
        """Test Redis connection."""
        try:
            return self.redis.ping()
        except Exception:
            return False
    
    def register_service(self, service_id: str, service_data: Dict[str, Any]) -> bool:
        """Register a service in Redis."""
        try:
            key = f"{settings.REGISTRY_KEY_PREFIX}:{service_id}"
            service_json = json.dumps(service_data)
            
            # Set service data with TTL
            self.redis.setex(key, settings.SERVICE_TTL, service_json)
            
            # Add to services set for enumeration
            self.redis.sadd(f"{settings.REGISTRY_KEY_PREFIX}:all", service_id)
            
            return True
        except Exception as e:
            print(f"Error registering service {service_id}: {e}")
            return False
    
    def deregister_service(self, service_id: str) -> bool:
        """Remove a service from registry."""
        try:
            key = f"{settings.REGISTRY_KEY_PREFIX}:{service_id}"
            
            # Remove service data
            self.redis.delete(key)
            
            # Remove from services set
            self.redis.srem(f"{settings.REGISTRY_KEY_PREFIX}:all", service_id)
            
            return True
        except Exception as e:
            print(f"Error deregistering service {service_id}: {e}")
            return False
    
    def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get service data by ID."""
        try:
            key = f"{settings.REGISTRY_KEY_PREFIX}:{service_id}"
            service_json = self.redis.get(key)
            
            if service_json:
                return json.loads(service_json)
            return None
        except Exception as e:
            print(f"Error getting service {service_id}: {e}")
            return None
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all registered services."""
        try:
            service_ids = self.redis.smembers(f"{settings.REGISTRY_KEY_PREFIX}:all")
            services = []
            
            for service_id in service_ids:
                service_data = self.get_service(service_id)
                if service_data:
                    services.append(service_data)
                else:
                    # Clean up orphaned service ID
                    self.redis.srem(f"{settings.REGISTRY_KEY_PREFIX}:all", service_id)
            
            return services
        except Exception as e:
            print(f"Error getting all services: {e}")
            return []
    
    def get_services_by_name(self, service_name: str) -> List[Dict[str, Any]]:
        """Get all instances of a service by name."""
        all_services = self.get_all_services()
        return [s for s in all_services if s.get('name') == service_name]
    
    def update_service_heartbeat(self, service_id: str) -> bool:
        """Update service heartbeat timestamp."""
        try:
            key = f"{settings.REGISTRY_KEY_PREFIX}:{service_id}"
            service_data = self.get_service(service_id)
            
            if service_data:
                import datetime
                service_data['last_heartbeat'] = datetime.datetime.utcnow().isoformat()
                return self.register_service(service_id, service_data)
            
            return False
        except Exception as e:
            print(f"Error updating heartbeat for {service_id}: {e}")
            return False
    
    def cleanup_expired_services(self) -> int:
        """Remove expired services that haven't sent heartbeats."""
        try:
            import datetime
            current_time = datetime.datetime.utcnow()
            expired_count = 0
            
            for service in self.get_all_services():
                try:
                    last_heartbeat = datetime.datetime.fromisoformat(service['last_heartbeat'])
                    seconds_since_heartbeat = (current_time - last_heartbeat).total_seconds()
                    
                    if seconds_since_heartbeat > settings.SERVICE_TTL:
                        self.deregister_service(service['id'])
                        expired_count += 1
                        print(f"Removed expired service: {service['id']}")
                
                except (KeyError, ValueError):
                    # Remove services with invalid heartbeat data
                    self.deregister_service(service['id'])
                    expired_count += 1
            
            return expired_count
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return 0


# Global Redis client instance
redis_client = RedisClient()