#!/usr/bin/env python3
"""
Test script to check menu API access
"""

import httpx
import asyncio
import json

async def test_menu_api():
    """Test the menu API directly"""
    print("Testing menu API access...")
    
    # Test unauthenticated access
    print("\n1. Testing unauthenticated access:")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8003/api/v1/menus/tree")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Total items: {data.get('total_items', 0)}")
                print(f"   Menus count: {len(data.get('menus', []))}")
            else:
                print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test with a service token
    print("\n2. Testing with service token:")
    try:
        async with httpx.AsyncClient() as client:
            # First get a service token from auth service
            auth_data = {
                "service_name": "menu-access-service",
                "service_key": "menu-access-service-key",
                "service_secret": "menu-access-service-secret-key-that-is-long-enough"
            }
            
            auth_response = await client.post(
                "http://localhost:8001/api/services/token",
                json=auth_data
            )
            
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                service_token = auth_data.get("access_token")
                print(f"   Got service token: {service_token[:20]}...")
                
                # Now test menu API with service token
                headers = {"Authorization": f"Bearer {service_token}"}
                menu_response = await client.get(
                    "http://localhost:8003/api/v1/menus/tree",
                    headers=headers
                )
                
                print(f"   Menu API Status: {menu_response.status_code}")
                if menu_response.status_code == 200:
                    data = menu_response.json()
                    print(f"   Total items: {data.get('total_items', 0)}")
                    print(f"   Menus count: {len(data.get('menus', []))}")
                    print(f"   Sample menu: {data.get('menus', [{}])[0] if data.get('menus') else 'None'}")
                else:
                    print(f"   Error: {menu_response.text}")
            else:
                print(f"   Auth failed: {auth_response.status_code} - {auth_response.text}")
                
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_menu_api())