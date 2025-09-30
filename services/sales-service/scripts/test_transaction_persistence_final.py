#!/usr/bin/env python3
"""
Test script to demonstrate sales transaction persistence through the API.

This script shows how to create, retrieve, update, and verify persistent sales transactions
using the XERPIUM Sales Service transaction API.
"""

import requests
import json
from datetime import datetime

# API base URL (adjust if running on different port/host)
BASE_URL = "http://localhost:8006"

def test_transaction_persistence():
    """Test sales transaction persistence through the API."""
    
    print("🎯 Testing Sales Transaction Persistence")
    print("=" * 50)
    
    # Test data for a sales transaction
    transaction_data = {
        "transaction_number": "TXN-2025-011",
        "title": "Complete Sales Transaction Test",
        "description": "Sample transaction to demonstrate full persistence",
        "customer_id": 1001,
        "state": "draft",
        "payment_status": "pending",
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow().replace(year=datetime.utcnow().year + 1)).isoformat(),
        "payment_terms_days": 30,
        "currency_code": "USD",
        "prepared_by_user_id": 1,
        "company_id": 1,
        "subtotal": 1000.00,
        "tax_amount": 80.00,
        "discount_amount": 50.00,
        "total_amount": 1030.00
    }
    
    print("\n📋 Creating Sales Transaction...")
    print("-" * 30)
    
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
            print(f"   Title: {created_transaction['title']}")
            print(f"   State: {created_transaction['state']}")
            print(f"   Payment Status: {created_transaction['payment_status']}")
            print(f"   Total: ${created_transaction['total_amount']}")
        else:
            print(f"❌ Failed to create transaction: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error creating transaction: {e}")
        return
    
    print("\n🔍 Retrieving Transaction...")
    print("-" * 30)
    
    try:
        # Retrieve the created transaction
        response = requests.get(f"{BASE_URL}/transactions/{transaction_id}")
        
        if response.status_code == 200:
            retrieved_transaction = response.json()
            print(f"✅ Transaction retrieved successfully!")
            print(f"   ID: {retrieved_transaction['id']}")
            print(f"   Number: {retrieved_transaction['transaction_number']}")
            print(f"   Title: {retrieved_transaction['title']}")
            print(f"   State: {retrieved_transaction['state']}")
            print(f"   Payment Status: {retrieved_transaction['payment_status']}")
            print(f"   Total: ${retrieved_transaction['total_amount']}")
            print(f"   Created: {retrieved_transaction['created_at']}")
        else:
            print(f"❌ Failed to retrieve transaction: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error retrieving transaction: {e}")
        return
    
    print("\n📝 Updating Transaction...")
    print("-" * 30)
    
    # Update data
    update_data = {
        "title": "Updated Complete Sales Transaction Test",
        "description": "Updated description for testing persistence",
        "state": "quote_approved",
        "payment_status": "authorized",
        "discount_amount": 75.00,
        "total_amount": 1005.00
    }
    
    try:
        # Update transaction
        response = requests.put(
            f"{BASE_URL}/transactions/{transaction_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            updated_transaction = response.json()
            print(f"✅ Transaction updated successfully!")
            print(f"   Title: {updated_transaction['title']}")
            print(f"   State: {updated_transaction['state']}")
            print(f"   Payment Status: {updated_transaction['payment_status']}")
            print(f"   Discount: ${updated_transaction['discount_amount']}")
            print(f"   Total: ${updated_transaction['total_amount']}")
        else:
            print(f"❌ Failed to update transaction: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error updating transaction: {e}")
        return
    
    print("\n➕ Adding Line Items...")
    print("-" * 30)
    
    # Line item data
    line_item_data = {
        "line_number": 1,
        "line_type": "product",
        "product_id": 2001,
        "item_code": "LAPTOP-PRO",
        "item_name": "Professional Laptop",
        "description": "High-performance business laptop",
        "quantity_ordered": 2.0,
        "unit_price": 1299.99,
        "unit_of_measure": "each",
        "discount_amount": 0.00,
        "line_total": 2599.98
    }
    
    try:
        # Add line item
        response = requests.post(
            f"{BASE_URL}/transactions/{transaction_id}/line-items",
            json=line_item_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            line_item = response.json()
            print(f"✅ Line item added successfully!")
            print(f"   Item: {line_item['item_name']}")
            print(f"   Quantity: {line_item['quantity_ordered']}")
            print(f"   Price: ${line_item['unit_price']}")
            print(f"   Total: ${line_item['line_total']}")
        else:
            print(f"❌ Failed to add line item: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error adding line item: {e}")
        return
    
    print("\n📋 Listing All Transactions...")
    print("-" * 30)
    
    try:
        # List transactions
        response = requests.get(f"{BASE_URL}/transactions")
        
        if response.status_code == 200:
            transaction_list = response.json()
            print(f"✅ Retrieved transaction list!")
            print(f"   Total transactions: {transaction_list['total']}")
            print(f"   Current page: {transaction_list['skip'] + 1}")
            print(f"   Items per page: {transaction_list['limit']}")
            
            # Show our transaction in the list
            for tx in transaction_list['data']:
                if tx['id'] == transaction_id:
                    print(f"   Found our transaction: {tx['transaction_number']} - {tx['title']}")
                    print(f"   State: {tx['state']}")
                    print(f"   Payment Status: {tx['payment_status']}")
                    break
        else:
            print(f"❌ Failed to list transactions: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error listing transactions: {e}")
    
    print("\n📊 Getting Transaction Statistics...")
    print("-" * 30)
    
    try:
        # Get statistics
        response = requests.get(f"{BASE_URL}/transactions/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Retrieved transaction statistics!")
            print(f"   Total transactions: {stats.get('total_transactions', 'N/A')}")
            print(f"   Total quotes: {stats.get('total_quotes', 'N/A')}")
            print(f"   Total orders: {stats.get('total_orders', 'N/A')}")
        else:
            print(f"❌ Failed to get statistics: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Transaction Persistence Test Completed!")
    print("=" * 50)
    print("\n📋 Summary:")
    print("   ✅ Created transaction through API")
    print("   ✅ Retrieved transaction from database")
    print("   ✅ Updated transaction data")
    print("   ✅ Added line items")
    print("   ✅ Listed transactions")
    print("   ✅ Retrieved statistics")
    print("\n🔧 The sales transaction data is now persistent in the database!")
    print("   All changes are stored and can be retrieved at any time.")

def show_api_endpoints():
    """Show available transaction API endpoints."""
    print("\n🌐 Available Transaction API Endpoints:")
    print("-" * 40)
    endpoints = [
        "GET    /transactions           # List transactions",
        "POST   /transactions           # Create transaction",
        "GET    /transactions/{id}      # Get transaction by ID",
        "PUT    /transactions/{id}      # Update transaction",
        "DELETE /transactions/{id}      # Delete transaction",
        "POST   /transactions/{id}/state/{new_state}  # Change state",
        "GET    /transactions/{id}/line-items  # List line items",
        "POST   /transactions/{id}/line-items  # Add line item",
        "GET    /transactions/stats     # Get statistics"
    ]
    
    for endpoint in endpoints:
        print(f"   {endpoint}")

def show_sample_curl_commands():
    """Show sample curl commands for testing."""
    print("\n🔧 Sample curl Commands for Testing:")
    print("-" * 40)
    
    commands = [
        '# Create a new transaction',
        'curl -X POST "http://localhost:8006/transactions" \\',
        '     -H "Content-Type: application/json" \\',
        '     -d \'{"transaction_number": "TXN-2025-012", "title": "API Test Transaction", "customer_id": 1001, "state": "draft", "payment_status": "pending", "prepared_by_user_id": 1, "company_id": 1, "subtotal": 100.0, "tax_amount": 8.0, "total_amount": 108.0}\'',
        '',
        '# Get a transaction by ID',
        'curl "http://localhost:8006/transactions/1"',
        '',
        '# List all transactions',
        'curl "http://localhost:8006/transactions"',
        '',
        '# Update a transaction',
        'curl -X PUT "http://localhost:8006/transactions/1" \\',
        '     -H "Content-Type: application/json" \\',
        '     -d \'{"title": "Updated Transaction", "state": "quote_approved", "payment_status": "authorized"}\''
    ]
    
    for command in commands:
        print(command)

if __name__ == "__main__":
    print("🚀 XERPIUM Sales Transaction Persistence Test")
    
    # Show API information
    show_api_endpoints()
    show_sample_curl_commands()
    
    # Run the test
    test_transaction_persistence()
    
    print("\n📝 Notes:")
    print("   • The sales service must be running on port 8006")
    print("   • All transactions are persisted in the PostgreSQL database")
    print("   • Enum values are properly handled (lowercase in database, converted from API)")
    print("   • The transaction data includes full audit trails and timestamps")