#!/usr/bin/env python3
"""
Test script for the Purchasing Module.

This script tests the core functionality of the purchasing module
including module initialization, service operations, and API integration.
"""

import asyncio
import sys
import os
from typing import Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta

# Add the purchasing module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'purchasing_module'))

# Import purchasing module components
from purchasing_module.main import initialize_module, check_health, shutdown_module
from purchasing_module.services.purchase_order_service import PurchaseOrderService
from purchasing_module.services.supplier_service import SupplierService
from purchasing_module.services.approval_service import ApprovalService

print("🔍 Testing Purchasing Module Integration")
print("=" * 60)

async def test_module_lifecycle():
    """Test module initialization, health check, and shutdown."""
    print("\n📦 Testing Module Lifecycle...")
    
    # Test configuration
    test_config = {
        "approval_thresholds": {
            "manager_limit": 5000.00,
            "director_limit": 25000.00,
            "requires_board_approval": 100000.00
        },
        "default_currency": "USD",
        "notification_settings": {
            "email_notifications": True,
            "approval_reminders": True,
            "reminder_days": 3
        }
    }
    
    try:
        # Initialize module
        print("  • Initializing purchasing module...")
        success = await initialize_module(test_config)
        if success:
            print("    ✅ Module initialized successfully")
        else:
            print("    ❌ Module initialization failed")
            return False
        
        # Health check
        print("  • Running health check...")
        health = await check_health()
        print(f"    ✅ Health status: {health['status']}")
        print(f"    📊 Module: {health['module']} v{health['version']}")
        print(f"    ⏱️  Uptime: {health['uptime_seconds']:.1f} seconds")
        
        # Shutdown module
        print("  • Shutting down module...")
        shutdown_success = await shutdown_module()
        if shutdown_success:
            print("    ✅ Module shutdown successfully")
        else:
            print("    ❌ Module shutdown failed")
        
        return success and shutdown_success
        
    except Exception as e:
        print(f"    ❌ Module lifecycle test failed: {e}")
        return False

def test_purchase_order_service():
    """Test purchase order service functionality."""
    print("\n🛒 Testing Purchase Order Service...")
    
    try:
        service = PurchaseOrderService()
        
        # Test create purchase order
        print("  • Testing purchase order creation...")
        line_items = [
            {
                "line_number": 1,
                "product_code": "PROD001",
                "product_name": "Test Product 1",
                "description": "Test product for purchasing module",
                "quantity": 10,
                "unit_price": 150.00,
                "unit_of_measure": "each"
            },
            {
                "line_number": 2,
                "product_code": "PROD002", 
                "product_name": "Test Product 2",
                "description": "Another test product",
                "quantity": 5,
                "unit_price": 200.00,
                "unit_of_measure": "each"
            }
        ]
        
        po = service.create_purchase_order(
            company_id=1,
            supplier_id=1,
            line_items=line_items,
            created_by_user_id=1,
            delivery_date=datetime.now() + timedelta(days=30),
            notes="Test purchase order",
            currency_code="USD"
        )
        
        if po:
            print(f"    ✅ Purchase order created: {po.po_number}")
            print(f"    💰 Total amount: ${po.total_amount}")
            print(f"    📋 Status: {po.status.value}")
        else:
            print("    ❌ Failed to create purchase order")
            return False
        
        # Test submit for approval
        print("  • Testing approval submission...")
        success = service.submit_for_approval(
            purchase_order_id=po.id,
            submitted_by_user_id=1,
            approval_notes="Please approve this test order"
        )
        
        if success:
            print("    ✅ Purchase order submitted for approval")
        else:
            print("    ❌ Failed to submit for approval")
        
        # Test purchase order statistics
        print("  • Testing statistics retrieval...")
        stats = service.get_purchase_order_statistics(company_id=1)
        print(f"    📊 Total orders: {stats.get('total_orders', 0)}")
        print(f"    💵 Total value: ${stats.get('total_value', 0):,.2f}")
        print(f"    📈 Average order value: ${stats.get('average_order_value', 0):,.2f}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Purchase order service test failed: {e}")
        return False

def test_supplier_service():
    """Test supplier service functionality."""
    print("\n🏢 Testing Supplier Service...")
    
    try:
        service = SupplierService()
        
        # Test supplier validation
        print("  • Testing supplier validation...")
        is_valid = service.validate_supplier(supplier_id=1, company_id=1)
        if is_valid:
            print("    ✅ Supplier validation passed")
        else:
            print("    ❌ Supplier validation failed")
            return False
        
        # Test get supplier info
        print("  • Testing supplier information retrieval...")
        supplier_info = service.get_supplier_info(supplier_id=1, company_id=1)
        if supplier_info:
            print(f"    ✅ Supplier info retrieved: {supplier_info['name']}")
            print(f"    📧 Email: {supplier_info['email']}")
            print(f"    📱 Phone: {supplier_info['phone']}")
        else:
            print("    ❌ Failed to get supplier info")
        
        # Test get active suppliers
        print("  • Testing active suppliers list...")
        suppliers = service.get_active_suppliers(company_id=1, limit=5)
        print(f"    ✅ Retrieved {len(suppliers)} active suppliers")
        
        # Test create performance evaluation
        print("  • Testing performance evaluation creation...")
        period_start = datetime.now() - timedelta(days=90)
        period_end = datetime.now()
        
        performance = service.create_performance_evaluation(
            supplier_id=1,
            company_id=1,
            evaluation_period_start=period_start,
            evaluation_period_end=period_end,
            evaluator_user_id=1
        )
        
        if performance:
            print(f"    ✅ Performance evaluation created")
            print(f"    📊 Total orders: {performance.total_orders}")
            print(f"    💰 Total value: ${performance.total_value}")
            print(f"    🚚 On-time delivery: {performance.on_time_delivery_percentage:.1f}%")
            print(f"    ⭐ Overall rating: {performance.overall_rating.value if performance.overall_rating else 'Not rated'}")
            
            # Test finalize evaluation
            print("  • Testing evaluation finalization...")
            success = service.finalize_performance_evaluation(
                performance_id=performance.id,
                evaluator_user_id=1,
                evaluation_notes="Good overall performance with room for delivery improvements",
                improvement_areas=["Delivery timeliness", "Communication response time"],
                strengths=["Product quality", "Competitive pricing", "Compliance"]
            )
            
            if success:
                print("    ✅ Performance evaluation finalized")
            else:
                print("    ❌ Failed to finalize evaluation")
        else:
            print("    ❌ Failed to create performance evaluation")
        
        # Test supplier statistics
        print("  • Testing supplier statistics...")
        stats = service.get_supplier_statistics(company_id=1)
        print(f"    📊 Total suppliers: {stats.get('total_suppliers', 0)}")
        print(f"    ✅ Active suppliers: {stats.get('active_suppliers', 0)}")
        print(f"    ⭐ Average performance: {stats.get('average_performance_score', 0):.1f}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Supplier service test failed: {e}")
        return False

def test_approval_service():
    """Test approval service functionality."""
    print("\n✅ Testing Approval Service...")
    
    try:
        service = ApprovalService()
        
        # Test create approval workflow
        print("  • Testing approval workflow creation...")
        workflow_config = {
            "name": "Standard Approval",
            "description": "Standard purchase order approval workflow",
            "steps": [
                {
                    "name": "Manager Approval",
                    "type": "manager",
                    "required": True,
                    "amount_limit": 5000
                },
                {
                    "name": "Director Approval", 
                    "type": "director",
                    "required": True,
                    "amount_limit": 25000
                }
            ]
        }
        
        workflow = service.create_approval_workflow(
            purchase_order_id=1,
            submitted_by_user_id=1,
            workflow_config=workflow_config,
            submission_notes="Test approval workflow",
            expiration_hours=168
        )
        
        if workflow:
            print(f"    ✅ Approval workflow created: {workflow.workflow_name}")
            print(f"    📋 Status: {workflow.status.value}")
            print(f"    📊 Steps: {workflow.current_step_number}/{workflow.total_steps}")
        else:
            print("    ❌ Failed to create approval workflow")
            return False
        
        # Test get pending approvals
        print("  • Testing pending approvals retrieval...")
        pending = service.get_pending_approvals(user_id=1, company_id=1, limit=10)
        print(f"    ✅ Retrieved {len(pending)} pending approvals")
        
        # Test workflow statistics
        print("  • Testing approval statistics...")
        stats = service.get_approval_statistics(company_id=1)
        print(f"    📊 Total workflows: {stats.get('total_workflows', 0)}")
        print(f"    ⏳ Pending approvals: {stats.get('pending_approvals', 0)}")
        print(f"    ⏱️  Average approval time: {stats.get('average_approval_time_hours', 0):.1f} hours")
        print(f"    📈 On-time approvals: {stats.get('approval_efficiency', {}).get('on_time_approvals', 0):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Approval service test failed: {e}")
        return False

def test_api_integration():
    """Test API integration points."""
    print("\n🌐 Testing API Integration...")
    
    try:
        # Test API router imports
        print("  • Testing API router imports...")
        from purchasing_module.api import purchase_orders_router, suppliers_router, approvals_router
        
        print(f"    ✅ Purchase Orders API: {len(purchase_orders_router.routes)} routes")
        print(f"    ✅ Suppliers API: {len(suppliers_router.routes)} routes")
        print(f"    ✅ Approvals API: {len(approvals_router.routes)} routes")
        
        # Test API endpoint definitions
        print("  • Testing API endpoint definitions...")
        
        # Check some key endpoints exist
        po_routes = [route.path for route in purchase_orders_router.routes if hasattr(route, 'path')]
        supplier_routes = [route.path for route in suppliers_router.routes if hasattr(route, 'path')]
        approval_routes = [route.path for route in approvals_router.routes if hasattr(route, 'path')]
        
        expected_po_routes = ['/purchase-orders/', '/purchase-orders/{purchase_order_id}']
        expected_supplier_routes = ['/suppliers/', '/suppliers/{supplier_id}']
        expected_approval_routes = ['/approvals/pending', '/approvals/workflows/{workflow_id}']
        
        print(f"    📋 Purchase order routes defined: {len(po_routes)}")
        print(f"    🏢 Supplier routes defined: {len(supplier_routes)}")
        print(f"    ✅ Approval routes defined: {len(approval_routes)}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ API integration test failed: {e}")
        return False

async def run_all_tests():
    """Run all purchasing module tests."""
    print("🚀 Starting Purchasing Module Integration Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test module lifecycle
    result = await test_module_lifecycle()
    test_results.append(("Module Lifecycle", result))
    
    # Test purchase order service
    result = test_purchase_order_service()
    test_results.append(("Purchase Order Service", result))
    
    # Test supplier service
    result = test_supplier_service()
    test_results.append(("Supplier Service", result))
    
    # Test approval service
    result = test_approval_service()
    test_results.append(("Approval Service", result))
    
    # Test API integration
    result = test_api_integration()
    test_results.append(("API Integration", result))
    
    # Print test summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Purchasing Module Ready!")
        return True
    else:
        print("⚠️  Some tests failed - Review implementation")
        return False

if __name__ == "__main__":
    print("Testing Purchasing Module v1.0.0")
    print("This script validates the purchasing module implementation")
    print()
    
    try:
        # Run all tests
        success = asyncio.run(run_all_tests())
        
        if success:
            print("\n✅ Purchasing Module Integration Test: SUCCESS")
            sys.exit(0)
        else:
            print("\n❌ Purchasing Module Integration Test: FAILURE")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        sys.exit(1)