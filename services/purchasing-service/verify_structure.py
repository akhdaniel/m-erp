#!/usr/bin/env python3
"""
Structure verification script for the Purchasing Module.

This script verifies that all necessary files and components are in place
for the purchasing module without requiring external dependencies.
"""

import os
import sys
from pathlib import Path

def verify_file_structure():
    """Verify that all required files exist."""
    print("📁 Verifying Purchasing Module File Structure...")
    
    # Base directory
    base_dir = Path(__file__).parent / "purchasing_module"
    
    # Required files and directories
    required_structure = {
        "__init__.py": "Module initialization",
        "main.py": "Module lifecycle management",
        "module.yaml": "Module configuration manifest",
        
        # Models
        "models/__init__.py": "Models package",
        "models/purchase_order.py": "Purchase order models",
        "models/supplier_performance.py": "Supplier performance models", 
        "models/approval_workflow.py": "Approval workflow models",
        
        # Services
        "services/__init__.py": "Services package",
        "services/purchase_order_service.py": "Purchase order business logic",
        "services/supplier_service.py": "Supplier management service",
        "services/approval_service.py": "Approval workflow service",
        
        # API
        "api/__init__.py": "API package",
        "api/purchase_orders.py": "Purchase orders API endpoints",
        "api/suppliers.py": "Suppliers API endpoints",
        "api/approvals.py": "Approvals API endpoints",
        
        # Framework
        "framework/__init__.py": "Framework interfaces",
        "framework/base.py": "Business object framework base classes"
    }
    
    missing_files = []
    existing_files = []
    
    for file_path, description in required_structure.items():
        full_path = base_dir / file_path
        if full_path.exists():
            existing_files.append((file_path, description))
            print(f"  ✅ {file_path:<35} - {description}")
        else:
            missing_files.append((file_path, description))
            print(f"  ❌ {file_path:<35} - {description} (MISSING)")
    
    print(f"\n📊 Structure Summary:")
    print(f"  ✅ Existing files: {len(existing_files)}")
    print(f"  ❌ Missing files: {len(missing_files)}")
    
    return len(missing_files) == 0

def verify_module_manifest():
    """Verify module.yaml configuration."""
    print("\n📋 Verifying Module Manifest...")
    
    manifest_path = Path(__file__).parent / "purchasing_module" / "module.yaml"
    
    if not manifest_path.exists():
        print("  ❌ module.yaml not found")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        # Check for required sections
        required_sections = [
            "name:", "version:", "description:",
            "endpoints:", "dependencies:", "config_schema:"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section in content:
                print(f"  ✅ {section:<20} Found")
            else:
                missing_sections.append(section)
                print(f"  ❌ {section:<20} Missing")
        
        print(f"  📊 Manifest size: {len(content)} characters")
        return len(missing_sections) == 0
        
    except Exception as e:
        print(f"  ❌ Error reading manifest: {e}")
        return False

def verify_code_structure():
    """Verify basic code structure in key files."""
    print("\n🔍 Verifying Code Structure...")
    
    key_files = {
        "purchasing_module/__init__.py": [
            "MODULE_INFO", "PurchaseOrder", "SupplierPerformance", "ApprovalWorkflow"
        ],
        "purchasing_module/main.py": [
            "PurchasingModuleManager", "initialize_module", "shutdown_module", "check_health"
        ],
        "purchasing_module/services/purchase_order_service.py": [
            "PurchaseOrderService", "create_purchase_order", "submit_for_approval"
        ],
        "purchasing_module/services/supplier_service.py": [
            "SupplierService", "validate_supplier", "create_performance_evaluation"
        ],
        "purchasing_module/services/approval_service.py": [
            "ApprovalService", "create_approval_workflow", "approve_workflow_step"
        ]
    }
    
    all_good = True
    
    for file_path, expected_elements in key_files.items():
        full_path = Path(__file__).parent / file_path
        
        if not full_path.exists():
            print(f"  ❌ {file_path} - File not found")
            all_good = False
            continue
        
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            
            missing_elements = []
            for element in expected_elements:
                if element in content:
                    pass  # Element found
                else:
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"  ⚠️  {file_path}")
                for element in missing_elements:
                    print(f"      Missing: {element}")
                all_good = False
            else:
                print(f"  ✅ {file_path} - All key elements found")
        
        except Exception as e:
            print(f"  ❌ {file_path} - Error reading file: {e}")
            all_good = False
    
    return all_good

def verify_api_structure():
    """Verify API endpoint structure."""
    print("\n🌐 Verifying API Structure...")
    
    api_files = [
        "purchasing_module/api/purchase_orders.py",
        "purchasing_module/api/suppliers.py", 
        "purchasing_module/api/approvals.py"
    ]
    
    expected_patterns = [
        "APIRouter", "response_model", "_router", "HTTPException"
    ]
    
    all_good = True
    
    for api_file in api_files:
        full_path = Path(__file__).parent / api_file
        
        if not full_path.exists():
            print(f"  ❌ {api_file} - File not found")
            all_good = False
            continue
        
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Count endpoints (approximate by counting @router decorators)
            endpoint_count = content.count("@") - content.count("@validator") - content.count("@property")
            
            missing_patterns = []
            for pattern in expected_patterns:
                if pattern.replace(".*", "") in content or any(p in content for p in pattern.split("|") if "|" in pattern):
                    pass
                else:
                    missing_patterns.append(pattern)
            
            if missing_patterns:
                print(f"  ⚠️  {api_file} - Missing patterns: {missing_patterns}")
                all_good = False
            else:
                print(f"  ✅ {api_file} - ~{endpoint_count} endpoints, all patterns found")
        
        except Exception as e:
            print(f"  ❌ {api_file} - Error reading file: {e}")
            all_good = False
    
    return all_good

def count_lines_of_code():
    """Count total lines of code in the module."""
    print("\n📏 Counting Lines of Code...")
    
    base_dir = Path(__file__).parent / "purchasing_module"
    total_lines = 0
    total_files = 0
    
    file_counts = {}
    
    for file_path in base_dir.rglob("*.py"):
        try:
            with open(file_path, 'r') as f:
                lines = len(f.readlines())
            
            relative_path = file_path.relative_to(base_dir)
            file_counts[str(relative_path)] = lines
            total_lines += lines
            total_files += 1
        
        except Exception as e:
            print(f"  ⚠️  Error reading {file_path}: {e}")
    
    # Sort files by line count
    sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
    
    print(f"  📊 Total files: {total_files}")
    print(f"  📊 Total lines: {total_lines:,}")
    print(f"  📊 Average lines per file: {total_lines/total_files:.1f}")
    
    print("\n  📋 Largest files:")
    for file_path, line_count in sorted_files[:5]:
        print(f"    {file_path:<35} {line_count:>4} lines")
    
    return total_lines

def main():
    """Run all verification checks."""
    print("🔍 Purchasing Module Structure Verification")
    print("=" * 60)
    
    checks = [
        ("File Structure", verify_file_structure),
        ("Module Manifest", verify_module_manifest), 
        ("Code Structure", verify_code_structure),
        ("API Structure", verify_api_structure)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"  ❌ {check_name} check failed: {e}")
            results.append((check_name, False))
    
    # Count lines of code
    total_lines = count_lines_of_code()
    
    # Print summary
    print("\n📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {check_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n  📋 Code Statistics:")
    print(f"    Total lines of code: {total_lines:,}")
    print(f"    Verification score: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL VERIFICATIONS PASSED")
        print("✅ Purchasing Module structure is complete and ready!")
        return True
    else:
        print(f"\n⚠️  {total - passed} verifications failed")
        print("❌ Review and fix issues before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)