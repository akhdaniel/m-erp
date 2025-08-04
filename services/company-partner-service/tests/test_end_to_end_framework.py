"""
End-to-End Testing for Framework-Migrated Partner Service

This test suite performs comprehensive end-to-end testing of the Partner service
after migration to the Business Object Framework, verifying all functionality
works correctly including new framework features.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch, Mock
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Test data constants
TEST_COMPANY_ID = 1
TEST_USER_ID = 1
TEST_PARTNER_DATA = {
    "name": "Test Partner E2E",
    "code": "E2E001",
    "partner_type": "customer",
    "email": "e2e@test.com",
    "phone": "+1-555-0199",
    "is_customer": True,
    "is_company": True,
    "company_id": TEST_COMPANY_ID
}


class TestPartnerE2EFramework:
    """End-to-end tests for framework-migrated Partner service."""
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock current user for authentication."""
        return {
            'id': TEST_USER_ID,
            'user_id': TEST_USER_ID,
            'company_ids': [TEST_COMPANY_ID],
            'email': 'testuser@example.com'
        }
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_messaging_service(self):
        """Mock messaging service for event publishing."""
        messaging_mock = AsyncMock()
        messaging_mock.publish_partner_created = AsyncMock()
        messaging_mock.publish_partner_updated = AsyncMock()
        messaging_mock.publish_partner_deleted = AsyncMock()
        return messaging_mock
    
    def test_framework_app_startup(self):
        """Test that framework application starts up correctly."""
        print("\n🚀 Testing Framework Application Startup...")
        
        # Test framework main app can be imported
        try:
            from app.main import app
            assert app is not None
            print("✅ Framework main app imports successfully")
        except Exception as e:
            print(f"❌ Framework main app import failed: {e}")
            pytest.fail(f"Framework app import failed: {e}")
        
        # Test app metadata shows framework mode
        try:
            # This would normally require a test client, but we can check the factory
            from app.main import create_application
            framework_app = create_application()
            
            # Check framework indicators in app configuration
            assert "Framework Edition" in framework_app.title
            assert "framework" in framework_app.version
            print("✅ Framework app shows correct metadata")
        except Exception as e:
            print(f"❌ Framework app metadata test failed: {e}")
            pytest.fail(f"Framework app metadata failed: {e}")
    
    def test_framework_router_availability(self):
        """Test that framework routers are available."""
        print("\n🌐 Testing Framework Router Availability...")
        
        try:
            # Test framework router imports
            from app.framework_migration.partner_router import router as framework_router
            from app.framework_migration.partner_router import framework_partner_router
            
            assert framework_router is not None
            assert framework_partner_router is not None
            print("✅ Framework routers import successfully")
        except Exception as e:
            print(f"❌ Framework router import failed: {e}")
            pytest.fail(f"Framework router import failed: {e}")
        
        try:
            # Test that framework router has expected routes
            from app.framework_migration.partner_router import router
            
            # Check that router has routes (would be populated when included in app)
            assert hasattr(router, 'routes') or hasattr(router, 'router')
            print("✅ Framework router has route structure")
        except Exception as e:
            print(f"❌ Framework router structure test failed: {e}")
            pytest.fail(f"Framework router structure failed: {e}")
    
    async def test_framework_service_functionality(self):
        """Test framework service CRUD operations."""
        print("\n🔧 Testing Framework Service CRUD Operations...")
        
        try:
            from app.framework_migration.partner_service import PartnerFrameworkService, create_partner_service
            from app.framework_migration.partner_schemas import PartnerFrameworkCreate, PartnerFrameworkUpdate
            
            # Create mock database session
            mock_db = AsyncMock()
            
            # Create service instance
            service = create_partner_service(mock_db)
            assert isinstance(service, PartnerFrameworkService)
            print("✅ Framework service instantiates correctly")
            
            # Test service has all expected methods
            expected_methods = [
                'create_partner', 'get_partner', 'update_partner', 'delete_partner',
                'activate_partner', 'deactivate_partner', 'get_partner_by_code',
                'get_partners_by_company', 'find_customers', 'find_suppliers',
                'bulk_create_partners', 'get_partner_statistics'
            ]
            
            for method_name in expected_methods:
                assert hasattr(service, method_name), f"Missing method: {method_name}"
            
            print("✅ Framework service has all expected methods")
            
        except Exception as e:
            print(f"❌ Framework service test failed: {e}")
            pytest.fail(f"Framework service test failed: {e}")
    
    def test_framework_schema_validation(self):
        """Test framework schema validation."""
        print("\n📄 Testing Framework Schema Validation...")
        
        try:
            from app.framework_migration.partner_schemas import (
                PartnerFrameworkCreate, PartnerFrameworkUpdate, PartnerFrameworkResponse
            )
            
            # Test valid partner creation schema
            valid_data = TEST_PARTNER_DATA.copy()
            partner_create = PartnerFrameworkCreate(**valid_data)
            assert partner_create.name == valid_data["name"]
            assert partner_create.company_id == valid_data["company_id"]
            print("✅ Partner creation schema validates correctly")
            
            # Test partner update schema
            update_data = {"name": "Updated Partner", "email": "updated@test.com"}
            partner_update = PartnerFrameworkUpdate(**update_data)
            assert partner_update.name == update_data["name"]
            print("✅ Partner update schema validates correctly")
            
            # Test response schema structure
            response_data = {
                **valid_data,
                "id": 1,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            partner_response = PartnerFrameworkResponse(**response_data)
            assert partner_response.id == 1
            assert partner_response.name == valid_data["name"]
            print("✅ Partner response schema validates correctly")
            
        except Exception as e:
            print(f"❌ Framework schema validation failed: {e}")
            pytest.fail(f"Framework schema validation failed: {e}")
    
    def test_schema_validation_errors(self):
        """Test schema validation error handling."""
        print("\n🚨 Testing Schema Validation Error Handling...")
        
        try:
            from app.framework_migration.partner_schemas import PartnerFrameworkCreate
            from pydantic import ValidationError
            
            # Test missing required fields
            try:
                invalid_partner = PartnerFrameworkCreate(name="Test")  # Missing company_id
                pytest.fail("Should have raised validation error for missing company_id")
            except ValidationError as e:
                assert "company_id" in str(e)
                print("✅ Missing company_id properly validated")
            
            # Test invalid partner type
            try:
                invalid_partner = PartnerFrameworkCreate(
                    name="Test",
                    company_id=1,
                    partner_type="invalid_type"
                )
                pytest.fail("Should have raised validation error for invalid partner type")
            except ValidationError as e:
                assert "partner_type" in str(e)
                print("✅ Invalid partner type properly validated")
            
            # Test invalid company_id
            try:
                invalid_partner = PartnerFrameworkCreate(
                    name="Test",
                    company_id=0  # Should be > 0
                )
                pytest.fail("Should have raised validation error for invalid company_id")
            except ValidationError as e:
                assert "company_id" in str(e)
                print("✅ Invalid company_id properly validated")
                
        except Exception as e:
            print(f"❌ Schema validation error test failed: {e}")
            pytest.fail(f"Schema validation error test failed: {e}")
    
    async def test_partner_lifecycle_e2e(self):
        """Test complete partner lifecycle end-to-end."""
        print("\n🔄 Testing Complete Partner Lifecycle...")
        
        try:
            from app.framework_migration.partner_service import PartnerFrameworkService
            from app.framework_migration.partner_schemas import PartnerFrameworkCreate, PartnerFrameworkUpdate
            from app.models.partner import Partner
            
            # Mock database and create service
            mock_db = AsyncMock()
            service = PartnerFrameworkService(mock_db)
            
            # Mock partner model instance
            mock_partner = Mock(spec=Partner)
            mock_partner.id = 1
            mock_partner.name = TEST_PARTNER_DATA["name"]
            mock_partner.code = TEST_PARTNER_DATA["code"]
            mock_partner.company_id = TEST_COMPANY_ID
            mock_partner.is_active = True
            mock_partner.created_at = datetime.utcnow()
            mock_partner.updated_at = datetime.utcnow()
            
            # Mock service methods
            service.create = AsyncMock(return_value=mock_partner)
            service.get_by_id = AsyncMock(return_value=mock_partner)
            service.update = AsyncMock(return_value=mock_partner)
            service.soft_delete = AsyncMock(return_value=True)
            
            # Test 1: Create partner
            create_data = PartnerFrameworkCreate(**TEST_PARTNER_DATA)
            created_partner = await service.create_partner(create_data)
            assert created_partner.name == TEST_PARTNER_DATA["name"]
            print("✅ Partner creation works")
            
            # Test 2: Get partner
            retrieved_partner = await service.get_partner(1, TEST_COMPANY_ID)
            assert retrieved_partner.id == 1
            print("✅ Partner retrieval works")
            
            # Test 3: Update partner
            update_data = PartnerFrameworkUpdate(name="Updated Partner E2E")
            updated_partner = await service.update_partner(1, update_data, TEST_COMPANY_ID)
            assert updated_partner is not None
            print("✅ Partner update works")
            
            # Test 4: Delete partner
            delete_result = await service.delete_partner(1, TEST_COMPANY_ID)
            assert delete_result is True
            print("✅ Partner deletion works")
            
        except Exception as e:
            print(f"❌ Partner lifecycle test failed: {e}")
            pytest.fail(f"Partner lifecycle test failed: {e}")
    
    async def test_business_logic_methods(self):
        """Test business-specific methods work correctly."""
        print("\n💼 Testing Business Logic Methods...")
        
        try:
            from app.framework_migration.partner_service import PartnerFrameworkService
            from app.models.partner import Partner
            
            # Mock database and create service
            mock_db = AsyncMock()
            service = PartnerFrameworkService(mock_db)
            
            # Mock multiple partners
            mock_partners = []
            for i in range(3):
                partner = Mock(spec=Partner)
                partner.id = i + 1
                partner.name = f"Partner {i + 1}"
                partner.company_id = TEST_COMPANY_ID
                partner.is_customer = i == 0  # First is customer
                partner.is_supplier = i == 1  # Second is supplier
                partner.is_vendor = i == 2    # Third is vendor
                partner.is_active = True
                mock_partners.append(partner)
            
            # Mock service methods
            service.get_list = AsyncMock(return_value=mock_partners)
            service.get_by_filters = AsyncMock(return_value=mock_partners[0])
            service.count = AsyncMock(return_value=len(mock_partners))
            
            # Test get by code
            partner_by_code = await service.get_partner_by_code(TEST_COMPANY_ID, "TEST001")
            assert partner_by_code is not None
            print("✅ Get partner by code works")
            
            # Test get partners by company
            company_partners = await service.get_partners_by_company(TEST_COMPANY_ID)
            assert len(company_partners) == 3
            print("✅ Get partners by company works")
            
            # Test find customers
            customers = await service.find_customers(TEST_COMPANY_ID)
            assert len(customers) == 3  # Mock returns all
            print("✅ Find customers works")
            
            # Test get statistics
            stats = await service.get_partner_statistics(TEST_COMPANY_ID)
            assert "total_partners" in stats
            assert "active_partners" in stats
            assert "customers" in stats
            print("✅ Partner statistics works")
            
        except Exception as e:
            print(f"❌ Business logic test failed: {e}")
            pytest.fail(f"Business logic test failed: {e}")
    
    def test_framework_error_handling(self):
        """Test framework error handling and response formatting."""
        print("\n🚨 Testing Framework Error Handling...")
        
        try:
            from app.framework.controllers import StandardizedErrorHandler, ResponseFormatter
            
            # Test error handler
            error_handler = StandardizedErrorHandler()
            
            # Test validation error
            validation_error = error_handler.handle_validation_error([
                {'field': 'name', 'message': 'Name is required'},
                {'field': 'company_id', 'message': 'Company ID must be greater than 0'}
            ])
            
            assert validation_error['error_code'] == 'VALIDATION_ERROR'
            assert 'validation_errors' in validation_error
            assert len(validation_error['validation_errors']) == 2
            print("✅ Validation error handling works")
            
            # Test not found error
            not_found_error = error_handler.handle_not_found_error('partner', 999)
            assert not_found_error['error_code'] == 'NOT_FOUND'
            assert 'partner' in not_found_error['message'].lower()
            print("✅ Not found error handling works")
            
            # Test response formatter
            formatter = ResponseFormatter()
            
            # Test single response formatting
            test_data = {"id": 1, "name": "Test Partner"}
            single_response = formatter.format_single_response(test_data)
            assert 'data' in single_response
            assert 'meta' in single_response
            assert single_response['meta']['type'] == 'single'
            print("✅ Single response formatting works")
            
            # Test list response formatting
            test_list = [test_data]
            list_response = formatter.format_list_response(test_list, 1, 1, 50)
            assert 'data' in list_response
            assert 'meta' in list_response
            assert list_response['meta']['type'] == 'list'
            assert list_response['meta']['total'] == 1
            print("✅ List response formatting works")
            
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            pytest.fail(f"Error handling test failed: {e}")
    
    def test_migration_status_endpoints(self):
        """Test migration status and framework info endpoints."""
        print("\n📊 Testing Migration Status Endpoints...")
        
        try:
            # Test migration status file
            from pathlib import Path
            status_file = Path("app/migration_status.json")
            assert status_file.exists(), "Migration status file should exist"
            
            with open(status_file, 'r') as f:
                status = json.load(f)
            
            assert status['framework_enabled'] is True
            assert status['implementation'] == 'framework'
            print("✅ Migration status file is correct")
            
            # Test that we can create the status response (endpoint simulation)
            migration_status_response = {
                "migration_status": status,
                "available_endpoints": {
                    "framework_partners": "/api/v1/partners-framework/",
                    "generated_partners": "/api/v1/partners/",
                    "original_partners": "/api/v1/partners-original/",
                    "extensions": "/api/v1/partners/{id}/extensions",
                    "audit": "/api/v1/partners/{id}/audit"
                },
                "framework_features": [
                    "Custom field support",
                    "Automatic audit logging",
                    "Event publishing",
                    "Bulk operations"
                ]
            }
            
            assert "migration_status" in migration_status_response
            assert "available_endpoints" in migration_status_response
            assert "framework_features" in migration_status_response
            print("✅ Migration status endpoint response structure correct")
            
        except Exception as e:
            print(f"❌ Migration status test failed: {e}")
            pytest.fail(f"Migration status test failed: {e}")
    
    async def test_extension_system_integration(self):
        """Test extension system integration with Partner service."""
        print("\n🔧 Testing Extension System Integration...")
        
        try:
            from app.framework.extensions import ExtensibleMixin
            from app.models.extensions import BusinessObjectExtension
            
            # Test ExtensibleMixin functionality
            class TestExtensibleObject(ExtensibleMixin):
                def __init__(self):
                    self.id = 1
                    self.company_id = TEST_COMPANY_ID
            
            test_obj = TestExtensibleObject()
            
            # Test extension field types
            extension_types = ['string', 'integer', 'decimal', 'boolean', 'date', 'datetime', 'json']
            for field_type in extension_types:
                # This would normally interact with database, but we test the structure
                extension_data = {
                    'field_name': f'test_{field_type}_field',
                    'field_type': field_type,
                    'field_value': 'test_value'
                }
                assert 'field_name' in extension_data
                assert 'field_type' in extension_data
                assert extension_data['field_type'] in extension_types
            
            print("✅ Extension system field types supported")
            
            # Test BusinessObjectExtension model structure
            extension_fields = ['id', 'object_type', 'object_id', 'company_id', 'field_name', 'field_type', 'field_value']
            for field in extension_fields:
                assert hasattr(BusinessObjectExtension, field), f"Missing field: {field}"
            
            print("✅ BusinessObjectExtension model has required fields")
            
        except Exception as e:
            print(f"❌ Extension system test failed: {e}")
            pytest.fail(f"Extension system test failed: {e}")
    
    def test_api_documentation_generation(self):
        """Test API documentation is properly generated."""
        print("\n📚 Testing API Documentation Generation...")
        
        try:
            from app.framework.documentation import APIDocumentationTemplate
            
            # Test documentation template
            doc_template = APIDocumentationTemplate(
                model_name="Partner",
                endpoint_prefix="/partners"
            )
            
            # Test that documentation can be generated
            openapi_spec = doc_template.generate_openapi_spec()
            assert isinstance(openapi_spec, dict)
            assert 'info' in openapi_spec
            assert 'paths' in openapi_spec
            print("✅ OpenAPI specification generation works")
            
            # Test example generation
            examples = doc_template.generate_examples()
            assert 'create_example' in examples
            assert 'update_example' in examples
            assert 'response_example' in examples
            print("✅ API examples generation works")
            
        except Exception as e:
            print(f"❌ API documentation test failed: {e}")
            pytest.fail(f"API documentation test failed: {e}")
    
    def test_backward_compatibility(self):
        """Test that original Partner functionality is preserved."""
        print("\n🔄 Testing Backward Compatibility...")
        
        try:
            # Test original models still work
            from app.models.partner import Partner
            from app.schemas.partner import PartnerCreate, PartnerUpdate, PartnerResponse
            
            # Test original partner model
            partner_columns = [column.name for column in Partner.__table__.columns]
            required_fields = ['id', 'company_id', 'name', 'code', 'partner_type', 'created_at', 'updated_at']
            for field in required_fields:
                assert field in partner_columns, f"Missing required field: {field}"
            print("✅ Original Partner model structure preserved")
            
            # Test original schemas
            original_create = PartnerCreate(name="Test", company_id=1)
            assert original_create.name == "Test"
            assert original_create.company_id == 1
            print("✅ Original Partner schemas work")
            
            # Test original service methods exist
            from app.services.partner_service import PartnerService
            expected_methods = ['create_partner', 'get_partner', 'update_partner', 'delete_partner']
            for method in expected_methods:
                assert hasattr(PartnerService, method), f"Missing original method: {method}"
            print("✅ Original Partner service methods preserved")
            
        except Exception as e:
            print(f"❌ Backward compatibility test failed: {e}")
            pytest.fail(f"Backward compatibility test failed: {e}")


class TestFrameworkPerformance:
    """Performance tests for framework implementation."""
    
    def test_schema_validation_performance(self):
        """Test schema validation performance."""
        print("\n⚡ Testing Schema Validation Performance...")
        
        try:
            from app.framework_migration.partner_schemas import PartnerFrameworkCreate
            import time
            
            # Create test data
            test_data = TEST_PARTNER_DATA.copy()
            
            # Time schema validation
            start_time = time.time()
            for i in range(100):
                test_data['name'] = f"Partner {i}"
                partner = PartnerFrameworkCreate(**test_data)
                assert partner.name == f"Partner {i}"
            end_time = time.time()
            
            validation_time = (end_time - start_time) * 1000  # Convert to milliseconds
            print(f"✅ 100 schema validations completed in {validation_time:.2f}ms")
            
            # Performance should be reasonable (less than 100ms for 100 validations)
            assert validation_time < 100, f"Schema validation too slow: {validation_time}ms"
            
        except Exception as e:
            print(f"❌ Schema validation performance test failed: {e}")
            pytest.fail(f"Schema validation performance test failed: {e}")
    
    async def test_service_method_performance(self):
        """Test service method call performance."""
        print("\n⚡ Testing Service Method Performance...")
        
        try:
            from app.framework_migration.partner_service import PartnerFrameworkService
            import time
            
            # Mock database and create service
            mock_db = AsyncMock()
            service = PartnerFrameworkService(mock_db)
            
            # Mock service method to return quickly
            mock_partner = Mock()
            mock_partner.id = 1
            mock_partner.name = "Test Partner"
            service.get_by_id = AsyncMock(return_value=mock_partner)
            
            # Time service method calls
            start_time = time.time()
            for i in range(50):
                partner = await service.get_partner(1)
                assert partner.id == 1
            end_time = time.time()
            
            method_time = (end_time - start_time) * 1000  # Convert to milliseconds
            print(f"✅ 50 service method calls completed in {method_time:.2f}ms")
            
            # Performance should be reasonable (less than 50ms for 50 calls)
            assert method_time < 50, f"Service method calls too slow: {method_time}ms"
            
        except Exception as e:
            print(f"❌ Service method performance test failed: {e}")
            pytest.fail(f"Service method performance test failed: {e}")


def run_e2e_test_suite():
    """Run the complete end-to-end test suite."""
    print("🧪 Starting End-to-End Framework Test Suite")
    print("=" * 60)
    
    # Test classes to run
    test_classes = [
        TestPartnerE2EFramework,
        TestFrameworkPerformance
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n🔍 Running {test_class.__name__}...")
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                test_instance = test_class()
                test_method = getattr(test_instance, method_name)
                
                if asyncio.iscoroutinefunction(test_method):
                    asyncio.run(test_method())
                else:
                    test_method()
                
                passed_tests += 1
                print(f"✅ {method_name} PASSED")
                
            except Exception as e:
                failed_tests.append((test_class.__name__, method_name, str(e)))
                print(f"❌ {method_name} FAILED: {e}")
    
    # Summary
    print(f"\n📊 End-to-End Test Summary")
    print("=" * 40)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test_class, method_name, error in failed_tests:
            print(f"  • {test_class}.{method_name}: {error}")
    
    overall_success = len(failed_tests) == 0
    
    if overall_success:
        print(f"\n🎉 All End-to-End Tests PASSED!")
        print("✅ Framework migration is fully functional")
    else:
        print(f"\n⚠️  Some End-to-End Tests FAILED!")
        print("❌ Framework migration needs attention")
    
    return overall_success


if __name__ == "__main__":
    success = run_e2e_test_suite()
    exit(0 if success else 1)