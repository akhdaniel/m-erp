#!/usr/bin/env python3
"""
Script to create default admin user for XERPIUM system.
Run this script to create a default admin user with full access rights.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_session_factory
from app.core.seed_data import create_default_admin_user, create_default_roles
from sqlalchemy import select
from app.models.user import User
from app.models.role import Role


async def check_existing_admin():
    """Check if admin user already exists."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.email == "admin@m-erp.com")
        )
        admin_user = result.scalar_one_or_none()
        return admin_user is not None


async def list_users():
    """List all users in the system."""
    async with async_session_factory() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("No users found in the system.")
            return
        
        print("\n📋 Current Users in System:")
        print("-" * 50)
        for user in users:
            print(f"👤 {user.full_name}")
            print(f"   📧 Email: {user.email}")
            print(f"   🔓 Active: {'Yes' if user.is_active else 'No'}")
            print(f"   👑 Superuser: {'Yes' if user.is_superuser else 'No'}")
            print(f"   ✅ Verified: {'Yes' if user.is_verified else 'No'}")
            print()


async def create_admin():
    """Create default admin user."""
    print("🚀 XERPIUM Admin User Creation")
    print("=" * 40)
    
    # Check if admin already exists
    if await check_existing_admin():
        print("⚠️  Default admin user already exists!")
        await list_users()
        return
    
    # Create roles first (if they don't exist)
    async with async_session_factory() as session:
        try:
            print("📋 Creating default roles...")
            await create_default_roles(session)
            
            print("👤 Creating default admin user...")
            await create_default_admin_user(session)
            
            print("\n🎉 Success! Default admin user created.")
            print("\n🔐 Login Credentials:")
            print("   📧 Email: admin@m-erp.com")
            print("   🔑 Password: admin123")
            print("\n⚠️  SECURITY WARNING:")
            print("   Please change the default password immediately after first login!")
            print("   This password is for development/testing purposes only.")
            
            print("\n📍 Access the system:")
            print("   🌐 Web Interface: http://localhost:3000")
            print("   🔗 API Documentation: http://localhost:8001/docs")
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            raise


async def main():
    """Main function."""
    try:
        await create_admin()
        await list_users()
    except Exception as e:
        print(f"💥 Script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())