"""
Seed data for initial database setup.
This module contains functions to create default roles and permissions.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.role import Role


async def create_default_roles(db: AsyncSession) -> None:
  """Create default system roles."""
  
  default_roles = [
    {
      "name": "superuser",
      "description": "Super administrator with full system access",
      "permissions": [
        "manage_users",
        "manage_roles", 
        "manage_system",
        "view_audit_logs",
        "manage_companies",
        "manage_partners",
        "manage_currencies",
        "access_admin_dashboard"
      ]
    },
    {
      "name": "admin",
      "description": "Administrator with user and content management access",
      "permissions": [
        "manage_users",
        "view_users",
        "manage_companies",
        "manage_partners",
        "view_audit_logs",
        "access_admin_dashboard"
      ]
    },
    {
      "name": "manager",
      "description": "Manager with limited administrative access",
      "permissions": [
        "view_users",
        "manage_partners",
        "view_companies",
        "view_reports"
      ]
    },
    {
      "name": "user",
      "description": "Standard user with basic access",
      "permissions": [
        "view_profile",
        "edit_profile",
        "view_partners",
        "view_companies"
      ]
    },
    {
      "name": "readonly",
      "description": "Read-only access for viewing data",
      "permissions": [
        "view_profile",
        "view_partners",
        "view_companies"
      ]
    }
  ]
  
  for role_data in default_roles:
    # Check if role already exists
    existing_role = await db.execute(
      select(Role).where(Role.name == role_data["name"])
    )
    if existing_role.scalar_one_or_none() is None:
      role = Role(
        name=role_data["name"],
        description=role_data["description"],
        permissions=role_data["permissions"]
      )
      db.add(role)
  
  await db.commit()


async def seed_database(db: AsyncSession) -> None:
  """Seed the database with initial data."""
  await create_default_roles(db)


async def seed_initial_data() -> None:
  """Initialize database with seed data using a session."""
  from app.core.database import async_session_factory
  
  async with async_session_factory() as session:
    try:
      await seed_database(session)
      print("✅ Default roles created successfully")
    except Exception as e:
      print(f"⚠️  Seed data warning: {e}")
      # Don't fail if data already exists


# Permission constants for easy reference
class Permissions:
  # User management
  MANAGE_USERS = "manage_users"
  VIEW_USERS = "view_users"
  
  # Role management
  MANAGE_ROLES = "manage_roles"
  
  # System management
  MANAGE_SYSTEM = "manage_system"
  ACCESS_ADMIN_DASHBOARD = "access_admin_dashboard"
  
  # Audit and logs
  VIEW_AUDIT_LOGS = "view_audit_logs"
  
  # Company management
  MANAGE_COMPANIES = "manage_companies"
  VIEW_COMPANIES = "view_companies"
  
  # Partner management
  MANAGE_PARTNERS = "manage_partners"
  VIEW_PARTNERS = "view_partners"
  
  # Currency management
  MANAGE_CURRENCIES = "manage_currencies"
  
  # Profile management
  VIEW_PROFILE = "view_profile"
  EDIT_PROFILE = "edit_profile"
  
  # Reporting
  VIEW_REPORTS = "view_reports"