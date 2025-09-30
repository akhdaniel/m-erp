#!/usr/bin/env python3
"""
Simple test to verify the state filtering fix.
"""

import requests

def test_state_filtering():
    print("Testing state filtering fix...")
    
    # Test 1: Valid state
    print("\n1. Testing valid state 'draft':")
    response = requests.get("http://localhost:8006/transactions?state=draft")
    if response.status_code == 200:
        data = response.json()
        print(f"   Total: {data['total']}")
        states = [tx['state'] for tx in data['data']]
        print(f"   All states: {set(states)}")
        if all(s == 'draft' for s in states):
            print("   ✅ Correctly filtered!")
        else:
            print("   ❌ Incorrect filtering!")
    else:
        print(f"   Error: {response.status_code}")
    
    # Test 2: Invalid state
    print("\n2. Testing invalid state 'nonexistent':")
    response = requests.get("http://localhost:8006/transactions?state=nonexistent")
    if response.status_code == 200:
        data = response.json()
        print(f"   Total: {data['total']}")
        print(f"   Data count: {len(data['data'])}")
        if data['total'] == 0 and len(data['data']) == 0:
            print("   ✅ Correctly returned empty results!")
        else:
            print("   ❌ Should have returned empty results!")
    else:
        print(f"   Error: {response.status_code}")

if __name__ == "__main__":
    test_state_filtering()