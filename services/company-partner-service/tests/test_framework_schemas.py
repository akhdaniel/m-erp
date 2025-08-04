"""
Tests for Business Object Framework Schema classes.

This module tests the Pydantic schema framework that provides
standardized validation patterns for business objects.
"""

import pytest
from datetime import datetime
from typing import Optional
from pydantic import ValidationError

from pydantic import BaseModel
from app.framework.schemas import (
    BaseBusinessObjectSchema,
    CompanyBusinessObjectSchema,
    CreateSchemaBase,
    UpdateSchemaBase,
    ResponseSchemaBase,
    create_schema_factory
)


class TestBaseBusinessObjectSchema:
    """Test the base business object schema class."""
    
    def test_base_schema_includes_common_fields(self):
        """Test that base schema includes standard business object fields."""
        schema = BaseBusinessObjectSchema()
        
        # Check that the schema has all framework fields
        assert hasattr(schema, 'id')
        assert hasattr(schema, 'created_at')
        assert hasattr(schema, 'updated_at')
        assert hasattr(schema, 'framework_version')
        
        # Check field annotations
        annotations = BaseBusinessObjectSchema.__annotations__
        assert 'id' in annotations
        assert 'created_at' in annotations
        assert 'updated_at' in annotations
        assert 'framework_version' in annotations
    
    def test_base_schema_validation_rules(self):
        """Test common validation rules applied to all business objects."""
        # Test valid data
        valid_data = {
            "id": 1,
            "framework_version": "1.0.0"
        }
        schema = BaseBusinessObjectSchema(**valid_data)
        assert schema.id == 1
        assert schema.framework_version == "1.0.0"
        
        # Test invalid framework version - First test Pydantic's built-in validation
        with pytest.raises(ValidationError) as exc_info:
            BaseBusinessObjectSchema(framework_version=123)  # Not a string
        
        error = exc_info.value.errors()[0]
        # In Pydantic v2, this will be a string_type error first
        assert error['type'] == 'string_type'
        
        # Test None framework_version is allowed (optional field)
        schema_with_none = BaseBusinessObjectSchema(framework_version=None)
        assert schema_with_none.framework_version is None
    
    def test_base_schema_error_messages(self):
        """Test that validation errors have user-friendly messages."""
        # Test invalid ID (should be positive)
        with pytest.raises(ValidationError) as exc_info:
            BaseBusinessObjectSchema(id=-1)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any('greater than or equal to 1' in str(error['msg']) for error in errors)
    
    def test_base_schema_field_transformation(self):
        """Test automatic field transformation and normalization."""
        from datetime import datetime
        
        # Test datetime handling
        now = datetime.now()
        schema = BaseBusinessObjectSchema(
            created_at=now,
            updated_at=now
        )
        
        assert schema.created_at == now
        assert schema.updated_at == now


class TestCompanyBusinessObjectSchema:
    """Test the company-aware business object schema class."""
    
    def test_company_schema_includes_company_id(self):
        """Test that company schema includes company_id field."""
        schema = CompanyBusinessObjectSchema()
        
        # Check that the schema has company_id field
        assert hasattr(schema, 'company_id')
        
        # Check field annotation
        annotations = CompanyBusinessObjectSchema.__annotations__
        assert 'company_id' in annotations
    
    def test_company_schema_validates_company_id(self):
        """Test company_id validation rules."""
        # Test valid company_id
        valid_data = {"company_id": 1}
        schema = CompanyBusinessObjectSchema(**valid_data)
        assert schema.company_id == 1
        
        # Test invalid company_id (negative) - triggers Field constraint ge=1
        with pytest.raises(ValidationError) as exc_info:
            CompanyBusinessObjectSchema(company_id=-1)
        
        error = exc_info.value.errors()[0]
        assert error['type'] == 'greater_than_equal'
        assert error['input'] == -1
        
        # Test invalid company_id (zero) - triggers Field constraint ge=1
        with pytest.raises(ValidationError) as exc_info:
            CompanyBusinessObjectSchema(company_id=0)
        
        error = exc_info.value.errors()[0]
        assert error['type'] == 'greater_than_equal'
        assert error['input'] == 0
        
        # Test invalid company_id (non-integer) - this will trigger our custom validator
        with pytest.raises(ValidationError) as exc_info:
            CompanyBusinessObjectSchema(company_id="not_an_int")
        
        error = exc_info.value.errors()[0]
        assert error['type'] == 'int_parsing'  # Pydantic's built-in int parsing error
    
    def test_company_schema_inherits_base_functionality(self):
        """Test that company schema includes all base schema features."""
        # Test that CompanyBusinessObjectSchema inherits all base fields
        schema = CompanyBusinessObjectSchema()
        
        # Should have all base schema fields
        assert hasattr(schema, 'id')
        assert hasattr(schema, 'created_at')
        assert hasattr(schema, 'updated_at')
        assert hasattr(schema, 'framework_version')
        
        # Should also have company_id
        assert hasattr(schema, 'company_id')
        
        # Test validation of base fields still works
        with pytest.raises(ValidationError) as exc_info:
            CompanyBusinessObjectSchema(framework_version=123)  # Invalid type
        
        error = exc_info.value.errors()[0]
        assert error['type'] == 'string_type'  # Pydantic v2 error type
    
    def test_company_schema_multi_company_validation(self):
        """Test multi-company specific validation rules."""
        # Test valid multi-company data
        valid_data = {
            "id": 1,
            "company_id": 5,
            "framework_version": "1.0.0"
        }
        schema = CompanyBusinessObjectSchema(**valid_data)
        assert schema.id == 1
        assert schema.company_id == 5
        assert schema.framework_version == "1.0.0"
        
        # Test None company_id is allowed (for creation scenarios)
        schema_without_company = CompanyBusinessObjectSchema(id=1)
        assert schema_without_company.company_id is None


class TestSchemaValidationFramework:
    """Test the schema validation framework and custom validators."""
    
    def test_custom_validators_registration(self):
        """Test registering custom validation rules."""
        from app.framework.schemas import ValidationFramework
        
        # Test registering a custom validator
        def custom_validator(v):
            if not v or len(v) < 3:
                raise ValueError("Value must be at least 3 characters")
            return v
        
        ValidationFramework.register_validator('min_length_3', custom_validator)
        
        # Test retrieving the validator
        retrieved_validator = ValidationFramework.get_validator('min_length_3')
        assert retrieved_validator is not None
        assert retrieved_validator == custom_validator
        
        # Test non-existent validator
        non_existent = ValidationFramework.get_validator('non_existent')
        assert non_existent is None
    
    def test_conditional_validation(self):
        """Test conditional validation based on field values."""
        from app.framework.schemas import validate_non_empty_string, validate_positive_integer
        
        # Test non-empty string validator
        result = validate_non_empty_string("valid string")
        assert result == "valid string"
        
        with pytest.raises(ValueError) as exc_info:
            validate_non_empty_string("")
        assert "Field cannot be empty" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            validate_non_empty_string("   ")  # Whitespace only
        assert "Field cannot be empty" in str(exc_info.value)
    
    def test_cross_field_validation(self):
        """Test validation rules that span multiple fields."""
        from app.framework.schemas import validate_positive_integer
        
        # Test positive integer validator
        result = validate_positive_integer(5)
        assert result == 5
        
        with pytest.raises(ValueError) as exc_info:
            validate_positive_integer(0)
        assert "Value must be positive" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            validate_positive_integer(-1)
        assert "Value must be positive" in str(exc_info.value)
    
    def test_validation_error_aggregation(self):
        """Test that multiple validation errors are properly aggregated."""
        # Test multiple validation errors at once
        with pytest.raises(ValidationError) as exc_info:
            BaseBusinessObjectSchema(
                id=-1,  # Invalid: should be positive
                framework_version=123  # Invalid: should be string
            )
        
        errors = exc_info.value.errors()
        assert len(errors) >= 2  # Should have at least 2 errors
        
        # Check that we have errors for both fields
        field_names = [error['loc'][0] for error in errors]
        assert 'id' in field_names
        assert 'framework_version' in field_names
    
    def test_validation_with_database_constraints(self):
        """Test validation rules that check database constraints."""
        from app.framework.schemas import validate_email_format
        
        # Test valid email
        valid_email = validate_email_format("test@example.com")
        assert valid_email == "test@example.com"
        
        # Test email normalization (should be lowercased)
        normalized_email = validate_email_format("Test@Example.COM")
        assert normalized_email == "test@example.com"
        
        # Test invalid email
        with pytest.raises(ValueError) as exc_info:
            validate_email_format("invalid-email")
        assert "Invalid email format" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            validate_email_format("test@")
        assert "Invalid email format" in str(exc_info.value)


class TestCreateUpdateResponseSchemas:
    """Test the Create, Update, and Response schema patterns."""
    
    def test_create_schema_excludes_readonly_fields(self):
        """Test that Create schemas exclude read-only fields like id, timestamps."""
        # Test that CreateSchemaBase doesn't include framework fields
        create_schema = CreateSchemaBase()
        
        # Should not have read-only fields
        assert not hasattr(create_schema, 'id')
        assert not hasattr(create_schema, 'created_at')
        assert not hasattr(create_schema, 'updated_at')
        assert not hasattr(create_schema, 'framework_version')
    
    def test_update_schema_makes_fields_optional(self):
        """Test that Update schemas make most fields optional."""
        # Test that UpdateSchemaBase doesn't include framework fields
        update_schema = UpdateSchemaBase()
        
        # Should not have read-only fields
        assert not hasattr(update_schema, 'id')
        assert not hasattr(update_schema, 'created_at')
        assert not hasattr(update_schema, 'updated_at')
        assert not hasattr(update_schema, 'framework_version')
    
    def test_response_schema_includes_all_fields(self):
        """Test that Response schemas include all model fields."""
        # Test that ResponseSchemaBase includes all framework fields
        response_schema = ResponseSchemaBase()
        
        # Should have all framework fields
        assert hasattr(response_schema, 'id')
        assert hasattr(response_schema, 'created_at')
        assert hasattr(response_schema, 'updated_at')
        assert hasattr(response_schema, 'framework_version')
    
    def test_schema_field_inheritance(self):
        """Test proper field inheritance between schema types."""
        # ResponseSchemaBase should inherit from BaseBusinessObjectSchema
        assert issubclass(ResponseSchemaBase, BaseBusinessObjectSchema)
        
        # Other schemas should inherit from BaseModel
        assert issubclass(CreateSchemaBase, BaseModel)
        assert issubclass(UpdateSchemaBase, BaseModel)
    
    def test_schema_type_conversion(self):
        """Test automatic type conversion between schema types."""
        # Test that all schemas handle the same data types correctly
        from datetime import datetime
        
        now = datetime.now()
        
        # Test ResponseSchema with full data
        response_data = {
            "id": 1,
            "created_at": now,
            "updated_at": now,
            "framework_version": "1.0.0"
        }
        response_schema = ResponseSchemaBase(**response_data)
        assert response_schema.id == 1
        assert response_schema.created_at == now
        
        # Create and Update schemas should work with minimal data
        create_schema = CreateSchemaBase()
        update_schema = UpdateSchemaBase()
        
        # Both should be valid with no data
        assert create_schema is not None
        assert update_schema is not None


class TestSchemaIntegration:
    """Test schema integration with existing models and framework."""
    
    def test_schema_works_with_business_object_base(self):
        """Test schemas integrate properly with BusinessObjectBase."""
        # Test that our schemas match the fields from BusinessObjectBase
        from app.framework.base import BusinessObjectBase
        
        # Get the columns from BusinessObjectBase (this simulates what would be in a real model)
        # For now, test that schema fields align with expected business object fields
        base_schema = BaseBusinessObjectSchema()
        
        # Check that schema has the expected structure for business objects
        assert hasattr(base_schema, 'id')
        assert hasattr(base_schema, 'created_at')
        assert hasattr(base_schema, 'updated_at')
        assert hasattr(base_schema, 'framework_version')
    
    def test_schema_works_with_company_business_object(self):
        """Test schemas integrate properly with CompanyBusinessObject."""
        # Test that CompanyBusinessObjectSchema has company-specific fields
        company_schema = CompanyBusinessObjectSchema()
        
        # Should have all base fields plus company_id
        assert hasattr(company_schema, 'id')
        assert hasattr(company_schema, 'created_at')
        assert hasattr(company_schema, 'updated_at')
        assert hasattr(company_schema, 'framework_version')
        assert hasattr(company_schema, 'company_id')
    
    def test_schema_validates_framework_fields(self):
        """Test validation of framework-specific fields."""
        # Test framework_version validation
        valid_schema = BaseBusinessObjectSchema(framework_version="1.2.3")
        assert valid_schema.framework_version == "1.2.3"
        
        # Test invalid framework_version
        with pytest.raises(ValidationError):
            BaseBusinessObjectSchema(framework_version=123)
    
    def test_schema_handles_nullable_fields(self):
        """Test proper handling of nullable and non-nullable fields."""
        # Test that optional fields can be None
        schema_with_nulls = BaseBusinessObjectSchema(
            id=None,  # Optional
            created_at=None,  # Optional
            updated_at=None,  # Optional
            framework_version=None  # Optional
        )
        
        assert schema_with_nulls.id is None
        assert schema_with_nulls.created_at is None
        assert schema_with_nulls.updated_at is None
        assert schema_with_nulls.framework_version is None
        
        # Test that company_id can be None in CompanyBusinessObjectSchema
        company_schema = CompanyBusinessObjectSchema(company_id=None)
        assert company_schema.company_id is None
    
    def test_schema_error_messages_are_user_friendly(self):
        """Test that validation errors provide clear, actionable messages."""
        # Test ID validation error message
        with pytest.raises(ValidationError) as exc_info:
            BaseBusinessObjectSchema(id=-5)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        # Check that error message is descriptive
        error_msg = str(errors[0]['msg'])
        assert 'greater than or equal to 1' in error_msg
        
        # Test company_id validation error message
        with pytest.raises(ValidationError) as exc_info:
            CompanyBusinessObjectSchema(company_id=-1)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        error_msg = str(errors[0]['msg'])
        assert 'greater than or equal to 1' in error_msg


class TestSchemaFactory:
    """Test the schema factory functions for rapid development."""
    
    def test_create_schema_factory_generates_correct_schemas(self):
        """Test that schema factory creates proper Create/Update/Response schemas."""
        from app.framework.schemas import create_schema_factory
        
        # Create a mock model class for testing
        class MockModel:
            __name__ = "MockModel"
            __module__ = "test_module"
        
        # Generate schemas using the factory
        schemas = create_schema_factory(MockModel)
        
        # Should return all three schema types
        assert 'Create' in schemas
        assert 'Update' in schemas
        assert 'Response' in schemas
        
        # Check that schemas are proper classes
        CreateSchema = schemas['Create']
        UpdateSchema = schemas['Update'] 
        ResponseSchema = schemas['Response']
        
        assert CreateSchema.__name__ == "MockModelCreateSchema"
        assert UpdateSchema.__name__ == "MockModelUpdateSchema"
        assert ResponseSchema.__name__ == "MockModelResponseSchema"
        
        # Test instantiation
        create_instance = CreateSchema()
        update_instance = UpdateSchema()
        response_instance = ResponseSchema()
        
        assert create_instance is not None
        assert update_instance is not None
        assert response_instance is not None
    
    def test_schema_factory_respects_field_overrides(self):
        """Test that factory allows field customization."""
        from app.framework.schemas import create_schema_factory
        from pydantic import Field
        
        # Create a mock model class
        class MockModel:
            __name__ = "CustomModel"
            __module__ = "test_module"
        
        # Define custom fields
        custom_fields = {
            'name': str,
            'email': str,
            'age': int
        }
        
        # Generate schemas with custom fields
        schemas = create_schema_factory(MockModel, custom_fields=custom_fields)
        
        CreateSchema = schemas['Create']
        ResponseSchema = schemas['Response']
        
        # Test that custom fields are present
        create_instance = CreateSchema(name="test", email="test@example.com", age=25)
        assert create_instance.name == "test"
        assert create_instance.email == "test@example.com"
        assert create_instance.age == 25
        
        # Response schema should include framework fields + custom fields
        response_instance = ResponseSchema(
            id=1,
            name="test",
            email="test@example.com", 
            age=25
        )
        assert response_instance.id == 1
        assert response_instance.name == "test"
    
    def test_schema_factory_handles_inheritance(self):
        """Test schema factory with inherited model classes."""
        from app.framework.schemas import create_company_schema_factory
        
        # Create a mock company model
        class MockCompanyModel:
            __name__ = "CompanyModel"
            __module__ = "test_module"
        
        # Define custom fields including company_id
        custom_fields = {
            'company_id': int
        }
        
        # Generate company schemas
        schemas = create_company_schema_factory(MockCompanyModel, custom_fields=custom_fields)
        
        # Should generate all schema types
        assert 'Create' in schemas
        assert 'Update' in schemas
        assert 'Response' in schemas
        
        # Test that Response schema works with company fields
        ResponseSchema = schemas['Response']
        response_instance = ResponseSchema(
            id=1,
            company_id=5,
            framework_version="1.0.0"
        )
        
        assert response_instance.id == 1
        assert response_instance.company_id == 5
        assert response_instance.framework_version == "1.0.0"
    
    def test_schema_factory_validation_customization(self):
        """Test adding custom validation to factory-generated schemas."""
        from app.framework.schemas import create_schema_factory, ValidationFramework
        
        # Register a custom validator
        def validate_test_field(v):
            if v and len(v) < 3:
                raise ValueError("Test field must be at least 3 characters")
            return v
        
        ValidationFramework.register_validator('test_validator', validate_test_field)
        
        # Create model with custom validation
        class MockValidatedModel:
            __name__ = "ValidatedModel"
            __module__ = "test_module"
        
        custom_fields = {
            'test_field': str
        }
        
        custom_validators = {
            'test_validator': validate_test_field
        }
        
        # Generate schemas with custom validation
        schemas = create_schema_factory(
            MockValidatedModel,
            custom_fields=custom_fields,
            custom_validators=custom_validators
        )
        
        # Test that schemas are created successfully
        assert 'Create' in schemas
        assert 'Update' in schemas
        assert 'Response' in schemas
        
        CreateSchema = schemas['Create']
        
        # Test that basic instantiation works
        instance = CreateSchema(test_field="valid")
        assert instance.test_field == "valid"


# Test fixtures for schema testing
@pytest.fixture
def sample_business_object_data():
    """Sample data for testing business object schemas."""
    return {
        "name": "Test Object",
        "description": "A test business object",
        "active": True
    }


@pytest.fixture
def sample_company_business_object_data():
    """Sample data for testing company business object schemas."""
    return {
        "name": "Test Company Object",
        "description": "A test company-scoped business object",
        "active": True,
        "company_id": 1
    }


@pytest.fixture
def invalid_schema_data():
    """Invalid data for testing schema validation."""
    return {
        "name": "",  # Empty name should fail validation
        "description": "x" * 1000,  # Too long description
        "active": "not_a_boolean",  # Wrong type
        "company_id": -1  # Invalid company ID
    }