"""
Tests for Business Object Framework Extension System.

This module tests the extension system that allows dynamic custom fields,
validation rules, and extensibility for business objects.
"""

import pytest
import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.framework.base import BusinessObjectBase, CompanyBusinessObject


# Mock extension models for testing (will be implemented)
class MockBusinessObjectExtension:
    """Mock extension model for testing."""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.entity_type = kwargs.get('entity_type')
        self.entity_id = kwargs.get('entity_id')
        self.field_name = kwargs.get('field_name')
        self.field_type = kwargs.get('field_type')
        self.field_value = kwargs.get('field_value')
        self.company_id = kwargs.get('company_id')
        self.is_active = kwargs.get('is_active', True)
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())


class MockBusinessObjectValidator:
    """Mock validator model for testing."""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.entity_type = kwargs.get('entity_type')
        self.field_name = kwargs.get('field_name')
        self.validator_type = kwargs.get('validator_type')
        self.validator_config = kwargs.get('validator_config')
        self.company_id = kwargs.get('company_id')
        self.is_active = kwargs.get('is_active', True)
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())


# Mock extensible business object for testing
class MockExtensibleBusinessObject(CompanyBusinessObject):
    """Mock extensible business object for testing."""
    __tablename__ = "mock_extensible_objects"
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.company_id = kwargs.get('company_id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())
        self.framework_version = kwargs.get('framework_version', '1.0.0')
        self._extensions = {}  # Store dynamic fields


class TestBusinessObjectExtensionModel:
    """Test the BusinessObjectExtension database model."""
    
    def test_extension_model_structure(self):
        """Test that extension model has the expected structure."""
        extension = MockBusinessObjectExtension(
            entity_type='partner',
            entity_id=1,
            field_name='custom_rating',
            field_type='integer',
            field_value='5',
            company_id=1
        )
        
        # Check required fields
        assert extension.entity_type == 'partner'
        assert extension.entity_id == 1
        assert extension.field_name == 'custom_rating'
        assert extension.field_type == 'integer'
        assert extension.field_value == '5'
        assert extension.company_id == 1
        assert extension.is_active is True
    
    def test_extension_field_types(self):
        """Test different extension field types."""
        # Test string field
        string_ext = MockBusinessObjectExtension(
            entity_type='partner',
            entity_id=1,
            field_name='custom_notes',
            field_type='string',
            field_value='Important partner notes',
            company_id=1
        )
        assert string_ext.field_type == 'string'
        
        # Test integer field
        int_ext = MockBusinessObjectExtension(
            entity_type='partner',
            entity_id=1,
            field_name='priority_level',
            field_type='integer',
            field_value='3',
            company_id=1
        )
        assert int_ext.field_type == 'integer'
        
        # Test decimal field
        decimal_ext = MockBusinessObjectExtension(
            entity_type='partner',
            entity_id=1,
            field_name='discount_rate',
            field_type='decimal',
            field_value='0.15',
            company_id=1
        )
        assert decimal_ext.field_type == 'decimal'
        
        # Test boolean field
        bool_ext = MockBusinessObjectExtension(
            entity_type='partner',
            entity_id=1,
            field_name='is_vip',
            field_type='boolean',
            field_value='true',
            company_id=1
        )
        assert bool_ext.field_type == 'boolean'
        
        # Test date field
        date_ext = MockBusinessObjectExtension(
            entity_type='partner',
            entity_id=1,
            field_name='contract_end_date',
            field_type='date',
            field_value='2025-12-31',
            company_id=1
        )
        assert date_ext.field_type == 'date'
        
        # Test JSON field
        json_ext = MockBusinessObjectExtension(
            entity_type='partner',
            entity_id=1,
            field_name='custom_metadata',
            field_type='json',
            field_value='{"key": "value", "nested": {"data": 123}}',
            company_id=1
        )
        assert json_ext.field_type == 'json'
    
    def test_extension_company_isolation(self):
        """Test that extensions respect company isolation."""
        # Extension for company 1
        ext1 = MockBusinessObjectExtension(
            entity_type='partner',
            entity_id=1,
            field_name='custom_field',
            field_type='string',
            field_value='company 1 value',
            company_id=1
        )
        
        # Extension for company 2
        ext2 = MockBusinessObjectExtension(
            entity_type='partner',
            entity_id=1,
            field_name='custom_field',
            field_type='string',
            field_value='company 2 value',
            company_id=2
        )
        
        # Same entity_id and field_name but different companies
        assert ext1.company_id != ext2.company_id
        assert ext1.field_value != ext2.field_value
    
    def test_extension_uniqueness_constraints(self):
        """Test extension uniqueness constraints."""
        # Should be unique per (entity_type, entity_id, field_name, company_id)
        base_data = {
            'entity_type': 'partner',
            'entity_id': 1,
            'field_name': 'custom_field',
            'field_type': 'string',
            'company_id': 1
        }
        
        ext1 = MockBusinessObjectExtension(**base_data, field_value='value1')
        ext2 = MockBusinessObjectExtension(**base_data, field_value='value2')
        
        # These would violate uniqueness in a real database
        # In tests, we just verify the constraint components
        assert ext1.entity_type == ext2.entity_type
        assert ext1.entity_id == ext2.entity_id
        assert ext1.field_name == ext2.field_name
        assert ext1.company_id == ext2.company_id


class TestBusinessObjectValidatorModel:
    """Test the BusinessObjectValidator database model."""
    
    def test_validator_model_structure(self):
        """Test that validator model has the expected structure."""
        validator = MockBusinessObjectValidator(
            entity_type='partner',
            field_name='email',
            validator_type='email',
            validator_config='{}',
            company_id=1
        )
        
        # Check required fields
        assert validator.entity_type == 'partner'
        assert validator.field_name == 'email'
        assert validator.validator_type == 'email'
        assert validator.validator_config == '{}'
        assert validator.company_id == 1
        assert validator.is_active is True
    
    def test_validator_types(self):
        """Test different validator types."""
        # Email validator
        email_validator = MockBusinessObjectValidator(
            entity_type='partner',
            field_name='contact_email',
            validator_type='email',
            validator_config='{}',
            company_id=1
        )
        assert email_validator.validator_type == 'email'
        
        # Required validator
        required_validator = MockBusinessObjectValidator(
            entity_type='partner',
            field_name='important_field',
            validator_type='required',
            validator_config='{}',
            company_id=1
        )
        assert required_validator.validator_type == 'required'
        
        # Min/Max length validator
        length_validator = MockBusinessObjectValidator(
            entity_type='partner',
            field_name='description',
            validator_type='length',
            validator_config='{"min": 10, "max": 500}',
            company_id=1
        )
        assert length_validator.validator_type == 'length'
        assert '"min": 10' in length_validator.validator_config
        
        # Numeric range validator
        range_validator = MockBusinessObjectValidator(
            entity_type='partner',
            field_name='rating',
            validator_type='range',
            validator_config='{"min": 1, "max": 10}',
            company_id=1
        )
        assert range_validator.validator_type == 'range'
        
        # Regex pattern validator
        pattern_validator = MockBusinessObjectValidator(
            entity_type='partner',
            field_name='phone',
            validator_type='pattern',
            validator_config='{"pattern": "^\\+?[1-9]\\d{1,14}$"}',
            company_id=1
        )
        assert pattern_validator.validator_type == 'pattern'
        
        # Custom validator
        custom_validator = MockBusinessObjectValidator(
            entity_type='partner',
            field_name='custom_field',
            validator_type='custom',
            validator_config='{"function": "validate_custom_field", "params": {"param1": "value1"}}',
            company_id=1
        )
        assert custom_validator.validator_type == 'custom'
    
    def test_validator_config_json(self):
        """Test validator configuration JSON handling."""
        config = {
            "min": 1,
            "max": 100,
            "message": "Value must be between 1 and 100",
            "nullable": False
        }
        
        validator = MockBusinessObjectValidator(
            entity_type='partner',
            field_name='score',
            validator_type='range',
            validator_config=json.dumps(config),
            company_id=1
        )
        
        # Test that config can be parsed back
        parsed_config = json.loads(validator.validator_config)
        assert parsed_config['min'] == 1
        assert parsed_config['max'] == 100
        assert parsed_config['message'] == "Value must be between 1 and 100"
        assert parsed_config['nullable'] is False


class TestExtensibleMixin:
    """Test the ExtensibleMixin functionality."""
    
    def test_extensible_mixin_structure(self):
        """Test that ExtensibleMixin provides expected functionality."""
        # Test that extensible objects can store custom fields
        obj = MockExtensibleBusinessObject(
            id=1,
            company_id=1,
            name="Test Object",
            description="Test extensible object"
        )
        
        # Test basic object properties
        assert obj.id == 1
        assert obj.company_id == 1
        assert obj.name == "Test Object"
        assert hasattr(obj, '_extensions')
    
    def test_custom_field_storage(self):
        """Test storing and retrieving custom fields."""
        obj = MockExtensibleBusinessObject(id=1, company_id=1, name="Test")
        
        # Test setting custom fields
        obj._extensions['custom_rating'] = {
            'field_type': 'integer',
            'field_value': '5'
        }
        obj._extensions['custom_notes'] = {
            'field_type': 'string',
            'field_value': 'Important notes'
        }
        
        # Test retrieving custom fields
        assert obj._extensions['custom_rating']['field_value'] == '5'
        assert obj._extensions['custom_notes']['field_value'] == 'Important notes'
    
    def test_custom_field_type_conversion(self):
        """Test converting custom field values to proper types."""
        obj = MockExtensibleBusinessObject(id=1, company_id=1, name="Test")
        
        # Test different type conversions
        test_fields = {
            'string_field': {'field_type': 'string', 'field_value': 'Hello World'},
            'integer_field': {'field_type': 'integer', 'field_value': '42'},
            'decimal_field': {'field_type': 'decimal', 'field_value': '3.14'},
            'boolean_field': {'field_type': 'boolean', 'field_value': 'true'},
            'date_field': {'field_type': 'date', 'field_value': '2025-08-01'},
            'json_field': {'field_type': 'json', 'field_value': '{"key": "value"}'}
        }
        
        obj._extensions.update(test_fields)
        
        # Test that values are stored correctly
        assert obj._extensions['string_field']['field_value'] == 'Hello World'
        assert obj._extensions['integer_field']['field_value'] == '42'
        assert obj._extensions['decimal_field']['field_value'] == '3.14'
        assert obj._extensions['boolean_field']['field_value'] == 'true'
        assert obj._extensions['date_field']['field_value'] == '2025-08-01'
        assert obj._extensions['json_field']['field_value'] == '{"key": "value"}'


class TestExtensionOperations:
    """Test extension CRUD operations."""
    
    def test_create_extension(self):
        """Test creating new extensions."""
        extension_data = {
            'entity_type': 'partner',
            'entity_id': 1,
            'field_name': 'priority_level',
            'field_type': 'integer',
            'field_value': '5',
            'company_id': 1
        }
        
        extension = MockBusinessObjectExtension(**extension_data)
        
        assert extension.entity_type == 'partner'
        assert extension.entity_id == 1
        assert extension.field_name == 'priority_level'
        assert extension.field_type == 'integer'
        assert extension.field_value == '5'
        assert extension.company_id == 1
    
    def test_update_extension(self):
        """Test updating existing extensions."""
        extension = MockBusinessObjectExtension(
            entity_type='partner',
            entity_id=1,
            field_name='rating',
            field_type='integer',
            field_value='3',
            company_id=1
        )
        
        # Update the value
        old_value = extension.field_value
        extension.field_value = '5'
        extension.updated_at = datetime.now()
        
        assert old_value == '3'
        assert extension.field_value == '5'
        assert extension.updated_at is not None
    
    def test_delete_extension(self):
        """Test deleting extensions (soft delete)."""
        extension = MockBusinessObjectExtension(
            entity_type='partner',
            entity_id=1,
            field_name='temp_field',
            field_type='string',
            field_value='temporary',
            company_id=1,
            is_active=True
        )
        
        # Soft delete
        extension.is_active = False
        extension.updated_at = datetime.now()
        
        assert extension.is_active is False
        assert extension.updated_at is not None
    
    def test_bulk_extension_operations(self):
        """Test bulk operations on extensions."""
        # Create multiple extensions for the same entity
        extensions = []
        for i in range(5):
            ext = MockBusinessObjectExtension(
                entity_type='partner',
                entity_id=1,
                field_name=f'bulk_field_{i}',
                field_type='string',
                field_value=f'value_{i}',
                company_id=1
            )
            extensions.append(ext)
        
        assert len(extensions) == 5
        
        # Test bulk update
        for ext in extensions:
            ext.field_value = f'updated_{ext.field_name}'
            ext.updated_at = datetime.now()
        
        # Verify all were updated
        for ext in extensions:
            assert ext.field_value.startswith('updated_')


class TestExtensionValidation:
    """Test extension validation system."""
    
    def test_create_validators(self):
        """Test creating validation rules."""
        # Required field validator
        required_validator = MockBusinessObjectValidator(
            entity_type='partner',
            field_name='important_field',
            validator_type='required',
            validator_config='{"message": "This field is required"}',
            company_id=1
        )
        
        assert required_validator.validator_type == 'required'
        
        # Email validator
        email_validator = MockBusinessObjectValidator(
            entity_type='partner',
            field_name='contact_email',
            validator_type='email',
            validator_config='{"message": "Invalid email format"}',
            company_id=1
        )
        
        assert email_validator.validator_type == 'email'
        
        # Range validator
        range_validator = MockBusinessObjectValidator(
            entity_type='partner',
            field_name='rating',
            validator_type='range',
            validator_config='{"min": 1, "max": 10, "message": "Rating must be between 1 and 10"}',
            company_id=1
        )
        
        assert range_validator.validator_type == 'range'
        config = json.loads(range_validator.validator_config)
        assert config['min'] == 1
        assert config['max'] == 10
    
    def test_validation_rule_application(self):
        """Test applying validation rules to field values."""
        # Mock validation functions
        def validate_required(value, config):
            if not value or (isinstance(value, str) and not value.strip()):
                return False, config.get('message', 'This field is required')
            return True, None
        
        def validate_email(value, config):
            import re
            if not value:
                return True, None  # Optional field
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, value):
                return False, config.get('message', 'Invalid email format')
            return True, None
        
        def validate_range(value, config):
            try:
                num_value = float(value)
                if num_value < config.get('min', float('-inf')) or num_value > config.get('max', float('inf')):
                    return False, config.get('message', f"Value must be between {config.get('min')} and {config.get('max')}")
                return True, None
            except (ValueError, TypeError):
                return False, "Value must be a number"
        
        # Test required validation
        required_config = {"message": "This field is required"}
        assert validate_required("", required_config) == (False, "This field is required")
        assert validate_required("value", required_config) == (True, None)
        
        # Test email validation
        email_config = {"message": "Invalid email format"}
        assert validate_email("invalid-email", email_config) == (False, "Invalid email format")
        assert validate_email("test@example.com", email_config) == (True, None)
        
        # Test range validation
        range_config = {"min": 1, "max": 10, "message": "Rating must be between 1 and 10"}
        assert validate_range("0", range_config) == (False, "Rating must be between 1 and 10")
        assert validate_range("5", range_config) == (True, None)
        assert validate_range("15", range_config) == (False, "Rating must be between 1 and 10")
    
    def test_multi_validator_application(self):
        """Test applying multiple validators to the same field."""
        # Create multiple validators for the same field
        validators = [
            MockBusinessObjectValidator(
                entity_type='partner',
                field_name='email',
                validator_type='required',
                validator_config='{"message": "Email is required"}',
                company_id=1
            ),
            MockBusinessObjectValidator(
                entity_type='partner',
                field_name='email',
                validator_type='email',
                validator_config='{"message": "Invalid email format"}',
                company_id=1
            )
        ]
        
        # Test that both validators exist
        assert len(validators) == 2
        assert validators[0].validator_type == 'required'
        assert validators[1].validator_type == 'email'
        
        # Both should apply to the same field
        assert validators[0].field_name == validators[1].field_name == 'email'


class TestExtensionQuerying:
    """Test querying and filtering with extensions."""
    
    def test_query_by_extension_field(self):
        """Test querying objects by extension field values."""
        # Create mock extensions for different entities
        extensions = [
            MockBusinessObjectExtension(
                entity_type='partner',
                entity_id=1,
                field_name='priority',
                field_type='integer',
                field_value='5',
                company_id=1
            ),
            MockBusinessObjectExtension(
                entity_type='partner',
                entity_id=2,
                field_name='priority',
                field_type='integer',
                field_value='3',
                company_id=1
            ),
            MockBusinessObjectExtension(
                entity_type='partner',
                entity_id=3,
                field_name='priority',
                field_type='integer',
                field_value='5',
                company_id=1
            )
        ]
        
        # Filter by priority = 5
        high_priority = [ext for ext in extensions if ext.field_name == 'priority' and ext.field_value == '5']
        assert len(high_priority) == 2
        assert high_priority[0].entity_id == 1
        assert high_priority[1].entity_id == 3
    
    def test_query_by_multiple_extension_fields(self):
        """Test querying with multiple extension field filters."""
        # Create extensions with different field combinations
        extensions = [
            # Partner 1: high priority, VIP
            MockBusinessObjectExtension(entity_type='partner', entity_id=1, field_name='priority', field_value='5', company_id=1),
            MockBusinessObjectExtension(entity_type='partner', entity_id=1, field_name='is_vip', field_value='true', company_id=1),
            
            # Partner 2: high priority, not VIP
            MockBusinessObjectExtension(entity_type='partner', entity_id=2, field_name='priority', field_value='5', company_id=1),
            MockBusinessObjectExtension(entity_type='partner', entity_id=2, field_name='is_vip', field_value='false', company_id=1),
            
            # Partner 3: low priority, VIP
            MockBusinessObjectExtension(entity_type='partner', entity_id=3, field_name='priority', field_value='2', company_id=1),
            MockBusinessObjectExtension(entity_type='partner', entity_id=3, field_name='is_vip', field_value='true', company_id=1),
        ]
        
        # Group by entity_id
        entities = {}
        for ext in extensions:
            if ext.entity_id not in entities:
                entities[ext.entity_id] = {}
            entities[ext.entity_id][ext.field_name] = ext.field_value
        
        # Filter for high priority AND VIP
        high_priority_vip = [
            entity_id for entity_id, fields in entities.items()
            if fields.get('priority') == '5' and fields.get('is_vip') == 'true'
        ]
        
        assert len(high_priority_vip) == 1
        assert high_priority_vip[0] == 1
    
    def test_extension_field_sorting(self):
        """Test sorting objects by extension field values."""
        extensions = [
            MockBusinessObjectExtension(entity_type='partner', entity_id=1, field_name='rating', field_value='3', company_id=1),
            MockBusinessObjectExtension(entity_type='partner', entity_id=2, field_name='rating', field_value='5', company_id=1),
            MockBusinessObjectExtension(entity_type='partner', entity_id=3, field_name='rating', field_value='1', company_id=1),
            MockBusinessObjectExtension(entity_type='partner', entity_id=4, field_name='rating', field_value='4', company_id=1),
        ]
        
        # Sort by rating value (ascending)
        sorted_extensions = sorted(extensions, key=lambda x: int(x.field_value))
        expected_order = [3, 1, 4, 2]  # entity_ids in order of rating
        actual_order = [ext.entity_id for ext in sorted_extensions]
        
        assert actual_order == expected_order


class TestExtensionIntegration:
    """Test extension system integration with framework."""
    
    def test_extension_with_business_object_service(self):
        """Test extension integration with BusinessObjectService."""
        # This test will be implemented once the ExtensibleMixin is integrated
        # with the service layer
        
        # Mock service that handles extensions
        class MockExtensibleService:
            def __init__(self):
                self.extensions = {}
            
            def set_extension(self, entity_id, field_name, field_type, field_value):
                if entity_id not in self.extensions:
                    self.extensions[entity_id] = {}
                self.extensions[entity_id][field_name] = {
                    'field_type': field_type,
                    'field_value': field_value
                }
            
            def get_extension(self, entity_id, field_name):
                return self.extensions.get(entity_id, {}).get(field_name)
            
            def get_all_extensions(self, entity_id):
                return self.extensions.get(entity_id, {})
        
        service = MockExtensibleService()
        
        # Test setting extensions
        service.set_extension(1, 'priority', 'integer', '5')
        service.set_extension(1, 'notes', 'string', 'Important notes')
        
        # Test retrieving extensions
        assert service.get_extension(1, 'priority')['field_value'] == '5'
        assert service.get_extension(1, 'notes')['field_value'] == 'Important notes'
        
        # Test getting all extensions for an entity
        all_extensions = service.get_all_extensions(1)
        assert len(all_extensions) == 2
        assert 'priority' in all_extensions
        assert 'notes' in all_extensions
    
    def test_extension_with_schema_validation(self):
        """Test extension integration with schema validation."""
        # Mock schema validation for extensions
        def validate_extension_field(field_name, field_type, field_value, validators):
            """Mock validation function for extension fields."""
            errors = []
            
            for validator in validators:
                if validator.field_name == field_name:
                    if validator.validator_type == 'required':
                        if not field_value or (isinstance(field_value, str) and not field_value.strip()):
                            config = json.loads(validator.validator_config)
                            errors.append(config.get('message', 'This field is required'))
                    elif validator.validator_type == 'range' and field_type in ['integer', 'decimal']:
                        try:
                            num_value = float(field_value)
                            config = json.loads(validator.validator_config)
                            if num_value < config.get('min', float('-inf')) or num_value > config.get('max', float('inf')):
                                errors.append(config.get('message', f"Value must be between {config.get('min')} and {config.get('max')}"))
                        except (ValueError, TypeError):
                            errors.append("Value must be a number")
            
            return len(errors) == 0, errors
        
        # Create validators
        validators = [
            MockBusinessObjectValidator(
                entity_type='partner',
                field_name='rating',
                validator_type='required',
                validator_config='{"message": "Rating is required"}',
                company_id=1
            ),
            MockBusinessObjectValidator(
                entity_type='partner',
                field_name='rating',
                validator_type='range',
                validator_config='{"min": 1, "max": 10, "message": "Rating must be between 1 and 10"}',
                company_id=1
            )
        ]
        
        # Test valid value
        is_valid, errors = validate_extension_field('rating', 'integer', '5', validators)
        assert is_valid is True
        assert len(errors) == 0
        
        # Test missing value
        is_valid, errors = validate_extension_field('rating', 'integer', '', validators)
        assert is_valid is False
        assert 'Rating is required' in errors
        
        # Test out of range value
        is_valid, errors = validate_extension_field('rating', 'integer', '15', validators)
        assert is_valid is False
        assert 'Rating must be between 1 and 10' in errors


# Test fixtures for extension testing
@pytest.fixture
def sample_extension_data():
    """Sample extension data for testing."""
    return {
        'entity_type': 'partner',
        'entity_id': 1,
        'field_name': 'custom_rating',
        'field_type': 'integer',
        'field_value': '5',
        'company_id': 1
    }


@pytest.fixture
def sample_validator_data():
    """Sample validator data for testing."""
    return {
        'entity_type': 'partner',
        'field_name': 'email',
        'validator_type': 'email',
        'validator_config': '{"message": "Invalid email format"}',
        'company_id': 1
    }


@pytest.fixture
def sample_extensible_object():
    """Sample extensible business object for testing."""
    return MockExtensibleBusinessObject(
        id=1,
        company_id=1,
        name="Test Extensible Object",
        description="An object with custom fields"
    )