"""
Module endpoint registration and API gateway integration
"""
import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi
import httpx
import logging
from app.framework.loader import LoadedModule, plugin_loader
from app.framework.manifest import ModuleEndpoint, EndpointMethod
from app.core.config import settings

logger = logging.getLogger(__name__)


class EndpointRegistry:
    """Registry for module endpoints with API gateway integration"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.registered_endpoints: Dict[int, List[Dict[str, Any]]] = {}
        self.module_routers: Dict[int, APIRouter] = {}
        
    async def register_module_endpoints(self, loaded_module: LoadedModule) -> bool:
        """Register all endpoints for a loaded module"""
        try:
            module_router = APIRouter(
                prefix=f"/modules/{loaded_module.module_name}",
                tags=[f"Module: {loaded_module.manifest.display_name}"]
            )
            
            registered_endpoints = []
            
            for endpoint_spec in loaded_module.manifest.endpoints or []:
                endpoint_info = await self._register_single_endpoint(
                    loaded_module, endpoint_spec, module_router
                )
                if endpoint_info:
                    registered_endpoints.append(endpoint_info)
            
            # Include router in main app
            self.app.include_router(module_router)
            
            # Store registration info
            self.registered_endpoints[loaded_module.module_id] = registered_endpoints
            self.module_routers[loaded_module.module_id] = module_router
            
            # Register with API gateway if configured
            await self._register_with_api_gateway(loaded_module, registered_endpoints)
            
            logger.info(f"Registered {len(registered_endpoints)} endpoints for module {loaded_module.full_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register endpoints for module {loaded_module.full_name}: {e}")
            return False
    
    async def _register_single_endpoint(
        self, 
        loaded_module: LoadedModule, 
        endpoint_spec: ModuleEndpoint,
        router: APIRouter
    ) -> Optional[Dict[str, Any]]:
        """Register a single endpoint"""
        try:
            # Resolve handler function
            handler_func = await self._resolve_endpoint_handler(loaded_module, endpoint_spec)
            if not handler_func:
                return None
            
            # Create wrapped handler with security and validation
            wrapped_handler = self._wrap_endpoint_handler(
                loaded_module, endpoint_spec, handler_func
            )
            
            # Add route to router
            route_kwargs = {
                "path": endpoint_spec.path,
                "endpoint": wrapped_handler,
                "methods": [endpoint_spec.method.value],
                "name": f"{loaded_module.module_name}_{endpoint_spec.path.replace('/', '_')}",
                "tags": endpoint_spec.tags or []
            }
            
            # Add response model if specified
            if hasattr(handler_func, '__annotations__'):
                return_annotation = handler_func.__annotations__.get('return')
                if return_annotation:
                    route_kwargs["response_model"] = return_annotation
            
            router.add_api_route(**route_kwargs)
            
            endpoint_info = {
                "module_id": loaded_module.module_id,
                "module_name": loaded_module.module_name,
                "path": f"/modules/{loaded_module.module_name}{endpoint_spec.path}",
                "method": endpoint_spec.method.value,
                "handler": endpoint_spec.handler,
                "description": endpoint_spec.description,
                "requires_auth": endpoint_spec.requires_auth,
                "company_scoped": endpoint_spec.company_scoped,
                "permissions": endpoint_spec.permissions
            }
            
            logger.debug(f"Registered endpoint {endpoint_spec.method.value} {endpoint_info['path']}")
            return endpoint_info
            
        except Exception as e:
            logger.error(f"Failed to register endpoint {endpoint_spec.path}: {e}")
            return None
    
    async def _resolve_endpoint_handler(
        self, 
        loaded_module: LoadedModule, 
        endpoint_spec: ModuleEndpoint
    ) -> Optional[Callable]:
        """Resolve endpoint handler function"""
        try:
            # Parse handler reference (module.path:function)
            module_path, function_name = endpoint_spec.handler.split(':')
            
            # Navigate to the function in the loaded module
            parts = module_path.split('.')
            current = loaded_module.python_module
            
            for part in parts:
                current = getattr(current, part)
            
            handler_func = getattr(current, function_name)
            
            if not callable(handler_func):
                raise ValueError(f"Handler {endpoint_spec.handler} is not callable")
            
            return handler_func
            
        except Exception as e:
            logger.error(f"Could not resolve handler {endpoint_spec.handler}: {e}")
            return None
    
    def _wrap_endpoint_handler(
        self, 
        loaded_module: LoadedModule, 
        endpoint_spec: ModuleEndpoint,
        handler_func: Callable
    ) -> Callable:
        """Wrap endpoint handler with security and validation"""
        
        async def wrapped_handler(request: Request, *args, **kwargs):
            try:
                # Add module context to request
                request.state.module_id = loaded_module.module_id
                request.state.module_name = loaded_module.module_name
                request.state.module_config = loaded_module.installation.configuration
                
                # TODO: Add authentication check if required
                if endpoint_spec.requires_auth:
                    # Integration with auth service would go here
                    pass
                
                # TODO: Add permission check
                if endpoint_spec.permissions:
                    # Check user permissions
                    pass
                
                # TODO: Add company scoping if required
                if endpoint_spec.company_scoped:
                    # Ensure user has access to company
                    pass
                
                # Call the actual handler
                if asyncio.iscoroutinefunction(handler_func):
                    return await handler_func(request, *args, **kwargs)
                else:
                    return handler_func(request, *args, **kwargs)
                    
            except Exception as e:
                logger.error(f"Error in module endpoint {endpoint_spec.path}: {e}")
                raise HTTPException(status_code=500, detail=f"Module endpoint error: {str(e)}")
        
        # Copy function metadata for OpenAPI documentation
        wrapped_handler.__name__ = handler_func.__name__
        wrapped_handler.__doc__ = handler_func.__doc__ or endpoint_spec.description
        
        return wrapped_handler
    
    async def _register_with_api_gateway(
        self, 
        loaded_module: LoadedModule, 
        endpoints: List[Dict[str, Any]]
    ) -> bool:
        """Register module endpoints with Kong API Gateway"""
        try:
            # Kong admin API configuration
            kong_admin_url = "http://kong:8001"  # Adjust based on your setup
            
            async with httpx.AsyncClient() as client:
                # Create service for module
                service_data = {
                    "name": f"module-{loaded_module.module_name}",
                    "url": f"http://module-registry-service:8005/modules/{loaded_module.module_name}"
                }
                
                # Create or update service
                service_response = await client.put(
                    f"{kong_admin_url}/services/{service_data['name']}",
                    json=service_data,
                    timeout=5.0
                )
                
                if service_response.status_code not in [200, 201]:
                    logger.warning(f"Failed to register service with Kong: {service_response.text}")
                    return False
                
                # Create routes for each endpoint
                for endpoint in endpoints:
                    route_data = {
                        "name": f"module-{loaded_module.module_name}-{endpoint['path'].replace('/', '-')}",
                        "paths": [endpoint['path']],
                        "methods": [endpoint['method']],
                        "strip_path": False
                    }
                    
                    route_response = await client.post(
                        f"{kong_admin_url}/services/{service_data['name']}/routes",
                        json=route_data,
                        timeout=5.0
                    )
                    
                    if route_response.status_code not in [200, 201]:
                        logger.warning(f"Failed to register route with Kong: {route_response.text}")
                
                logger.info(f"Registered module {loaded_module.module_name} with API Gateway")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register with API Gateway: {e}")
            return False
    
    async def unregister_module_endpoints(self, module_id: int) -> bool:
        """Unregister all endpoints for a module"""
        try:
            if module_id not in self.registered_endpoints:
                return True
            
            # Remove from API gateway
            await self._unregister_from_api_gateway(module_id)
            
            # Remove router from app (this is tricky with FastAPI)
            # For now, we'll mark as inactive rather than removing
            if module_id in self.module_routers:
                # TODO: Implement proper router removal
                pass
            
            # Clean up registration data
            if module_id in self.registered_endpoints:
                del self.registered_endpoints[module_id]
            
            if module_id in self.module_routers:
                del self.module_routers[module_id]
            
            logger.info(f"Unregistered endpoints for module {module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister endpoints for module {module_id}: {e}")
            return False
    
    async def _unregister_from_api_gateway(self, module_id: int) -> bool:
        """Unregister module from Kong API Gateway"""
        try:
            if module_id not in self.registered_endpoints:
                return True
            
            kong_admin_url = "http://kong:8001"
            endpoints = self.registered_endpoints[module_id]
            
            if not endpoints:
                return True
            
            module_name = endpoints[0]['module_name']
            
            async with httpx.AsyncClient() as client:
                # Delete service (this will cascade delete routes)
                service_name = f"module-{module_name}"
                response = await client.delete(
                    f"{kong_admin_url}/services/{service_name}",
                    timeout=5.0
                )
                
                if response.status_code not in [204, 404]:
                    logger.warning(f"Failed to unregister service from Kong: {response.text}")
                
                logger.info(f"Unregistered module {module_name} from API Gateway")
                return True
                
        except Exception as e:
            logger.error(f"Failed to unregister from API Gateway: {e}")
            return False
    
    def get_module_endpoints(self, module_id: int) -> List[Dict[str, Any]]:
        """Get registered endpoints for a module"""
        return self.registered_endpoints.get(module_id, [])
    
    def get_all_module_endpoints(self) -> Dict[int, List[Dict[str, Any]]]:
        """Get all registered module endpoints"""
        return self.registered_endpoints.copy()
    
    def generate_module_openapi_spec(self, module_id: int) -> Optional[Dict[str, Any]]:
        """Generate OpenAPI specification for module endpoints"""
        if module_id not in self.module_routers:
            return None
        
        try:
            module_router = self.module_routers[module_id]
            endpoints = self.registered_endpoints.get(module_id, [])
            
            if not endpoints:
                return None
            
            module_name = endpoints[0]['module_name']
            
            # Create a temporary app with just this module's router
            temp_app = FastAPI(title=f"Module: {module_name}")
            temp_app.include_router(module_router)
            
            # Generate OpenAPI spec
            openapi_spec = get_openapi(
                title=f"Module: {module_name}",
                version="1.0.0",
                description=f"API endpoints for module {module_name}",
                routes=temp_app.routes
            )
            
            return openapi_spec
            
        except Exception as e:
            logger.error(f"Failed to generate OpenAPI spec for module {module_id}: {e}")
            return None


class ModuleEndpointManager:
    """Manager for module endpoint lifecycle"""
    
    def __init__(self, app: FastAPI):
        self.registry = EndpointRegistry(app)
        
    async def on_module_loaded(self, loaded_module: LoadedModule) -> bool:
        """Handle module loaded event"""
        return await self.registry.register_module_endpoints(loaded_module)
    
    async def on_module_unloaded(self, module_id: int) -> bool:
        """Handle module unloaded event"""
        return await self.registry.unregister_module_endpoints(module_id)
    
    async def on_module_updated(self, old_module_id: int, new_loaded_module: LoadedModule) -> bool:
        """Handle module updated event"""
        # Unregister old endpoints
        await self.registry.unregister_module_endpoints(old_module_id)
        
        # Register new endpoints
        return await self.registry.register_module_endpoints(new_loaded_module)
    
    def get_module_endpoints(self, module_id: int) -> List[Dict[str, Any]]:
        """Get endpoints for a specific module"""
        return self.registry.get_module_endpoints(module_id)
    
    def get_all_endpoints(self) -> Dict[int, List[Dict[str, Any]]]:
        """Get all registered module endpoints"""
        return self.registry.get_all_module_endpoints()
    
    def get_module_openapi_spec(self, module_id: int) -> Optional[Dict[str, Any]]:
        """Get OpenAPI specification for module"""
        return self.registry.generate_module_openapi_spec(module_id)


# Global endpoint manager (to be initialized with FastAPI app)
endpoint_manager: Optional[ModuleEndpointManager] = None


def initialize_endpoint_manager(app: FastAPI) -> ModuleEndpointManager:
    """Initialize the global endpoint manager"""
    global endpoint_manager
    endpoint_manager = ModuleEndpointManager(app)
    return endpoint_manager


def get_endpoint_manager() -> ModuleEndpointManager:
    """Get the global endpoint manager"""
    if endpoint_manager is None:
        raise RuntimeError("Endpoint manager not initialized")
    return endpoint_manager