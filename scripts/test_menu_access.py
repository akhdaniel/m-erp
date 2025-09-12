#!/usr/bin/env python3
"""
Test script to verify menu access with and without authentication
"""

import requests
import json

# First, login to get a token
print("Logging in as admin@m-erp.com...")
login_data = {
    "email": "admin@m-erp.com",
    "password": "admin123"
}

# Login through Kong
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json=login_data,
    headers={"Host": "demo.xerpium.com"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code} - {login_response.text}")
    exit(1)

token = login_response.json().get("access_token")
print(f"Got token: {token[:20]}...")

# Test 1: Access menus without authentication (should only show public menus)
print("\n=== Test 1: Access menus without authentication ===")
response = requests.get(
    "http://localhost:8000/api/v1/menus/tree",
    headers={"Host": "demo.xerpium.com"}
)

if response.status_code == 200:
    menu_data = response.json()
    print(f"Menu count without auth: {len(menu_data.get('menus', []))}")
    for menu in menu_data.get('menus', []):
        print(f"  - {menu.get('title')}")
else:
    print(f"Error: {response.status_code} - {response.text}")

# Test 2: Access menus with authentication (should show all menus)
print("\n=== Test 2: Access menus with authentication ===")
response = requests.get(
    "http://localhost:8000/api/v1/menus/tree",
    headers={
        "Host": "demo.xerpium.com",
        "Authorization": f"Bearer {token}"
    }
)

if response.status_code == 200:
    menu_data = response.json()
    print(f"Menu count with auth: {len(menu_data.get('menus', []))}")
    for menu in menu_data.get('menus', []):
        print(f"  - {menu.get('title')}")
        
    # Show permissions if available
    if 'user_permissions' in menu_data:
        print(f"User permissions: {len(menu_data['user_permissions'])}")
        print("First 5 permissions:", menu_data['user_permissions'][:5])
else:
    print(f"Error: {response.status_code} - {response.text}")

print("\n=== Test completed ===")