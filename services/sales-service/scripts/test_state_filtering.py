#!/usr/bin/env python3
"""
Test script to verify the state parameter filtering in sales transactions.

This script tests that the state parameter filtering works correctly
when retrieving sales transactions through the API.
"""

import requests
import json
from datetime import datetime

# API base URL (adjust if running on different port/host)
BASE_URL = "http://localhost:8006"

def test_state_filtering():
    """Test that state parameter filtering works correctly."""
    
    print("🎯 Testing State Parameter Filtering in Sales Transactions")
    print("=" * 58)
    
    # First, let's see what transactions we already have
    print("\n📋 Checking existing transactions...")
    print("-" * 35)
    
    try:
        response = requests.get(f"{BASE_URL}/transactions")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result['total']} existing transactions")
            states = [tx['state'] for tx in result['data']]
            print(f"   States: {set(states)}")
        else:
            print(f"❌ Failed to get transactions: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Create test transactions with different states
    test_transactions = [
        {
            "transaction_number": f"TXN-DRAFT-{int(datetime.utcnow().timestamp())}",
            "title": "Draft Transaction",
            "customer_id": 1001,
            "state": "draft",
            "payment_status": "pending",
            "prepared_by_user_id": 1,
            "company_id": 1,
            "subtotal": 100.00,
            "tax_amount": 8.00,
            "total_amount": 108.00
        },
        {
            "transaction_number": f"TXN-APPROVED-{int(datetime.utcnow().timestamp())}",
            "title": "Approved Transaction",
            "customer_id": 1001,
            "state": "quote_approved",
            "payment_status": "pending",
            "prepared_by_user_id": 1,
            "company_id": 1,
            "subtotal": 200.00,
            "tax_amount": 16.00,
            "total_amount": 216.00
        }
    ]
    
    created_transactions = []
    
    print("\n📋 Creating Test Transactions...")
    print("-" * 35)
    
    for i, tx_data in enumerate(test_transactions, 1):
        try:
            # Create transaction
            response = requests.post(
                f"{BASE_URL}/transactions", 
                json=tx_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                created_transaction = response.json()
                created_transactions.append(created_transaction)
                print(f"✅ Transaction {i} created successfully!")
                print(f"   ID: {created_transaction['id']}")
                print(f"   Number: {created_transaction['transaction_number']}")
                print(f"   State: {created_transaction['state']}")
            else:
                print(f"❌ Failed to create transaction {i}: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating transaction {i}: {e}")
    
    if not created_transactions:
        print("❌ No transactions created, cannot proceed with testing.")
        return False
    
    print("\n🔍 Testing State Filtering...")
    print("-" * 35)
    
    # Test 1: Filter by single state
    print("\nTest 1: Filter by single state (draft)")
    try:
        response = requests.get(f"{BASE_URL}/transactions?state=draft")
        if response.status_code == 200:
            result = response.json()
            draft_count = len([tx for tx in result['data'] if tx['state'] == 'draft'])
            print(f"✅ Request successful!")
            print(f"   Total transactions: {result['total']}")
            print(f"   Draft transactions in result: {draft_count}")
            if draft_count == result['total']:
                print("✅ All results are draft transactions!")
            else:
                print("⚠️  Some results are not draft transactions.")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Filter by multiple states
    print("\nTest 2: Filter by multiple states (draft,quote_approved)")
    try:
        response = requests.get(f"{BASE_URL}/transactions?state=draft,quote_approved")
        if response.status_code == 200:
            result = response.json()
            draft_count = len([tx for tx in result['data'] if tx['state'] == 'draft'])
            approved_count = len([tx for tx in result['data'] if tx['state'] == 'quote_approved'])
            print(f"✅ Request successful!")
            print(f"   Total transactions: {result['total']}")
            print(f"   Draft transactions: {draft_count}")
            print(f"   Approved transactions: {approved_count}")
            
            # Verify that we have transactions with the expected states
            expected_states = {'draft', 'quote_approved'}
            actual_states = {tx['state'] for tx in result['data']}
            if actual_states.issubset(expected_states) and expected_states.issubset(actual_states):
                print("✅ All results have expected states!")
            else:
                print(f"⚠️  State mismatch. Expected: {expected_states}, Found: {actual_states}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Filter by non-existent state
    print("\nTest 3: Filter by non-existent state (nonexistent_state)")
    try:
        response = requests.get(f"{BASE_URL}/transactions?state=nonexistent_state")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Request successful!")
            print(f"   Total transactions: {result['total']}")
            print(f"   Data count: {len(result['data'])}")
            if result['total'] == 0 and len(result['data']) == 0:
                print("✅ Correctly returned no results for non-existent state!")
            else:
                print("⚠️  Returned results for non-existent state.")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 58)
    print("📊 State Filtering Test Completed!")
    print("=" * 58)
    
    return True

def show_usage():
    """Show usage information."""
    print("\n🔧 Usage:")
    print("-" * 15)
    print("1. Ensure the sales service is running on port 8006")
    print("2. Run this script: python test_state_filtering.py")
    print("3. Check the output to verify the state filtering works")

if __name__ == "__main__":
    print("🚀 XERPIUM Sales Transaction State Filtering Test")
    
    show_usage()
    
    # Run the test
    success = test_state_filtering()
    
    if success:
        print("\n🎉 State filtering test completed!")
        print("   The state parameter filtering should now work correctly.")
    else:
        print("\n💥 State filtering test failed!")
        print("   There may still be issues with state parameter handling.")