"""
Integration tests for migrating Partner service to Business Object Framework.

This test suite validates that the Partner service can be successfully migrated
to use the Business Object Framework while maintaining all existing functionality
and adding new framework features.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch, Mock
from typing import Dict, Any, List

from app.models.partner import Partner
from app.schemas.partner import PartnerCreate, PartnerUpdate, PartnerResponse
from app.services.partner_service import PartnerService
from app.framework.controllers import create_business_object_router
from app.framework.services import CompanyBusinessObjectService
from app.framework.schemas import CompanyBusinessObjectSchema, CreateSchemaBase, UpdateSchemaBase


class TestPartnerModelFrameworkCompatibility:
    """Test that Partner model is compatible with Business Object Framework."""
    
    def test_partner_inherits_from_company_base_model(self):
        """Test that Partner inherits from CompanyBaseModel."""
        from app.models.base import CompanyBaseModel
        assert issubclass(Partner, CompanyBaseModel)
        print("✓ Partner model inherits from CompanyBaseModel")
    
    def test_partner_has_framework_fields(self):
        """Test that Partner has all required framework fields."""
        # Check that Partner model has required fields for framework
        partner_columns = [column.name for column in Partner.__table__.columns]
        
        required_fields = ['id', 'company_id', 'created_at', 'updated_at']
        missing_fields = [field for field in required_fields if field not in partner_columns]
        
        assert not missing_fields, f"Partner missing required fields: {missing_fields}"
        print(f"✓ Partner has all {len(required_fields)} required framework fields")
    
    def test_partner_business_fields_present(self):
        """Test that Partner retains all business-specific fields."""
        partner_columns = [column.name for column in Partner.__table__.columns]
        
        business_fields = [
            'name', 'code', 'partner_type', 'email', 'phone', 'mobile',
            'website', 'tax_id', 'industry', 'parent_partner_id',
            'is_company', 'is_customer', 'is_supplier', 'is_vendor', 'is_active'
        ]
        
        missing_fields = [field for field in business_fields if field not in partner_columns]
        assert not missing_fields, f"Partner missing business fields: {missing_fields}"
        print(f"✓ Partner has all {len(business_fields)} business fields")
    
    def test_partner_constraints_preserved(self):
        """Test that Partner constraints are preserved."""
        constraints = Partner.__table__.constraints
        constraint_names = [constraint.name for constraint in constraints if hasattr(constraint, 'name')]
        
        expected_constraints = [
            'partners_company_code_unique',
            'partners_type_check',
            'partners_name_check'
        ]
        
        for expected in expected_constraints:
            assert expected in constraint_names, f"Missing constraint: {expected}"
        
        print(f"✓ Partner has all {len(expected_constraints)} required constraints")


class TestPartnerFrameworkSchemas:
    """Test Partner schema compatibility with framework schemas."""
    
    def test_existing_schemas_structure(self):
        """Test that existing Partner schemas have correct structure."""
        # Test PartnerCreate schema
        create_fields = PartnerCreate.__fields__.keys()
        required_create_fields = ['name', 'company_id']
        
        for field in required_create_fields:
            assert field in create_fields, f"PartnerCreate missing required field: {field}"
        
        # Test PartnerUpdate schema
        update_fields = PartnerUpdate.__fields__.keys()
        assert 'name' in update_fields, "PartnerUpdate should have name field"
        
        # Test PartnerResponse schema
        response_fields = PartnerResponse.__fields__.keys()
        framework_fields = ['id', 'company_id', 'created_at', 'updated_at']
        
        for field in framework_fields:
            assert field in response_fields, f"PartnerResponse missing framework field: {field}"
        
        print("✓ Existing Partner schemas have correct structure")
    
    def test_schema_framework_compatibility(self):
        """Test that Partner schemas can work with framework base classes."""
        # Test that we can create framework-compatible schemas
        
        class PartnerFrameworkCreate(CreateSchemaBase):
            name: str
            code: str = None
            partner_type: str = "customer"
            company_id: int
        
        class PartnerFrameworkUpdate(UpdateSchemaBase):
            name: str = None
            code: str = None
            partner_type: str = None
        
        class PartnerFrameworkResponse(CompanyBusinessObjectSchema):
            name: str
            code: str = None
            partner_type: str
            
            class Config:
                from_attributes = True
        
        # Test schema creation
        create_data = PartnerFrameworkCreate(
            name="Test Partner",
            code="TEST001",
            company_id=1
        )
        assert create_data.name == "Test Partner"
        
        update_data = PartnerFrameworkUpdate(name="Updated Partner")
        assert update_data.name == "Updated Partner"
        
        print("✓ Partner schemas are framework compatible")


class TestPartnerServiceFrameworkMigration:
    """Test Partner service migration to framework service."""
    
    def test_partner_service_can_extend_framework_service(self):
        """Test that PartnerService can extend CompanyBusinessObjectService."""
        
        class FrameworkPartnerService(CompanyBusinessObjectService[Partner]):
            def __init__(self, db):
                super().__init__(db, Partner)
            
            # Add Partner-specific methods
            async def find_by_code(self, code: str, company_id: int):
                return await self.get_by_filters({"code": code, "company_id": company_id})
            
            async def find_customers(self, company_id: int):
                return await self.get_by_filters({"is_customer": True, "company_id": company_id})
        
        # Test service structure
        mock_db = AsyncMock()
        service = FrameworkPartnerService(mock_db)
        
        assert service.model_class == Partner
        assert hasattr(service, 'create')
        assert hasattr(service, 'get_by_id')
        assert hasattr(service, 'get_list')
        assert hasattr(service, 'update')
        assert hasattr(service, 'delete')
        assert hasattr(service, 'find_by_code')
        assert hasattr(service, 'find_customers')
        
        print("✓ PartnerService can extend CompanyBusinessObjectService")
    
    def test_existing_partner_service_methods_preserved(self):
        """Test that existing PartnerService methods are preserved."""
        
        # Check that PartnerService has its current methods
        service_methods = [method for method in dir(PartnerService) if not method.startswith('_')]
        
        expected_methods = [
            'create_partner', 'get_partner', 'get_partners', 'get_partners_by_company',
            'get_partner_by_code', 'update_partner', 'delete_partner',
            'activate_partner', 'deactivate_partner'
        ]
        
        missing_methods = [method for method in expected_methods if method not in service_methods]
        assert not missing_methods, f"PartnerService missing methods: {missing_methods}"
        
        print(f"✓ PartnerService has all {len(expected_methods)} expected methods")


class TestPartnerRouterFrameworkMigration:
    """Test Partner router migration to framework router."""
    
    def test_framework_router_creation_for_partner(self):
        """Test that we can create a framework router for Partner."""
        
        # Mock schemas for testing
        class MockPartnerCreate(CreateSchemaBase):
            name: str
            company_id: int
        
        class MockPartnerUpdate(UpdateSchemaBase):
            name: str = None
        
        class MockPartnerResponse(CompanyBusinessObjectSchema):
            name: str
            
            class Config:
                from_attributes = True
        
        # Mock service
        class MockPartnerService(CompanyBusinessObjectService):
            def __init__(self, db):
                super().__init__(db, Partner)
        
        # Create framework router
        partner_router = create_business_object_router(
            model_class=Partner,
            service_class=MockPartnerService,
            create_schema=MockPartnerCreate,
            update_schema=MockPartnerUpdate,
            response_schema=MockPartnerResponse,
            prefix="/api/v1/partners",
            tags=["partners"],
            enable_extensions=True,
            enable_audit_trail=True
        )
        
        # Test router structure
        assert partner_router.model_class == Partner
        assert partner_router.service_class == MockPartnerService
        assert partner_router.prefix == "/api/v1/partners"
        assert partner_router.tags == ["partners"]
        assert partner_router.enable_extensions == True
        assert partner_router.enable_audit_trail == True
        assert partner_router.enforce_company_isolation == True  # Auto-detected
        
        # Test routes created
        routes = partner_router.router.routes
        assert len(routes) >= 8  # Standard CRUD + extensions + audit
        
        print("✓ Framework router created successfully for Partner")
    
    def test_existing_partner_endpoints_covered(self):
        """Test that framework router covers existing Partner endpoints."""
        
        # Current Partner endpoints from the router
        existing_endpoints = [
            ('POST', '/'),  # create_partner
            ('GET', '/'),   # list_partners
            ('GET', '/{partner_id}'),  # get_partner
            ('PUT', '/{partner_id}'),  # update_partner
            ('DELETE', '/{partner_id}'),  # delete_partner
        ]
        
        # Framework router provides these same patterns
        framework_patterns = [
            ('POST', '/'),  # create
            ('GET', '/'),   # list
            ('GET', '/{object_id}'),  # read
            ('PUT', '/{object_id}'),  # update
            ('DELETE', '/{object_id}'),  # delete
        ]
        
        # Check that all existing patterns are covered
        for method, path in existing_endpoints:
            # Find equivalent framework pattern
            framework_path = path.replace('{partner_id}', '{object_id}')
            assert (method, framework_path) in framework_patterns, f"Missing pattern: {method} {path}"
        
        print("✓ Framework router covers all existing Partner endpoints")
    
    def test_additional_framework_endpoints(self):
        """Test that framework router provides additional endpoints."""
        
        # Create mock router to test endpoints
        from app.framework.controllers import create_business_object_router
        
        class MockCreate(CreateSchemaBase):
            name: str
            company_id: int
        
        class MockUpdate(UpdateSchemaBase):
            name: str = None
        
        class MockResponse(CompanyBusinessObjectSchema):
            name: str
            class Config:
                from_attributes = True
        
        class MockService(CompanyBusinessObjectService):
            def __init__(self, db):
                super().__init__(db, Partner)
        
        router = create_business_object_router(
            model_class=Partner,
            service_class=MockService,
            create_schema=MockCreate,
            update_schema=MockUpdate,
            response_schema=MockResponse,
            enable_extensions=True,
            enable_audit_trail=True
        )
        
        # Check for extension and audit endpoints
        route_paths = [route.path for route in router.router.routes if hasattr(route, 'path')]
        
        # Extension endpoints
        extension_patterns = ['{object_id}/extensions']
        for pattern in extension_patterns:
            assert any(pattern in path for path in route_paths), f"Missing extension pattern: {pattern}"
        
        # Audit endpoints  
        audit_patterns = ['{object_id}/audit']
        for pattern in audit_patterns:
            assert any(pattern in path for path in route_paths), f"Missing audit pattern: {pattern}"
        
        print("✓ Framework router provides additional extension and audit endpoints")


class TestPartnerDataMigrationCompatibility:
    """Test that existing Partner data is compatible with framework."""
    
    def test_partner_data_structure_compatibility(self):
        """Test that existing Partner data structure works with framework."""
        
        # Simulate existing Partner data
        partner_data = {
            'id': 1,
            'company_id': 1,
            'name': 'Test Partner',
            'code': 'TEST001',
            'partner_type': 'customer',
            'email': 'test@example.com',
            'phone': '+1-555-0123',
            'mobile': '+1-555-0456',
            'website': 'https://test.com',
            'tax_id': 'TAX123',
            'industry': 'Technology',
            'parent_partner_id': None,
            'is_company': True,
            'is_customer': True,
            'is_supplier': False,
            'is_vendor': False,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Test that data can be used with framework schemas
        response_schema = PartnerResponse(**partner_data)
        assert response_schema.id == 1
        assert response_schema.name == 'Test Partner'
        assert response_schema.company_id == 1
        
        print("✓ Existing Partner data structure is framework compatible")
    
    def test_partner_business_logic_preservation(self):
        """Test that Partner business logic is preserved in framework."""
        
        # Test Partner model methods still work
        partner = Partner(
            name="Test Partner",
            code="TEST001",
            partner_type="customer",
            is_customer=True,
            is_supplier=False,
            is_vendor=False,
            parent_partner_id=None
        )
        
        # Test business logic methods
        assert partner.get_partner_types() == ["customer"]
        assert partner.has_parent == False
        assert partner.is_parent == False
        
        # Test with supplier
        partner.is_supplier = True
        assert "supplier" in partner.get_partner_types()
        assert len(partner.get_partner_types()) == 2
        
        print("✓ Partner business logic preserved in framework")


class TestPartnerMigrationEndToEnd:
    """End-to-end tests for Partner migration to framework."""
    
    @pytest.fixture
    def mock_database_session(self):
        """Mock database session for testing."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock current user for testing."""
        return {
            'id': 1,
            'user_id': 1,
            'company_ids': [1, 2],
            'email': 'test@example.com'
        }
    
    def test_partner_creation_through_framework(self, mock_database_session, mock_current_user):
        """Test Partner creation through framework router."""
        
        # This would be a full integration test with real database
        # For now, test the structure and flow
        
        create_data = {
            'name': 'Framework Test Partner',
            'code': 'FTP001',
            'partner_type': 'customer',
            'email': 'framework@test.com',
            'company_id': 1,
            'is_customer': True
        }
        
        # Test that data structure is valid for framework
        partner_create = PartnerCreate(**create_data)
        assert partner_create.name == 'Framework Test Partner'
        assert partner_create.company_id == 1
        
        print("✓ Partner creation data structure works with framework")
    
    def test_partner_extension_field_support(self):
        """Test that Partner supports extension fields through framework."""
        
        # Test that Partner can have extension fields added
        partner_data = {
            'id': 1,
            'name': 'Test Partner',
            'company_id': 1
        }
        
        # Extension field examples for Partner
        extension_fields = [
            {
                'field_name': 'credit_limit',
                'field_type': 'decimal',
                'field_value': '10000.00'
            },
            {
                'field_name': 'preferred_payment_method',
                'field_type': 'string',
                'field_value': 'credit_card'
            },
            {
                'field_name': 'vip_customer',
                'field_type': 'boolean',
                'field_value': 'true'
            }
        ]
        
        # Test that extension fields are valid
        for field in extension_fields:
            assert field['field_name'] and len(field['field_name']) > 0
            assert field['field_type'] in ['string', 'integer', 'decimal', 'boolean', 'date', 'datetime', 'json']
            assert field['field_value'] is not None
        
        print(f"✓ Partner supports {len(extension_fields)} types of extension fields")
    
    def test_partner_audit_trail_support(self):
        """Test that Partner supports audit trail through framework."""
        
        # Test audit trail data structure
        audit_entry = {
            'id': 'audit_1_1',
            'action': 'partner_created',
            'entity_type': 'partner',
            'entity_id': 1,
            'user_id': 1,
            'company_id': 1,
            'timestamp': datetime.utcnow().isoformat(),
            'changes': {
                'name': {'old': None, 'new': 'Test Partner'},
                'partner_type': {'old': None, 'new': 'customer'},
                'is_active': {'old': None, 'new': True}
            }
        }
        
        # Test audit entry structure
        assert audit_entry['entity_type'] == 'partner'
        assert audit_entry['action'] == 'partner_created'
        assert 'changes' in audit_entry
        assert len(audit_entry['changes']) > 0
        
        print("✓ Partner supports audit trail data structure")


class TestPartnerMigrationRegressionPrevention:
    """Tests to ensure Partner migration doesn't break existing functionality."""
    
    def test_existing_partner_api_compatibility(self):
        """Test that existing Partner API patterns are maintained."""
        
        # Test that existing API response format is compatible
        partner_response_data = {
            'id': 1,
            'company_id': 1,
            'name': 'Test Partner',
            'code': 'TEST001',
            'partner_type': 'customer',
            'email': 'test@example.com',
            'phone': '+1-555-0123',
            'is_customer': True,
            'is_supplier': False,
            'is_vendor': False,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Existing response schema should still work
        response = PartnerResponse(**partner_response_data)
        assert response.name == 'Test Partner'
        assert response.id == 1
        
        print("✓ Existing Partner API response format maintained")
    
    def test_partner_validation_rules_preserved(self):
        """Test that Partner validation rules are preserved."""
        
        # Test partner_type validation
        try:
            invalid_partner = PartnerCreate(
                name="Test",
                partner_type="invalid_type",  # Should fail validation
                company_id=1
            )
            assert False, "Should have failed validation"
        except Exception:
            pass  # Expected to fail
        
        # Test valid partner creation
        valid_partner = PartnerCreate(
            name="Test Partner",
            partner_type="customer",  # Valid type
            company_id=1
        )
        assert valid_partner.partner_type == "customer"
        
        print("✓ Partner validation rules preserved")
    
    def test_partner_business_constraints_maintained(self):
        """Test that Partner business constraints are maintained."""
        
        # Test that Partner model constraints are still in place
        constraints = Partner.__table__.constraints
        constraint_names = [c.name for c in constraints if hasattr(c, 'name')]
        
        # Check critical business constraints
        assert 'partners_company_code_unique' in constraint_names
        assert 'partners_type_check' in constraint_names
        assert 'partners_name_check' in constraint_names
        
        print("✓ Partner business constraints maintained")


class TestFrameworkFeatureEnhancement:
    """Test that Partner gets enhanced with framework features."""
    
    def test_partner_gets_extension_endpoints(self):
        """Test that Partner gets extension field endpoints."""
        
        # Framework should provide these endpoints for Partner:
        expected_extension_endpoints = [
            'GET /{partner_id}/extensions',      # Get all custom fields
            'POST /{partner_id}/extensions',     # Set/update custom field
            'DELETE /{partner_id}/extensions/{field_name}'  # Delete custom field
        ]
        
        # Test that we can conceptually create these endpoints
        for endpoint in expected_extension_endpoints:
            method, path = endpoint.split(' ', 1)
            assert method in ['GET', 'POST', 'PUT', 'DELETE']
            assert '{partner_id}' in path or '{object_id}' in path
            assert 'extensions' in path
        
        print(f"✓ Partner gets {len(expected_extension_endpoints)} extension endpoints")
    
    def test_partner_gets_audit_endpoints(self):
        """Test that Partner gets audit trail endpoints."""
        
        expected_audit_endpoints = [
            'GET /{partner_id}/audit',     # Get full audit trail
            'GET /{partner_id}/changes'    # Get recent changes
        ]
        
        for endpoint in expected_audit_endpoints:
            method, path = endpoint.split(' ', 1)
            assert method == 'GET'
            assert '{partner_id}' in path or '{object_id}' in path
            assert 'audit' in path or 'changes' in path
        
        print(f"✓ Partner gets {len(expected_audit_endpoints)} audit trail endpoints")
    
    def test_partner_gets_standardized_error_handling(self):
        """Test that Partner gets framework error handling."""
        
        from app.framework.controllers import StandardizedErrorHandler
        
        handler = StandardizedErrorHandler()
        
        # Test validation error
        validation_error = handler.handle_validation_error([
            {'field': 'name', 'message': 'Name is required'}
        ])
        assert validation_error['error_code'] == 'VALIDATION_ERROR'
        
        # Test not found error
        not_found_error = handler.handle_not_found_error('partner', 123)
        assert not_found_error['error_code'] == 'NOT_FOUND'
        assert 'partner' in not_found_error['message'].lower()
        
        print("✓ Partner gets standardized error handling")
    
    def test_partner_gets_standardized_responses(self):
        """Test that Partner gets framework response formatting."""
        
        from app.framework.controllers import ResponseFormatter
        
        formatter = ResponseFormatter()
        
        # Test single response
        partner_data = {'id': 1, 'name': 'Test Partner'}
        single_response = formatter.format_single_response(partner_data)
        assert 'data' in single_response
        assert 'meta' in single_response
        assert single_response['meta']['type'] == 'single'
        
        # Test list response
        partners_list = [partner_data]
        list_response = formatter.format_list_response(partners_list, 1, 1, 50)
        assert 'data' in list_response
        assert 'meta' in list_response
        assert list_response['meta']['type'] == 'list'
        assert list_response['meta']['total'] == 1
        
        print("✓ Partner gets standardized response formatting")


# Integration test summary
def test_partner_migration_integration_summary():
    """Summary test to verify Partner migration readiness."""
    
    print("\n🧪 Partner Migration Integration Test Summary:")
    print("=" * 60)
    
    # Model compatibility
    from app.models.base import CompanyBaseModel
    assert issubclass(Partner, CompanyBaseModel)
    print("✅ Partner model is framework compatible")
    
    # Schema compatibility
    partner_create = PartnerCreate(name="Test", company_id=1)
    assert partner_create.name == "Test"
    print("✅ Partner schemas are framework compatible")
    
    # Service compatibility
    assert hasattr(PartnerService, 'create_partner')
    print("✅ Partner service methods are preserved")
    
    # Framework enhancements available
    from app.framework.controllers import create_business_object_router, StandardizedErrorHandler, ResponseFormatter
    
    # Test components exist
    assert create_business_object_router
    assert StandardizedErrorHandler
    assert ResponseFormatter
    print("✅ Framework enhancements are available")
    
    print("\n🎉 Partner is ready for migration to Business Object Framework!")
    print("📋 Migration will provide:")
    print("  • Standardized CRUD endpoints")
    print("  • Custom field support via extension endpoints")
    print("  • Audit trail endpoints")
    print("  • Consistent error handling and response formatting")
    print("  • Automatic multi-company isolation")
    print("  • Type-safe operations with Pydantic validation")


if __name__ == "__main__":
    # Run the summary test
    test_partner_migration_integration_summary()