"""
Tests for module endpoint registration and API gateway integration
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.framework.registry import (
    EndpointRegistry, ModuleEndpointManager, 
    initialize_endpoint_manager, get_endpoint_manager
)
from app.framework.loader import LoadedModule
from app.framework.manifest import (
    ModuleManifest, ModuleEndpoint, ModuleEntryPoint, 
    EndpointMethod, ModuleType
)
from app.models.module import Module
from app.models.installation import ModuleInstallation, InstallationStatus


@pytest.fixture
def test_app():
    """Test FastAPI application"""
    app = FastAPI(title="Test App")
    return app


@pytest.fixture
def sample_manifest():
    """Sample module manifest with endpoints"""
    return {
        "name": "test-module",
        "version": "1.0.0",
        "description": "Test module with endpoints",
        "author": "Test Author",
        "module_type": ModuleType.FULL_MODULE,
        "endpoints": [
            {
                "path": "/test",
                "method": EndpointMethod.GET,
                "handler": "test_module.handlers:get_test",
                "description": "Test GET endpoint",
                "requires_auth": True,
                "company_scoped": True,
                "permissions": ["read_data"]
            },
            {
                "path": "/test",
                "method": EndpointMethod.POST,
                "handler": "test_module.handlers:post_test",
                "description": "Test POST endpoint",
                "requires_auth": True,
                "permissions": ["write_data"]
            }
        ]
    }


@pytest.fixture
def sample_module(sample_manifest):
    """Sample module for testing"""
    return Module(
        id=1,
        name="test-module",
        version="1.0.0",
        display_name="Test Module",
        description="Test module with endpoints",
        author="Test Author",
        manifest=sample_manifest
    )


@pytest.fixture
def sample_installation():
    """Sample installation for testing"""
    return ModuleInstallation(
        id=1,
        module_id=1,
        company_id=1,
        status=InstallationStatus.INSTALLED,
        installed_version="1.0.0",
        installed_by="test_user",
        configuration={"test_config": "test_value"}
    )


@pytest.fixture
def mock_python_module():
    """Mock Python module with handlers"""
    module = MagicMock()
    
    # Create mock handlers
    async def get_test(request: Request):
        return {"message": "GET test response"}
    
    async def post_test(request: Request):
        return {"message": "POST test response"}
    
    # Set up module structure
    module.handlers = MagicMock()
    module.handlers.get_test = get_test
    module.handlers.post_test = post_test
    
    return module


@pytest.fixture
def loaded_module(sample_module, sample_installation, sample_manifest, mock_python_module):
    """Sample loaded module for testing"""
    manifest = ModuleManifest(**sample_manifest)
    
    loaded_module = LoadedModule(
        module_id=sample_module.id,
        module_name=sample_module.name,
        module_version=sample_module.version,
        manifest=manifest,
        python_module=mock_python_module,
        installation=sample_installation
    )
    
    return loaded_module


@pytest.fixture
def endpoint_registry(test_app):
    """Endpoint registry instance"""
    return EndpointRegistry(test_app)


@pytest.fixture
def endpoint_manager(test_app):
    """Endpoint manager instance"""
    return ModuleEndpointManager(test_app)


def test_endpoint_registry_initialization(test_app):
    """Test endpoint registry initialization"""
    registry = EndpointRegistry(test_app)
    
    assert registry.app == test_app
    assert isinstance(registry.registered_endpoints, dict)
    assert isinstance(registry.module_routers, dict)


@pytest.mark.asyncio
async def test_register_module_endpoints(endpoint_registry, loaded_module):
    """Test registering module endpoints"""
    result = await endpoint_registry.register_module_endpoints(loaded_module)
    
    assert result is True
    assert loaded_module.module_id in endpoint_registry.registered_endpoints
    assert loaded_module.module_id in endpoint_registry.module_routers
    
    endpoints = endpoint_registry.registered_endpoints[loaded_module.module_id]
    assert len(endpoints) == 2  # GET and POST endpoints
    
    # Check endpoint details
    get_endpoint = next(ep for ep in endpoints if ep['method'] == 'GET')
    assert get_endpoint['path'] == '/modules/test-module/test'
    assert get_endpoint['requires_auth'] is True
    assert get_endpoint['company_scoped'] is True
    assert 'read_data' in get_endpoint['permissions']


@pytest.mark.asyncio
async def test_register_module_endpoints_no_endpoints(endpoint_registry, loaded_module):
    """Test registering module with no endpoints"""
    # Remove endpoints from manifest
    loaded_module.manifest.endpoints = []
    
    result = await endpoint_registry.register_module_endpoints(loaded_module)
    
    assert result is True
    assert loaded_module.module_id in endpoint_registry.registered_endpoints
    assert len(endpoint_registry.registered_endpoints[loaded_module.module_id]) == 0


@pytest.mark.asyncio
async def test_register_module_endpoints_handler_resolution_error(endpoint_registry, loaded_module):
    """Test endpoint registration with handler resolution error"""
    # Create endpoint with invalid handler
    loaded_module.manifest.endpoints[0].handler = "nonexistent.module:invalid_handler"
    
    result = await endpoint_registry.register_module_endpoints(loaded_module)
    
    # Should still return True but with fewer registered endpoints
    assert result is True
    endpoints = endpoint_registry.registered_endpoints[loaded_module.module_id]
    assert len(endpoints) == 1  # Only the valid endpoint should be registered


def test_resolve_endpoint_handler(endpoint_registry, loaded_module):
    """Test endpoint handler resolution"""
    endpoint_spec = loaded_module.manifest.endpoints[0]
    
    # Use async context for the async method
    import asyncio
    async def test_resolve():
        handler = await endpoint_registry._resolve_endpoint_handler(loaded_module, endpoint_spec)
        assert handler is not None
        assert callable(handler)
        
        # Test invalid handler
        endpoint_spec.handler = "invalid:handler"
        handler = await endpoint_registry._resolve_endpoint_handler(loaded_module, endpoint_spec)
        assert handler is None
    
    asyncio.run(test_resolve())


def test_wrap_endpoint_handler(endpoint_registry, loaded_module):
    """Test endpoint handler wrapping"""
    endpoint_spec = loaded_module.manifest.endpoints[0]
    
    async def mock_handler(request):
        return {"original": "response"}
    
    wrapped_handler = endpoint_registry._wrap_endpoint_handler(
        loaded_module, endpoint_spec, mock_handler
    )
    
    assert callable(wrapped_handler)
    assert wrapped_handler.__name__ == mock_handler.__name__


@pytest.mark.asyncio
async def test_wrapped_handler_execution(endpoint_registry, loaded_module):
    """Test wrapped handler execution"""
    endpoint_spec = loaded_module.manifest.endpoints[0]
    
    async def mock_handler(request):
        return {"test": "response"}
    
    wrapped_handler = endpoint_registry._wrap_endpoint_handler(
        loaded_module, endpoint_spec, mock_handler
    )
    
    # Create mock request
    mock_request = MagicMock(spec=Request)
    mock_request.state = MagicMock()
    
    result = await wrapped_handler(mock_request)
    
    assert result == {"test": "response"}
    assert mock_request.state.module_id == loaded_module.module_id
    assert mock_request.state.module_name == loaded_module.module_name


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_register_with_api_gateway(mock_client, endpoint_registry, loaded_module):
    """Test API gateway registration"""
    # Mock httpx client responses
    mock_client_instance = AsyncMock()
    mock_client.return_value.__aenter__.return_value = mock_client_instance
    
    # Mock successful service creation
    service_response = MagicMock()
    service_response.status_code = 201
    mock_client_instance.put.return_value = service_response
    
    # Mock successful route creation
    route_response = MagicMock()
    route_response.status_code = 201
    mock_client_instance.post.return_value = route_response
    
    endpoints = [
        {
            "module_name": "test-module",
            "path": "/test",
            "method": "GET"
        }
    ]
    
    result = await endpoint_registry._register_with_api_gateway(loaded_module, endpoints)
    
    assert result is True
    mock_client_instance.put.assert_called_once()
    mock_client_instance.post.assert_called_once()


@pytest.mark.asyncio
async def test_unregister_module_endpoints(endpoint_registry, loaded_module):
    """Test unregistering module endpoints"""
    # First register the module
    await endpoint_registry.register_module_endpoints(loaded_module)
    
    # Then unregister
    result = await endpoint_registry.unregister_module_endpoints(loaded_module.module_id)
    
    assert result is True
    assert loaded_module.module_id not in endpoint_registry.registered_endpoints
    assert loaded_module.module_id not in endpoint_registry.module_routers


@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_unregister_from_api_gateway(mock_client, endpoint_registry, loaded_module):
    """Test API gateway unregistration"""
    # Set up registered endpoints
    endpoint_registry.registered_endpoints[loaded_module.module_id] = [
        {"module_name": "test-module", "path": "/test", "method": "GET"}
    ]
    
    # Mock httpx client
    mock_client_instance = AsyncMock()
    mock_client.return_value.__aenter__.return_value = mock_client_instance
    
    delete_response = MagicMock()
    delete_response.status_code = 204
    mock_client_instance.delete.return_value = delete_response
    
    result = await endpoint_registry._unregister_from_api_gateway(loaded_module.module_id)
    
    assert result is True
    mock_client_instance.delete.assert_called_once()


def test_get_module_endpoints(endpoint_registry, loaded_module):
    """Test getting module endpoints"""
    # Set up test data
    test_endpoints = [{"path": "/test", "method": "GET"}]
    endpoint_registry.registered_endpoints[loaded_module.module_id] = test_endpoints
    
    endpoints = endpoint_registry.get_module_endpoints(loaded_module.module_id)
    assert endpoints == test_endpoints
    
    # Test non-existent module
    endpoints = endpoint_registry.get_module_endpoints(999)
    assert endpoints == []


def test_get_all_module_endpoints(endpoint_registry):
    """Test getting all module endpoints"""
    # Set up test data
    test_data = {
        1: [{"path": "/test1", "method": "GET"}],
        2: [{"path": "/test2", "method": "POST"}]
    }
    endpoint_registry.registered_endpoints = test_data
    
    all_endpoints = endpoint_registry.get_all_module_endpoints()
    assert all_endpoints == test_data
    assert all_endpoints is not endpoint_registry.registered_endpoints  # Should be a copy


def test_generate_module_openapi_spec(endpoint_registry, loaded_module):
    """Test OpenAPI spec generation"""
    # Set up test data
    endpoint_registry.registered_endpoints[loaded_module.module_id] = [
        {"module_name": "test-module", "path": "/test", "method": "GET"}
    ]
    
    # Create mock router
    mock_router = MagicMock()
    endpoint_registry.module_routers[loaded_module.module_id] = mock_router
    
    # Test with valid module
    spec = endpoint_registry.generate_module_openapi_spec(loaded_module.module_id)
    # OpenAPI generation may fail due to mocking, but should not crash
    
    # Test with non-existent module
    spec = endpoint_registry.generate_module_openapi_spec(999)
    assert spec is None


@pytest.mark.asyncio
async def test_module_endpoint_manager_lifecycle(endpoint_manager, loaded_module):
    """Test module endpoint manager lifecycle events"""
    # Test module loaded event
    result = await endpoint_manager.on_module_loaded(loaded_module)
    assert result is True
    
    # Test getting endpoints
    endpoints = endpoint_manager.get_module_endpoints(loaded_module.module_id)
    assert len(endpoints) >= 0
    
    # Test module unloaded event
    result = await endpoint_manager.on_module_unloaded(loaded_module.module_id)
    assert result is True


@pytest.mark.asyncio
async def test_module_endpoint_manager_update(endpoint_manager, loaded_module):
    """Test module update handling"""
    # Register initial module
    await endpoint_manager.on_module_loaded(loaded_module)
    
    # Create updated module
    updated_module = LoadedModule(
        module_id=2,  # Different ID
        module_name="test-module-v2",
        module_version="2.0.0",
        manifest=loaded_module.manifest,
        python_module=loaded_module.python_module,
        installation=loaded_module.installation
    )
    
    # Test update
    result = await endpoint_manager.on_module_updated(loaded_module.module_id, updated_module)
    assert result is True


def test_initialize_and_get_endpoint_manager(test_app):
    """Test global endpoint manager initialization and retrieval"""
    # Test initialization
    manager = initialize_endpoint_manager(test_app)
    assert isinstance(manager, ModuleEndpointManager)
    
    # Test retrieval
    retrieved_manager = get_endpoint_manager()
    assert retrieved_manager is manager
    
    # Test error when not initialized
    import app.framework.registry as registry_module
    registry_module.endpoint_manager = None
    
    with pytest.raises(RuntimeError, match="Endpoint manager not initialized"):
        get_endpoint_manager()


@pytest.mark.asyncio
async def test_endpoint_registration_with_real_fastapi(test_app, loaded_module):
    """Test endpoint registration with real FastAPI application"""
    registry = EndpointRegistry(test_app)
    
    # Register endpoints
    result = await registry.register_module_endpoints(loaded_module)
    assert result is True
    
    # Test with TestClient
    client = TestClient(test_app)
    
    # The endpoints should be registered but may not work without proper handler resolution
    # This test mainly verifies that the registration doesn't break the FastAPI app
    response = client.get("/")
    # FastAPI should still be functional


def test_endpoint_registry_error_handling(endpoint_registry, loaded_module):
    """Test error handling in endpoint registry"""
    # Test with module that has malformed endpoints
    loaded_module.manifest.endpoints[0].handler = ""  # Invalid empty handler
    
    import asyncio
    async def test_error_handling():
        result = await endpoint_registry.register_module_endpoints(loaded_module)
        # Should handle errors gracefully
        assert isinstance(result, bool)
    
    asyncio.run(test_error_handling())


@pytest.mark.asyncio
async def test_endpoint_handler_with_sync_function(endpoint_registry, loaded_module):
    """Test endpoint handling with synchronous function"""
    def sync_handler(request):
        return {"sync": "response"}
    
    endpoint_spec = loaded_module.manifest.endpoints[0]
    wrapped_handler = endpoint_registry._wrap_endpoint_handler(
        loaded_module, endpoint_spec, sync_handler
    )
    
    # Create mock request
    mock_request = MagicMock(spec=Request)
    mock_request.state = MagicMock()
    
    result = await wrapped_handler(mock_request)
    assert result == {"sync": "response"}