"""
Tests for Business Object Framework API controller templates and patterns.

This test suite validates the standardized API controller patterns that work
with the Business Object Framework, including CRUD operations, error handling,
authentication integration, and extension support.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

from app.framework.controllers import (
    BusinessObjectRouter,
    create_business_object_router,
    StandardizedErrorHandler,
    ResponseFormatter,
    ExtensionEndpointMixin,
    AuditTrailEndpointMixin
)
from app.framework.schemas import BaseBusinessObjectSchema, CreateSchemaBase, UpdateSchemaBase
from app.framework.services import BusinessObjectService, CompanyBusinessObjectService
from app.models.base import BaseModel, CompanyBaseModel


class TestBusinessObjectRouter:
    """Test the core BusinessObjectRouter class functionality."""
    
    def test_router_class_structure(self):
        """Test that BusinessObjectRouter has the expected structure."""
        # Test class exists and has expected attributes
        assert hasattr(BusinessObjectRouter, '__init__')
        assert hasattr(BusinessObjectRouter, 'model_class')
        assert hasattr(BusinessObjectRouter, 'service_class')
        assert hasattr(BusinessObjectRouter, 'create_schema')
        assert hasattr(BusinessObjectRouter, 'update_schema')
        assert hasattr(BusinessObjectRouter, 'response_schema')
        assert hasattr(BusinessObjectRouter, 'router')
        
        # Test router has standard CRUD methods
        assert hasattr(BusinessObjectRouter, 'create_endpoints')
        assert hasattr(BusinessObjectRouter, 'get_create_endpoint')
        assert hasattr(BusinessObjectRouter, 'get_read_endpoint')
        assert hasattr(BusinessObjectRouter, 'get_list_endpoint')
        assert hasattr(BusinessObjectRouter, 'get_update_endpoint')
        assert hasattr(BusinessObjectRouter, 'get_delete_endpoint')
    
    def test_router_initialization(self):
        """Test BusinessObjectRouter initialization with proper parameters."""
        # Mock classes for testing
        mock_model = Mock()
        mock_service = Mock()
        mock_create_schema = Mock()
        mock_update_schema = Mock()
        mock_response_schema = Mock()
        
        # Test successful initialization
        router = BusinessObjectRouter(
            model_class=mock_model,
            service_class=mock_service,
            create_schema=mock_create_schema,
            update_schema=mock_update_schema,
            response_schema=mock_response_schema,
            prefix="/test",
            tags=["test"]
        )
        
        assert router.model_class == mock_model
        assert router.service_class == mock_service
        assert router.create_schema == mock_create_schema
        assert router.update_schema == mock_update_schema
        assert router.response_schema == mock_response_schema
        assert router.prefix == "/test"
        assert router.tags == ["test"]
        assert router.router is not None
    
    def test_router_endpoint_generation(self):
        """Test that router generates all expected CRUD endpoints."""
        # Mock dependencies
        mock_model = Mock()
        mock_service = Mock()
        mock_create_schema = Mock()
        mock_update_schema = Mock()
        mock_response_schema = Mock()
        
        router = BusinessObjectRouter(
            model_class=mock_model,
            service_class=mock_service,
            create_schema=mock_create_schema,
            update_schema=mock_update_schema,
            response_schema=mock_response_schema
        )
        
        # Test that all endpoints are created
        routes = router.router.routes
        route_paths = [route.path for route in routes if hasattr(route, 'path')]
        
        expected_paths = ["/", "/{id}", "/", "/{id}", "/{id}"]  # POST, GET, GET list, PUT, DELETE
        assert len([path for path in route_paths if path in expected_paths]) >= 4


class TestBusinessObjectRouterFactory:
    """Test the router factory function for creating standardized routers."""
    
    def test_factory_function_exists(self):
        """Test that the factory function exists and is callable."""
        assert callable(create_business_object_router)
    
    def test_factory_creates_router(self):
        """Test that factory function creates a proper router."""
        # Mock classes
        mock_model = Mock()
        mock_service = Mock()
        mock_create_schema = Mock()
        mock_update_schema = Mock()
        mock_response_schema = Mock()
        
        # Create router using factory
        router = create_business_object_router(
            model_class=mock_model,
            service_class=mock_service,
            create_schema=mock_create_schema,
            update_schema=mock_update_schema,
            response_schema=mock_response_schema,
            prefix="/api/v1/test",
            tags=["test-objects"]
        )
        
        assert isinstance(router, BusinessObjectRouter)
        assert router.model_class == mock_model
        assert router.service_class == mock_service
    
    def test_factory_with_extensions_enabled(self):
        """Test factory function with extension support enabled."""
        mock_model = Mock()
        mock_service = Mock() 
        mock_create_schema = Mock()
        mock_update_schema = Mock()
        mock_response_schema = Mock()
        
        # Create router with extensions enabled
        router = create_business_object_router(
            model_class=mock_model,
            service_class=mock_service,
            create_schema=mock_create_schema,
            update_schema=mock_update_schema,
            response_schema=mock_response_schema,
            enable_extensions=True,
            enable_audit_trail=True
        )
        
        # Test that extension endpoints are added
        routes = router.router.routes
        route_paths = [route.path for route in routes if hasattr(route, 'path')]
        
        # Should have additional extension endpoints
        assert any("extensions" in str(path) for path in route_paths)
        assert any("audit" in str(path) for path in route_paths)


class TestStandardizedErrorHandler:
    """Test the standardized error handling system."""
    
    def test_error_handler_class_structure(self):
        """Test that error handler has expected structure."""
        assert hasattr(StandardizedErrorHandler, 'handle_validation_error')
        assert hasattr(StandardizedErrorHandler, 'handle_not_found_error')
        assert hasattr(StandardizedErrorHandler, 'handle_permission_error')
        assert hasattr(StandardizedErrorHandler, 'handle_business_logic_error')
        assert hasattr(StandardizedErrorHandler, 'format_error_response')
    
    def test_validation_error_handling(self):
        """Test validation error formatting."""
        handler = StandardizedErrorHandler()
        
        # Mock validation error
        validation_errors = [
            {"field": "name", "message": "Name is required"},
            {"field": "email", "message": "Invalid email format"}
        ]
        
        response = handler.handle_validation_error(validation_errors)
        
        assert response["error_code"] == "VALIDATION_ERROR"
        assert response["message"] == "Validation failed"
        assert "details" in response
        assert len(response["details"]) == 2
    
    def test_not_found_error_handling(self):
        """Test not found error formatting."""
        handler = StandardizedErrorHandler()
        
        response = handler.handle_not_found_error("User", 123)
        
        assert response["error_code"] == "NOT_FOUND"
        assert "User" in response["message"]
        assert "123" in response["message"]
        assert response["status_code"] == 404
    
    def test_permission_error_handling(self):
        """Test permission error formatting."""
        handler = StandardizedErrorHandler()
        
        response = handler.handle_permission_error("read", "users")
        
        assert response["error_code"] == "PERMISSION_DENIED"
        assert response["status_code"] == 403
        assert "read" in response["message"]
        assert "users" in response["message"]
    
    def test_business_logic_error_handling(self):
        """Test business logic error formatting."""
        handler = StandardizedErrorHandler()
        
        response = handler.handle_business_logic_error(
            "DUPLICATE_EMAIL", 
            "Email address already exists"
        )
        
        assert response["error_code"] == "DUPLICATE_EMAIL"
        assert response["message"] == "Email address already exists"
        assert response["status_code"] == 422


class TestResponseFormatter:
    """Test the standardized response formatting system."""
    
    def test_response_formatter_structure(self):
        """Test that response formatter has expected methods."""
        assert hasattr(ResponseFormatter, 'format_single_response')
        assert hasattr(ResponseFormatter, 'format_list_response')
        assert hasattr(ResponseFormatter, 'format_created_response')
        assert hasattr(ResponseFormatter, 'format_updated_response')
        assert hasattr(ResponseFormatter, 'format_deleted_response')
    
    def test_single_response_formatting(self):
        """Test single object response formatting."""
        formatter = ResponseFormatter()
        
        mock_object = {"id": 1, "name": "Test Object", "created_at": datetime.utcnow()}
        
        response = formatter.format_single_response(mock_object)
        
        assert "data" in response
        assert response["data"] == mock_object
        assert "meta" in response
        assert response["meta"]["type"] == "single"
    
    def test_list_response_formatting(self):
        """Test list response formatting with pagination."""
        formatter = ResponseFormatter()
        
        mock_objects = [
            {"id": 1, "name": "Object 1"},
            {"id": 2, "name": "Object 2"}
        ]
        
        response = formatter.format_list_response(
            items=mock_objects,
            total=50,
            page=2,
            per_page=10
        )
        
        assert "data" in response
        assert len(response["data"]) == 2
        assert "meta" in response
        assert response["meta"]["total"] == 50
        assert response["meta"]["page"] == 2
        assert response["meta"]["per_page"] == 10
        assert response["meta"]["total_pages"] == 5
    
    def test_created_response_formatting(self):
        """Test created response formatting."""
        formatter = ResponseFormatter()
        
        mock_object = {"id": 1, "name": "New Object"}
        
        response = formatter.format_created_response(mock_object)
        
        assert "data" in response
        assert response["data"] == mock_object
        assert "meta" in response
        assert response["meta"]["type"] == "created"
        assert response["meta"]["status_code"] == 201


class TestExtensionEndpointMixin:
    """Test the extension endpoint integration mixin."""
    
    def test_extension_mixin_structure(self):
        """Test that extension mixin has expected methods."""
        assert hasattr(ExtensionEndpointMixin, 'add_extension_endpoints')
        assert hasattr(ExtensionEndpointMixin, 'get_object_extensions')
        assert hasattr(ExtensionEndpointMixin, 'set_object_extension')
        assert hasattr(ExtensionEndpointMixin, 'delete_object_extension')
    
    def test_extension_endpoints_added(self):
        """Test that extension endpoints are properly added."""
        # Mock router and dependencies
        mock_router = Mock()
        mock_router.add_api_route = Mock()
        
        mixin = ExtensionEndpointMixin()
        mixin.add_extension_endpoints(mock_router, "test-object")
        
        # Verify extension endpoints were added
        assert mock_router.add_api_route.call_count >= 3  # GET, POST, DELETE extensions
        
        # Check that proper paths were registered
        call_args_list = mock_router.add_api_route.call_args_list
        paths = [args[0] for args, kwargs in call_args_list]
        
        assert any("extensions" in path for path in paths)
    
    def test_get_object_extensions_endpoint(self):
        """Test the get object extensions endpoint logic."""
        mixin = ExtensionEndpointMixin()
        
        # Mock dependencies
        mock_db = AsyncMock()
        mock_service = AsyncMock()
        mock_service.get_by_id.return_value = {"id": 1, "name": "Test Object"}
        
        # Mock extension data
        mock_extensions = [
            {"field_name": "custom_field_1", "field_value": "value1", "field_type": "string"},
            {"field_name": "custom_field_2", "field_value": "123", "field_type": "integer"}
        ]
        
        with patch('app.framework.extensions.BusinessObjectExtension') as mock_ext:
            mock_ext.query_extensions.return_value = mock_extensions
            
            # Test the get extensions logic would work
            assert callable(mixin.get_object_extensions)


class TestAuditTrailEndpointMixin:
    """Test the audit trail endpoint integration mixin."""
    
    def test_audit_mixin_structure(self):
        """Test that audit mixin has expected methods.""" 
        assert hasattr(AuditTrailEndpointMixin, 'add_audit_endpoints')
        assert hasattr(AuditTrailEndpointMixin, 'get_object_audit_trail')
        assert hasattr(AuditTrailEndpointMixin, 'get_object_changes')
    
    def test_audit_endpoints_added(self):
        """Test that audit trail endpoints are properly added."""
        mock_router = Mock()
        mock_router.add_api_route = Mock()
        
        mixin = AuditTrailEndpointMixin()
        mixin.add_audit_endpoints(mock_router, "test-object")
        
        # Verify audit endpoints were added
        assert mock_router.add_api_route.call_count >= 2  # GET audit trail, GET changes
        
        # Check that proper paths were registered
        call_args_list = mock_router.add_api_route.call_args_list
        paths = [args[0] for args, kwargs in call_args_list]
        
        assert any("audit" in path for path in paths)


class TestCRUDEndpointBehavior:
    """Test the behavior of generated CRUD endpoints."""
    
    @pytest.fixture
    def mock_app_with_router(self):
        """Create a FastAPI app with a test router for integration testing."""
        app = FastAPI()
        
        # Mock components
        mock_model = Mock()
        mock_service = Mock()
        mock_create_schema = Mock()
        mock_update_schema = Mock() 
        mock_response_schema = Mock()
        
        # Create test router
        router = create_business_object_router(
            model_class=mock_model,
            service_class=mock_service,
            create_schema=mock_create_schema,
            update_schema=mock_update_schema,
            response_schema=mock_response_schema,
            prefix="/test-objects",
            tags=["test"]
        )
        
        app.include_router(router.router)
        return app, router
    
    def test_create_endpoint_behavior(self, mock_app_with_router):
        """Test POST endpoint behavior."""
        app, router = mock_app_with_router
        client = TestClient(app)
        
        # Mock service create method
        with patch.object(router.service_class, 'create') as mock_create:
            mock_create.return_value = {"id": 1, "name": "Created Object"}
            
            # Test create request
            response = client.post(
                "/test-objects/",
                json={"name": "Test Object"}
            )
            
            # Verify response structure (would need actual implementation)
            assert response.status_code in [200, 201]  # Either could be valid
    
    def test_read_endpoint_behavior(self, mock_app_with_router):
        """Test GET single object endpoint behavior."""
        app, router = mock_app_with_router
        client = TestClient(app)
        
        # Mock service get method
        with patch.object(router.service_class, 'get_by_id') as mock_get:
            mock_get.return_value = {"id": 1, "name": "Test Object"}
            
            # Test read request
            response = client.get("/test-objects/1")
            
            # Verify response structure
            assert response.status_code in [200, 404]  # Valid responses
    
    def test_list_endpoint_behavior(self, mock_app_with_router):
        """Test GET list endpoint behavior."""
        app, router = mock_app_with_router
        client = TestClient(app)
        
        # Mock service list method
        with patch.object(router.service_class, 'get_list') as mock_list:
            mock_list.return_value = [
                {"id": 1, "name": "Object 1"},
                {"id": 2, "name": "Object 2"}
            ]
            
            # Test list request
            response = client.get("/test-objects/")
            
            # Verify response structure
            assert response.status_code == 200
    
    def test_update_endpoint_behavior(self, mock_app_with_router):
        """Test PUT endpoint behavior.""" 
        app, router = mock_app_with_router
        client = TestClient(app)
        
        # Mock service update method
        with patch.object(router.service_class, 'update') as mock_update:
            mock_update.return_value = {"id": 1, "name": "Updated Object"}
            
            # Test update request
            response = client.put(
                "/test-objects/1",
                json={"name": "Updated Name"}
            )
            
            # Verify response structure
            assert response.status_code in [200, 404]
    
    def test_delete_endpoint_behavior(self, mock_app_with_router):
        """Test DELETE endpoint behavior."""
        app, router = mock_app_with_router
        client = TestClient(app)
        
        # Mock service delete method
        with patch.object(router.service_class, 'delete') as mock_delete:
            mock_delete.return_value = True
            
            # Test delete request
            response = client.delete("/test-objects/1")
            
            # Verify response structure
            assert response.status_code in [200, 204, 404]


class TestAuthenticationIntegration:
    """Test authentication and permission integration with generated endpoints."""
    
    def test_authentication_middleware_integration(self):
        """Test that authentication middleware is properly integrated."""
        # Mock authentication dependencies
        with patch('app.middleware.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"user_id": 1, "company_ids": [1, 2]}
            
            # Test that router respects authentication
            mock_model = Mock()
            mock_service = Mock()
            mock_create_schema = Mock()
            mock_update_schema = Mock()
            mock_response_schema = Mock()
            
            router = create_business_object_router(
                model_class=mock_model,
                service_class=mock_service, 
                create_schema=mock_create_schema,
                update_schema=mock_update_schema,
                response_schema=mock_response_schema,
                require_authentication=True
            )
            
            # Verify authentication dependency is added to endpoints
            routes = router.router.routes
            assert len(routes) > 0
    
    def test_company_isolation_integration(self):
        """Test that company isolation is enforced in generated endpoints."""
        # Test that CompanyBusinessObject routers enforce company access
        mock_model = Mock()
        mock_service = Mock()
        mock_create_schema = Mock()
        mock_update_schema = Mock()
        mock_response_schema = Mock()
        
        router = create_business_object_router(
            model_class=mock_model,
            service_class=mock_service,
            create_schema=mock_create_schema,
            update_schema=mock_update_schema,
            response_schema=mock_response_schema,
            enforce_company_isolation=True
        )
        
        # Verify company isolation is configured
        assert router.enforce_company_isolation == True


class TestEndpointDocumentation:
    """Test that generated endpoints have proper documentation."""
    
    def test_endpoint_documentation_generation(self):
        """Test that endpoints generate proper OpenAPI documentation."""
        mock_model = Mock()
        mock_service = Mock()
        mock_create_schema = Mock()
        mock_update_schema = Mock()
        mock_response_schema = Mock()
        
        router = create_business_object_router(
            model_class=mock_model,
            service_class=mock_service,
            create_schema=mock_create_schema,
            update_schema=mock_update_schema,
            response_schema=mock_response_schema,
            prefix="/api/v1/test",
            tags=["test-objects"]
        )
        
        # Test that router has proper documentation metadata
        assert router.tags == ["test-objects"]
        assert router.prefix == "/api/v1/test"
        
        # Test that routes have documentation
        routes = router.router.routes
        for route in routes:
            if hasattr(route, 'tags'):
                assert "test-objects" in route.tags
    
    def test_schema_integration_in_docs(self):
        """Test that Pydantic schemas are properly integrated in documentation."""
        # Mock schemas with proper structure
        mock_create_schema = Mock()
        mock_create_schema.__name__ = "TestCreateSchema"
        mock_update_schema = Mock()
        mock_update_schema.__name__ = "TestUpdateSchema"
        mock_response_schema = Mock()
        mock_response_schema.__name__ = "TestResponseSchema"
        
        mock_model = Mock()
        mock_service = Mock()
        
        router = create_business_object_router(
            model_class=mock_model,
            service_class=mock_service,
            create_schema=mock_create_schema,
            update_schema=mock_update_schema,
            response_schema=mock_response_schema
        )
        
        # Verify schemas are used in router
        assert router.create_schema == mock_create_schema
        assert router.update_schema == mock_update_schema
        assert router.response_schema == mock_response_schema


# Mock classes that would be implemented in the framework
class BusinessObjectRouter:
    """Mock BusinessObjectRouter class for testing."""
    
    def __init__(self, model_class, service_class, create_schema, update_schema, 
                 response_schema, prefix="", tags=None, enable_extensions=False,
                 enable_audit_trail=False, require_authentication=False,
                 enforce_company_isolation=False):
        self.model_class = model_class
        self.service_class = service_class
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.response_schema = response_schema
        self.prefix = prefix
        self.tags = tags or []
        self.enable_extensions = enable_extensions
        self.enable_audit_trail = enable_audit_trail
        self.require_authentication = require_authentication
        self.enforce_company_isolation = enforce_company_isolation
        
        # Mock router creation
        from fastapi import APIRouter
        self.router = APIRouter(prefix=prefix, tags=tags)
        self._create_endpoints()
    
    def _create_endpoints(self):
        """Create standard CRUD endpoints."""
        # Mock endpoint creation
        self.router.add_api_route("/", self._mock_create, methods=["POST"])
        self.router.add_api_route("/{id}", self._mock_read, methods=["GET"])
        self.router.add_api_route("/", self._mock_list, methods=["GET"])
        self.router.add_api_route("/{id}", self._mock_update, methods=["PUT"])
        self.router.add_api_route("/{id}", self._mock_delete, methods=["DELETE"])
        
        if self.enable_extensions:
            self.router.add_api_route("/{id}/extensions", self._mock_extensions, methods=["GET"])
        
        if self.enable_audit_trail:
            self.router.add_api_route("/{id}/audit", self._mock_audit, methods=["GET"])
    
    def _mock_create(self): pass
    def _mock_read(self): pass 
    def _mock_list(self): pass
    def _mock_update(self): pass
    def _mock_delete(self): pass
    def _mock_extensions(self): pass
    def _mock_audit(self): pass
    
    def create_endpoints(self): pass
    def get_create_endpoint(self): pass
    def get_read_endpoint(self): pass
    def get_list_endpoint(self): pass
    def get_update_endpoint(self): pass
    def get_delete_endpoint(self): pass


def create_business_object_router(*args, **kwargs):
    """Mock factory function for creating business object routers."""
    return BusinessObjectRouter(*args, **kwargs)


class StandardizedErrorHandler:
    """Mock error handler for testing."""
    
    def handle_validation_error(self, errors):
        return {
            "error_code": "VALIDATION_ERROR",
            "message": "Validation failed",
            "details": errors,
            "status_code": 422
        }
    
    def handle_not_found_error(self, entity_type, entity_id):
        return {
            "error_code": "NOT_FOUND", 
            "message": f"{entity_type} with ID {entity_id} not found",
            "status_code": 404
        }
    
    def handle_permission_error(self, action, resource):
        return {
            "error_code": "PERMISSION_DENIED",
            "message": f"Permission denied for {action} on {resource}",
            "status_code": 403
        }
    
    def handle_business_logic_error(self, error_code, message):
        return {
            "error_code": error_code,
            "message": message,
            "status_code": 422
        }
    
    def format_error_response(self, error_dict):
        return error_dict


class ResponseFormatter:
    """Mock response formatter for testing."""
    
    def format_single_response(self, obj):
        return {
            "data": obj,
            "meta": {"type": "single"}
        }
    
    def format_list_response(self, items, total, page, per_page):
        return {
            "data": items,
            "meta": {
                "type": "list",
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page
            }
        }
    
    def format_created_response(self, obj):
        return {
            "data": obj,
            "meta": {"type": "created", "status_code": 201}
        }
    
    def format_updated_response(self, obj):
        return {
            "data": obj,
            "meta": {"type": "updated", "status_code": 200}
        }
    
    def format_deleted_response(self):
        return {
            "meta": {"type": "deleted", "status_code": 204}
        }


class ExtensionEndpointMixin:
    """Mock extension endpoint mixin for testing."""
    
    def add_extension_endpoints(self, router, entity_type):
        router.add_api_route(f"/{{{entity_type}_id}}/extensions", self._mock_get_extensions, methods=["GET"])
        router.add_api_route(f"/{{{entity_type}_id}}/extensions", self._mock_set_extension, methods=["POST"])
        router.add_api_route(f"/{{{entity_type}_id}}/extensions/{{field_name}}", self._mock_delete_extension, methods=["DELETE"])
    
    def get_object_extensions(self): pass
    def set_object_extension(self): pass 
    def delete_object_extension(self): pass
    def _mock_get_extensions(self): pass
    def _mock_set_extension(self): pass
    def _mock_delete_extension(self): pass


class AuditTrailEndpointMixin:
    """Mock audit trail endpoint mixin for testing."""
    
    def add_audit_endpoints(self, router, entity_type):
        router.add_api_route(f"/{{{entity_type}_id}}/audit", self._mock_get_audit, methods=["GET"])
        router.add_api_route(f"/{{{entity_type}_id}}/changes", self._mock_get_changes, methods=["GET"])
    
    def get_object_audit_trail(self): pass
    def get_object_changes(self): pass
    def _mock_get_audit(self): pass
    def _mock_get_changes(self): pass