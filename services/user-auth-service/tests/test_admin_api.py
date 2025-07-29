import pytest
import json
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.user import User
from app.models.role import Role, UserRole
from app.services.password_service import PasswordService
from app.services.jwt_service import JWTService
from app.core.database import get_db


# Helper function to create admin user with proper permissions
async def create_admin_user(test_db_session):
    """Create an admin user with manage_users permission."""
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    
    admin_user = User(
        email=f"admin-{unique_suffix}@example.com",
        password_hash=PasswordService.hash_password("AdminPassword123!"),
        first_name="Admin",
        last_name="User"
    )
    test_db_session.add(admin_user)
    await test_db_session.commit()
    await test_db_session.refresh(admin_user)
    
    # Create admin role with manage_users permission
    admin_role = Role(
        name=f"admin-{unique_suffix}",
        description="Administrator role",
        permissions=["read", "write", "manage_users", "manage_roles"]
    )
    test_db_session.add(admin_role)
    await test_db_session.commit()
    await test_db_session.refresh(admin_role)
    
    # Assign admin role to user
    user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
    test_db_session.add(user_role)
    await test_db_session.commit()
    
    return admin_user


async def create_regular_user(test_db_session, email=None):
    """Create a regular user for testing."""
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    
    if email is None:
        email = f"user-{unique_suffix}@example.com"
    
    user = User(
        email=email,
        password_hash=PasswordService.hash_password("UserPassword123!"),
        first_name="Regular",
        last_name="User"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create user role
    role_name = f"user-{unique_suffix}"
    user_role = Role(
        name=role_name,
        description="Regular user role",
        permissions=["read", "write"]
    )
    test_db_session.add(user_role)
    await test_db_session.commit()
    await test_db_session.refresh(user_role)
    
    # Assign user role
    assignment = UserRole(user_id=user.id, role_id=user_role.id)
    test_db_session.add(assignment)
    await test_db_session.commit()
    
    # Add role_name as an attribute to the user for testing
    user.test_role_name = role_name
    return user


# Admin User Listing and Search Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_list_users_success(test_db_session):
    """Test admin can list all users."""
    # Create admin user
    admin_user = await create_admin_user(test_db_session)
    
    # Create some regular users
    user1 = await create_regular_user(test_db_session, "user1@example.com")
    user2 = await create_regular_user(test_db_session, "user2@example.com")
    
    # Create admin access token
    access_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users", "manage_roles"]
    )
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/admin/users", headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert "users" in response_data
    assert "total" in response_data
    assert "page" in response_data
    assert "per_page" in response_data
    assert response_data["total"] >= 3  # admin + 2 regular users
    assert len(response_data["users"]) >= 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_list_users_pagination(test_db_session):
    """Test admin user listing with pagination."""
    # Create admin user
    admin_user = await create_admin_user(test_db_session)
    
    # Create access token
    access_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users"]
    )
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/admin/users?page=1&per_page=2", headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["page"] == 1
    assert response_data["per_page"] == 2
    assert len(response_data["users"]) <= 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_search_users_by_email(test_db_session):
    """Test admin can search users by email."""
    # Create admin user
    admin_user = await create_admin_user(test_db_session)
    
    # Create test users
    user1 = await create_regular_user(test_db_session, "alice@example.com")
    user2 = await create_regular_user(test_db_session, "bob@example.com")
    
    # Create access token
    access_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users"]
    )
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/admin/users?search=alice", headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert len(response_data["users"]) >= 1
    assert any("alice" in user["email"] for user in response_data["users"])


@pytest.mark.asyncio
@pytest.mark.integration  
async def test_admin_list_users_unauthorized(test_db_session):
    """Test non-admin cannot list users."""
    # Create regular user without admin permissions
    user = await create_regular_user(test_db_session)
    
    # Create access token with regular permissions
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/admin/users", headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 403  # Forbidden


@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_get_user_by_id(test_db_session):
    """Test admin can get specific user by ID."""
    # Create admin user
    admin_user = await create_admin_user(test_db_session)
    
    # Create target user
    target_user = await create_regular_user(test_db_session, "target@example.com")
    
    # Create access token
    access_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users"]
    )
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get(f"/api/admin/users/{target_user.id}", headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["id"] == target_user.id
    assert response_data["email"] == target_user.email
    assert "roles" in response_data


# Admin Role Management Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_assign_role_success(test_db_session):
    """Test admin can assign role to user."""
    # Create admin user
    admin_user = await create_admin_user(test_db_session)
    
    # Create target user
    target_user = await create_regular_user(test_db_session, "target@example.com")
    
    # Create moderator role
    mod_role = Role(
        name="moderator",
        description="Moderator role",
        permissions=["read", "write", "moderate"]
    )
    test_db_session.add(mod_role)
    await test_db_session.commit()
    
    # Create access token
    access_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users", "manage_roles"]
    )
    
    assign_data = {
        "user_id": target_user.id,
        "role_name": "moderator"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/admin/assign-role", json=assign_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    assert "success" in response_data["message"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_remove_role_success(test_db_session):
    """Test admin can remove role from user."""
    # Create admin user
    admin_user = await create_admin_user(test_db_session)
    
    # Create target user with user role
    target_user = await create_regular_user(test_db_session, "target@example.com")
    
    # Create access token
    access_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users", "manage_roles"]
    )
    
    remove_data = {
        "user_id": target_user.id,
        "role_name": target_user.test_role_name
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/admin/remove-role", json=remove_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    assert "success" in response_data["message"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_assign_nonexistent_role(test_db_session):
    """Test admin cannot assign non-existent role."""
    # Create admin user
    admin_user = await create_admin_user(test_db_session)
    
    # Create target user
    target_user = await create_regular_user(test_db_session, "target@example.com")
    
    # Create access token
    access_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users", "manage_roles"]
    )
    
    assign_data = {
        "user_id": target_user.id,
        "role_name": "nonexistent_role"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/admin/assign-role", json=assign_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 404
    response_data = response.json()
    assert "not found" in response_data["detail"].lower()


# Admin User Status Management Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_deactivate_user_success(test_db_session):
    """Test admin can deactivate user."""
    # Create admin user
    admin_user = await create_admin_user(test_db_session)
    
    # Create target user
    target_user = await create_regular_user(test_db_session, "target@example.com")
    
    # Create access token
    access_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users"]
    )
    
    status_data = {
        "user_id": target_user.id,
        "is_active": False
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/admin/user-status", json=status_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["is_active"] is False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_activate_user_success(test_db_session):
    """Test admin can activate user."""
    # Create admin user
    admin_user = await create_admin_user(test_db_session)
    
    # Create inactive target user
    target_user = User(
        email="inactive@example.com",
        password_hash=PasswordService.hash_password("password123"),
        first_name="Inactive",
        last_name="User",
        is_active=False
    )
    test_db_session.add(target_user)
    await test_db_session.commit()
    await test_db_session.refresh(target_user)
    
    # Create access token
    access_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users"]
    )
    
    status_data = {
        "user_id": target_user.id,
        "is_active": True
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/admin/user-status", json=status_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["is_active"] is True


# Admin User Creation Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_create_user_success(test_db_session):
    """Test admin can create new user."""
    # Create admin user
    admin_user = await create_admin_user(test_db_session)
    
    # Create a "user" role for assignment
    user_role = Role(
        name="user",
        description="Standard user role",
        permissions=["read", "write"]
    )
    test_db_session.add(user_role)
    await test_db_session.commit()
    
    # Create access token
    access_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users"]
    )
    
    create_data = {
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "first_name": "New",
        "last_name": "User",
        "is_active": True,
        "role_names": ["user"]
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/admin/create-user", json=create_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 201
    response_data = response.json()
    
    assert response_data["email"] == create_data["email"]
    assert response_data["first_name"] == create_data["first_name"]
    assert response_data["last_name"] == create_data["last_name"]
    assert response_data["is_active"] == create_data["is_active"]
    assert "user" in response_data["roles"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_create_user_duplicate_email(test_db_session):
    """Test admin cannot create user with duplicate email."""
    # Create admin user
    admin_user = await create_admin_user(test_db_session)
    
    # Create existing user
    existing_user = await create_regular_user(test_db_session, "existing@example.com")
    
    # Create access token
    access_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users"]
    )
    
    create_data = {
        "email": "existing@example.com",  # Duplicate
        "password": "SecurePassword123!",
        "first_name": "Duplicate",
        "last_name": "User",
        "is_active": True
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/admin/create-user", json=create_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 400
    response_data = response.json()
    assert "already exists" in response_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_endpoints_require_permission(test_db_session):
    """Test that admin endpoints require manage_users permission."""
    # Create regular user without admin permissions
    user = await create_regular_user(test_db_session)
    
    # Create access token with regular permissions
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    endpoints_and_data = [
        ("GET", "/api/admin/users", None),
        ("GET", f"/api/admin/users/{user.id}", None),
        ("POST", "/api/admin/assign-role", {"user_id": 1, "role_name": "admin"}),
        ("POST", "/api/admin/remove-role", {"user_id": 1, "role_name": "user"}),
        ("POST", "/api/admin/user-status", {"user_id": 1, "is_active": False}),
        ("POST", "/api/admin/create-user", {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }),
    ]
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        for method, endpoint, data in endpoints_and_data:
            if method == "GET":
                response = await client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await client.post(endpoint, json=data, headers=headers)
            
            assert response.status_code == 403, f"Endpoint {method} {endpoint} should require admin permission"
        
        app.dependency_overrides.clear()