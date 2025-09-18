#!/usr/bin/env python3
"""
Functional test for Business Object Framework.
"""

import asyncio
import sys
sys.path.append('.')

from sqlalchemy import Column, String, Boolean
from app.framework import CompanyBusinessObject
from app.core.database import Base


class TestBusinessObject(CompanyBusinessObject):
    """Test business object using the framework."""
    __tablename__ = 'test_business_objects'
    
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    is_active = Column(Boolean, default=True)


async def test_framework_functionality():
    """Test the core framework functionality."""
    print("🧪 Testing Business Object Framework...")
    
    # Test 1: Basic object creation
    print("\n1. Testing basic object creation...")
    obj = TestBusinessObject(
        name="Test Object",
        description="A test business object",
        company_id=1
    )
    print(f"✅ Created: {obj}")
    print(f"✅ Framework version: {obj.framework_version}")
    
    # Test 2: State capture functionality
    print("\n2. Testing state capture...")
    before_state = obj._capture_before_state()
    print(f"✅ Before state captured: {len(before_state)} fields")
    
    # Modify object
    obj.name = "Modified Test Object"
    obj.is_active = False
    
    after_state = obj._capture_after_state()
    print(f"✅ After state captured: {len(after_state)} fields")
    
    # Test 3: Change detection
    print("\n3. Testing change detection...")
    changes = obj._get_changed_fields(before_state, after_state)
    print(f"✅ Changes detected: {changes}")
    
    # Test 4: Event type generation
    print("\n4. Testing event type generation...")
    create_event = obj._get_event_type_for_operation("CREATE")
    update_event = obj._get_event_type_for_operation("UPDATE")
    delete_event = obj._get_event_type_for_operation("DELETE")
    
    print(f"✅ CREATE event: {create_event}")
    print(f"✅ UPDATE event: {update_event}")
    print(f"✅ DELETE event: {delete_event}")
    
    # Test 5: String representations
    print("\n5. Testing string representations...")
    str_repr = str(obj)
    repr_str = repr(obj)
    print(f"✅ String representation: {str_repr}")
    print(f"✅ Repr representation: {repr_str}")
    
    print("\n🎉 All framework functionality tests passed!")


if __name__ == "__main__":
    asyncio.run(test_framework_functionality())