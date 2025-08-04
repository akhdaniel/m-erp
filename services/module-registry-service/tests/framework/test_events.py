"""
Tests for event hook system and module lifecycle events
"""
import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from app.framework.events import (
    EventBus, EventHandler, ModuleEventManager,
    EventData, ModuleLifecycleEventData, BusinessEventData,
    ModuleLifecycleEvent, event_bus, event_manager
)
from app.framework.loader import LoadedModule
from app.framework.manifest import ModuleManifest, EventType
from app.models.installation import ModuleInstallation, InstallationStatus


@pytest.fixture
def sample_event_data():
    """Sample event data for testing"""
    return EventData(
        event_type="test_event",
        event_id="test_123",
        timestamp=datetime.utcnow(),
        source_module="test_module",
        correlation_id="corr_123",
        data={"test": "data"}
    )


@pytest.fixture
def sample_lifecycle_event_data():
    """Sample lifecycle event data for testing"""
    return ModuleLifecycleEventData(
        event_type=ModuleLifecycleEvent.MODULE_LOADED.value,
        event_id="lifecycle_123",
        timestamp=datetime.utcnow(),
        source_module="module-registry-service",
        module_id=1,
        module_name="test-module",
        module_version="1.0.0",
        installation_id=1,
        company_id=1
    )


@pytest.fixture
def sample_business_event_data():
    """Sample business event data for testing"""
    return BusinessEventData(
        event_type="partner.created",
        event_id="business_123",
        timestamp=datetime.utcnow(),
        source_module="partner-service",
        entity_type="partner",
        entity_id=123,
        action="created",
        changes={"name": "New Partner"},
        user_id=1,
        company_id=1
    )


@pytest.fixture
def test_event_bus():
    """Test event bus instance"""
    return EventBus(redis_url="redis://localhost:6379")


@pytest.fixture
def sample_loaded_module():
    """Sample loaded module for testing"""
    manifest = ModuleManifest(
        name="test-module",
        version="1.0.0",
        description="Test module",
        author="Test Author"
    )
    
    installation = ModuleInstallation(
        id=1,
        module_id=1,
        company_id=1,
        status=InstallationStatus.INSTALLED,
        installed_version="1.0.0",
        installed_by="test_user"
    )
    
    return LoadedModule(
        module_id=1,
        module_name="test-module",
        module_version="1.0.0",
        manifest=manifest,
        python_module=None,
        installation=installation
    )


def test_event_data_serialization(sample_event_data):
    """Test event data serialization and deserialization"""
    # Test to_dict
    event_dict = sample_event_data.to_dict()
    assert isinstance(event_dict, dict)
    assert event_dict['event_type'] == "test_event"
    assert event_dict['event_id'] == "test_123"
    assert isinstance(event_dict['timestamp'], str)
    
    # Test from_dict
    restored_event = EventData.from_dict(event_dict)
    assert restored_event.event_type == sample_event_data.event_type
    assert restored_event.event_id == sample_event_data.event_id
    assert isinstance(restored_event.timestamp, datetime)


def test_lifecycle_event_data_creation(sample_lifecycle_event_data):
    """Test lifecycle event data creation"""
    assert sample_lifecycle_event_data.module_id == 1
    assert sample_lifecycle_event_data.module_name == "test-module"
    assert sample_lifecycle_event_data.event_type == ModuleLifecycleEvent.MODULE_LOADED.value
    
    # Test serialization
    event_dict = sample_lifecycle_event_data.to_dict()
    assert event_dict['module_id'] == 1
    assert event_dict['module_name'] == "test-module"


def test_business_event_data_creation(sample_business_event_data):
    """Test business event data creation"""
    assert sample_business_event_data.entity_type == "partner"
    assert sample_business_event_data.entity_id == 123
    assert sample_business_event_data.action == "created"
    assert sample_business_event_data.changes == {"name": "New Partner"}
    
    # Test serialization
    event_dict = sample_business_event_data.to_dict()
    assert event_dict['entity_type'] == "partner"
    assert event_dict['entity_id'] == 123


def test_event_handler_creation():
    """Test event handler creation and matching"""
    async def test_handler(event_data):
        return f"Handled: {event_data.event_type}"
    
    handler = EventHandler(
        module_id=1,
        event_pattern="test\\..*",
        handler_func=test_handler,
        priority=100,
        event_type=EventType.BUSINESS_OBJECT
    )
    
    assert handler.module_id == 1
    assert handler.priority == 100
    assert handler.event_type == EventType.BUSINESS_OBJECT
    
    # Test pattern matching
    assert handler.matches("test.event")
    assert handler.matches("test.another_event")
    assert not handler.matches("other.event")


@pytest.mark.asyncio
async def test_event_handler_execution():
    """Test event handler execution"""
    async def async_handler(event_data):
        return f"Async: {event_data.event_type}"
    
    def sync_handler(event_data):
        return f"Sync: {event_data.event_type}"
    
    # Test async handler
    async_event_handler = EventHandler(1, "test.*", async_handler)
    result = await async_event_handler.handle(EventData("test.event", "123", datetime.utcnow()))
    assert result == "Async: test.event"
    
    # Test sync handler
    sync_event_handler = EventHandler(1, "test.*", sync_handler)
    result = await sync_event_handler.handle(EventData("test.event", "123", datetime.utcnow()))
    assert result == "Sync: test.event"


@pytest.mark.asyncio
async def test_event_handler_error_handling():
    """Test event handler error handling"""
    def error_handler(event_data):
        raise ValueError("Test error")
    
    handler = EventHandler(1, "test.*", error_handler)
    
    with pytest.raises(ValueError, match="Test error"):
        await handler.handle(EventData("test.event", "123", datetime.utcnow()))


def test_event_bus_initialization(test_event_bus):
    """Test event bus initialization"""
    assert test_event_bus.redis_url == "redis://localhost:6379"
    assert test_event_bus.redis_client is None
    assert isinstance(test_event_bus.event_handlers, dict)
    assert isinstance(test_event_bus.lifecycle_handlers, list)
    assert test_event_bus.running is False


@pytest.mark.asyncio
@patch('redis.asyncio.from_url')
async def test_event_bus_start_stop(mock_redis, test_event_bus):
    """Test event bus start and stop"""
    # Mock Redis client
    mock_client = AsyncMock()
    mock_redis.return_value = mock_client
    
    # Test start
    await test_event_bus.start()
    assert test_event_bus.running is True
    assert test_event_bus.redis_client is not None
    mock_client.ping.assert_called_once()
    
    # Test stop
    await test_event_bus.stop()
    assert test_event_bus.running is False
    mock_client.close.assert_called_once()


@pytest.mark.asyncio
@patch('redis.asyncio.from_url')
async def test_event_bus_publish_event(mock_redis, test_event_bus, sample_event_data):
    """Test event publishing"""
    # Mock Redis client
    mock_client = AsyncMock()
    mock_redis.return_value = mock_client
    
    await test_event_bus.start()
    
    # Test publish event
    await test_event_bus.publish_event(sample_event_data, "test_stream")
    
    mock_client.xadd.assert_called_once()
    call_args = mock_client.xadd.call_args
    assert call_args[0][0] == "test_stream"  # Stream name
    assert isinstance(call_args[0][1], dict)  # Event data


@pytest.mark.asyncio
@patch('redis.asyncio.from_url')
async def test_event_bus_publish_lifecycle_event(mock_redis, test_event_bus):
    """Test lifecycle event publishing"""
    # Mock Redis client
    mock_client = AsyncMock()
    mock_redis.return_value = mock_client
    
    await test_event_bus.start()
    
    # Test publish lifecycle event
    await test_event_bus.publish_lifecycle_event(
        event_type=ModuleLifecycleEvent.MODULE_LOADED,
        module_id=1,
        module_name="test-module",
        module_version="1.0.0",
        installation_id=1,
        company_id=1
    )
    
    mock_client.xadd.assert_called_once()
    call_args = mock_client.xadd.call_args
    assert call_args[0][0] == "module_lifecycle_events"


@pytest.mark.asyncio
@patch('redis.asyncio.from_url')
async def test_event_bus_publish_business_event(mock_redis, test_event_bus):
    """Test business event publishing"""
    # Mock Redis client
    mock_client = AsyncMock()
    mock_redis.return_value = mock_client
    
    await test_event_bus.start()
    
    # Test publish business event
    await test_event_bus.publish_business_event(
        event_type="partner.created",
        entity_type="partner",
        entity_id=123,
        action="created",
        changes={"name": "New Partner"},
        user_id=1,
        company_id=1,
        source_module="partner-service"
    )
    
    mock_client.xadd.assert_called_once()
    call_args = mock_client.xadd.call_args
    assert call_args[0][0] == "business_events"


def test_event_bus_register_event_handler(test_event_bus):
    """Test event handler registration"""
    def test_handler(event_data):
        return "handled"
    
    # Register business event handler
    handler = test_event_bus.register_event_handler(
        module_id=1,
        event_pattern="test\\..*",
        handler_func=test_handler,
        priority=100,
        event_type=EventType.BUSINESS_OBJECT
    )
    
    assert isinstance(handler, EventHandler)
    assert "test\\..*" in test_event_bus.event_handlers
    assert len(test_event_bus.event_handlers["test\\..*"]) == 1
    
    # Register lifecycle event handler
    lifecycle_handler = test_event_bus.register_event_handler(
        module_id=1,
        event_pattern="module_.*",
        handler_func=test_handler,
        event_type=EventType.MODULE_LIFECYCLE
    )
    
    assert len(test_event_bus.lifecycle_handlers) == 1


def test_event_bus_unregister_module_handlers(test_event_bus):
    """Test unregistering module event handlers"""
    def test_handler(event_data):
        return "handled"
    
    # Register some handlers
    test_event_bus.register_event_handler(1, "test1.*", test_handler)
    test_event_bus.register_event_handler(1, "test2.*", test_handler)
    test_event_bus.register_event_handler(2, "test3.*", test_handler)
    test_event_bus.register_event_handler(1, "lifecycle.*", test_handler, event_type=EventType.MODULE_LIFECYCLE)
    
    # Unregister handlers for module 1
    test_event_bus.unregister_module_handlers(1)
    
    # Check that module 1 handlers are removed
    assert len(test_event_bus.lifecycle_handlers) == 0
    assert "test1.*" not in test_event_bus.event_handlers
    assert "test2.*" not in test_event_bus.event_handlers
    assert "test3.*" in test_event_bus.event_handlers  # Module 2 handler should remain


@pytest.mark.asyncio
async def test_event_bus_handle_lifecycle_event(test_event_bus, sample_lifecycle_event_data):
    """Test lifecycle event handling"""
    handled_events = []
    
    def lifecycle_handler(event_data):
        handled_events.append(event_data)
        return "handled"
    
    # Register lifecycle handler
    test_event_bus.register_event_handler(
        module_id=1,
        event_pattern="module_.*",
        handler_func=lifecycle_handler,
        event_type=EventType.MODULE_LIFECYCLE
    )
    
    # Handle lifecycle event
    await test_event_bus._handle_lifecycle_event(sample_lifecycle_event_data)
    
    assert len(handled_events) == 1
    assert handled_events[0].module_id == 1


@pytest.mark.asyncio
async def test_event_bus_handle_business_event(test_event_bus, sample_business_event_data):
    """Test business event handling"""
    handled_events = []
    
    def business_handler(event_data):
        handled_events.append(event_data)
        return "handled"
    
    # Register business event handler
    test_event_bus.register_event_handler(
        module_id=1,
        event_pattern="partner\\..*",
        handler_func=business_handler,
        event_type=EventType.BUSINESS_OBJECT
    )
    
    # Handle business event
    await test_event_bus._handle_business_event(sample_business_event_data)
    
    assert len(handled_events) == 1
    assert handled_events[0].entity_type == "partner"


@pytest.mark.asyncio
async def test_event_bus_process_stream_message(test_event_bus):
    """Test processing messages from Redis stream"""
    # Test lifecycle event processing
    lifecycle_fields = {
        b'event_type': b'module_loaded',
        b'event_id': b'test_123',
        b'timestamp': datetime.utcnow().isoformat().encode(),
        b'module_id': b'1',
        b'module_name': b'test-module',
        b'module_version': b'1.0.0',
        b'installation_id': b'1',
        b'company_id': b'1'
    }
    
    await test_event_bus._process_stream_message("module_lifecycle_events", lifecycle_fields)
    
    # Test business event processing
    business_fields = {
        b'event_type': b'partner.created',
        b'event_id': b'business_123',
        b'timestamp': datetime.utcnow().isoformat().encode(),
        b'entity_type': b'partner',
        b'entity_id': b'123',
        b'action': b'created',
        b'changes': b'{"name": "New Partner"}',
        b'user_id': b'1',
        b'company_id': b'1'
    }
    
    await test_event_bus._process_stream_message("business_events", business_fields)


def test_module_event_manager_initialization():
    """Test module event manager initialization"""
    mock_event_bus = MagicMock()
    manager = ModuleEventManager(mock_event_bus)
    
    assert manager.event_bus == mock_event_bus


@pytest.mark.asyncio
async def test_module_event_manager_register_handlers(sample_loaded_module):
    """Test registering module event handlers"""
    mock_event_bus = MagicMock()
    manager = ModuleEventManager(mock_event_bus)
    
    # Add event handlers to manifest
    from app.framework.manifest import ModuleEventHandler
    sample_loaded_module.manifest.event_handlers = [
        ModuleEventHandler(
            event_type=EventType.BUSINESS_OBJECT,
            event_pattern="partner\\..*",
            handler="test_module.handlers:handle_partner_event"
        )
    ]
    
    # Add event handlers to loaded module
    sample_loaded_module.event_handlers = {
        "partner\\..*": lambda event: "handled"
    }
    
    await manager.register_module_event_handlers(sample_loaded_module)
    
    mock_event_bus.register_event_handler.assert_called_once()


@pytest.mark.asyncio
async def test_module_event_manager_unregister_handlers():
    """Test unregistering module event handlers"""
    mock_event_bus = MagicMock()
    manager = ModuleEventManager(mock_event_bus)
    
    await manager.unregister_module_event_handlers(1)
    
    mock_event_bus.unregister_module_handlers.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_module_event_manager_publish_lifecycle_event(sample_loaded_module):
    """Test publishing module lifecycle events"""
    mock_event_bus = AsyncMock()
    manager = ModuleEventManager(mock_event_bus)
    
    await manager.publish_module_lifecycle_event(
        event_type=ModuleLifecycleEvent.MODULE_LOADED,
        loaded_module=sample_loaded_module
    )
    
    mock_event_bus.publish_lifecycle_event.assert_called_once()


def test_event_handler_priority_sorting(test_event_bus):
    """Test event handler priority sorting"""
    def handler1(event_data):
        return "handler1"
    
    def handler2(event_data):
        return "handler2"
    
    def handler3(event_data):
        return "handler3"
    
    # Register handlers with different priorities
    test_event_bus.register_event_handler(1, "test.*", handler2, priority=200)
    test_event_bus.register_event_handler(1, "test.*", handler1, priority=100)
    test_event_bus.register_event_handler(1, "test.*", handler3, priority=150)
    
    handlers = test_event_bus.event_handlers["test.*"]
    assert len(handlers) == 3
    
    # Check priority sorting (lower priority = higher precedence)
    assert handlers[0].priority == 100
    assert handlers[1].priority == 150
    assert handlers[2].priority == 200


@pytest.mark.asyncio
async def test_event_bus_error_in_handler(test_event_bus):
    """Test error handling in event handlers"""
    def error_handler(event_data):
        raise ValueError("Handler error")
    
    test_event_bus.register_event_handler(
        1, "test.*", error_handler, event_type=EventType.MODULE_LIFECYCLE
    )
    
    event_data = ModuleLifecycleEventData(
        event_type="test.event",
        event_id="test_123",
        timestamp=datetime.utcnow(),
        module_id=1,
        module_name="test",
        module_version="1.0.0",
        installation_id=1
    )
    
    # Should not raise exception, but log error
    await test_event_bus._handle_lifecycle_event(event_data)


def test_global_event_bus_and_manager():
    """Test global event bus and manager instances"""
    assert isinstance(event_bus, EventBus)
    assert isinstance(event_manager, ModuleEventManager)
    assert event_manager.event_bus == event_bus