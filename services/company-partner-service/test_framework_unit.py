#!/usr/bin/env python3
"""
Unit tests for Business Object Framework core infrastructure.
Simplified tests that can run without pytest.
"""

import asyncio
import sys
sys.path.append('.')

from sqlalchemy import Column, Integer, String, Boolean
from app.framework.mixins import BusinessObjectMixin, AuditableMixin, EventPublisherMixin
from app.framework.base import BusinessObjectBase, CompanyBusinessObject
from app.core.database import Base


def test_business_object_mixin_fields():
    """Test that BusinessObjectMixin provides all required common fields."""
    print("Testing BusinessObjectMixin fields...")
    
    class TestModel(Base, BusinessObjectMixin):
        __tablename__ = "test_model"
        name = Column(String(100))
    
    # Check that all required fields are present
    assert hasattr(TestModel, 'id'), "Missing id field"
    assert hasattr(TestModel, 'created_at'), "Missing created_at field"
    assert hasattr(TestModel, 'updated_at'), "Missing updated_at field"
    assert hasattr(TestModel, 'framework_version'), "Missing framework_version field"
    
    # Check field types
    assert TestModel.id.type.python_type == int, "id should be integer"
    assert TestModel.created_at.default is not None, "created_at should have default"
    assert TestModel.updated_at.onupdate is not None, "updated_at should have onupdate"
    
    print("✅ BusinessObjectMixin fields test passed")


def test_business_object_mixin_metadata():
    """Test that BusinessObjectMixin tracks metadata correctly."""
    print("Testing BusinessObjectMixin metadata...")
    
    class TestModel(Base, BusinessObjectMixin):
        __tablename__ = "test_model_meta"
        name = Column(String(100))
    
    # Test instance creation
    instance = TestModel(name="Test")
    
    # Check string representations
    str_repr = str(instance)
    assert "TestModel" in str_repr, "Class name should be in string representation"
    assert "Test" in str_repr, "Name should be in string representation"
    
    repr_str = repr(instance)
    assert "TestModel" in repr_str, "Class name should be in repr"
    
    print("✅ BusinessObjectMixin metadata test passed")


def test_auditable_mixin_methods():
    """Test that AuditableMixin provides audit methods."""
    print("Testing AuditableMixin methods...")
    
    class TestModelAudit(Base, BusinessObjectMixin, AuditableMixin):
        __tablename__ = "test_model_audit"
        name = Column(String(100))
        is_active = Column(Boolean, default=True)
    
    # Check that audit methods are present
    assert hasattr(TestModelAudit, '_capture_before_state'), "Missing _capture_before_state method"
    assert hasattr(TestModelAudit, '_capture_after_state'), "Missing _capture_after_state method"
    assert hasattr(TestModelAudit, '_send_audit_log'), "Missing _send_audit_log method"
    assert hasattr(TestModelAudit, '_get_changed_fields'), "Missing _get_changed_fields method"
    
    print("✅ AuditableMixin methods test passed")


def test_auditable_mixin_state_capture():
    """Test state capture functionality."""
    print("Testing AuditableMixin state capture...")
    
    class TestModelAudit(Base, BusinessObjectMixin, AuditableMixin):
        __tablename__ = "test_model_audit2"
        name = Column(String(100))
        is_active = Column(Boolean, default=True)
    
    instance = TestModelAudit(id=1, name="Test", is_active=True)
    
    # Test before state capture
    before_state = instance._capture_before_state()
    assert before_state['id'] == 1, "Before state should capture id"
    assert before_state['name'] == "Test", "Before state should capture name"
    assert before_state['is_active'] == True, "Before state should capture is_active"
    
    # Modify instance
    instance.name = "Modified Test"
    instance.is_active = False
    
    # Test after state capture
    after_state = instance._capture_after_state()
    assert after_state['name'] == "Modified Test", "After state should capture modified name"
    assert after_state['is_active'] == False, "After state should capture modified is_active"
    
    print("✅ AuditableMixin state capture test passed")


def test_auditable_mixin_change_detection():
    """Test change detection functionality."""
    print("Testing AuditableMixin change detection...")
    
    class TestModelAudit(Base, BusinessObjectMixin, AuditableMixin):
        __tablename__ = "test_model_audit3"
        name = Column(String(100))
        is_active = Column(Boolean, default=True)
    
    instance = TestModelAudit(id=1, name="Test", is_active=True)
    
    before_state = {'id': 1, 'name': 'Test', 'is_active': True}
    after_state = {'id': 1, 'name': 'Modified Test', 'is_active': False}
    
    changes = instance._get_changed_fields(before_state, after_state)
    
    assert 'name' in changes, "Changes should include name"
    assert changes['name']['from'] == 'Test', "Name change from value incorrect"
    assert changes['name']['to'] == 'Modified Test', "Name change to value incorrect"
    
    assert 'is_active' in changes, "Changes should include is_active"
    assert changes['is_active']['from'] == True, "is_active change from value incorrect"
    assert changes['is_active']['to'] == False, "is_active change to value incorrect"
    
    assert 'id' not in changes, "Unchanged fields should not be in changes"
    
    print("✅ AuditableMixin change detection test passed")


def test_event_publisher_mixin_methods():
    """Test that EventPublisherMixin provides event methods."""
    print("Testing EventPublisherMixin methods...")
    
    class TestModelEvents(Base, BusinessObjectMixin, EventPublisherMixin):
        __tablename__ = "test_model_events"
        name = Column(String(100))
        status = Column(String(50))
    
    # Check that event methods are present
    assert hasattr(TestModelEvents, '_publish_event'), "Missing _publish_event method"
    assert hasattr(TestModelEvents, '_get_event_type_for_operation'), "Missing _get_event_type_for_operation method"
    assert hasattr(TestModelEvents, '_get_entity_type'), "Missing _get_entity_type method"
    
    print("✅ EventPublisherMixin methods test passed")


def test_event_publisher_entity_type():
    """Test entity type derivation from model name."""
    print("Testing EventPublisherMixin entity type...")
    
    class TestModelEvents(Base, BusinessObjectMixin, EventPublisherMixin):
        __tablename__ = "test_model_events2"
        name = Column(String(100))
    
    instance = TestModelEvents(id=1, name="Test")
    
    entity_type = instance._get_entity_type()
    assert entity_type == "TestModelEvents", f"Expected 'TestModelEvents', got '{entity_type}'"
    
    print("✅ EventPublisherMixin entity type test passed")


def test_event_publisher_event_type_generation():
    """Test event type generation for operations."""
    print("Testing EventPublisherMixin event type generation...")
    
    class TestModelEvents(Base, BusinessObjectMixin, EventPublisherMixin):
        __tablename__ = "test_model_events3"
        name = Column(String(100))
    
    instance = TestModelEvents(id=1, name="Test")
    
    # Test different operations
    create_event = instance._get_event_type_for_operation("CREATE")
    assert create_event == "testmodelevents.created", f"Expected 'testmodelevents.created', got '{create_event}'"
    
    update_event = instance._get_event_type_for_operation("UPDATE")
    assert update_event == "testmodelevents.updated", f"Expected 'testmodelevents.updated', got '{update_event}'"
    
    delete_event = instance._get_event_type_for_operation("DELETE")
    assert delete_event == "testmodelevents.deleted", f"Expected 'testmodelevents.deleted', got '{delete_event}'"
    
    print("✅ EventPublisherMixin event type generation test passed")


def test_business_object_base_inheritance():
    """Test that BusinessObjectBase properly inherits from all mixins."""
    print("Testing BusinessObjectBase inheritance...")
    
    # Check MRO (Method Resolution Order)
    mro_classes = [cls.__name__ for cls in BusinessObjectBase.__mro__]
    
    assert 'BusinessObjectBase' in mro_classes, "BusinessObjectBase should be in MRO"
    assert 'BusinessObjectMixin' in mro_classes, "BusinessObjectMixin should be in MRO"
    assert 'AuditableMixin' in mro_classes, "AuditableMixin should be in MRO"
    assert 'EventPublisherMixin' in mro_classes, "EventPublisherMixin should be in MRO"
    
    print("✅ BusinessObjectBase inheritance test passed")


def test_business_object_base_abstract():
    """Test that BusinessObjectBase is abstract."""
    print("Testing BusinessObjectBase abstract...")
    
    assert BusinessObjectBase.__abstract__ == True, "BusinessObjectBase should be abstract"
    
    print("✅ BusinessObjectBase abstract test passed")


def test_company_business_object_inheritance():
    """Test that CompanyBusinessObject inherits from BusinessObjectBase."""
    print("Testing CompanyBusinessObject inheritance...")
    
    mro_classes = [cls.__name__ for cls in CompanyBusinessObject.__mro__]
    
    assert 'CompanyBusinessObject' in mro_classes, "CompanyBusinessObject should be in MRO"
    assert 'BusinessObjectBase' in mro_classes, "BusinessObjectBase should be in MRO"
    assert 'BusinessObjectMixin' in mro_classes, "BusinessObjectMixin should be in MRO"
    assert 'AuditableMixin' in mro_classes, "AuditableMixin should be in MRO"
    assert 'EventPublisherMixin' in mro_classes, "EventPublisherMixin should be in MRO"
    
    print("✅ CompanyBusinessObject inheritance test passed")


def test_company_business_object_company_id():
    """Test that CompanyBusinessObject includes company_id field."""
    print("Testing CompanyBusinessObject company_id...")
    
    # Check that company_id field is present at class level
    assert hasattr(CompanyBusinessObject, 'company_id'), "Missing company_id field"
    
    # Check that it has the right properties (we can't check FK without the companies table existing)
    try:
        # Try to create a test model
        class TestCompanyModel(CompanyBusinessObject):
            __tablename__ = "test_company_model_fk"
            name = Column(String(100))
        
        # Check that company_id is there
        assert hasattr(TestCompanyModel, 'company_id'), "Missing company_id field on derived class"
        
        # We can check the column definition even if FK validation fails
        company_id_column = TestCompanyModel.company_id
        assert company_id_column.nullable == False, "company_id should not be nullable"
        
    except Exception as e:
        # If foreign key validation fails, that's expected in test context
        # Just ensure the field exists and has basic properties
        if "could not find table 'companies'" in str(e):
            print("⚠️  FK validation skipped (companies table not available in test context)")
        else:
            raise e
    
    print("✅ CompanyBusinessObject company_id test passed")


def test_company_business_object_abstract():
    """Test that CompanyBusinessObject is abstract."""
    print("Testing CompanyBusinessObject abstract...")
    
    assert CompanyBusinessObject.__abstract__ == True, "CompanyBusinessObject should be abstract"
    
    print("✅ CompanyBusinessObject abstract test passed")


def test_framework_integration():
    """Test framework integration with existing systems."""
    print("Testing framework integration...")
    
    from app.framework import BusinessObjectBase, CompanyBusinessObject
    
    # Test that classes are properly configured
    assert BusinessObjectBase is not None, "BusinessObjectBase should not be None"
    assert CompanyBusinessObject is not None, "CompanyBusinessObject should not be None"
    
    # Test that they have the expected attributes
    assert hasattr(BusinessObjectBase, '__abstract__'), "BusinessObjectBase should have __abstract__"
    assert hasattr(CompanyBusinessObject, '__abstract__'), "CompanyBusinessObject should have __abstract__"
    
    print("✅ Framework integration test passed")


def test_framework_version_consistency():
    """Test that framework version is consistent across components."""
    print("Testing framework version consistency...")
    
    from app.framework import __version__
    
    # Version should be consistent
    assert __version__ == "1.0.0", f"Framework version should be 1.0.0, got {__version__}"
    
    print("✅ Framework version consistency test passed")


def run_all_tests():
    """Run all unit tests."""
    print("🧪 Running Business Object Framework Unit Tests\n")
    
    tests = [
        test_business_object_mixin_fields,
        test_business_object_mixin_metadata,
        test_auditable_mixin_methods,
        test_auditable_mixin_state_capture,
        test_auditable_mixin_change_detection,
        test_event_publisher_mixin_methods,
        test_event_publisher_entity_type,
        test_event_publisher_event_type_generation,
        test_business_object_base_inheritance,
        test_business_object_base_abstract,
        test_company_business_object_inheritance,
        test_company_business_object_company_id,
        test_company_business_object_abstract,
        test_framework_integration,
        test_framework_version_consistency,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\n🎯 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)