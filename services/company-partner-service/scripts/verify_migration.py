#!/usr/bin/env python3
"""
Migration Verification Script

This script verifies that the Partner service migration to the Business Object
Framework has been completed successfully and all components are working.

Usage:
    python verify_migration.py [--detailed]
"""

import asyncio
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


class MigrationVerifier:
    """Verifies the Partner service migration to Business Object Framework."""
    
    def __init__(self):
        self.service_root = Path(".")
        self.results = []
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log a test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append((test_name, success, message))
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
    
    def verify_file_structure(self) -> bool:
        """Verify all required framework files exist."""
        print("\n🗂️  Verifying File Structure...")
        
        required_files = [
            "app/framework_migration/__init__.py",
            "app/framework_migration/partner_schemas.py",
            "app/framework_migration/partner_service.py", 
            "app/framework_migration/partner_router.py",
            "app/framework_migration/main_app_update.py",
            "app/main_framework.py",
            "app/main_original.py",
            "app/migration_status.json",
            "migrations/partner_framework_migration.py",
            "migration_config.py",
            "rollback_migration.py"
        ]
        
        all_exist = True
        for file_path in required_files:
            full_path = self.service_root / file_path
            exists = full_path.exists()
            self.log_result(f"File exists: {file_path}", exists)
            if not exists:
                all_exist = False
        
        return all_exist
    
    def verify_backup_files(self) -> bool:
        """Verify backup files were created."""
        print("\n💾 Verifying Backup Files...")
        
        backup_dir = self.service_root / "migrations" / "backups"
        if not backup_dir.exists():
            self.log_result("Backup directory exists", False, "No backups found")
            return False
        
        # Find most recent backup
        backup_dirs = [d for d in backup_dir.iterdir() if d.is_dir() and "partner_migration" in d.name]
        if not backup_dirs:
            self.log_result("Partner backup exists", False, "No partner migration backups found")
            return False
        
        latest_backup = max(backup_dirs, key=lambda x: x.name)
        self.log_result("Backup directory exists", True, f"Found backup: {latest_backup.name}")
        
        # Check backup contents
        backup_files = [
            "app/schemas/partner.py",
            "app/services/partner_service.py",
            "app/routers/partners.py"
        ]
        
        all_backed_up = True
        for file_path in backup_files:
            full_path = latest_backup / file_path
            exists = full_path.exists()
            self.log_result(f"Backup file: {file_path}", exists)
            if not exists:
                all_backed_up = False
        
        return all_backed_up
    
    def verify_import_structure(self) -> bool:
        """Verify framework modules can be imported."""
        print("\n📦 Verifying Import Structure...")
        
        imports_to_test = [
            ("Framework schemas", "app.framework_migration.partner_schemas", ["PartnerFrameworkCreate", "PartnerFrameworkUpdate", "PartnerFrameworkResponse"]),
            ("Framework service", "app.framework_migration.partner_service", ["PartnerFrameworkService", "create_partner_service"]),
            ("Framework router", "app.framework_migration.partner_router", ["router", "framework_partner_router"]),
            ("Main app update", "app.framework_migration.main_app_update", ["include_framework_partner_routes"]),
        ]
        
        all_imports_work = True
        
        # Add current directory to Python path
        sys.path.insert(0, str(self.service_root.absolute()))
        
        for test_name, module_name, expected_objects in imports_to_test:
            try:
                module = __import__(module_name, fromlist=expected_objects)
                
                # Check if expected objects exist
                missing_objects = []
                for obj_name in expected_objects:
                    if not hasattr(module, obj_name):
                        missing_objects.append(obj_name)
                
                if missing_objects:
                    self.log_result(test_name, False, f"Missing objects: {', '.join(missing_objects)}")
                    all_imports_work = False
                else:
                    self.log_result(test_name, True, f"All objects available: {', '.join(expected_objects)}")
                    
            except Exception as e:
                self.log_result(test_name, False, f"Import error: {str(e)}")
                all_imports_work = False
        
        return all_imports_work
    
    def verify_main_app_migration(self) -> bool:
        """Verify main.py has been updated to framework version."""
        print("\n🚀 Verifying Main Application Migration...")
        
        main_py = self.service_root / "app" / "main.py"
        if not main_py.exists():
            self.log_result("main.py exists", False)
            return False
        
        content = main_py.read_text()
        
        # Check for framework indicators
        framework_indicators = [
            "Framework Edition",
            "framework_migration",
            "Framework Mode",
            "/migration/status",
            "/framework/info"
        ]
        
        found_indicators = []
        missing_indicators = []
        
        for indicator in framework_indicators:
            if indicator in content:
                found_indicators.append(indicator)
            else:
                missing_indicators.append(indicator)
        
        success = len(missing_indicators) == 0
        self.log_result("Main app migrated", success, 
                       f"Found {len(found_indicators)}/{len(framework_indicators)} framework indicators")
        
        if missing_indicators:
            self.log_result("Missing indicators", False, f"Missing: {', '.join(missing_indicators)}")
        
        return success
    
    def verify_migration_status(self) -> bool:
        """Verify migration status file is correct."""
        print("\n📊 Verifying Migration Status...")
        
        status_file = self.service_root / "app" / "migration_status.json"
        if not status_file.exists():
            self.log_result("Migration status file exists", False)
            return False
        
        try:
            import json
            with open(status_file, 'r') as f:
                status = json.load(f)
            
            required_fields = ["framework_enabled", "implementation", "migration_date"]
            missing_fields = [field for field in required_fields if field not in status]
            
            if missing_fields:
                self.log_result("Status file structure", False, f"Missing fields: {', '.join(missing_fields)}")
                return False
            
            self.log_result("Status file structure", True, "All required fields present")
            
            # Check values
            framework_enabled = status.get("framework_enabled", False)
            implementation = status.get("implementation", "")
            
            self.log_result("Framework enabled", framework_enabled, f"Implementation: {implementation}")
            
            return framework_enabled and implementation == "framework"
            
        except Exception as e:
            self.log_result("Status file parsing", False, f"JSON error: {str(e)}")
            return False
    
    def verify_documentation(self) -> bool:
        """Verify migration documentation was created."""
        print("\n📚 Verifying Documentation...")
        
        doc_files = [
            "docs/BUSINESS_OBJECT_MIGRATION_GUIDE.md",
            "docs/MIGRATION_SCRIPTS_README.md",
            "docs/PARTNER_MIGRATION_GUIDE.md", 
            "docs/MIGRATION_TEMPLATE.md"
        ]
        
        all_docs_exist = True
        for doc_file in doc_files:
            full_path = self.service_root / doc_file
            exists = full_path.exists()
            self.log_result(f"Documentation: {doc_file}", exists)
            if not exists:
                all_docs_exist = False
        
        return all_docs_exist
    
    def verify_framework_features(self) -> bool:
        """Verify framework feature files are present."""
        print("\n🔧 Verifying Framework Features...")
        
        framework_files = [
            ("Framework schemas", "app/framework/schemas.py"),
            ("Framework services", "app/framework/services.py"),
            ("Framework controllers", "app/framework/controllers.py"),
            ("Framework extensions", "app/framework/extensions.py"),
            ("Framework documentation", "app/framework/documentation.py"),
            ("Extension models", "app/models/extensions.py"),
            ("Extension migration", "migrations/versions/20250801_120000_create_extension_tables.py")
        ]
        
        all_features_exist = True
        for feature_name, file_path in framework_files:
            full_path = self.service_root / file_path
            exists = full_path.exists()
            self.log_result(feature_name, exists, f"File: {file_path}")
            if not exists:
                all_features_exist = False
        
        return all_features_exist
    
    def run_verification(self, detailed: bool = False) -> bool:
        """Run complete migration verification."""
        print("🔍 Starting Partner Service Migration Verification")
        print("=" * 60)
        
        # Run all verification tests
        tests = [
            ("File Structure", self.verify_file_structure),
            ("Backup Files", self.verify_backup_files),
            ("Import Structure", self.verify_import_structure),
            ("Main App Migration", self.verify_main_app_migration),
            ("Migration Status", self.verify_migration_status),
            ("Documentation", self.verify_documentation),
            ("Framework Features", self.verify_framework_features)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                success = test_func()
                if success:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ FAIL {test_name}: {str(e)}")
        
        # Summary
        print(f"\n📊 Verification Summary")
        print("=" * 30)
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if detailed:
            print(f"\n📋 Detailed Results:")
            for test_name, success, message in self.results:
                status = "✅" if success else "❌"
                print(f"{status} {test_name}")
                if message:
                    print(f"    {message}")
        
        overall_success = passed_tests == total_tests
        
        if overall_success:
            print(f"\n🎉 Migration Verification PASSED!")
            print("✅ Partner service successfully migrated to Business Object Framework")
            print("\n📋 Next steps:")
            print("  1. Test end-to-end functionality")
            print("  2. Verify audit logging and events")
            print("  3. Test new framework features")
            print("  4. Performance testing")
        else:
            print(f"\n⚠️  Migration Verification FAILED!")
            print("❌ Some components need attention before migration is complete")
            print("\n🔧 Troubleshooting:")
            print("  1. Check file structure and permissions")
            print("  2. Verify Python path and imports")
            print("  3. Review error messages above")
            print("  4. Use rollback_migration.py if needed")
        
        return overall_success


def main():
    """Main verification script entry point."""
    parser = argparse.ArgumentParser(description="Verify Partner service migration")
    parser.add_argument("--detailed", action="store_true", help="Show detailed test results")
    
    args = parser.parse_args()
    
    verifier = MigrationVerifier()
    success = verifier.run_verification(detailed=args.detailed)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())