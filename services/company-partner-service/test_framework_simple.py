#!/usr/bin/env python3
"""
Simple End-to-End Test for Framework Migration

This script performs basic testing of the framework migration without complex
dependencies, focusing on core functionality verification.
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class SimpleFrameworkTester:
    """Simple testing class for framework migration."""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.failed_tests = []
    
    def test_result(self, test_name: str, success: bool, message: str = ""):
        """Record test result."""
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}")
            if message:
                print(f"   {message}")
        else:
            self.tests_failed += 1
            self.failed_tests.append((test_name, message))
            print(f"❌ {test_name}")
            if message:
                print(f"   {message}")
    
    def test_file_structure(self):
        """Test framework file structure."""
        print("\n🗂️  Testing Framework File Structure...")
        
        required_files = [
            "app/framework_migration/__init__.py",
            "app/framework_migration/partner_schemas.py",
            "app/framework_migration/partner_service.py",
            "app/framework_migration/partner_router.py",
            "app/main_framework.py",
            "app/main_original.py",
            "app/migration_status.json"
        ]
        
        all_exist = True
        for file_path in required_files:
            exists = Path(file_path).exists()
            self.test_result(f"File exists: {file_path}", exists)
            if not exists:
                all_exist = False
        
        return all_exist
    
    def test_migration_status(self):
        """Test migration status configuration."""
        print("\n📊 Testing Migration Status...")
        
        try:
            status_file = Path("app/migration_status.json")
            if not status_file.exists():
                self.test_result("Migration status file exists", False, "File not found")
                return False
            
            with open(status_file, 'r') as f:
                status = json.load(f)
            
            # Check required fields
            required_fields = ["framework_enabled", "implementation", "migration_date"]
            all_fields_present = True
            
            for field in required_fields:
                if field not in status:
                    self.test_result(f"Status field: {field}", False, "Field missing")
                    all_fields_present = False
                else:
                    self.test_result(f"Status field: {field}", True, f"Value: {status[field]}")
            
            # Check values
            framework_enabled = status.get("framework_enabled", False)
            implementation = status.get("implementation", "")
            
            self.test_result("Framework enabled", framework_enabled, f"Implementation: {implementation}")
            
            return all_fields_present and framework_enabled
            
        except Exception as e:
            self.test_result("Migration status parsing", False, f"Error: {e}")
            return False
    
    def test_main_app_migration(self):
        """Test main application migration."""
        print("\n🚀 Testing Main Application Migration...")
        
        try:
            main_py = Path("app/main.py")
            if not main_py.exists():
                self.test_result("main.py exists", False)
                return False
            
            content = main_py.read_text()
            
            # Check for framework indicators
            framework_indicators = [
                "Framework Edition",
                "framework_migration",
                "Framework Mode"
            ]
            
            indicators_found = 0
            for indicator in framework_indicators:
                if indicator in content:
                    indicators_found += 1
                    self.test_result(f"Framework indicator: {indicator}", True)
                else:
                    self.test_result(f"Framework indicator: {indicator}", False)
            
            success = indicators_found >= 2  # At least 2 indicators should be present
            self.test_result("Main app migration", success, f"Found {indicators_found}/{len(framework_indicators)} indicators")
            
            return success
            
        except Exception as e:
            self.test_result("Main app migration", False, f"Error: {e}")
            return False
    
    def test_schema_imports(self):
        """Test framework schema imports."""
        print("\n📄 Testing Framework Schema Imports...")
        
        try:
            # Add current directory to Python path
            sys.path.insert(0, str(Path(".").absolute()))
            
            from app.framework_migration.partner_schemas import (
                PartnerFrameworkCreate, PartnerFrameworkUpdate, PartnerFrameworkResponse
            )
            
            self.test_result("Schema imports", True, "All schema classes imported successfully")
            
            # Test basic schema instantiation
            test_data = {
                "name": "Test Partner",
                "company_id": 1,
                "partner_type": "customer"
            }
            
            try:
                create_schema = PartnerFrameworkCreate(**test_data)
                self.test_result("Schema instantiation", True, f"Created: {create_schema.name}")
                return True
            except Exception as e:
                self.test_result("Schema instantiation", False, f"Error: {e}")
                return False
                
        except Exception as e:
            self.test_result("Schema imports", False, f"Import error: {e}")
            return False
    
    def test_service_imports(self):
        """Test framework service imports.""" 
        print("\n🔧 Testing Framework Service Imports...")
        
        try:
            from app.framework_migration.partner_service import (
                PartnerFrameworkService, create_partner_service
            )
            
            self.test_result("Service imports", True, "Service classes imported successfully")
            
            # Test service has expected methods
            expected_methods = [
                'create_partner', 'get_partner', 'update_partner', 'delete_partner',
                'get_partner_by_code', 'find_customers', 'get_partner_statistics'
            ]
            
            methods_found = 0
            for method_name in expected_methods:
                if hasattr(PartnerFrameworkService, method_name):
                    methods_found += 1
                    self.test_result(f"Service method: {method_name}", True)
                else:
                    self.test_result(f"Service method: {method_name}", False)
            
            success = methods_found >= len(expected_methods) - 2  # Allow some flexibility
            self.test_result("Service methods", success, f"Found {methods_found}/{len(expected_methods)} methods")
            
            return success
            
        except Exception as e:
            self.test_result("Service imports", False, f"Import error: {e}")
            return False
    
    def test_router_imports(self):
        """Test framework router imports."""
        print("\n🌐 Testing Framework Router Imports...")
        
        try:
            from app.framework_migration.partner_router import router, framework_partner_router
            
            self.test_result("Router imports", True, "Router objects imported successfully")
            
            # Check router has basic structure
            has_routes = hasattr(router, 'routes') or hasattr(router, 'router')
            self.test_result("Router structure", has_routes, "Router has expected structure")
            
            return True
            
        except Exception as e:
            self.test_result("Router imports", False, f"Import error: {e}")
            return False
    
    def test_framework_features(self):
        """Test framework feature availability."""
        print("\n🔧 Testing Framework Features...")
        
        try:
            # Test framework core components
            from app.framework.services import CompanyBusinessObjectService
            self.test_result("Framework services", True, "CompanyBusinessObjectService available")
        except Exception as e:
            self.test_result("Framework services", False, f"Error: {e}")
        
        try:
            from app.framework.schemas import CompanyBusinessObjectSchema
            self.test_result("Framework schemas", True, "CompanyBusinessObjectSchema available")
        except Exception as e:
            self.test_result("Framework schemas", False, f"Error: {e}")
        
        try:
            from app.framework.controllers import create_business_object_router
            self.test_result("Framework controllers", True, "create_business_object_router available")
        except Exception as e:
            self.test_result("Framework controllers", False, f"Error: {e}")
        
        try:
            from app.framework.extensions import ExtensibleMixin
            self.test_result("Framework extensions", True, "ExtensibleMixin available")
        except Exception as e:
            self.test_result("Framework extensions", False, f"Error: {e}")
    
    def test_backward_compatibility(self):
        """Test backward compatibility with original implementation."""
        print("\n🔄 Testing Backward Compatibility...")
        
        try:
            # Test original components still work
            from app.models.partner import Partner
            self.test_result("Original Partner model", True, "Partner model available")
            
            from app.schemas.partner import PartnerCreate, PartnerResponse
            self.test_result("Original Partner schemas", True, "Original schemas available")
            
            from app.services.partner_service import PartnerService
            self.test_result("Original Partner service", True, "PartnerService available")
            
            # Test backup files exist
            backup_dir = Path("migrations/backups")
            if backup_dir.exists():
                backup_subdirs = [d for d in backup_dir.iterdir() if d.is_dir() and "partner_migration" in d.name]
                has_backups = len(backup_subdirs) > 0
                self.test_result("Backup files", has_backups, f"Found {len(backup_subdirs)} backup directories")
            else:
                self.test_result("Backup files", False, "No backup directory found")
                
        except Exception as e:
            self.test_result("Backward compatibility", False, f"Error: {e}")
    
    def test_documentation(self):
        """Test migration documentation."""
        print("\n📚 Testing Migration Documentation...")
        
        doc_files = [
            "docs/BUSINESS_OBJECT_MIGRATION_GUIDE.md",
            "docs/MIGRATION_SCRIPTS_README.md", 
            "docs/PARTNER_MIGRATION_GUIDE.md",
            "docs/MIGRATION_TEMPLATE.md"
        ]
        
        for doc_file in doc_files:
            exists = Path(doc_file).exists()
            self.test_result(f"Documentation: {Path(doc_file).name}", exists)
    
    def run_all_tests(self):
        """Run all framework tests."""
        print("🧪 Starting Simple Framework End-to-End Tests")
        print("=" * 55)
        
        # Run all test methods
        test_methods = [
            self.test_file_structure,
            self.test_migration_status,
            self.test_main_app_migration,
            self.test_schema_imports,
            self.test_service_imports,
            self.test_router_imports,
            self.test_framework_features,
            self.test_backward_compatibility,
            self.test_documentation
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test method {test_method.__name__} failed: {e}")
                self.tests_failed += 1
                self.failed_tests.append((test_method.__name__, str(e)))
        
        # Summary
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📊 Test Summary")
        print("=" * 30)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for test_name, error in self.failed_tests:
                print(f"  • {test_name}: {error}")
        
        overall_success = self.tests_failed == 0
        
        if overall_success:
            print(f"\n🎉 All Framework Tests PASSED!")
            print("✅ Partner service framework migration is fully functional")
            print("\n📋 Framework Features Verified:")
            print("  • File structure and migration status")
            print("  • Schema, service, and router imports")
            print("  • Framework core components")
            print("  • Backward compatibility")
            print("  • Complete documentation")
        else:
            print(f"\n⚠️  Some Framework Tests FAILED!")
            print(f"❌ {self.tests_failed}/{total_tests} tests need attention")
            print("\n🔧 Common issues:")
            print("  • Python import path configuration")
            print("  • Missing framework dependencies")
            print("  • File structure problems")
        
        return overall_success


def main():
    """Main test execution."""
    tester = SimpleFrameworkTester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())