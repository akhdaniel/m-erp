"""
Seed data for initial database setup.
This module contains functions to create default roles, permissions, and admin user.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.role import Role, UserRole
from app.models.user import User


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
        "access_admin_dashboard",
        # Inventory permissions
        "access_inventory",
        "manage_inventory",
        "manage_products",
        "manage_stock",
        "manage_warehouses",
        "view_inventory_reports",
        # Sales permissions
        "access_sales",
        "manage_sales",
        "manage_quotes",
        "manage_orders",
        "view_sales_reports",
        # Purchase permissions
        "access_purchase",
        "manage_purchase",
        "manage_purchase_orders",
        "manage_suppliers",
        "view_purchase_reports",
        # Accounting permissions
        "access_accounting",
        "manage_accounting",
        "manage_accounts",
        "manage_journals",
        "view_financial_reports"
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
      "name": "inventory_manager",
      "description": "Inventory Manager with full inventory access",
      "permissions": [
        "view_profile",
        "edit_profile",
        "view_partners",
        "view_companies",
        "access_inventory",
        "manage_inventory",
        "manage_products",
        "manage_stock",
        "manage_warehouses",
        "view_inventory_reports"
      ]
    },
    {
      "name": "inventory_user",
      "description": "Inventory User with basic inventory access",
      "permissions": [
        "view_profile",
        "edit_profile",
        "view_partners",
        "view_companies",
        "access_inventory",
        "view_products",
        "view_stock",
        "view_warehouses"
      ]
    },
    {
      "name": "sales_manager",
      "description": "Sales Manager with full sales access",
      "permissions": [
        "view_profile",
        "edit_profile",
        "view_partners",
        "manage_partners",
        "view_companies",
        "access_sales",
        "manage_sales",
        "manage_quotes",
        "manage_orders",
        "view_sales_reports",
        "access_inventory",
        "view_products",
        "view_stock"
      ]
    },
    {
      "name": "sales_user",
      "description": "Sales User with basic sales access",
      "permissions": [
        "view_profile",
        "edit_profile",
        "view_partners",
        "view_companies",
        "access_sales",
        "view_quotes",
        "view_orders",
        "access_inventory",
        "view_products",
        "view_stock"
      ]
    },
    {
      "name": "purchase_manager",
      "description": "Purchase Manager with full purchase access",
      "permissions": [
        "view_profile",
        "edit_profile",
        "view_partners",
        "manage_partners",
        "view_companies",
        "access_purchase",
        "manage_purchase",
        "manage_purchase_orders",
        "manage_suppliers",
        "view_purchase_reports",
        "access_inventory",
        "view_products",
        "view_stock"
      ]
    },
    {
      "name": "purchase_user",
      "description": "Purchase User with basic purchase access",
      "permissions": [
        "view_profile",
        "edit_profile",
        "view_partners",
        "view_companies",
        "access_purchase",
        "view_purchase_orders",
        "view_suppliers",
        "access_inventory",
        "view_products",
        "view_stock"
      ]
    },
    {
      "name": "accountant",
      "description": "Accountant with full accounting access",
      "permissions": [
        "view_profile",
        "edit_profile",
        "view_partners",
        "view_companies",
        "access_accounting",
        "manage_accounting",
        "manage_accounts",
        "manage_journals",
        "view_financial_reports",
        "view_sales_reports",
        "view_purchase_reports",
        "view_inventory_reports"
      ]
    },
    {
      "name": "manager",
      "description": "Manager with limited administrative access",
      "permissions": [
        "view_users",
        "manage_partners",
        "view_companies",
        "view_reports",
        "access_inventory",
        "view_inventory_reports",
        "access_sales",
        "view_sales_reports",
        "access_purchase",
        "view_purchase_reports"
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


async def create_default_admin_user(db: AsyncSession) -> None:
  """Create default admin user with full access."""
  from app.services.password_service import PasswordService
  
  # Check if admin user already exists
  existing_admin = await db.execute(
    select(User).where(User.email == "admin@m-erp.com")
  )
  if existing_admin.scalar_one_or_none() is not None:
    print("✅ Default admin user already exists")
    return
  
  # Create password service instance
  password_service = PasswordService()
  
  # Hash the default password
  default_password = "admin123"
  password_hash = password_service.hash_password(default_password)
  
  # Create admin user
  admin_user = User(
    email="admin@m-erp.com",
    password_hash=password_hash,
    first_name="System",
    last_name="Administrator",
    is_active=True,
    is_verified=True,
    is_superuser=True
  )
  
  db.add(admin_user)
  await db.flush()  # Get the user ID
  
  # Get superuser role
  superuser_role = await db.execute(
    select(Role).where(Role.name == "superuser")
  )
  role = superuser_role.scalar_one_or_none()
  
  if role:
    # Assign superuser role to admin
    user_role = UserRole(
      user_id=admin_user.id,
      role_id=role.id,
      assigned_by=None  # System assignment
    )
    db.add(user_role)
  
  await db.commit()
  
  print("✅ Default admin user created successfully")
  print("   📧 Email: admin@m-erp.com")
  print("   🔑 Password: admin123")
  print("   ⚠️  IMPORTANT: Change this password immediately in production!")


async def seed_database(db: AsyncSession) -> None:
  """Seed the database with initial data."""
  await create_default_roles(db)
  await create_default_admin_user(db)


async def seed_initial_data() -> None:
  """Initialize database with seed data using a session."""
  from app.core.database import async_session_factory
  
  async with async_session_factory() as session:
    try:
      await seed_database(session)
      print("✅ Database initialization completed successfully")
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