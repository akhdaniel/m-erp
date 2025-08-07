#!/usr/bin/env python3
"""
Script to update admin role with menu permissions.
"""

import asyncio
import json
import psycopg2
from psycopg2.extras import Json

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'user_auth_db',
    'user': 'postgres',
    'password': 'password'
}

def get_menu_permissions():
    """Get all required permissions from menu_access_db."""
    permissions = set()
    
    try:
        # Connect to menu_access_db
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database='menu_access_db',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cur = conn.cursor()
        
        # Get all permissions
        cur.execute("SELECT code FROM permissions ORDER BY code")
        for row in cur.fetchall():
            permissions.add(row[0])
        
        cur.close()
        conn.close()
        
        return permissions
    except Exception as e:
        print(f"Error getting menu permissions: {e}")
        return set()

def update_admin_role():
    """Update admin role with all permissions."""
    try:
        # Get menu permissions
        menu_permissions = get_menu_permissions()
        print(f"Found {len(menu_permissions)} menu permissions:")
        for perm in sorted(menu_permissions):
            print(f"  - {perm}")
        
        # Connect to user_auth_db
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get current admin role permissions
        cur.execute("SELECT id, name, permissions FROM roles WHERE name IN ('admin', 'Admin', 'superuser')")
        role = cur.fetchone()
        
        if not role:
            print("❌ Admin role not found!")
            return
        
        role_id, role_name, current_permissions = role
        print(f"\nFound role: {role_name} (ID: {role_id})")
        print(f"Current permissions: {len(current_permissions)}")
        
        # Combine existing and new permissions
        all_permissions = set(current_permissions)
        all_permissions.update(menu_permissions)
        
        # Add other standard permissions
        all_permissions.update([
            "manage_currencies",
            "access_admin_dashboard",
            "manage_users",
            "manage_system",
            "manage_partners",
            "manage_companies",
            "manage_roles",
            "view_audit_logs"
        ])
        
        # Convert to sorted list
        updated_permissions = sorted(list(all_permissions))
        
        # Update the role
        cur.execute(
            "UPDATE roles SET permissions = %s WHERE id = %s",
            (Json(updated_permissions), role_id)
        )
        
        conn.commit()
        
        print(f"\n✅ Updated {role_name} role with {len(updated_permissions)} permissions!")
        print("\nAll permissions:")
        for perm in updated_permissions:
            print(f"  - {perm}")
        
        print("\n📘 Next steps:")
        print("1. Users need to log out and log back in to get updated permissions")
        print("2. The menu should now be visible to admin users")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error updating admin role: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 Updating admin role with menu permissions...")
    update_admin_role()