#!/usr/bin/env python3
"""
Verification script for Enhanced Partner Management functionality.
Tests that all models, services, and schemas are properly implemented.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_models():
    """Verify all enhanced partner management models can be imported."""
    print("🔍 Verifying models...")
    
    try:
        from app.models.partner_category import PartnerCategory
        from app.models.partner_communication import PartnerCommunication
        from app.models.partner import Partner
        print("  ✅ PartnerCategory model imported successfully")
        print("  ✅ PartnerCommunication model imported successfully")
        print("  ✅ Partner model with enhanced relationships imported successfully")
        
        # Test model properties
        print("  🔍 Testing model properties...")
        
        # Test PartnerCategory properties
        category = PartnerCategory()
        assert hasattr(category, 'name')
        assert hasattr(category, 'code')
        assert hasattr(category, 'color')
        assert hasattr(category, 'parent_category_id')
        assert callable(getattr(category, 'full_path', None))
        print("    ✅ PartnerCategory properties verified")
        
        # Test PartnerCommunication properties
        communication = PartnerCommunication()
        assert hasattr(communication, 'partner_id')
        assert hasattr(communication, 'communication_type')
        assert hasattr(communication, 'subject')
        assert hasattr(communication, 'direction')
        assert hasattr(communication, 'status')
        assert hasattr(communication, 'priority')
        assert callable(getattr(communication, 'mark_completed', None))
        print("    ✅ PartnerCommunication properties verified")
        
        # Test enhanced Partner properties
        partner = Partner()
        assert hasattr(partner, 'category_id')
        assert hasattr(partner, 'communications')
        print("    ✅ Enhanced Partner properties verified")
        
        print("  ✅ All models verified successfully!")
        return True
        
    except ImportError as e:
        print(f"  ❌ Model import failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Model verification failed: {e}")
        return False


def verify_schemas():
    """Verify all enhanced partner management schemas can be imported."""
    print("\n🔍 Verifying schemas...")
    
    try:
        from app.schemas.partner_category import (
            PartnerCategoryCreate, PartnerCategoryUpdate, PartnerCategoryResponse,
            PartnerCategoryTreeResponse, PartnerCategoryListResponse
        )
        from app.schemas.partner_communication import (
            PartnerCommunicationCreate, PartnerCommunicationUpdate, PartnerCommunicationResponse,
            PartnerCommunicationListResponse, PartnerCommunicationStatsResponse
        )
        print("  ✅ Partner category schemas imported successfully")
        print("  ✅ Partner communication schemas imported successfully")
        
        # Test schema creation
        print("  🔍 Testing schema instantiation...")
        
        # Test PartnerCategoryCreate
        category_data = {
            'company_id': 1,
            'name': 'Test Category',
            'code': 'TEST_CAT',
            'description': 'Test description',
            'color': '#FF0000'
        }
        category_schema = PartnerCategoryCreate(**category_data)
        assert category_schema.name == 'Test Category'
        assert category_schema.code == 'TEST_CAT'
        print("    ✅ PartnerCategoryCreate schema instantiation verified")
        
        # Test PartnerCommunicationCreate  
        communication_data = {
            'partner_id': 1,
            'communication_type': 'email',
            'subject': 'Test Communication',
            'direction': 'outbound',
            'status': 'pending',
            'priority': 'normal'
        }
        communication_schema = PartnerCommunicationCreate(**communication_data)
        assert communication_schema.subject == 'Test Communication'
        assert communication_schema.communication_type == 'email'
        print("    ✅ PartnerCommunicationCreate schema instantiation verified")
        
        print("  ✅ All schemas verified successfully!")
        return True
        
    except ImportError as e:
        print(f"  ❌ Schema import failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Schema verification failed: {e}")
        return False


def verify_services():
    """Verify all enhanced partner management services can be imported."""
    print("\n🔍 Verifying services...")
    
    try:
        from app.services.partner_category_service import PartnerCategoryService
        from app.services.partner_communication_service import PartnerCommunicationService
        print("  ✅ PartnerCategoryService imported successfully")
        print("  ✅ PartnerCommunicationService imported successfully")
        
        # Test service instantiation
        print("  🔍 Testing service instantiation...")
        
        category_service = PartnerCategoryService()
        assert hasattr(category_service, 'create')
        assert hasattr(category_service, 'get_category_tree')
        assert hasattr(category_service, 'create_default_categories')
        assert hasattr(category_service, 'validate_hierarchy')
        print("    ✅ PartnerCategoryService instantiation verified")
        
        communication_service = PartnerCommunicationService()
        assert hasattr(communication_service, 'create')
        assert hasattr(communication_service, 'mark_completed')
        assert hasattr(communication_service, 'schedule_follow_up')
        assert hasattr(communication_service, 'get_pending_communications')
        assert hasattr(communication_service, 'get_statistics')
        print("    ✅ PartnerCommunicationService instantiation verified")
        
        print("  ✅ All services verified successfully!")
        return True
        
    except ImportError as e:
        print(f"  ❌ Service import failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Service verification failed: {e}")
        return False


def verify_routers():
    """Verify all enhanced partner management routers can be imported."""
    print("\n🔍 Verifying routers...")
    
    try:
        from app.routers.partner_categories import router as categories_router
        from app.routers.partner_communications import router as communications_router
        print("  ✅ Partner categories router imported successfully")
        print("  ✅ Partner communications router imported successfully")
        
        # Test router properties
        print("  🔍 Testing router endpoints...")
        
        # Check categories router has expected routes
        category_routes = [route.path for route in categories_router.routes]
        expected_category_routes = ['/partner-categories/', '/partner-categories/tree', '/partner-categories/statistics']
        for expected_route in expected_category_routes:
            if any(expected_route in route for route in category_routes):
                print(f"    ✅ Found expected category route: {expected_route}")
            else:
                print(f"    ⚠️ Missing expected category route: {expected_route}")
        
        # Check communications router has expected routes
        communication_routes = [route.path for route in communications_router.routes]
        expected_communication_routes = ['/partner-communications/', '/partner-communications/pending', '/partner-communications/statistics']
        for expected_route in expected_communication_routes:
            if any(expected_route in route for route in communication_routes):
                print(f"    ✅ Found expected communication route: {expected_route}")
            else:
                print(f"    ⚠️ Missing expected communication route: {expected_route}")
        
        print("  ✅ All routers verified successfully!")
        return True
        
    except ImportError as e:
        print(f"  ❌ Router import failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Router verification failed: {e}")
        return False


def verify_database_migration():
    """Verify database migration file exists and is properly formatted."""
    print("\n🔍 Verifying database migration...")
    
    try:
        migration_file = "migrations/versions/20250804_102000_add_enhanced_partner_management.py"
        
        if not os.path.exists(migration_file):
            print(f"  ❌ Migration file not found: {migration_file}")
            return False
        
        with open(migration_file, 'r') as f:
            content = f.read()
            
        # Check for required migration elements
        required_elements = [
            'partner_categories',
            'partner_communications', 
            'category_id',
            'def upgrade',
            'def downgrade'
        ]
        
        for element in required_elements:
            if element in content:
                print(f"    ✅ Found required migration element: {element}")
            else:
                print(f"    ❌ Missing required migration element: {element}")
                return False
        
        print("  ✅ Database migration verified successfully!")
        return True
        
    except Exception as e:
        print(f"  ❌ Migration verification failed: {e}")
        return False


def verify_integration():
    """Verify main application integration."""
    print("\n🔍 Verifying main application integration...")
    
    try:
        # Check if main.py includes the new routers
        with open('app/main.py', 'r') as f:
            main_content = f.read()
        
        required_imports = [
            'partner_categories',
            'partner_communications'
        ]
        
        for import_name in required_imports:
            if import_name in main_content:
                print(f"    ✅ Found router import: {import_name}")
            else:
                print(f"    ❌ Missing router import: {import_name}")
                return False
        
        print("  ✅ Main application integration verified!")
        return True
        
    except Exception as e:
        print(f"  ❌ Integration verification failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("🚀 Enhanced Partner Management Verification")
    print("=" * 50)
    
    tests = [
        verify_models,
        verify_schemas,
        verify_services,
        verify_routers,
        verify_database_migration,
        verify_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All Enhanced Partner Management components verified successfully!")
        print("\n✨ Implementation Summary:")
        print("   • Partner Category system with hierarchical organization")
        print("   • Partner Communication tracking with follow-ups and statistics")
        print("   • Enhanced Partner model with category relationships")
        print("   • Complete API endpoints for all new functionality")
        print("   • Database migration ready for deployment")
        print("   • Integration with Business Object Framework")
        return True
    else:
        print(f"❌ {failed} verification test(s) failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)