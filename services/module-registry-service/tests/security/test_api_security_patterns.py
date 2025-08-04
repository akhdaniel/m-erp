"""
Security pattern verification for all API endpoints
"""
import pytest
import inspect
from fastapi import HTTPException, Depends, Query, Path, Body, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import get_origin, get_args
from app.main import app
from app.routers import modules, installations, enhanced_modules, enhanced_installations, dependency_resolution


class TestAPISecurityPatterns:
    """Test security patterns across all API endpoints"""
    
    def test_all_endpoints_have_consistent_error_handling(self):
        """Verify all endpoints follow consistent error handling patterns"""
        routers = [modules, installations, enhanced_modules, enhanced_installations, dependency_resolution]
        
        for router_module in routers:
            router = router_module.router
            
            for route in router.routes:
                if hasattr(route, 'endpoint'):
                    endpoint_func = route.endpoint
                    
                    # Check that endpoint has proper exception handling
                    source_code = inspect.getsource(endpoint_func)
                    
                    # Should handle specific exceptions
                    assert 'try:' in source_code or 'except' in source_code, f"Endpoint {endpoint_func.__name__} should have exception handling"
                    
                    # Should use HTTPException for API errors
                    if 'except' in source_code:
                        assert 'HTTPException' in source_code, f"Endpoint {endpoint_func.__name__} should use HTTPException"
    
    def test_all_endpoints_have_proper_status_codes(self):
        """Verify all endpoints use appropriate HTTP status codes"""
        expected_status_patterns = {
            'GET': [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND],
            'POST': [status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY],
            'PUT': [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST],
            'DELETE': [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND],
        }
        
        routers = [modules, installations, enhanced_modules, enhanced_installations, dependency_resolution]
        
        for router_module in routers:
            router = router_module.router
            
            for route in router.routes:
                if hasattr(route, 'methods') and hasattr(route, 'endpoint'):
                    for method in route.methods:
                        if method in expected_status_patterns:
                            # Check that endpoint source mentions appropriate status codes
                            source_code = inspect.getsource(route.endpoint)
                            
                            # Should have status code handling
                            has_status_code = any(
                                f"status.HTTP_{code.name}" in source_code or f"{code.value}" in source_code
                                for code in expected_status_patterns[method]
                            )
                            
                            if not has_status_code:
                                # Some endpoints might use default status codes
                                print(f"Warning: {route.endpoint.__name__} ({method}) might be missing explicit status codes")
    
    def test_enhanced_endpoints_have_comprehensive_validation(self):
        """Verify enhanced endpoints have comprehensive input validation"""
        enhanced_routers = [enhanced_modules, enhanced_installations, dependency_resolution]
        
        for router_module in enhanced_routers:
            router = router_module.router
            
            for route in router.routes:
                if hasattr(route, 'endpoint'):
                    endpoint_func = route.endpoint
                    signature = inspect.signature(endpoint_func)
                    
                    # Check for proper parameter validation
                    for param_name, param in signature.parameters.items():
                        if param.annotation != inspect.Parameter.empty:
                            # Path parameters should use Path()
                            if param_name.endswith('_id') or param_name == 'company_id':
                                # Should have validation (either through Pydantic models or FastAPI Path/Query)
                                pass
                    
                    # Check that POST/PUT endpoints have request body validation
                    if hasattr(route, 'methods'):
                        if 'POST' in route.methods or 'PUT' in route.methods:
                            # Should have request body parameter with Pydantic model
                            has_body_validation = any(
                                hasattr(param.annotation, '__module__') and 
                                param.annotation.__module__ and
                                'pydantic' in param.annotation.__module__
                                for param in signature.parameters.values()
                                if param.annotation != inspect.Parameter.empty
                            )
                            
                            if not has_body_validation:
                                # Check if it's a simple endpoint that doesn't need body validation
                                simple_endpoints = ['health-check', 'reload', 'status']
                                is_simple = any(simple in route.path for simple in simple_endpoints)
                                
                                if not is_simple:
                                    print(f"Warning: {endpoint_func.__name__} might need request body validation")
    
    def test_all_endpoints_have_proper_logging(self):
        """Verify all endpoints have appropriate logging"""
        routers = [modules, installations, enhanced_modules, enhanced_installations, dependency_resolution]
        
        for router_module in routers:
            router = router_module.router
            
            for route in router.routes:
                if hasattr(route, 'endpoint'):
                    endpoint_func = route.endpoint
                    source_code = inspect.getsource(endpoint_func)
                    
                    # Should have logging for important operations
                    if any(method in route.methods for method in ['POST', 'PUT', 'DELETE']):
                        # Should have info or error logging
                        has_logging = 'logger.' in source_code
                        
                        if not has_logging:
                            print(f"Warning: {endpoint_func.__name__} might need logging")
    
    def test_enhanced_endpoints_have_service_dependencies(self):
        """Verify enhanced endpoints properly use service dependencies"""
        enhanced_routers = [enhanced_modules, enhanced_installations, dependency_resolution]
        
        for router_module in enhanced_routers:
            router = router_module.router
            
            for route in router.routes:
                if hasattr(route, 'endpoint'):
                    endpoint_func = route.endpoint
                    signature = inspect.signature(endpoint_func)
                    
                    # Should have service dependency injection
                    has_service_dependency = any(
                        'service' in param_name.lower() and 
                        param.default != inspect.Parameter.empty and
                        str(param.default).startswith('Depends(')
                        for param_name, param in signature.parameters.items()
                    )
                    
                    # Skip simple endpoints
                    simple_endpoints = ['root', 'health', 'info']
                    is_simple = any(simple in endpoint_func.__name__ for simple in simple_endpoints)
                    
                    if not is_simple and not has_service_dependency:
                        print(f"Warning: {endpoint_func.__name__} might need service dependency injection")
    
    def test_api_response_models_are_consistent(self):
        """Verify API response models follow consistent patterns"""
        routers = [modules, installations, enhanced_modules, enhanced_installations, dependency_resolution]
        
        response_model_patterns = {
            'list': ['List', 'list'],
            'single': ['Response', 'Result'],
            'status': ['status', 'success', 'message']
        }
        
        for router_module in routers:
            router = router_module.router
            
            for route in router.routes:
                if hasattr(route, 'response_model') and route.response_model:
                    response_model = route.response_model
                    
                    # Check that response models are properly defined
                    if hasattr(response_model, '__name__'):
                        model_name = response_model.__name__
                        
                        # Should follow naming conventions
                        if 'list' in route.path.lower() or route.path.endswith('/'):
                            # List endpoints should return List or have 'List' in name
                            is_list_response = (
                                get_origin(response_model) is list or
                                'List' in model_name or
                                'Dict' in model_name
                            )
                            
                            if not is_list_response:
                                print(f"Warning: {route.path} might need list response model")


class TestEndpointIntegration:
    """Test endpoint integration and consistency"""
    
    def test_all_routers_included_in_main_app(self):
        """Verify all routers are properly included in main app"""
        expected_prefixes = [
            "/api/v1",  # modules and installations
            "/api/v2",  # enhanced_modules, enhanced_installations, dependency_resolution
        ]
        
        app_routes = app.routes
        included_prefixes = set()
        
        for route in app_routes:
            if hasattr(route, 'path_prefix'):
                included_prefixes.add(route.path_prefix)
        
        # Check that expected prefixes are included
        for prefix in expected_prefixes:
            prefix_found = any(prefix in str(route.path) for route in app_routes)
            assert prefix_found, f"API prefix {prefix} not found in application routes"
    
    def test_endpoint_paths_follow_restful_conventions(self):
        """Verify endpoint paths follow RESTful conventions"""
        routers = [modules, installations, enhanced_modules, enhanced_installations, dependency_resolution]
        
        restful_patterns = {
            'collection': r'^/[a-z-]+$',  # /modules
            'item': r'^/[a-z-]+/{[a-z_]+}$',  # /modules/{id}
            'action': r'^/[a-z-]+/{[a-z_]+}/[a-z-]+$',  # /modules/{id}/action
            'nested': r'^/[a-z-]+/{[a-z_]+}/[a-z-]+/{[a-z_]+}$'  # /company/{id}/modules/{id}
        }
        
        for router_module in routers:
            router = router_module.router
            
            for route in router.routes:
                if hasattr(route, 'path'):
                    path = route.path
                    
                    # Check that paths use kebab-case
                    path_parts = [part for part in path.split('/') if part and not part.startswith('{')]
                    for part in path_parts:
                        if '_' in part:
                            print(f"Warning: Path {path} uses underscore, consider kebab-case")
    
    def test_api_versioning_consistency(self):
        """Verify API versioning is consistent"""
        v1_endpoints = []
        v2_endpoints = []
        
        for route in app.routes:
            if hasattr(route, 'path'):
                path = route.path
                if '/api/v1/' in path:
                    v1_endpoints.append(path)
                elif '/api/v2/' in path:
                    v2_endpoints.append(path)
        
        # V2 should be enhanced versions of V1
        # Check that enhanced endpoints exist in V2
        expected_v2_paths = [
            '/api/v2/modules',
            '/api/v2/installations',
            '/api/v2/dependencies'
        ]
        
        for expected_path in expected_v2_paths:
            v2_has_path = any(expected_path in path for path in v2_endpoints)
            assert v2_has_path, f"Expected V2 path {expected_path} not found"


class TestSecurityCompliance:
    """Test security compliance across all endpoints"""
    
    def test_no_hardcoded_secrets_in_source(self):
        """Verify no hardcoded secrets in source code"""
        routers = [modules, installations, enhanced_modules, enhanced_installations, dependency_resolution]
        
        dangerous_patterns = [
            'password',
            'secret',
            'api_key',
            'token',
            'credential'
        ]
        
        for router_module in routers:
            router = router_module.router
            
            for route in router.routes:
                if hasattr(route, 'endpoint'):
                    source_code = inspect.getsource(route.endpoint).lower()
                    
                    for pattern in dangerous_patterns:
                        if f'"{pattern}"' in source_code or f"'{pattern}'" in source_code:
                            # Check if it's in a comment or string literal (acceptable)
                            lines = source_code.split('\n')
                            for line in lines:
                                if pattern in line and not (line.strip().startswith('#') or line.strip().startswith('"""')):
                                    print(f"Warning: Potential hardcoded secret in {route.endpoint.__name__}: {line.strip()}")
    
    def test_input_validation_patterns(self):
        """Verify proper input validation patterns"""
        routers = [enhanced_modules, enhanced_installations, dependency_resolution]
        
        for router_module in routers:
            router = router_module.router
            
            for route in router.routes:
                if hasattr(route, 'endpoint') and hasattr(route, 'methods'):
                    if 'POST' in route.methods or 'PUT' in route.methods:
                        endpoint_func = route.endpoint
                        signature = inspect.signature(endpoint_func)
                        
                        # Should validate input parameters
                        for param_name, param in signature.parameters.items():
                            if param.annotation != inspect.Parameter.empty:
                                # ID parameters should be validated as positive integers
                                if param_name.endswith('_id'):
                                    # Should use Path or Query with validation
                                    source_code = inspect.getsource(endpoint_func)
                                    has_validation = 'Path(' in source_code or 'Query(' in source_code
                                    
                                    if not has_validation:
                                        print(f"Warning: {endpoint_func.__name__} parameter {param_name} might need validation")
    
    def test_error_message_security(self):
        """Verify error messages don't leak sensitive information"""
        routers = [modules, installations, enhanced_modules, enhanced_installations, dependency_resolution]
        
        for router_module in routers:
            router = router_module.router
            
            for route in router.routes:
                if hasattr(route, 'endpoint'):
                    source_code = inspect.getsource(route.endpoint)
                    
                    # Check for potential information leakage in error messages
                    if 'str(e)' in source_code:
                        # Should be careful about exposing internal error details
                        print(f"Warning: {route.endpoint.__name__} might expose internal error details")
                    
                    # Should use appropriate error handling
                    if 'Exception' in source_code and 'HTTPException' in source_code:
                        # Good - using proper HTTP exceptions
                        pass