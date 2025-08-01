"""
Tests for Business Object Framework core infrastructure.
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, Boolean

from app.framework.mixins import BusinessObjectMixin, AuditableMixin, EventPublisherMixin
from app.framework.base import BusinessObjectBase, CompanyBusinessObject
from app.core.database import Base


class TestBusinessObjectMixin:
    """Tests for BusinessObjectMixin core functionality."""
    
    def test_business_object_mixin_has_required_fields(self):
        """Test that BusinessObjectMixin provides all required common fields."""
        # Create a test model using the mixin
        class TestModel(Base, BusinessObjectMixin):
            __tablename__ = "test_model"
            name = Column(String(100))
        
        # Check that all required fields are present
        assert hasattr(TestModel, 'id')
        assert hasattr(TestModel, 'created_at')
        assert hasattr(TestModel, 'updated_at')
        assert hasattr(TestModel, 'framework_version')
        
        # Check field types and properties
        assert TestModel.id.type.python_type == int
        assert TestModel.created_at.default is not None
        assert TestModel.updated_at.onupdate is not None
        assert TestModel.framework_version.default is not None
    
    def test_business_object_mixin_metadata_tracking(self):
        """Test that BusinessObjectMixin tracks metadata correctly."""
        class TestModel(Base, BusinessObjectMixin):
            __tablename__ = "test_model_meta"
            name = Column(String(100))
        
        # Test instance creation
        instance = TestModel(name="Test")
        
        # Check that framework version is set
        assert instance.framework_version == "1.0.0"
        
        # Check that created_at is set when accessed (due to default)
        assert instance.created_at is not None or hasattr(instance, '_created_at_default')
    
    def test_business_object_mixin_string_representations(self):
        """Test string representation methods."""
        class TestModel(Base, BusinessObjectMixin):
            __tablename__ = "test_model_str"
            name = Column(String(100))
        
        instance = TestModel(id=1, name="Test Object")
        
        # Test __str__
        str_repr = str(instance)
        assert "TestModel" in str_repr
        assert "Test Object" in str_repr
        
        # Test __repr__
        repr_str = repr(instance)
        assert "TestModel" in repr_str
        assert "id=1" in repr_str


class TestAuditableMixin:
    """Tests for AuditableMixin automatic audit integration."""
    
    @pytest.fixture
    def mock_audit_service(self):
        """Mock audit service for testing."""
        with patch('app.framework.mixins.audit_service_client') as mock:
            yield mock
    
    @pytest.fixture
    def test_model_with_audit(self):
        """Create a test model with AuditableMixin."""
        class TestModelAudit(Base, BusinessObjectMixin, AuditableMixin):
            __tablename__ = "test_model_audit"
            name = Column(String(100))
            is_active = Column(Boolean, default=True)
        
        return TestModelAudit
    
    def test_auditable_mixin_has_audit_methods(self, test_model_with_audit):
        """Test that AuditableMixin provides audit methods."""
        TestModel = test_model_with_audit
        
        # Check that audit methods are present
        assert hasattr(TestModel, '_capture_before_state')
        assert hasattr(TestModel, '_capture_after_state')
        assert hasattr(TestModel, '_send_audit_log')
        assert hasattr(TestModel, '_get_changed_fields')
    
    @pytest.mark.asyncio
    async def test_auditable_mixin_capture_state(self, test_model_with_audit):
        """Test state capture functionality."""
        TestModel = test_model_with_audit
        instance = TestModel(id=1, name="Test", is_active=True)
        
        # Test before state capture
        before_state = instance._capture_before_state()
        assert before_state['id'] == 1
        assert before_state['name'] == "Test"
        assert before_state['is_active'] == True
        
        # Modify instance
        instance.name = "Modified Test"
        instance.is_active = False
        
        # Test after state capture
        after_state = instance._capture_after_state()
        assert after_state['name'] == "Modified Test"
        assert after_state['is_active'] == False
    
    @pytest.mark.asyncio
    async def test_auditable_mixin_detect_changes(self, test_model_with_audit):
        """Test change detection functionality."""
        TestModel = test_model_with_audit
        instance = TestModel(id=1, name="Test", is_active=True)
        
        before_state = {'id': 1, 'name': 'Test', 'is_active': True}
        after_state = {'id': 1, 'name': 'Modified Test', 'is_active': False}
        
        changes = instance._get_changed_fields(before_state, after_state)
        
        assert 'name' in changes
        assert changes['name']['from'] == 'Test'
        assert changes['name']['to'] == 'Modified Test'
        
        assert 'is_active' in changes  
        assert changes['is_active']['from'] == True
        assert changes['is_active']['to'] == False
        
        assert 'id' not in changes  # Unchanged fields should not be in changes
    
    @pytest.mark.asyncio
    async def test_auditable_mixin_send_audit_log(self, test_model_with_audit, mock_audit_service):
        """Test audit log sending functionality."""
        TestModel = test_model_with_audit
        instance = TestModel(id=1, name="Test")
        
        # Mock audit service response
        mock_audit_service.create_audit_log.return_value = AsyncMock()
        
        # Test audit log sending
        await instance._send_audit_log(
            event_type="test.created",
            before_data={'name': 'Test'},
            after_data={'name': 'Modified Test'},
            changes={'name': {'from': 'Test', 'to': 'Modified Test'}}
        )
        
        # Verify audit service was called
        mock_audit_service.create_audit_log.assert_called_once()
        call_args = mock_audit_service.create_audit_log.call_args[1]
        
        assert call_args['event_type'] == "test.created"
        assert call_args['entity_type'] == "TestModelAudit"
        assert call_args['entity_id'] == "1"
        assert call_args['before_data'] == {'name': 'Test'}
        assert call_args['after_data'] == {'name': 'Modified Test'}


class TestEventPublisherMixin:
    """Tests for EventPublisherMixin automatic event publishing."""
    
    @pytest.fixture
    def mock_message_publisher(self):
        """Mock message publisher for testing."""
        with patch('app.framework.mixins.MessagePublisher') as mock:
            mock_instance = AsyncMock()
            mock.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture  
    def test_model_with_events(self):
        """Create a test model with EventPublisherMixin."""
        class TestModelEvents(Base, BusinessObjectMixin, EventPublisherMixin):
            __tablename__ = "test_model_events"
            name = Column(String(100))
            status = Column(String(50))
        
        return TestModelEvents
    
    def test_event_publisher_mixin_has_event_methods(self, test_model_with_events):
        """Test that EventPublisherMixin provides event methods."""
        TestModel = test_model_with_events
        
        # Check that event methods are present
        assert hasattr(TestModel, '_publish_event')
        assert hasattr(TestModel, '_get_event_type_for_operation')
        assert hasattr(TestModel, '_get_entity_type')
    
    def test_event_publisher_get_entity_type(self, test_model_with_events):
        """Test entity type derivation from model name."""
        TestModel = test_model_with_events
        instance = TestModel(id=1, name="Test")
        
        entity_type = instance._get_entity_type()
        assert entity_type == "TestModelEvents"
    
    def test_event_publisher_get_event_type_for_operation(self, test_model_with_events):
        """Test event type generation for operations."""
        TestModel = test_model_with_events
        instance = TestModel(id=1, name="Test")
        
        # Test different operations
        create_event = instance._get_event_type_for_operation("CREATE")
        assert create_event == "testmodelevents.created"
        
        update_event = instance._get_event_type_for_operation("UPDATE")
        assert update_event == "testmodelevents.updated"
        
        delete_event = instance._get_event_type_for_operation("DELETE")
        assert delete_event == "testmodelevents.deleted"
    
    @pytest.mark.asyncio
    async def test_event_publisher_publish_event(self, test_model_with_events, mock_message_publisher):
        """Test event publishing functionality."""
        TestModel = test_model_with_events
        instance = TestModel(id=1, name="Test")
        
        # Test event publishing
        await instance._publish_event(
            operation="CREATE",
            before_data=None,
            after_data={'id': 1, 'name': 'Test'},
            changes=None
        )
        
        # Verify message publisher was called
        mock_message_publisher.publish_event.assert_called_once()
        call_args = mock_message_publisher.publish_event.call_args[1]
        
        assert call_args['event_type'] == "testmodelevents.created"
        assert call_args['entity_type'] == "TestModelEvents"
        assert call_args['entity_id'] == 1
        assert call_args['after_data'] == {'id': 1, 'name': 'Test'}


class TestBusinessObjectBase:
    """Tests for BusinessObjectBase class."""
    
    def test_business_object_base_inheritance(self):
        """Test that BusinessObjectBase properly inherits from all mixins."""
        # Check MRO (Method Resolution Order)
        mro_classes = [cls.__name__ for cls in BusinessObjectBase.__mro__]
        
        assert 'BusinessObjectBase' in mro_classes
        assert 'BusinessObjectMixin' in mro_classes
        assert 'AuditableMixin' in mro_classes
        assert 'EventPublisherMixin' in mro_classes
    
    def test_business_object_base_abstract(self):
        """Test that BusinessObjectBase is abstract and cannot be instantiated directly."""
        assert BusinessObjectBase.__abstract__ == True
        
        # Should not be able to create table directly
        with pytest.raises(Exception):
            BusinessObjectBase()


class TestCompanyBusinessObject:
    """Tests for CompanyBusinessObject class."""
    
    def test_company_business_object_inheritance(self):
        """Test that CompanyBusinessObject inherits from BusinessObjectBase."""
        mro_classes = [cls.__name__ for cls in CompanyBusinessObject.__mro__]
        
        assert 'CompanyBusinessObject' in mro_classes
        assert 'BusinessObjectBase' in mro_classes
        assert 'BusinessObjectMixin' in mro_classes
        assert 'AuditableMixin' in mro_classes
        assert 'EventPublisherMixin' in mro_classes
    
    def test_company_business_object_has_company_id(self):
        """Test that CompanyBusinessObject includes company_id field."""
        # Create a test model using CompanyBusinessObject
        class TestCompanyModel(CompanyBusinessObject):
            __tablename__ = "test_company_model"
            name = Column(String(100))
        
        # Check that company_id field is present
        assert hasattr(TestCompanyModel, 'company_id')
        
        # Check that it's a foreign key to companies table
        company_id_column = TestCompanyModel.company_id
        assert company_id_column.nullable == False
        assert len(company_id_column.foreign_keys) > 0
        
        # Check foreign key points to companies.id
        fk = list(company_id_column.foreign_keys)[0]
        assert str(fk.column) == "companies.id"
    
    def test_company_business_object_abstract(self):
        """Test that CompanyBusinessObject is abstract."""
        assert CompanyBusinessObject.__abstract__ == True


class TestFrameworkIntegration:
    """Tests for framework integration with existing systems."""
    
    @pytest.mark.asyncio
    async def test_framework_with_existing_database(self):
        """Test that framework classes work with existing database connections."""
        # This would test with actual database session
        # For now, just test that the classes can be imported and used
        from app.framework import BusinessObjectBase, CompanyBusinessObject
        
        # Test that classes are properly configured
        assert BusinessObjectBase is not None
        assert CompanyBusinessObject is not None
        
        # Test that they have the expected attributes
        assert hasattr(BusinessObjectBase, '__abstract__')
        assert hasattr(CompanyBusinessObject, '__abstract__')
    
    def test_framework_version_consistency(self):
        """Test that framework version is consistent across components."""
        from app.framework import __version__
        from app.framework.mixins import BusinessObjectMixin
        
        # Create test instance to check version
        class TestModel(Base, BusinessObjectMixin):
            __tablename__ = "test_version"
        
        instance = TestModel()
        
        # Version should be consistent
        assert __version__ == "1.0.0"
        assert instance.framework_version == "1.0.0"