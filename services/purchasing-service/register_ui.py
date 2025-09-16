#!/usr/bin/env python3
"""
Script to register purchasing service UI components with the UI Registry.
This demonstrates the service-driven UI architecture.
"""

import requests
import json
import sys
import os
from dotenv import load_dotenv

# UI Registry endpoint
load_dotenv()
UI_REGISTRY_URL = os.getenv("UI_REGISTRY_URL") or os.getenv("UI_REGISTRY_SERVICE") or "http://localhost:8010"

# Purchasing UI Package Definition
# Using the PURCHASING_UI_PACKAGE from ui_definitions.py
from purchasing_module.ui_definitions import PURCHASING_UI_PACKAGE

def register_ui_package():
    """Register the purchasing UI package with the UI Registry"""
    try:
        # Register the complete UI package
        response = requests.post(
            f"{UI_REGISTRY_URL}/api/v1/services/purchasing-service/ui-package",
            json=PURCHASING_UI_PACKAGE,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Successfully registered purchasing UI package")
            result = response.json()
            print(f"   Status: {result.get('status')}")
            print(f"   Service: {result.get('service')}")
            
            # Verify registration
            print("\n📊 Registered components:")
            
            # Check widgets
            widgets_response = requests.get(f"{UI_REGISTRY_URL}/api/v1/dashboard/widgets")
            if widgets_response.status_code == 200:
                widgets = widgets_response.json()
                purchasing_widgets = [w for w in widgets if w.get('service') == 'purchasing-service']
                print(f"   - {len(purchasing_widgets)} dashboard widgets")
                for widget in purchasing_widgets:
                    print(f"     • {widget['id']}: {widget['title']}")
            
            # Check lists
            lists_response = requests.get(f"{UI_REGISTRY_URL}/api/v1/lists")
            if lists_response.status_code == 200:
                lists = lists_response.json()
                purchasing_lists = [l for l in lists if l.get('service') == 'purchasing-service']
                print(f"   - {len(purchasing_lists)} list views")
                for lst in purchasing_lists:
                    print(f"     • {lst['id']}: {lst['title']}")
            
            # Check forms
            forms_response = requests.get(f"{UI_REGISTRY_URL}/api/v1/forms")
            if forms_response.status_code == 200:
                forms = forms_response.json()
                purchasing_forms = [f for f in forms if f.get('service') == 'purchasing-service']
                print(f"   - {len(purchasing_forms)} form views")
                for form in purchasing_forms:
                    print(f"     • {form['id']}: {form['title']}")
            
            return True
        else:
            print(f"❌ Failed to register UI package: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to UI Registry Service")
        print("   Make sure the service is running on http://localhost:8010")
        return False
    except Exception as e:
        print(f"❌ Error registering UI package: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Registering Purchasing Service UI Components")
    print("=" * 50)
    
    success = register_ui_package()
    
    if success:
        print("\n✨ Purchasing UI components are now available in the UI Registry!")
        print("   The UI service can now fetch and render these components dynamically.")
    else:
        print("\n⚠️  Failed to register UI components. Please check the errors above.")
        sys.exit(1)