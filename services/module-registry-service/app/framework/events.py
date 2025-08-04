"""
Event hook system for module lifecycle and business event integration
"""
import asyncio
import json
import re
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, asdict
import redis.asyncio as redis
import logging
from app.framework.loader import LoadedModule
from app.framework.manifest import EventType
from app.core.config import settings

logger = logging.getLogger(__name__)


class ModuleLifecycleEvent(str, Enum):
    """Module lifecycle events"""
    MODULE_LOADING = "module_loading"
    MODULE_LOADED = "module_loaded"
    MODULE_INITIALIZING = "module_initializing"
    MODULE_INITIALIZED = "module_initialized"
    MODULE_STARTING = "module_starting"
    MODULE_STARTED = "module_started"
    MODULE_STOPPING = "module_stopping"
    MODULE_STOPPED = "module_stopped"
    MODULE_UNLOADING = "module_unloading"
    MODULE_UNLOADED = "module_unloaded"
    MODULE_ERROR = "module_error"
    MODULE_HEALTH_CHECK = "module_health_check"


@dataclass
class EventData:
    """Base event data structure"""
    event_type: str
    event_id: str
    timestamp: datetime
    source_module: Optional[str] = None
    correlation_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventData':
        """Create from dictionary"""
        if isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class ModuleLifecycleEventData(EventData):
    """Module lifecycle event data"""
    module_id: int
    module_name: str
    module_version: str
    installation_id: int
    company_id: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class BusinessEventData(EventData):
    """Business event data"""
    entity_type: str
    entity_id: int
    action: str
    changes: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    company_id: Optional[int] = None


class EventHandler:
    """Event handler registration"""
    
    def __init__(
        self,
        module_id: int,
        event_pattern: str,
        handler_func: Callable,
        priority: int = 100,
        event_type: EventType = EventType.BUSINESS_OBJECT
    ):
        self.module_id = module_id
        self.event_pattern = event_pattern
        self.handler_func = handler_func
        self.priority = priority
        self.event_type = event_type
        self.compiled_pattern = re.compile(event_pattern)
    
    def matches(self, event_type: str) -> bool:
        """Check if this handler matches the event type"""
        return bool(self.compiled_pattern.match(event_type))
    
    async def handle(self, event_data: EventData) -> Any:
        """Handle the event"""
        try:
            if asyncio.iscoroutinefunction(self.handler_func):
                return await self.handler_func(event_data)
            else:
                return self.handler_func(event_data)
        except Exception as e:
            logger.error(f"Error in event handler {self.event_pattern}: {e}")
            raise


class EventBus:
    """Event bus for module event publishing and subscription"""
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or settings.redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.event_handlers: Dict[str, List[EventHandler]] = {}
        self.lifecycle_handlers: List[EventHandler] = []
        self.running = False
        self.consumer_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the event bus"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            self.running = True
            self.consumer_task = asyncio.create_task(self._event_consumer())
            
            logger.info("Event bus started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start event bus: {e}")
            raise
    
    async def stop(self):
        """Stop the event bus"""
        self.running = False
        
        if self.consumer_task:
            self.consumer_task.cancel()
            try:
                await self.consumer_task
            except asyncio.CancelledError:
                pass
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Event bus stopped")
    
    async def publish_event(self, event_data: EventData, stream_name: str = "module_events"):
        """Publish an event to the event bus"""
        if not self.redis_client:
            logger.warning("Event bus not started, cannot publish event")
            return
        
        try:
            event_dict = event_data.to_dict()
            await self.redis_client.xadd(stream_name, event_dict)
            
            logger.debug(f"Published event {event_data.event_type} to stream {stream_name}")
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
    
    async def publish_lifecycle_event(
        self,
        event_type: ModuleLifecycleEvent,
        module_id: int,
        module_name: str,
        module_version: str,
        installation_id: int,
        company_id: Optional[int] = None,
        error_message: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Publish a module lifecycle event"""
        event_data = ModuleLifecycleEventData(
            event_type=event_type.value,
            event_id=f"lifecycle_{module_id}_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            source_module="module-registry-service",
            correlation_id=correlation_id,
            module_id=module_id,
            module_name=module_name,
            module_version=module_version,
            installation_id=installation_id,
            company_id=company_id,
            error_message=error_message
        )
        
        await self.publish_event(event_data, "module_lifecycle_events")
        
        # Also handle locally
        await self._handle_lifecycle_event(event_data)
    
    async def publish_business_event(
        self,
        event_type: str,
        entity_type: str,
        entity_id: int,
        action: str,
        changes: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        company_id: Optional[int] = None,
        source_module: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Publish a business event"""
        event_data = BusinessEventData(
            event_type=event_type,
            event_id=f"business_{entity_type}_{entity_id}_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            source_module=source_module,
            correlation_id=correlation_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            changes=changes,
            user_id=user_id,
            company_id=company_id
        )
        
        await self.publish_event(event_data, "business_events")
        
        # Also handle locally
        await self._handle_business_event(event_data)
    
    def register_event_handler(
        self,
        module_id: int,
        event_pattern: str,
        handler_func: Callable,
        priority: int = 100,
        event_type: EventType = EventType.BUSINESS_OBJECT
    ) -> EventHandler:
        """Register an event handler"""
        handler = EventHandler(module_id, event_pattern, handler_func, priority, event_type)
        
        if event_type == EventType.MODULE_LIFECYCLE:
            self.lifecycle_handlers.append(handler)
            # Sort by priority (lower = higher priority)
            self.lifecycle_handlers.sort(key=lambda h: h.priority)
        else:
            if event_pattern not in self.event_handlers:
                self.event_handlers[event_pattern] = []
            
            self.event_handlers[event_pattern].append(handler)
            # Sort by priority
            self.event_handlers[event_pattern].sort(key=lambda h: h.priority)
        
        logger.debug(f"Registered event handler for pattern {event_pattern} from module {module_id}")
        return handler
    
    def unregister_module_handlers(self, module_id: int):
        """Unregister all event handlers for a module"""
        # Remove from lifecycle handlers
        self.lifecycle_handlers = [h for h in self.lifecycle_handlers if h.module_id != module_id]
        
        # Remove from event handlers
        for pattern in list(self.event_handlers.keys()):
            self.event_handlers[pattern] = [
                h for h in self.event_handlers[pattern] if h.module_id != module_id
            ]
            # Remove empty patterns
            if not self.event_handlers[pattern]:
                del self.event_handlers[pattern]
        
        logger.debug(f"Unregistered all event handlers for module {module_id}")
    
    async def _handle_lifecycle_event(self, event_data: ModuleLifecycleEventData):
        """Handle lifecycle event with registered handlers"""
        for handler in self.lifecycle_handlers:
            if handler.matches(event_data.event_type):
                try:
                    await handler.handle(event_data)
                except Exception as e:
                    logger.error(f"Error in lifecycle event handler: {e}")
    
    async def _handle_business_event(self, event_data: BusinessEventData):
        """Handle business event with registered handlers"""
        matching_handlers = []
        
        for pattern, handlers in self.event_handlers.items():
            for handler in handlers:
                if handler.matches(event_data.event_type):
                    matching_handlers.append(handler)
        
        # Sort by priority
        matching_handlers.sort(key=lambda h: h.priority)
        
        # Execute handlers
        for handler in matching_handlers:
            try:
                await handler.handle(event_data)
            except Exception as e:
                logger.error(f"Error in business event handler: {e}")
    
    async def _event_consumer(self):
        """Background task to consume events from Redis streams"""
        if not self.redis_client:
            return
        
        streams = {
            "module_lifecycle_events": "$",
            "business_events": "$"
        }
        
        while self.running:
            try:
                # Read from streams
                messages = await self.redis_client.xread(streams, block=1000)
                
                for stream_name, stream_messages in messages:
                    for message_id, fields in stream_messages:
                        await self._process_stream_message(stream_name.decode(), fields)
                        
                        # Update stream position
                        streams[stream_name.decode()] = message_id.decode()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in event consumer: {e}")
                await asyncio.sleep(1)
    
    async def _process_stream_message(self, stream_name: str, fields: Dict[bytes, bytes]):
        """Process a message from Redis stream"""
        try:
            # Convert bytes to string
            str_fields = {k.decode(): v.decode() for k, v in fields.items()}
            
            # Parse event data
            if stream_name == "module_lifecycle_events":
                # Reconstruct lifecycle event data
                event_data = ModuleLifecycleEventData(
                    event_type=str_fields.get('event_type', ''),
                    event_id=str_fields.get('event_id', ''),
                    timestamp=datetime.fromisoformat(str_fields.get('timestamp', datetime.utcnow().isoformat())),
                    source_module=str_fields.get('source_module'),
                    correlation_id=str_fields.get('correlation_id'),
                    module_id=int(str_fields.get('module_id', 0)),
                    module_name=str_fields.get('module_name', ''),
                    module_version=str_fields.get('module_version', ''),
                    installation_id=int(str_fields.get('installation_id', 0)),
                    company_id=int(str_fields['company_id']) if str_fields.get('company_id') else None,
                    error_message=str_fields.get('error_message')
                )
                await self._handle_lifecycle_event(event_data)
                
            elif stream_name == "business_events":
                # Parse changes if present
                changes = None
                if str_fields.get('changes'):
                    changes = json.loads(str_fields['changes'])
                
                event_data = BusinessEventData(
                    event_type=str_fields.get('event_type', ''),
                    event_id=str_fields.get('event_id', ''),
                    timestamp=datetime.fromisoformat(str_fields.get('timestamp', datetime.utcnow().isoformat())),
                    source_module=str_fields.get('source_module'),
                    correlation_id=str_fields.get('correlation_id'),
                    entity_type=str_fields.get('entity_type', ''),
                    entity_id=int(str_fields.get('entity_id', 0)),
                    action=str_fields.get('action', ''),
                    changes=changes,
                    user_id=int(str_fields['user_id']) if str_fields.get('user_id') else None,
                    company_id=int(str_fields['company_id']) if str_fields.get('company_id') else None
                )
                await self._handle_business_event(event_data)
                
        except Exception as e:
            logger.error(f"Error processing stream message: {e}")


class ModuleEventManager:
    """Manager for module event integration"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
    async def register_module_event_handlers(self, loaded_module: LoadedModule):
        """Register event handlers for a loaded module"""
        for handler_spec in loaded_module.manifest.event_handlers or []:
            if handler_spec.event_pattern in loaded_module.event_handlers:
                handler_func = loaded_module.event_handlers[handler_spec.event_pattern]
                
                self.event_bus.register_event_handler(
                    module_id=loaded_module.module_id,
                    event_pattern=handler_spec.event_pattern,
                    handler_func=handler_func,
                    priority=handler_spec.priority,
                    event_type=handler_spec.event_type
                )
        
        logger.info(f"Registered event handlers for module {loaded_module.full_name}")
    
    async def unregister_module_event_handlers(self, module_id: int):
        """Unregister event handlers for a module"""
        self.event_bus.unregister_module_handlers(module_id)
        logger.info(f"Unregistered event handlers for module {module_id}")
    
    async def publish_module_lifecycle_event(
        self,
        event_type: ModuleLifecycleEvent,
        loaded_module: LoadedModule,
        error_message: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Publish module lifecycle event"""
        await self.event_bus.publish_lifecycle_event(
            event_type=event_type,
            module_id=loaded_module.module_id,
            module_name=loaded_module.module_name,
            module_version=loaded_module.module_version,
            installation_id=loaded_module.installation.id,
            company_id=loaded_module.installation.company_id,
            error_message=error_message,
            correlation_id=correlation_id
        )


# Global event bus and manager
event_bus = EventBus()
event_manager = ModuleEventManager(event_bus)