#!/usr/bin/env python3
"""
Test script to verify the fix for line items in sales transactions.

This script tests that line items are properly included when retrieving
a sales transaction through the API.
"""

import requests
import json
from datetime import datetime

# API base URL (adjust if running on different port/host)
BASE_URL = "http://localhost:8006"

def test_line_items_inclusion():
    """Test that line items are properly included in transaction data."""
    
    print("🎯 Testing Line Items Inclusion in Sales Transactions")
    print("=" * 55)
    
    # Test data for a sales transaction
    transaction_data = {
        "transaction_number": f"TXN-LI-TEST-{int(datetime.utcnow().timestamp())}",
        "title": "Line Items Test Transaction",
        "description": "Test transaction to verify line items inclusion",
        "customer_id": 1001,
        "state": "draft",
        "payment_status": "pending",
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow().replace(year=datetime.utcnow().year + 1)).isoformat(),
        "payment_terms_days": 30,
        "currency_code": "USD",
        "prepared_by_user_id": 1,
        "company_id": 1,
        "subtotal": 500.00,
        "tax_amount": 40.00,
        "total_amount": 540.00
    }
    
    print("\n📋 Creating Sales Transaction...")
    print("-" * 35)
    
    try:
        # Create transaction
        response = requests.post(
            f"{BASE_URL}/transactions", 
            json=transaction_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            created_transaction = response.json()
            transaction_id = created_transaction["id"]
            print(f"✅ Transaction created successfully!")
            print(f"   ID: {transaction_id}")
            print(f"   Number: {created_transaction['transaction_number']}")
        else:
            print(f"❌ Failed to create transaction: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error creating transaction: {e}")
        return
    
    print("\n➕ Adding Line Items...")
    print("-" * 35)
    
    # Add two line items
    line_items_data = [
        {
            "line_number": 1,
            "line_type": "product",
            "product_id": 2001,
            "item_code": "WIDGET-A",
            "item_name": "Premium Widget A",
            "description": "High-quality premium widget",
            "quantity_ordered": 2.0,
            "unit_price": 125.00,
            "unit_of_measure": "each",
            "discount_amount": 0.00,
            "line_total": 250.00
        },
        {
            "line_number": 2,
            "line_type": "product",
            "product_id": 2002,
            "item_code": "GADGET-B",
            "item_name": "Advanced Gadget B",
            "description": "Advanced multi-purpose gadget",
            "quantity_ordered": 1.0,
            "unit_price": 250.00,
            "unit_of_measure": "each",
            "discount_amount": 0.00,
            "line_total": 250.00
        }
    ]
    
    added_line_items = []
    for i, line_item_data in enumerate(line_items_data, 1):
        try:
            # Add line item
            response = requests.post(
                f"{BASE_URL}/transactions/{transaction_id}/line-items",
                json=line_item_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                line_item = response.json()
                added_line_items.append(line_item)
                print(f"✅ Line item {i} added successfully!")
                print(f"   Item: {line_item['item_name']}")
                print(f"   Quantity: {line_item['quantity_ordered']}")
                print(f"   Total: ${line_item['line_total']}")
            else:
                print(f"❌ Failed to add line item {i}: {response.status_code}")
                print(f"   Error: {response.text}")
                return
                
        except Exception as e:
            print(f"❌ Error adding line item {i}: {e}")
            return
    
    print("\n🔍 Retrieving Transaction with Line Items...")
    print("-" * 45)
    
    try:
        # Retrieve the transaction with line items
        response = requests.get(f"{BASE_URL}/transactions/{transaction_id}")
        
        if response.status_code == 200:
            retrieved_transaction = response.json()
            print(f"✅ Transaction retrieved successfully!")
            print(f"   ID: {retrieved_transaction['id']}")
            print(f"   Number: {retrieved_transaction['transaction_number']}")
            print(f"   Title: {retrieved_transaction['title']}")
            
            # Check if line items are included
            line_items = retrieved_transaction.get('line_items', [])
            items = retrieved_transaction.get('items', [])
            
            print(f"\n📋 Line Items Analysis:")
            print(f"   line_items key exists: {'line_items' in retrieved_transaction}")
            print(f"   line_items count: {len(line_items)}")
            print(f"   items key exists: {'items' in retrieved_transaction}")
            print(f"   items count: {len(items)}")
            
            if line_items:
                print(f"\n📦 Line Items Details:")
                for i, item in enumerate(line_items, 1):
                    print(f"   {i}. {item.get('item_name', 'Unknown')} (Qty: {item.get('quantity_ordered', 0)})")
                    print(f"      Price: ${item.get('unit_price', 0)}")
                    print(f"      Total: ${item.get('line_total', 0)}")
            else:
                print(f"\n⚠️  No line items found in transaction data!")
                print(f"   This indicates the bug is still present.")
                
        else:
            print(f"❌ Failed to retrieve transaction: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error retrieving transaction: {e}")
        return
    
    print("\n" + "=" * 55)
    print("📊 Test Results Summary:")
    print("=" * 55)
    
    # Final assessment
    line_items = retrieved_transaction.get('line_items', [])
    if line_items and len(line_items) == 2:
        print("✅ SUCCESS: Line items are properly included in transaction data!")
        print("   The fix is working correctly.")
    elif line_items:
        print("⚠️  PARTIAL: Some line items are included, but count is unexpected.")
        print(f"   Expected: 2, Got: {len(line_items)}")
    else:
        print("❌ FAILURE: No line items found in transaction data!")
        print("   The bug is still present.")
    
    return len(line_items) == 2

def show_usage():
    """Show usage information."""
    print("\n🔧 Usage:")
    print("-" * 15)
    print("1. Ensure the sales service is running on port 8006")
    print("2. Run this script: python test_line_items_fix.py")
    print("3. Check the output to verify the fix is working")

if __name__ == "__main__":
    print("🚀 XERPIUM Sales Transaction Line Items Fix Test")
    
    show_usage()
    
    # Run the test
    success = test_line_items_inclusion()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("   The line items fix is working correctly.")
    else:
        print("\n💥 Test failed!")
        print("   There may still be issues with line items inclusion.")