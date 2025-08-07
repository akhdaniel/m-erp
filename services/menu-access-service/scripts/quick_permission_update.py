#!/usr/bin/env python3
"""
Quick script to update admin role with menu permissions.
"""

import requests
import json

# Login as admin
login_response = requests.post(
    "http://localhost:8001/api/auth/login",
    json={"email": "admin@example.com", "password": "admin123"}
)

if login_response.status_code != 200:
    print(f"Failed to login: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get current admin role
roles_response = requests.get(
    "http://localhost:8001/roles/",
    headers=headers
)

if roles_response.status_code != 200:
    print(f"Failed to get roles: {roles_response.text}")
    exit(1)

roles = roles_response.json()
admin_role = None
for role in roles:
    if role["name"] in ["admin", "Admin", "superuser"]:
        admin_role = role
        break

if not admin_role:
    print("Admin role not found")
    exit(1)

print(f"Found admin role: {admin_role['name']} (ID: {admin_role['id']})")
print(f"Current permissions: {len(admin_role['permissions'])}")

# Add menu permissions
menu_permissions = [
    "companies.view",
    "companies.create",
    "companies.update",
    "companies.delete",
    "partners.view",
    "partners.create",
    "partners.update",
    "partners.delete",
    "users.view",
    "users.create",
    "users.update",
    "users.delete",
    "inventory.access",
    "inventory.manage",
    "sales.access",
    "sales.manage",
    "menu.view",
    "menu.admin"
]

# Combine with existing permissions
all_permissions = list(set(admin_role["permissions"] + menu_permissions))

# Update the role
update_response = requests.put(
    f"http://localhost:8001/roles/{admin_role['id']}",
    headers=headers,
    json={
        "name": admin_role["name"],
        "description": admin_role["description"],
        "permissions": all_permissions
    }
)

if update_response.status_code != 200:
    print(f"Failed to update role: {update_response.text}")
    exit(1)

print(f"\n✅ Updated {admin_role['name']} role with {len(all_permissions)} permissions!")
print("\nAll permissions:")
for perm in sorted(all_permissions):
    print(f"  - {perm}")

print("\n📘 Next steps:")
print("1. Users need to log out and log back in to get updated permissions")
print("2. The menu should now be visible to admin users")