# Integration Patterns for XERPIUM

> **Comprehensive guide to service communication, discovery, and integration patterns in XERPIUM**
>
> Version: 1.0.0  
> Last Updated: August 8, 2025

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Service Discovery](#service-discovery)
3. [Event-Driven Communication](#event-driven-communication)
4. [Menu Registration](#menu-registration)
5. [UI Component Registration](#ui-component-registration)
6. [Redis Messaging](#redis-messaging)
7. [Service Authentication](#service-authentication)
8. [Multi-Company Integration](#multi-company-integration)
9. [Error Handling and Resilience](#error-handling-and-resilience)
10. [Monitoring and Observability](#monitoring-and-observability)

## Architecture Overview

XERPIUM follows a **plugin-within-service** microservices architecture with event-driven communication. Services are loosely coupled and communicate through:

- **Service Registry**: Centralized service discovery
- **Redis Streams**: Event-driven messaging
- **REST APIs**: Synchronous communication when needed
- **Menu System**: Dynamic UI integration
- **UI Registry**: Component registration and discovery

### Integration Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   New Service   │    │ Service Registry│    │ Existing System │
│                 │    │                 │    │                 │
│ 1. Register     │───▶│ 2. Discovery    │◀───│ 3. Find Service │
│ 2. Publish Menu │    │                 │    │                 │
│ 3. Register UI  │    └─────────────────┘    └─────────────────┘
│ 4. Publish      │             │                       │
│    Events       │             ▼                       ▼
└─────────────────┘    ┌─────────────────┐    ┌─────────────────┐
        │              │ Menu/Access     │    │ Event Handlers  │
        │              │ Service         │    │                 │
        │              └─────────────────┘    └─────────────────┘
        ▼
┌─────────────────┐
│ Redis Message   │
│ Bus             │
└─────────────────┘
```

## Service Discovery

### 1. Service Registry Integration

Every service registers itself with the service registry on startup for automatic discovery.

#### Service Registration

**registration.py**
```python
"""Service registration with XERPIUM service registry."""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class ServiceRegistry:
    """Service registry client for registration and discovery."""
    
    def __init__(self, registry_url: str):
        self.registry_url = registry_url
        self.service_info = None
    
    async def register_service(self, service_info: Dict[str, Any]) -> bool:
        """Register this service with the registry."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.registry_url}/api/v1/services/register",
                    json=service_info,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 201:
                        self.service_info = service_info
                        logger.info(f"Successfully registered service: {service_info['name']}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Service registration failed: {response.status} - {error_text}")
                        return False
                        
        except asyncio.TimeoutError:
            logger.error("Service registration timeout")
            return False
        except Exception as e:
            logger.error(f"Service registration error: {e}")
            return False
    
    async def update_health_status(self, status: str, details: Dict = None) -> bool:
        """Update service health status."""
        if not self.service_info:
            return False
            
        health_data = {
            "service_name": self.service_info["name"],
            "status": status,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.registry_url}/api/v1/services/health",
                    json=health_data,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Health status update failed: {e}")
            return False
    
    async def discover_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Discover service by name."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.registry_url}/api/v1/services/{service_name}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"Service {service_name} not found")
                        return None
                        
        except Exception as e:
            logger.error(f"Service discovery error: {e}")
            return None

# Global registry instance
service_registry = ServiceRegistry(settings.SERVICE_REGISTRY_URL)

async def register_current_service():
    """Register current service on startup."""
    service_info = {
        "name": settings.SERVICE_NAME,
        "version": "1.0.0",
        "host": settings.SERVICE_HOST,
        "port": settings.SERVICE_PORT,
        "health_check_url": f"http://{settings.SERVICE_HOST}:{settings.SERVICE_PORT}/health",
        "api_base_url": f"http://{settings.SERVICE_HOST}:{settings.SERVICE_PORT}/api/v1",
        "api_docs_url": f"http://{settings.SERVICE_HOST}:{settings.SERVICE_PORT}/api/docs",
        "tags": ["business", "erp", "products"],
        "capabilities": [
            "product_management",
            "category_management", 
            "inventory_tracking"
        ],
        "dependencies": [
            "user-auth-service",
            "company-partner-service"
        ]
    }
    
    success = await service_registry.register_service(service_info)
    if not success:
        logger.error("Failed to register service - continuing anyway")
    
    return success
```

#### FastAPI Integration

**app/main.py**
```python
"""FastAPI application with service registration."""

from fastapi import FastAPI
import asyncio
import logging
from contextlib import asynccontextmanager

from .core.config import settings
from .registration import register_current_service, service_registry

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage service lifecycle - registration and cleanup."""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME}")
    
    # Register with service registry
    await register_current_service()
    
    # Start health status reporting
    health_task = asyncio.create_task(health_status_reporter())
    
    try:
        yield
    finally:
        # Shutdown
        logger.info(f"Shutting down {settings.SERVICE_NAME}")
        health_task.cancel()

async def health_status_reporter():
    """Periodically report health status to registry."""
    while True:
        try:
            await asyncio.sleep(30)  # Report every 30 seconds
            
            # Gather health metrics
            health_details = {
                "cpu_usage": "5%",  # Would get actual metrics
                "memory_usage": "150MB",
                "active_connections": 10,
                "last_error": None
            }
            
            await service_registry.update_health_status("healthy", health_details)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Health reporting error: {e}")

app = FastAPI(
    title="Product Catalog Service",
    description="Product and category management",
    version="1.0.0",
    lifespan=lifespan
)
```

### 2. Service Discovery Client

**service_client.py**
```python
"""Client for discovering and communicating with other services."""

import aiohttp
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from .registration import service_registry

logger = logging.getLogger(__name__)

@dataclass
class ServiceEndpoint:
    """Service endpoint information."""
    name: str
    base_url: str
    health_url: str
    version: str
    capabilities: List[str]

class ServiceClient:
    """Client for inter-service communication."""
    
    def __init__(self):
        self._service_cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    async def get_service(self, service_name: str) -> Optional[ServiceEndpoint]:
        """Get service endpoint with caching."""
        # Check cache first
        if service_name in self._service_cache:
            cached_service, timestamp = self._service_cache[service_name]
            if time.time() - timestamp < self._cache_ttl:
                return cached_service
        
        # Discover service
        service_info = await service_registry.discover_service(service_name)
        if not service_info:
            return None
        
        endpoint = ServiceEndpoint(
            name=service_info["name"],
            base_url=service_info["api_base_url"],
            health_url=service_info["health_check_url"],
            version=service_info["version"],
            capabilities=service_info.get("capabilities", [])
        )
        
        # Cache the result
        self._service_cache[service_name] = (endpoint, time.time())
        return endpoint
    
    async def call_service(self, 
                          service_name: str, 
                          endpoint: str, 
                          method: str = "GET",
                          data: Dict = None,
                          headers: Dict = None) -> Optional[Dict]:
        """Make HTTP call to another service."""
        
        service = await self.get_service(service_name)
        if not service:
            logger.error(f"Service {service_name} not found")
            return None
        
        url = f"{service.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            async with aiohttp.ClientSession() as session:
                request_kwargs = {
                    "url": url,
                    "headers": headers or {},
                    "timeout": aiohttp.ClientTimeout(total=10)
                }
                
                if data:
                    request_kwargs["json"] = data
                
                async with session.request(method, **request_kwargs) as response:
                    if response.status < 400:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"Service call failed: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Service call error to {service_name}: {e}")
            return None
    
    async def check_service_capability(self, service_name: str, capability: str) -> bool:
        """Check if service supports a specific capability."""
        service = await self.get_service(service_name)
        return service and capability in service.capabilities

# Global service client
service_client = ServiceClient()
```

## Event-Driven Communication

### 1. Redis Streams Integration

XERPIUM uses Redis Streams for event-driven communication between services.

**messaging/publisher.py**
```python
"""Event publisher for Redis Streams."""

import redis
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
from .config import get_redis_connection

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Standard event types across XERPIUM services."""
    
    # User events
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_LOGIN = "user_login"
    
    # Company events  
    COMPANY_CREATED = "company_created"
    COMPANY_UPDATED = "company_updated"
    
    # Partner events
    PARTNER_CREATED = "partner_created"
    PARTNER_UPDATED = "partner_updated"
    PARTNER_DELETED = "partner_deleted"
    
    # Product events
    PRODUCT_CREATED = "product_created"
    PRODUCT_UPDATED = "product_updated"
    PRODUCT_DELETED = "product_deleted"
    PRODUCT_PRICE_CHANGED = "product_price_changed"
    
    # Inventory events
    STOCK_MOVEMENT = "stock_movement"
    STOCK_LOW = "stock_low"
    WAREHOUSE_CREATED = "warehouse_created"
    
    # Order events
    ORDER_CREATED = "order_created"
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    
    # Quote events
    QUOTE_CREATED = "quote_created"
    QUOTE_SENT = "quote_sent"
    QUOTE_APPROVED = "quote_approved"
    QUOTE_CONVERTED = "quote_converted"
    
    # System events
    SYSTEM_ERROR = "system_error"
    AUDIT_LOG_CREATED = "audit_log_created"

@dataclass
class EventPayload:
    """Standard event payload structure."""
    event_id: str
    event_type: EventType
    service_name: str
    entity_type: str
    entity_id: Optional[int]
    company_id: Optional[int]
    user_id: Optional[int]
    timestamp: str
    data: Dict[str, Any]
    version: str = "1.0"
    correlation_id: Optional[str] = None

class EventPublisher:
    """Publisher for Redis Streams events."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.redis = get_redis_connection()
    
    def publish_event(self, 
                     event_type: EventType,
                     entity_type: str,
                     entity_id: Optional[int] = None,
                     company_id: Optional[int] = None,
                     user_id: Optional[int] = None,
                     data: Dict[str, Any] = None,
                     correlation_id: Optional[str] = None) -> str:
        """Publish event to Redis Stream."""
        
        import uuid
        event_id = str(uuid.uuid4())
        
        payload = EventPayload(
            event_id=event_id,
            event_type=event_type,
            service_name=self.service_name,
            entity_type=entity_type,
            entity_id=entity_id,
            company_id=company_id,
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat(),
            data=data or {},
            correlation_id=correlation_id
        )
        
        try:
            # Publish to main events stream
            stream_name = "xerpium:events"
            message_data = asdict(payload)
            
            # Convert enum to string for JSON serialization
            message_data['event_type'] = event_type.value
            
            # Convert to JSON strings for Redis
            for key, value in message_data.items():
                if isinstance(value, (dict, list)):
                    message_data[key] = json.dumps(value)
                elif value is None:
                    message_data[key] = ""
            
            message_id = self.redis.xadd(stream_name, message_data)
            
            logger.info(f"Published event {event_type.value} with ID {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to publish event {event_type.value}: {e}")
            raise
    
    def publish_business_event(self, 
                              event_type: EventType,
                              business_object: Any,
                              action: str = "created",
                              changed_fields: List[str] = None) -> str:
        """Publish business object event with automatic data extraction."""
        
        # Extract common fields from business object
        entity_id = getattr(business_object, 'id', None)
        company_id = getattr(business_object, 'company_id', None)
        entity_type = business_object.__class__.__name__
        
        # Build event data
        event_data = {
            "action": action,
            "entity_name": str(business_object)
        }
        
        # Add changed fields for updates
        if changed_fields:
            event_data["changed_fields"] = changed_fields
        
        # Add key business object fields
        if hasattr(business_object, 'name'):
            event_data["name"] = business_object.name
        if hasattr(business_object, 'code'):
            event_data["code"] = business_object.code
        if hasattr(business_object, 'email'):
            event_data["email"] = business_object.email
        
        return self.publish_event(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            company_id=company_id,
            data=event_data
        )
```

### 2. Event Consumer

**messaging/consumer.py**
```python
"""Event consumer for Redis Streams."""

import redis
import json
import logging
import asyncio
from typing import Dict, Any, Callable, List
from datetime import datetime
from .publisher import EventType, EventPayload
from .config import get_redis_connection

logger = logging.getLogger(__name__)

class EventConsumer:
    """Consumer for Redis Streams events."""
    
    def __init__(self, service_name: str, consumer_group: str = None):
        self.service_name = service_name
        self.consumer_group = consumer_group or f"{service_name}-group"
        self.consumer_name = f"{service_name}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.redis = get_redis_connection()
        self.handlers = {}
        self.running = False
    
    def register_handler(self, event_type: EventType, handler: Callable[[EventPayload], None]):
        """Register event handler for specific event type."""
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for {event_type.value}")
    
    def register_handlers(self, handlers: Dict[EventType, Callable]):
        """Register multiple event handlers."""
        for event_type, handler in handlers.items():
            self.register_handler(event_type, handler)
    
    async def start_consuming(self):
        """Start consuming events from Redis Stream."""
        stream_name = "xerpium:events"
        
        try:
            # Create consumer group if it doesn't exist
            try:
                self.redis.xgroup_create(stream_name, self.consumer_group, id='0', mkstream=True)
                logger.info(f"Created consumer group: {self.consumer_group}")
            except redis.exceptions.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise
                # Group already exists
                logger.info(f"Consumer group already exists: {self.consumer_group}")
            
            self.running = True
            logger.info(f"Starting event consumer: {self.consumer_name}")
            
            while self.running:
                try:
                    # Read messages from stream
                    messages = self.redis.xreadgroup(
                        self.consumer_group,
                        self.consumer_name,
                        {stream_name: '>'},
                        count=10,
                        block=1000  # Block for 1 second
                    )
                    
                    for stream, stream_messages in messages:
                        for message_id, fields in stream_messages:
                            await self._process_message(stream_name, message_id, fields)
                
                except Exception as e:
                    logger.error(f"Error consuming events: {e}")
                    await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"Fatal error in event consumer: {e}")
        
        finally:
            self.running = False
            logger.info("Event consumer stopped")
    
    async def _process_message(self, stream_name: str, message_id: bytes, fields: Dict):
        """Process individual message."""
        try:
            # Convert bytes keys/values to strings
            message_data = {}
            for key, value in fields.items():
                key_str = key.decode() if isinstance(key, bytes) else key
                value_str = value.decode() if isinstance(value, bytes) else value
                message_data[key_str] = value_str
            
            # Parse event payload
            event_payload = self._parse_event_payload(message_data)
            
            # Find and call appropriate handler
            if event_payload.event_type in self.handlers:
                handler = self.handlers[event_payload.event_type]
                
                try:
                    # Call handler (could be sync or async)
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event_payload)
                    else:
                        handler(event_payload)
                    
                    # Acknowledge message
                    self.redis.xack(stream_name, self.consumer_group, message_id)
                    
                    logger.debug(f"Processed event {event_payload.event_id}")
                    
                except Exception as e:
                    logger.error(f"Error in event handler for {event_payload.event_type.value}: {e}")
                    # Don't acknowledge - will be retried
            else:
                # No handler for this event type - acknowledge anyway to avoid reprocessing
                self.redis.xack(stream_name, self.consumer_group, message_id)
                logger.debug(f"No handler for event type: {event_payload.event_type.value}")
        
        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")
    
    def _parse_event_payload(self, message_data: Dict[str, str]) -> EventPayload:
        """Parse Redis message data into EventPayload."""
        
        # Parse JSON fields
        data = json.loads(message_data.get('data', '{}'))
        
        # Convert event_type string back to enum
        event_type = EventType(message_data['event_type'])
        
        # Parse optional fields
        entity_id = int(message_data['entity_id']) if message_data.get('entity_id') else None
        company_id = int(message_data['company_id']) if message_data.get('company_id') else None
        user_id = int(message_data['user_id']) if message_data.get('user_id') else None
        
        return EventPayload(
            event_id=message_data['event_id'],
            event_type=event_type,
            service_name=message_data['service_name'],
            entity_type=message_data['entity_type'],
            entity_id=entity_id,
            company_id=company_id,
            user_id=user_id,
            timestamp=message_data['timestamp'],
            data=data,
            version=message_data.get('version', '1.0'),
            correlation_id=message_data.get('correlation_id') or None
        )
    
    def stop(self):
        """Stop the event consumer."""
        self.running = False
        logger.info("Stopping event consumer...")
```

### 3. Service Integration Example

**event_handlers.py**
```python
"""Event handlers for product service."""

import logging
from typing import Dict, Any
from .messaging.consumer import EventConsumer
from .messaging.publisher import EventType, EventPayload
from .services.product_service import ProductService

logger = logging.getLogger(__name__)

class ProductEventHandlers:
    """Event handlers for product-related events."""
    
    def __init__(self, product_service: ProductService):
        self.product_service = product_service
    
    async def handle_partner_created(self, event: EventPayload):
        """Handle new partner creation - could create default catalog."""
        logger.info(f"Partner created: {event.data}")
        
        # Example: Create default product category for new partner
        if event.data.get('partner_type') == 'supplier':
            try:
                category_data = {
                    "name": f"Products from {event.data.get('name', 'Supplier')}",
                    "description": f"Auto-created category for partner {event.entity_id}"
                }
                
                category = self.product_service.create_category(category_data, event.company_id)
                logger.info(f"Created default category {category.id} for partner {event.entity_id}")
                
            except Exception as e:
                logger.error(f"Failed to create category for partner {event.entity_id}: {e}")
    
    async def handle_inventory_low_stock(self, event: EventPayload):
        """Handle low stock notification."""
        product_id = event.data.get('product_id')
        current_stock = event.data.get('current_stock')
        minimum_stock = event.data.get('minimum_stock')
        
        logger.warning(f"Low stock alert for product {product_id}: {current_stock} < {minimum_stock}")
        
        # Could trigger automatic reordering, notifications, etc.
    
    async def handle_order_created(self, event: EventPayload):
        """Handle new order - update product metrics."""
        order_items = event.data.get('line_items', [])
        
        for item in order_items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            
            try:
                # Update product order statistics
                product = self.product_service.get_product_by_id(product_id, event.company_id)
                if product:
                    # Would update order frequency, last ordered date, etc.
                    logger.info(f"Updated metrics for product {product_id}: ordered {quantity}")
                    
            except Exception as e:
                logger.error(f"Failed to update metrics for product {product_id}: {e}")

def setup_event_handlers(product_service: ProductService) -> EventConsumer:
    """Set up event handlers for the product service."""
    
    consumer = EventConsumer("product-service")
    handlers = ProductEventHandlers(product_service)
    
    # Register handlers
    consumer.register_handlers({
        EventType.PARTNER_CREATED: handlers.handle_partner_created,
        EventType.STOCK_LOW: handlers.handle_inventory_low_stock,
        EventType.ORDER_CREATED: handlers.handle_order_created,
    })
    
    return consumer

# Usage in main.py
async def start_event_consumer():
    """Start event consumer in background task."""
    from .services.product_service import ProductService
    from .core.database import SessionLocal
    
    db = SessionLocal()
    try:
        product_service = ProductService(db)
        consumer = setup_event_handlers(product_service)
        await consumer.start_consuming()
    finally:
        db.close()
```

## Menu Registration

XERPIUM uses a dynamic menu system where services register their menu items with the menu service.

### 1. Menu Registration Client

**menu_integration.py**
```python
"""Menu system integration for service registration."""

import requests
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MenuItem:
    """Menu item definition."""
    name: str
    path: str
    icon: str
    parent_name: Optional[str] = None
    parent_id: Optional[int] = None
    order_number: int = 100
    required_permissions: List[str] = None
    is_active: bool = True
    description: Optional[str] = None

class MenuRegistrationClient:
    """Client for registering menu items with menu service."""
    
    def __init__(self, menu_service_url: str, service_name: str):
        self.menu_service_url = menu_service_url.rstrip('/')
        self.service_name = service_name
        self.registered_items = []
    
    def register_menu_item(self, menu_item: MenuItem) -> bool:
        """Register single menu item."""
        try:
            item_data = {
                "name": menu_item.name,
                "path": menu_item.path,
                "icon": menu_item.icon,
                "parent_name": menu_item.parent_name,
                "parent_id": menu_item.parent_id,
                "order_number": menu_item.order_number,
                "required_permissions": menu_item.required_permissions or [],
                "is_active": menu_item.is_active,
                "description": menu_item.description,
                "service_name": self.service_name
            }
            
            response = requests.post(
                f"{self.menu_service_url}/api/v1/menu-items/",
                json=item_data,
                timeout=10
            )
            
            if response.status_code == 201:
                menu_data = response.json()
                self.registered_items.append(menu_data['id'])
                logger.info(f"Registered menu item: {menu_item.name}")
                return True
            else:
                logger.error(f"Failed to register menu item {menu_item.name}: {response.status_code}")
                logger.error(response.text)
                return False
                
        except Exception as e:
            logger.error(f"Menu registration error for {menu_item.name}: {e}")
            return False
    
    def register_menu_items(self, menu_items: List[MenuItem]) -> Dict[str, bool]:
        """Register multiple menu items."""
        results = {}
        
        for item in menu_items:
            results[item.name] = self.register_menu_item(item)
        
        successful = sum(1 for success in results.values() if success)
        logger.info(f"Menu registration complete: {successful}/{len(menu_items)} successful")
        
        return results
    
    def unregister_all_items(self) -> bool:
        """Unregister all menu items registered by this service."""
        success_count = 0
        
        for item_id in self.registered_items:
            try:
                response = requests.delete(
                    f"{self.menu_service_url}/api/v1/menu-items/{item_id}",
                    timeout=10
                )
                
                if response.status_code == 204:
                    success_count += 1
                    logger.info(f"Unregistered menu item: {item_id}")
                else:
                    logger.error(f"Failed to unregister menu item {item_id}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Menu unregistration error for item {item_id}: {e}")
        
        self.registered_items = []
        return success_count == len(self.registered_items)

def register_product_menus() -> bool:
    """Register product service menu items."""
    
    menu_client = MenuRegistrationClient(
        menu_service_url="http://menu-access-service:8004",
        service_name="product-service"
    )
    
    # Define menu structure
    menu_items = [
        # Main catalog menu
        MenuItem(
            name="Product Catalog",
            path="/products",
            icon="package",
            order_number=200,
            required_permissions=["product.view"],
            description="Product and category management"
        ),
        
        # Products submenu
        MenuItem(
            name="Products",
            path="/products/list",
            icon="box",
            parent_name="Product Catalog",
            order_number=1,
            required_permissions=["product.view"],
            description="Manage products and pricing"
        ),
        
        # Categories submenu
        MenuItem(
            name="Categories", 
            path="/products/categories",
            icon="folder",
            parent_name="Product Catalog",
            order_number=2,
            required_permissions=["product.view"],
            description="Organize products into categories"
        ),
        
        # Price management
        MenuItem(
            name="Pricing",
            path="/products/pricing",
            icon="dollar-sign",
            parent_name="Product Catalog", 
            order_number=3,
            required_permissions=["product.edit"],
            description="Manage product pricing and margins"
        ),
        
        # Reports submenu
        MenuItem(
            name="Product Reports",
            path="/products/reports",
            icon="bar-chart",
            parent_name="Product Catalog",
            order_number=10,
            required_permissions=["product.report"],
            description="Product analytics and reports"
        )
    ]
    
    results = menu_client.register_menu_items(menu_items)
    return all(results.values())
```

### 2. FastAPI Integration

**app/main.py** (updated with menu registration)
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage service lifecycle."""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME}")
    
    # Register with service registry
    await register_current_service()
    
    # Register menu items
    menu_success = register_product_menus()
    if menu_success:
        logger.info("Menu items registered successfully")
    else:
        logger.warning("Some menu items failed to register")
    
    # Start event consumer
    consumer_task = asyncio.create_task(start_event_consumer())
    
    try:
        yield
    finally:
        # Shutdown
        logger.info(f"Shutting down {settings.SERVICE_NAME}")
        consumer_task.cancel()
```

## UI Component Registration

Services can register UI components for integration with the admin interface.

### 1. UI Registry Client

**ui_integration.py**
```python
"""UI component registration for admin interface integration."""

import requests
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class UIComponent:
    """UI component definition."""
    name: str
    component_type: str  # 'page', 'widget', 'modal', 'form'
    service_name: str
    route_path: str
    api_endpoint: str
    permissions: List[str] = None
    props: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    is_active: bool = True

@dataclass
class UIWidget:
    """Dashboard widget definition."""
    name: str
    service_name: str
    widget_type: str  # 'chart', 'metric', 'table', 'custom'
    api_endpoint: str
    refresh_interval: int = 30  # seconds
    size: str = "medium"  # small, medium, large
    permissions: List[str] = None
    config: Dict[str, Any] = None
    is_active: bool = True

class UIRegistryClient:
    """Client for registering UI components."""
    
    def __init__(self, ui_registry_url: str, service_name: str):
        self.ui_registry_url = ui_registry_url.rstrip('/')
        self.service_name = service_name
        self.registered_components = []
        self.registered_widgets = []
    
    def register_component(self, component: UIComponent) -> bool:
        """Register UI component."""
        try:
            component_data = asdict(component)
            
            response = requests.post(
                f"{self.ui_registry_url}/api/v1/components/",
                json=component_data,
                timeout=10
            )
            
            if response.status_code == 201:
                component_info = response.json()
                self.registered_components.append(component_info['id'])
                logger.info(f"Registered UI component: {component.name}")
                return True
            else:
                logger.error(f"Failed to register component {component.name}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"UI component registration error: {e}")
            return False
    
    def register_widget(self, widget: UIWidget) -> bool:
        """Register dashboard widget."""
        try:
            widget_data = asdict(widget)
            
            response = requests.post(
                f"{self.ui_registry_url}/api/v1/widgets/",
                json=widget_data,
                timeout=10
            )
            
            if response.status_code == 201:
                widget_info = response.json()
                self.registered_widgets.append(widget_info['id'])
                logger.info(f"Registered UI widget: {widget.name}")
                return True
            else:
                logger.error(f"Failed to register widget {widget.name}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"UI widget registration error: {e}")
            return False

def register_product_ui_components():
    """Register product service UI components."""
    
    ui_client = UIRegistryClient(
        ui_registry_url="http://ui-registry-service:8008",
        service_name="product-service"
    )
    
    # Register page components
    components = [
        UIComponent(
            name="Product List",
            component_type="page",
            service_name="product-service",
            route_path="/products/list",
            api_endpoint="/api/v1/products/",
            permissions=["product.view"],
            metadata={
                "title": "Products",
                "description": "Product catalog management",
                "breadcrumb": ["Catalog", "Products"]
            }
        ),
        
        UIComponent(
            name="Product Form",
            component_type="form",
            service_name="product-service", 
            route_path="/products/edit/:id",
            api_endpoint="/api/v1/products/{id}",
            permissions=["product.edit"],
            props={
                "fields": [
                    {"name": "name", "type": "text", "required": True},
                    {"name": "sku", "type": "text", "required": True},
                    {"name": "list_price", "type": "currency", "required": True},
                    {"name": "cost_price", "type": "currency"},
                    {"name": "category_id", "type": "select", "source": "/api/v1/categories/"}
                ]
            }
        )
    ]
    
    # Register dashboard widgets
    widgets = [
        UIWidget(
            name="Product Count",
            service_name="product-service",
            widget_type="metric",
            api_endpoint="/api/v1/products/stats/count",
            size="small",
            permissions=["product.view"],
            config={
                "title": "Total Products",
                "icon": "package",
                "color": "blue"
            }
        ),
        
        UIWidget(
            name="Low Stock Alert",
            service_name="product-service",
            widget_type="table", 
            api_endpoint="/api/v1/products/low-stock",
            refresh_interval=60,
            size="medium",
            permissions=["inventory.view"],
            config={
                "title": "Low Stock Products",
                "columns": ["name", "sku", "current_stock", "minimum_stock"],
                "max_rows": 10
            }
        ),
        
        UIWidget(
            name="Product Categories",
            service_name="product-service",
            widget_type="chart",
            api_endpoint="/api/v1/categories/stats",
            size="medium",
            permissions=["product.view"],
            config={
                "title": "Products by Category",
                "chart_type": "pie",
                "color_scheme": "category20"
            }
        )
    ]
    
    # Register all components and widgets
    component_results = [ui_client.register_component(comp) for comp in components]
    widget_results = [ui_client.register_widget(widget) for widget in widgets]
    
    all_successful = all(component_results + widget_results)
    logger.info(f"UI registration complete: {all_successful}")
    
    return all_successful
```

## Redis Messaging

### 1. Configuration

**messaging/config.py**
```python
"""Redis configuration for messaging."""

import redis
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_redis_connection() -> redis.Redis:
    """Get Redis connection with proper configuration."""
    try:
        redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Test connection
        redis_client.ping()
        logger.info("Redis connection established")
        return redis_client
        
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise

def get_redis_async_connection():
    """Get async Redis connection for high-performance scenarios."""
    import aioredis
    
    return aioredis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        retry_on_timeout=True
    )
```

### 2. Message Patterns

**messaging/patterns.py**
```python
"""Common messaging patterns for XERPIUM services."""

import asyncio
import logging
from typing import Dict, Any, List, Callable
from .publisher import EventPublisher, EventType
from .consumer import EventConsumer

logger = logging.getLogger(__name__)

class RequestResponsePattern:
    """Implement request-response pattern over Redis."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.publisher = EventPublisher(service_name)
        self.pending_requests = {}
    
    async def send_request(self, 
                          target_service: str,
                          request_type: str,
                          data: Dict[str, Any],
                          timeout: int = 30) -> Dict[str, Any]:
        """Send request and wait for response."""
        
        import uuid
        request_id = str(uuid.uuid4())
        
        # Store request for response handling
        response_future = asyncio.Future()
        self.pending_requests[request_id] = response_future
        
        # Send request event
        request_data = {
            "request_id": request_id,
            "response_service": self.service_name,
            "request_type": request_type,
            "data": data
        }
        
        self.publisher.publish_event(
            event_type=EventType.CUSTOM,
            entity_type="Request",
            data=request_data
        )
        
        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            logger.error(f"Request {request_id} to {target_service} timed out")
            raise
        finally:
            # Clean up pending request
            self.pending_requests.pop(request_id, None)
    
    def handle_response(self, event_payload):
        """Handle response event."""
        request_id = event_payload.data.get("request_id")
        
        if request_id in self.pending_requests:
            future = self.pending_requests[request_id]
            if not future.done():
                future.set_result(event_payload.data)

class BulkProcessingPattern:
    """Pattern for processing events in batches."""
    
    def __init__(self, 
                 batch_size: int = 10,
                 batch_timeout: int = 5,
                 processor: Callable[[List], None] = None):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.processor = processor
        self.batch = []
        self.last_batch_time = asyncio.get_event_loop().time()
    
    async def add_to_batch(self, item: Any):
        """Add item to batch and process if needed."""
        self.batch.append(item)
        current_time = asyncio.get_event_loop().time()
        
        should_process = (
            len(self.batch) >= self.batch_size or
            (current_time - self.last_batch_time) >= self.batch_timeout
        )
        
        if should_process:
            await self.process_batch()
    
    async def process_batch(self):
        """Process current batch."""
        if not self.batch:
            return
        
        batch_to_process = self.batch.copy()
        self.batch.clear()
        self.last_batch_time = asyncio.get_event_loop().time()
        
        try:
            if self.processor:
                if asyncio.iscoroutinefunction(self.processor):
                    await self.processor(batch_to_process)
                else:
                    self.processor(batch_to_process)
                    
            logger.info(f"Processed batch of {len(batch_to_process)} items")
            
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            # Could implement retry logic here
```

## Service Authentication

### 1. Inter-Service Authentication

**auth/service_auth.py**
```python
"""Inter-service authentication for XERPIUM."""

import jwt
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class ServiceAuthClient:
    """Client for service-to-service authentication."""
    
    def __init__(self, auth_service_url: str, service_name: str, service_key: str):
        self.auth_service_url = auth_service_url.rstrip('/')
        self.service_name = service_name
        self.service_key = service_key
        self._token = None
        self._token_expires = None
    
    def get_service_token(self) -> Optional[str]:
        """Get or refresh service authentication token."""
        
        # Check if current token is still valid
        if (self._token and self._token_expires and 
            datetime.utcnow() < self._token_expires - timedelta(minutes=5)):
            return self._token
        
        # Get new token
        try:
            response = requests.post(
                f"{self.auth_service_url}/api/v1/service-auth/token",
                json={
                    "service_name": self.service_name,
                    "service_key": self.service_key
                },
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self._token = token_data["access_token"]
                
                # Parse expiration from JWT
                try:
                    payload = jwt.decode(self._token, options={"verify_signature": False})
                    self._token_expires = datetime.fromtimestamp(payload["exp"])
                except:
                    # Fallback: assume 1 hour expiration
                    self._token_expires = datetime.utcnow() + timedelta(hours=1)
                
                logger.info(f"Service token obtained for {self.service_name}")
                return self._token
            else:
                logger.error(f"Service token request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Service authentication error: {e}")
            return None
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for service requests."""
        token = self.get_service_token()
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}
    
    def validate_service_request(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate incoming service request token."""
        try:
            response = requests.post(
                f"{self.auth_service_url}/api/v1/service-auth/validate",
                json={"token": token},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Service token validation failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Service token validation error: {e}")
            return None

# Global service auth client
service_auth = ServiceAuthClient(
    auth_service_url="http://user-auth-service:8001",
    service_name=settings.SERVICE_NAME,
    service_key=settings.SERVICE_KEY
)

# FastAPI middleware for service authentication
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

async def verify_service_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify service-to-service authentication."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service_data = service_auth.validate_service_request(credentials.credentials)
    if not service_data:
        raise HTTPException(status_code=401, detail="Invalid service token")
    
    return service_data
```

## Multi-Company Integration

### 1. Company Context Middleware

**middleware/company_context.py**
```python
"""Company context middleware for multi-tenant support."""

import logging
from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth.service_auth import verify_service_auth

logger = logging.getLogger(__name__)
security = HTTPBearer()

class CompanyContext:
    """Company context for current request."""
    
    def __init__(self, company_id: int, user_id: Optional[int] = None):
        self.company_id = company_id
        self.user_id = user_id
        self.permissions = []

async def get_company_context(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CompanyContext:
    """Extract company context from request."""
    
    try:
        # Validate token with auth service
        service_data = await verify_service_auth(credentials)
        
        # Extract company information
        company_id = service_data.get("company_id")
        user_id = service_data.get("user_id")
        
        if not company_id:
            raise HTTPException(
                status_code=400,
                detail="No company context in request"
            )
        
        context = CompanyContext(
            company_id=company_id,
            user_id=user_id
        )
        
        # Store in request state for access in business logic
        request.state.company_context = context
        
        return context
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Company context extraction error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to extract company context"
        )

# Usage in endpoints
@router.get("/products/")
async def get_products(
    company_context: CompanyContext = Depends(get_company_context),
    service: ProductService = Depends(get_product_service)
):
    """Get products for current company."""
    return service.get_products(company_id=company_context.company_id)
```

## Error Handling and Resilience

### 1. Circuit Breaker Pattern

**resilience/circuit_breaker.py**
```python
"""Circuit breaker for service resilience."""

import asyncio
import logging
from typing import Callable, Any
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for external service calls."""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - reset failure count
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset."""
        return (
            self.last_failure_time and
            datetime.utcnow() - self.last_failure_time >= timedelta(seconds=self.recovery_timeout)
        )
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker reset to CLOSED state")
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker OPEN after {self.failure_count} failures")

# Usage with service calls
auth_service_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

async def call_auth_service_with_protection(endpoint: str, data: dict):
    """Call auth service with circuit breaker protection."""
    
    async def auth_call():
        response = await service_client.call_service("user-auth-service", endpoint, "POST", data)
        if not response:
            raise Exception("Auth service call failed")
        return response
    
    return await auth_service_breaker.call(auth_call)
```

### 2. Retry and Timeout Patterns

**resilience/retry.py**
```python
"""Retry patterns for resilient service communication."""

import asyncio
import logging
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for exponential backoff retry."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            delay = base_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries")
                        raise
                    
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # Similar implementation for sync functions
            import time
            delay = base_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries")
                        raise
                    
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}): {e}")
                    time.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator

# Usage examples
@retry_with_exponential_backoff(max_retries=3, base_delay=0.5)
async def register_with_service_registry():
    """Register service with retry logic."""
    success = await service_registry.register_service(service_info)
    if not success:
        raise Exception("Service registration failed")
    return success

@retry_with_exponential_backoff(max_retries=2, exceptions=(requests.RequestException,))
def register_menu_items():
    """Register menu items with retry logic."""  
    return menu_client.register_menu_items(items)
```

## Monitoring and Observability

### 1. Health Checks

**monitoring/health.py**
```python
"""Health check implementations for service monitoring."""

import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from app.core.database import engine
from app.core.config import settings

logger = logging.getLogger(__name__)

class HealthChecker:
    """Comprehensive health checking for service components."""
    
    def __init__(self):
        self.checks = {}
        self.register_default_checks()
    
    def register_check(self, name: str, check_func: callable):
        """Register a health check function."""
        self.checks[name] = check_func
    
    def register_default_checks(self):
        """Register default health checks."""
        self.register_check("database", self._check_database)
        self.register_check("redis", self._check_redis)
        self.register_check("external_services", self._check_external_services)
        self.register_check("disk_space", self._check_disk_space)
        self.register_check("memory", self._check_memory)
    
    async def check_health(self) -> Dict[str, Any]:
        """Run all health checks and return status."""
        
        results = {
            "service": settings.SERVICE_NAME,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "checks": {},
            "version": "1.0.0"
        }
        
        overall_healthy = True
        
        for check_name, check_func in self.checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    check_result = await check_func()
                else:
                    check_result = check_func()
                
                results["checks"][check_name] = {
                    "status": "healthy" if check_result["healthy"] else "unhealthy",
                    "details": check_result.get("details", {}),
                    "response_time_ms": check_result.get("response_time_ms", 0)
                }
                
                if not check_result["healthy"]:
                    overall_healthy = False
                    
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {e}")
                results["checks"][check_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "response_time_ms": 0
                }
                overall_healthy = False
        
        results["status"] = "healthy" if overall_healthy else "unhealthy"
        return results
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Test connection
            with engine.connect() as connection:
                result = connection.execute("SELECT 1")
                row = result.fetchone()
                
                if row and row[0] == 1:
                    end_time = asyncio.get_event_loop().time()
                    return {
                        "healthy": True,
                        "details": {
                            "driver": "postgresql",
                            "pool_size": engine.pool.size(),
                            "pool_checked_in": engine.pool.checkedin(),
                            "pool_checked_out": engine.pool.checkedout()
                        },
                        "response_time_ms": round((end_time - start_time) * 1000, 2)
                    }
                else:
                    return {"healthy": False, "details": {"error": "Invalid database response"}}
                    
        except Exception as e:
            return {
                "healthy": False,
                "details": {"error": str(e)},
                "response_time_ms": 0
            }
    
    def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity."""
        start_time = time.time()
        
        try:
            from messaging.config import get_redis_connection
            redis_client = get_redis_connection()
            
            # Test basic operations
            test_key = f"health_check_{int(time.time())}"
            redis_client.set(test_key, "test", ex=10)
            value = redis_client.get(test_key)
            redis_client.delete(test_key)
            
            if value == "test":
                end_time = time.time()
                return {
                    "healthy": True,
                    "details": {
                        "version": redis_client.info()["redis_version"],
                        "memory_used": redis_client.info()["used_memory_human"]
                    },
                    "response_time_ms": round((end_time - start_time) * 1000, 2)
                }
            else:
                return {"healthy": False, "details": {"error": "Redis test failed"}}
                
        except Exception as e:
            return {
                "healthy": False,
                "details": {"error": str(e)},
                "response_time_ms": 0
            }
    
    async def _check_external_services(self) -> Dict[str, Any]:
        """Check connectivity to external services."""
        from .integration.service_client import service_client
        
        required_services = [
            "user-auth-service",
            "company-partner-service",
            "service-registry"
        ]
        
        service_statuses = {}
        all_healthy = True
        
        for service_name in required_services:
            try:
                service_info = await service_client.get_service(service_name)
                if service_info:
                    service_statuses[service_name] = "available"
                else:
                    service_statuses[service_name] = "not_found"
                    all_healthy = False
            except Exception as e:
                service_statuses[service_name] = f"error: {str(e)}"
                all_healthy = False
        
        return {
            "healthy": all_healthy,
            "details": service_statuses
        }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space."""
        import shutil
        
        try:
            total, used, free = shutil.disk_usage("/")
            free_percentage = (free / total) * 100
            
            return {
                "healthy": free_percentage > 10,  # Alert if less than 10% free
                "details": {
                    "total_gb": round(total / (1024**3), 2),
                    "used_gb": round(used / (1024**3), 2),
                    "free_gb": round(free / (1024**3), 2),
                    "free_percentage": round(free_percentage, 2)
                }
            }
        except Exception as e:
            return {
                "healthy": False,
                "details": {"error": str(e)}
            }
    
    def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage."""
        import psutil
        
        try:
            memory = psutil.virtual_memory()
            
            return {
                "healthy": memory.percent < 90,  # Alert if more than 90% used
                "details": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "free_gb": round(memory.free / (1024**3), 2),
                    "percentage": memory.percent
                }
            }
        except Exception as e:
            return {
                "healthy": False,
                "details": {"error": str(e)}
            }

# Global health checker
health_checker = HealthChecker()

# FastAPI endpoint
from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/health", status_code=200)
async def health_check():
    """Service health check endpoint."""
    health_status = await health_checker.check_health()
    
    # Return appropriate HTTP status
    if health_status["status"] == "healthy":
        return health_status
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=health_status)
```

---

## Summary

The integration patterns in XERPIUM provide:

- **Service Discovery**: Automatic registration and discovery of services
- **Event-Driven Communication**: Asynchronous messaging via Redis Streams
- **Menu Integration**: Dynamic menu system for UI components
- **UI Component Registry**: Pluggable UI components and widgets
- **Service Authentication**: Secure inter-service communication
- **Multi-Company Support**: Tenant isolation across all operations
- **Resilience Patterns**: Circuit breakers, retries, and error handling
- **Health Monitoring**: Comprehensive service health checking

These patterns ensure services can integrate seamlessly while maintaining loose coupling and high availability.