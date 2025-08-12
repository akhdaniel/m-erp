#!/usr/bin/env python3
"""
Script to register purchasing menus directly with the menu-access-service
"""

import requests
import json

def register_purchasing_menus():
    """Register purchasing menus with the menu-access-service."""
    
    # Menu service URL
    menu_service_url = "http://localhost:8003"
    
    # Get auth token first (admin user)
    auth_url = "http://localhost:8001/api/token"
    auth_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    
    # Get auth token
    print("Getting auth token...")
    auth_response = requests.post(auth_url, data=auth_data)
    if auth_response.status_code != 200:
        print(f"Failed to get auth token: {auth_response.status_code}")
        print(auth_response.text)
        return
    
    token_data = auth_response.json()
    access_token = token_data.get("access_token")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Define purchasing menus
    menus = [
        # Parent menu
        {
            "code": "purchasing",
            "title": "Purchasing",
            "description": "Purchasing management",
            "parent_id": None,
            "order_index": 30,
            "level": 0,
            "url": "/purchasing",
            "icon": "shopping-cart",
            "item_type": "dropdown",
            "is_active": True,
            "is_visible": True,
            "required_permission": "purchasing.access"
        },
        # Child menus - we'll add these after getting the parent ID
        {
            "code": "purchasing.orders",
            "title": "Purchase Orders",
            "description": "Manage purchase orders",
            "parent_code": "purchasing",  # We'll replace with parent_id
            "order_index": 10,
            "level": 1,
            "url": "/purchasing/orders",
            "icon": "file-text",
            "item_type": "link",
            "is_active": True,
            "is_visible": True,
            "required_permission": "purchasing.orders.read"
        },
        {
            "code": "purchasing.suppliers",
            "title": "Suppliers",
            "description": "Manage suppliers",
            "parent_code": "purchasing",
            "order_index": 20,
            "level": 1,
            "url": "/purchasing/suppliers",
            "icon": "truck",
            "item_type": "link",
            "is_active": True,
            "is_visible": True,
            "required_permission": "purchasing.suppliers.read"
        },
        {
            "code": "purchasing.approvals",
            "title": "Approvals",
            "description": "Purchase approvals",
            "parent_code": "purchasing",
            "order_index": 30,
            "level": 1,
            "url": "/purchasing/approvals",
            "icon": "check-circle",
            "item_type": "link",
            "is_active": True,
            "is_visible": True,
            "required_permission": "purchasing.approvals.read"
        },
        {
            "code": "purchasing.reports",
            "title": "Reports",
            "description": "Purchasing reports",
            "parent_code": "purchasing",
            "order_index": 40,
            "level": 1,
            "url": "/purchasing/reports",
            "icon": "bar-chart",
            "item_type": "link",
            "is_active": True,
            "is_visible": True,
            "required_permission": "purchasing.reports.read"
        },
        {
            "code": "purchasing.settings",
            "title": "Settings",
            "description": "Purchasing settings",
            "parent_code": "purchasing",
            "order_index": 50,
            "level": 1,
            "url": "/purchasing/settings",
            "icon": "settings",
            "item_type": "link",
            "is_active": True,
            "is_visible": True,
            "required_permission": "purchasing.settings.read"
        }
    ]
    
    # First, create the parent menu
    parent_menu = menus[0]
    print(f"Creating parent menu: {parent_menu['title']}")
    
    response = requests.post(
        f"{menu_service_url}/api/v1/menus/",
        json=parent_menu,
        headers=headers
    )
    
    if response.status_code == 200:
        parent_data = response.json()
        parent_id = parent_data['id']
        print(f"Created parent menu with ID: {parent_id}")
        
        # Now create child menus
        for menu in menus[1:]:
            # Replace parent_code with parent_id
            menu.pop('parent_code', None)
            menu['parent_id'] = parent_id
            
            print(f"Creating child menu: {menu['title']}")
            
            response = requests.post(
                f"{menu_service_url}/api/v1/menus/",
                json=menu,
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"  ✓ Created: {menu['title']}")
            else:
                print(f"  ✗ Failed to create {menu['title']}: {response.status_code}")
                print(f"    Error: {response.text}")
    else:
        print(f"Failed to create parent menu: {response.status_code}")
        print(response.text)
    
    print("\nMenu registration complete!")
    
    # Verify the menus were created
    print("\nVerifying menus...")
    verify_response = requests.get(
        f"{menu_service_url}/api/v1/menus/",
        headers=headers
    )
    
    if verify_response.status_code == 200:
        all_menus = verify_response.json()
        purchasing_menus = [m for m in all_menus if 'purchasing' in m.get('code', '')]
        print(f"Found {len(purchasing_menus)} purchasing menus in the system")
        for menu in purchasing_menus:
            print(f"  - {menu['code']}: {menu['title']}")

if __name__ == "__main__":
    register_purchasing_menus()