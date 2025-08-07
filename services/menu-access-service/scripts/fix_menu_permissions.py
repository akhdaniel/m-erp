#!/usr/bin/env python3
"""
Fix menu permissions to allow some menus to be public or ensure proper admin access.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import psycopg2

# Database configuration
DATABASE_URL = "postgresql://merp_user:merp_password@localhost:5432/menu_access_db"

def fix_menu_permissions():
    """Make dashboard and some basic menus public (no permission required)"""
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Make dashboard menu public (remove permission requirement)
        print("Making dashboard menu public...")
        result = session.execute(
            text("""
                UPDATE menus 
                SET required_permission = NULL 
                WHERE code IN ('dashboard', 'home')
                RETURNING id, name, code
            """)
        )
        session.commit()
        
        updated_menus = result.fetchall()
        for menu in updated_menus:
            print(f"  - Made public: {menu.name} ({menu.code})")
        
        # Also ensure admin role has all the required permissions
        print("\nChecking admin role permissions...")
        
        # First, get the admin role ID
        admin_role = session.execute(
            text("SELECT id FROM roles WHERE name = 'admin' OR name = 'Admin'")
        ).fetchone()
        
        if admin_role:
            print(f"Found admin role with ID: {admin_role.id}")
            
            # Get all unique permissions required by menus
            menu_permissions = session.execute(
                text("""
                    SELECT DISTINCT required_permission 
                    FROM menus 
                    WHERE required_permission IS NOT NULL
                """)
            ).fetchall()
            
            print(f"Found {len(menu_permissions)} unique menu permissions")
            
            # Ensure admin role has all these permissions
            for perm in menu_permissions:
                permission_code = perm.required_permission
                
                # Check if permission exists
                existing_perm = session.execute(
                    text("SELECT id FROM permissions WHERE code = :code"),
                    {"code": permission_code}
                ).fetchone()
                
                if not existing_perm:
                    # Create the permission if it doesn't exist
                    session.execute(
                        text("""
                            INSERT INTO permissions (code, name, description, category)
                            VALUES (:code, :name, :description, :category)
                            ON CONFLICT (code) DO NOTHING
                        """),
                        {
                            "code": permission_code,
                            "name": permission_code.replace('_', ' ').title(),
                            "description": f"Permission to {permission_code.replace('_', ' ')}",
                            "category": "menu_access"
                        }
                    )
                    session.commit()
                    
                    existing_perm = session.execute(
                        text("SELECT id FROM permissions WHERE code = :code"),
                        {"code": permission_code}
                    ).fetchone()
                    print(f"  - Created permission: {permission_code}")
                
                # Add permission to admin role if not already present
                if existing_perm:
                    session.execute(
                        text("""
                            INSERT INTO role_permissions (role_id, permission_id)
                            VALUES (:role_id, :permission_id)
                            ON CONFLICT DO NOTHING
                        """),
                        {
                            "role_id": admin_role.id,
                            "permission_id": existing_perm.id
                        }
                    )
            
            session.commit()
            print("Admin role permissions updated successfully!")
        else:
            print("Admin role not found!")
        
        # Show current menu status
        print("\nCurrent menu status:")
        menus = session.execute(
            text("""
                SELECT name, code, required_permission, is_visible 
                FROM menus 
                ORDER BY sequence, name
            """)
        ).fetchall()
        
        for menu in menus:
            perm_status = "PUBLIC" if menu.required_permission is None else f"Requires: {menu.required_permission}"
            visible = "✓" if menu.is_visible else "✗"
            print(f"  [{visible}] {menu.name} ({menu.code}) - {perm_status}")
        
        print("\n✅ Menu permissions fixed successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error fixing menu permissions: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    fix_menu_permissions()