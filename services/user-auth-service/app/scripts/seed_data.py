"""
Script to seed initial data for production deployment.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.role import Role, Permission


async def seed_initial_data(db: AsyncSession):
    """Seed initial roles and permissions for production."""
    
    # Check if roles already exist
    stmt = select(Role).where(Role.name == "superuser")
    result = await db.execute(stmt)
    existing_role = result.scalar_one_or_none()
    
    if existing_role:
        print("✅ Initial data already exists, skipping seeding")
        return
    
    print("🌱 Seeding initial roles and permissions...")
    
    # Define roles and their permissions
    roles_data = [
        {
            "name": "superuser",
            "description": "Super administrator with full system access",
            "permissions": [
                "manage_users", "manage_roles", "manage_services", "view_audit_logs",
                "manage_system", "manage_security", "view_metrics", "manage_backups"
            ]
        },
        {
            "name": "admin",
            "description": "Administrator with user and service management access",
            "permissions": [
                "manage_users", "manage_roles", "view_audit_logs", "manage_services"
            ]
        },
        {
            "name": "manager",
            "description": "Manager with limited administrative access",
            "permissions": [
                "view_users", "manage_own_team", "view_audit_logs"
            ]
        },
        {
            "name": "user",
            "description": "Standard user with basic access",
            "permissions": [
                "view_profile", "edit_profile", "change_password"
            ]
        },
        {
            "name": "readonly",
            "description": "Read-only access for monitoring and reporting",
            "permissions": [
                "view_profile", "view_public_data"
            ]
        }
    ]
    
    # Create roles
    for role_data in roles_data:
        role = Role(
            name=role_data["name"],
            description=role_data["description"],
            permissions=role_data["permissions"]
        )
        db.add(role)
    
    await db.commit()
    print("✅ Default roles created successfully")


if __name__ == "__main__":
    # This can be run standalone for testing
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from app.core.database import get_db
    
    async def main():
        async for db in get_db():
            await seed_initial_data(db)
            break
    
    asyncio.run(main())