#!/usr/bin/env python3
"""
Script to assign menu permissions to admin role.
"""

import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, and_

# Add menu-access-service to Python path
sys.path.insert(0, '/app')

from app.models.permission import Permission
from app.models.role import Role, role_permissions

# Database configuration
DATABASE_URL = "postgresql+asyncpg://postgres:password@postgres:5432/menu_access_db"
USER_AUTH_DB_URL = "postgresql+asyncpg://postgres:password@postgres:5432/user_auth_db"

# Create engines for both databases
menu_engine = create_async_engine(DATABASE_URL)
auth_engine = create_async_engine(USER_AUTH_DB_URL)

MenuSession = async_sessionmaker(menu_engine, expire_on_commit=False)
AuthSession = async_sessionmaker(auth_engine, expire_on_commit=False)

async def assign_permissions_to_admin():
    """Assign all menu permissions to admin role in user_auth_db."""
    # First, get all permissions from menu_access_db
    async with MenuSession() as menu_session:
        result = await menu_session.execute(
            select(Permission)
        )
        menu_permissions = result.scalars().all()
        
        print(f"Found {len(menu_permissions)} permissions in menu_access_db:")
        for perm in menu_permissions:
            print(f"  - {perm.code}: {perm.name}")
    
    # Now work with user_auth_db
    async with AuthSession() as auth_session:
        # First, ensure all permissions exist in user_auth_db
        for menu_perm in menu_permissions:
            # Check if permission exists
            result = await auth_session.execute(
                select(Permission).where(Permission.code == menu_perm.code)
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                # Create permission in user_auth_db
                new_perm = Permission(
                    code=menu_perm.code,
                    name=menu_perm.name,
                    description=menu_perm.description,
                    category=menu_perm.category,
                    action=menu_perm.action
                )
                auth_session.add(new_perm)
                print(f"✅ Created permission: {menu_perm.code}")
            else:
                print(f"ℹ️  Permission already exists: {menu_perm.code}")
        
        await auth_session.commit()
        
        # Get the superuser/admin role
        result = await auth_session.execute(
            select(Role).where(Role.name.in_(["superuser", "admin", "Admin"]))
        )
        admin_role = result.scalar_one_or_none()
        
        if not admin_role:
            print("❌ Admin role not found!")
            return
        
        print(f"\nFound admin role: {admin_role.name} (ID: {admin_role.id})")
        
        # Get all permissions again (now they exist in user_auth_db)
        result = await auth_session.execute(
            select(Permission)
        )
        all_permissions = result.scalars().all()
        
        # Assign all permissions to admin role
        for perm in all_permissions:
            # Check if already assigned
            result = await auth_session.execute(
                select(role_permissions).where(
                    and_(
                        role_permissions.c.role_id == admin_role.id,
                        role_permissions.c.permission_id == perm.id
                    )
                )
            )
            existing = result.first()
            
            if not existing:
                # Assign permission to role
                await auth_session.execute(
                    role_permissions.insert().values(
                        role_id=admin_role.id,
                        permission_id=perm.id
                    )
                )
                print(f"✅ Assigned {perm.code} to {admin_role.name} role")
            else:
                print(f"ℹ️  {perm.code} already assigned to {admin_role.name} role")
        
        await auth_session.commit()
        print(f"\n✅ Successfully assigned all permissions to {admin_role.name} role!")
        print("\n📘 Next steps:")
        print("1. Users need to log out and log back in to get updated permissions")
        print("2. The menu should now be visible to admin users")

async def main():
    """Main function."""
    print("🔧 Assigning menu permissions to admin role...")
    try:
        await assign_permissions_to_admin()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())