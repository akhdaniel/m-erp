#!/usr/bin/env python3
"""
Script to create admin@example.com user for testing.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import async_session_factory
from app.models.user import User
from app.models.role import Role, UserRole
from app.services.password_service import PasswordService


async def create_example_admin():
    """Create admin@example.com user with Inventory Manager and User roles."""
    async with async_session_factory() as session:
        # Check if user already exists
        stmt = select(User).where(User.email == "admin@example.com")
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("✅ User admin@example.com already exists")
            return
        
        # Create the user
        password_hash = PasswordService.hash_password("admin123")
        admin_user = User(
            email="admin@example.com",
            password_hash=password_hash,
            first_name="Example",
            last_name="Admin",
            is_active=True,
            is_verified=True,
            is_superuser=False,
            failed_login_attempts=0
        )
        
        session.add(admin_user)
        await session.flush()
        
        # Get Inventory Manager and User roles
        inventory_manager_stmt = select(Role).where(Role.name == "inventory_manager")
        inventory_user_stmt = select(Role).where(Role.name == "inventory_user")
        
        inventory_manager_result = await session.execute(inventory_manager_stmt)
        inventory_user_result = await session.execute(inventory_user_stmt)
        
        inventory_manager_role = inventory_manager_result.scalar_one_or_none()
        inventory_user_role = inventory_user_result.scalar_one_or_none()
        
        # Assign roles
        if inventory_manager_role:
            user_role_manager = UserRole(
                user_id=admin_user.id,
                role_id=inventory_manager_role.id
            )
            session.add(user_role_manager)
            print(f"✅ Assigned Inventory Manager role")
        
        if inventory_user_role:
            user_role_user = UserRole(
                user_id=admin_user.id,
                role_id=inventory_user_role.id
            )
            session.add(user_role_user)
            print(f"✅ Assigned Inventory User role")
        
        await session.commit()
        
        print(f"\n🎉 User created successfully!")
        print(f"📧 Email: admin@example.com")
        print(f"🔑 Password: admin123")
        print(f"👤 Roles: Inventory Manager, Inventory User")


async def main():
    """Main function."""
    try:
        await create_example_admin()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())