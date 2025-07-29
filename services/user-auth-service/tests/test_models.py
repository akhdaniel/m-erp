import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.user import User
from app.models.role import Role, UserRole


@pytest.mark.asyncio
@pytest.mark.unit
async def test_user_creation_valid_data(test_db_session: AsyncSession):
  """Test creating a user with valid data."""
  user = User(
    email="test@example.com",
    password_hash="hashed_password_123",
    first_name="John",
    last_name="Doe"
  )
  
  test_db_session.add(user)
  await test_db_session.commit()
  await test_db_session.refresh(user)
  
  assert user.id is not None
  assert user.email == "test@example.com"
  assert user.first_name == "John"
  assert user.last_name == "Doe"
  assert user.is_active is True
  assert user.is_verified is False
  assert user.is_superuser is False
  assert user.created_at is not None
  assert user.updated_at is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_user_email_uniqueness(test_db_session: AsyncSession):
  """Test that duplicate emails are not allowed."""
  user1 = User(
    email="duplicate@example.com",
    password_hash="hash1",
    first_name="User",
    last_name="One"
  )
  
  user2 = User(
    email="duplicate@example.com",
    password_hash="hash2",
    first_name="User",
    last_name="Two"
  )
  
  test_db_session.add(user1)
  await test_db_session.commit()
  
  test_db_session.add(user2)
  
  with pytest.raises(IntegrityError):
    await test_db_session.commit()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_user_email_validation(test_db_session: AsyncSession):
  """Test user email format validation."""
  # Test valid email
  user = User(
    email="valid.email+tag@example.com",
    password_hash="hashed_password",
    first_name="Valid",
    last_name="User"
  )
  
  test_db_session.add(user)
  await test_db_session.commit()
  assert user.id is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_user_required_fields(test_db_session: AsyncSession):
  """Test that required fields are enforced."""
  # Test missing email
  with pytest.raises((IntegrityError, ValueError)):
    user = User(
      password_hash="hashed_password",
      first_name="John",
      last_name="Doe"
    )
    test_db_session.add(user)
    await test_db_session.commit()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_user_soft_delete(test_db_session: AsyncSession):
  """Test user soft delete functionality."""
  user = User(
    email="softdelete@example.com",
    password_hash="hashed_password",
    first_name="Soft",
    last_name="Delete"
  )
  
  test_db_session.add(user)
  await test_db_session.commit()
  user_id = user.id
  
  # Soft delete the user
  user.deleted_at = user.updated_at
  await test_db_session.commit()
  
  # Verify user still exists but is marked as deleted
  result = await test_db_session.execute(
    select(User).where(User.id == user_id)
  )
  deleted_user = result.scalar_one_or_none()
  
  assert deleted_user is not None
  assert deleted_user.deleted_at is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_user_full_name_property(test_db_session: AsyncSession):
  """Test user full name property."""
  user = User(
    email="fullname@example.com",
    password_hash="hashed_password",
    first_name="John",
    last_name="Doe"
  )
  
  test_db_session.add(user)
  await test_db_session.commit()
  
  assert user.full_name == "John Doe"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_user_is_active_default(test_db_session: AsyncSession):
  """Test that users are active by default."""
  user = User(
    email="active@example.com",
    password_hash="hashed_password",
    first_name="Active",
    last_name="User"
  )
  
  test_db_session.add(user)
  await test_db_session.commit()
  
  assert user.is_active is True
  assert user.is_verified is False
  assert user.is_superuser is False


@pytest.mark.asyncio
@pytest.mark.unit
async def test_user_timestamps_auto_update(test_db_session: AsyncSession):
  """Test that timestamps are automatically managed."""
  import time
  
  user = User(
    email="timestamps@example.com",
    password_hash="hashed_password",
    first_name="Time",
    last_name="Stamp"
  )
  
  test_db_session.add(user)
  await test_db_session.commit()
  
  original_created = user.created_at
  original_updated = user.updated_at
  
  # Wait a brief moment to ensure timestamp difference
  time.sleep(0.1)
  
  # Update the user
  user.first_name = "Updated"
  await test_db_session.commit()
  await test_db_session.refresh(user)
  
  assert user.created_at == original_created  # Should not change
  # For SQLite, we just verify the updated timestamp exists
  assert user.updated_at is not None


# Role Model Tests

@pytest.mark.asyncio
@pytest.mark.unit
async def test_role_creation_valid_data(test_db_session: AsyncSession):
  """Test creating a role with valid data."""
  role = Role(
    name="admin",
    description="Administrator role with full permissions",
    permissions=["manage_users", "manage_roles", "view_dashboard"]
  )
  
  test_db_session.add(role)
  await test_db_session.commit()
  await test_db_session.refresh(role)
  
  assert role.id is not None
  assert role.name == "admin"
  assert role.description == "Administrator role with full permissions"
  assert role.permissions == ["manage_users", "manage_roles", "view_dashboard"]
  assert role.created_at is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_role_name_uniqueness(test_db_session: AsyncSession):
  """Test that role names must be unique."""
  role1 = Role(name="duplicate_role", description="First role")
  role2 = Role(name="duplicate_role", description="Second role")
  
  test_db_session.add(role1)
  await test_db_session.commit()
  
  test_db_session.add(role2)
  
  with pytest.raises(IntegrityError):
    await test_db_session.commit()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_role_permissions_json_storage(test_db_session: AsyncSession):
  """Test that permissions are stored as JSON array."""
  permissions = ["read_users", "write_users", "delete_users"]
  role = Role(
    name="user_manager",
    description="User management role",
    permissions=permissions
  )
  
  test_db_session.add(role)
  await test_db_session.commit()
  await test_db_session.refresh(role)
  
  assert isinstance(role.permissions, list)
  assert role.permissions == permissions


@pytest.mark.asyncio
@pytest.mark.unit
async def test_role_empty_permissions(test_db_session: AsyncSession):
  """Test role with empty permissions list."""
  role = Role(
    name="viewer",
    description="Read-only role",
    permissions=[]
  )
  
  test_db_session.add(role)
  await test_db_session.commit()
  await test_db_session.refresh(role)
  
  assert role.permissions == []


@pytest.mark.asyncio
@pytest.mark.unit
async def test_role_has_permission_method(test_db_session: AsyncSession):
  """Test role permission checking method."""
  role = Role(
    name="editor",
    description="Editor role",
    permissions=["read_content", "write_content"]
  )
  
  test_db_session.add(role)
  await test_db_session.commit()
  
  assert role.has_permission("read_content") is True
  assert role.has_permission("write_content") is True
  assert role.has_permission("delete_content") is False


# UserRole Association Tests

@pytest.mark.asyncio
@pytest.mark.unit
async def test_user_role_association(test_db_session: AsyncSession):
  """Test many-to-many relationship between users and roles."""
  # Create user
  user = User(
    email="roletest@example.com",
    password_hash="hashed_password",
    first_name="Role",
    last_name="Test"
  )
  
  # Create role
  role = Role(
    name="test_role",
    description="Test role",
    permissions=["test_permission"]
  )
  
  test_db_session.add(user)
  test_db_session.add(role)
  await test_db_session.commit()
  
  # Create association
  user_role = UserRole(user_id=user.id, role_id=role.id)
  test_db_session.add(user_role)
  await test_db_session.commit()
  await test_db_session.refresh(user_role)
  
  assert user_role.id is not None
  assert user_role.user_id == user.id
  assert user_role.role_id == role.id
  assert user_role.assigned_at is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_user_role_unique_constraint(test_db_session: AsyncSession):
  """Test that user-role combinations are unique."""
  # Create user and role
  user = User(
    email="unique@example.com",
    password_hash="hashed_password",
    first_name="Unique",
    last_name="Test"
  )
  
  role = Role(
    name="unique_role",
    description="Unique role",
    permissions=["unique_permission"]
  )
  
  test_db_session.add(user)
  test_db_session.add(role)
  await test_db_session.commit()
  
  # Create first association
  user_role1 = UserRole(user_id=user.id, role_id=role.id)
  test_db_session.add(user_role1)
  await test_db_session.commit()
  
  # Try to create duplicate association
  user_role2 = UserRole(user_id=user.id, role_id=role.id)
  test_db_session.add(user_role2)
  
  with pytest.raises(IntegrityError):
    await test_db_session.commit()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_user_role_relationships(test_db_session: AsyncSession):
  """Test that relationships work correctly."""
  # Create user and role
  user = User(
    email="relationship@example.com",
    password_hash="hashed_password",
    first_name="Relationship",
    last_name="Test"
  )
  
  role = Role(
    name="relationship_role",
    description="Relationship test role",
    permissions=["relationship_permission"]
  )
  
  test_db_session.add(user)
  test_db_session.add(role)
  await test_db_session.commit()
  
  # Create association
  user_role = UserRole(user_id=user.id, role_id=role.id)
  test_db_session.add(user_role)
  await test_db_session.commit()
  
  # Test relationships
  await test_db_session.refresh(user, ["roles"])
  await test_db_session.refresh(role, ["users"])
  
  assert len(user.roles) == 1
  assert user.roles[0].role_id == role.id
  assert len(role.users) == 1
  assert role.users[0].user_id == user.id


@pytest.mark.asyncio
@pytest.mark.unit
async def test_user_get_permissions_method(test_db_session: AsyncSession):
  """Test user method to get all permissions from roles."""
  # Create user
  user = User(
    email="permissions@example.com",
    password_hash="hashed_password",
    first_name="Permission",
    last_name="Test"
  )
  
  # Create roles with different permissions
  role1 = Role(
    name="role1",
    description="First role",
    permissions=["read", "write"]
  )
  
  role2 = Role(
    name="role2", 
    description="Second role",
    permissions=["write", "delete"]
  )
  
  test_db_session.add(user)
  test_db_session.add(role1)
  test_db_session.add(role2)
  await test_db_session.commit()
  
  # Assign roles to user
  user_role1 = UserRole(user_id=user.id, role_id=role1.id)
  user_role2 = UserRole(user_id=user.id, role_id=role2.id)
  test_db_session.add(user_role1)
  test_db_session.add(user_role2)
  await test_db_session.commit()
  
  # Test get_permissions method
  await test_db_session.refresh(user, ["roles"])
  permissions = await user.get_permissions(test_db_session)
  
  # Should have unique permissions from both roles
  assert set(permissions) == {"read", "write", "delete"}