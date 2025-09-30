#!/usr/bin/env python3
"""
Simple test script to debug state filtering.
"""

import requests

# API base URL (adjust if running on different port/host)
BASE_URL = "http://localhost:8006"

def test_simple_state_filter():
    """Test simple state filtering."""
    
    print("Testing state filtering...")
    
    # Test 1: Get all transactions
    print("\n1. Getting all transactions:")
    response = requests.get(f"{BASE_URL}/transactions")
    if response.status_code == 200:
        result = response.json()
        print(f"   Total: {result['total']}")
        states = [tx['state'] for tx in result['data']]
        print(f"   States: {set(states)}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")
    
    # Test 2: Filter by draft state
    print("\n2. Filtering by draft state:")
    response = requests.get(f"{BASE_URL}/transactions?state=draft")
    if response.status_code == 200:
        result = response.json()
        print(f"   Total: {result['total']}")
        states = [tx['state'] for tx in result['data']]
        print(f"   States: {set(states)}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")
    
    # Test 3: Filter by multiple states
    print("\n3. Filtering by multiple states (draft,quote_approved):")
    response = requests.get(f"{BASE_URL}/transactions?state=draft,quote_approved")
    if response.status_code == 200:
        result = response.json()
        print(f"   Total: {result['total']}")
        states = [tx['state'] for tx in result['data']]
        print(f"   States: {set(states)}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")
    
    # Test 4: Filter by non-existent state
    print("\n4. Filtering by non-existent state:")
    response = requests.get(f"{BASE_URL}/transactions?state=nonexistent")
    if response.status_code == 200:
        result = response.json()
        print(f"   Total: {result['total']}")
        states = [tx['state'] for tx in result['data']]
        print(f"   States: {set(states)}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_simple_state_filter()