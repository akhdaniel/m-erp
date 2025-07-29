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


# Profile Management API Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_profile_success(test_db_session):
    """Test successful profile update."""
    # Create test user
    password = "TestPassword123!"
    user = User(
        email="profile@example.com",
        password_hash=PasswordService.hash_password(password),
        first_name="Original",
        last_name="Name"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create access token
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    update_data = {
        "first_name": "Updated",
        "last_name": "Profile"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.put("/api/auth/profile", json=update_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["first_name"] == "Updated"
    assert response_data["last_name"] == "Profile"
    assert response_data["email"] == user.email  # Email unchanged


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_profile_partial(test_db_session):
    """Test partial profile update (only first name)."""
    # Create test user
    password = "TestPassword123!"
    user = User(
        email="partial@example.com",
        password_hash=PasswordService.hash_password(password),
        first_name="Original",
        last_name="Name"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create access token
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    update_data = {
        "first_name": "Updated"
        # last_name not provided
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.put("/api/auth/profile", json=update_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["first_name"] == "Updated"
    assert response_data["last_name"] == "Name"  # Unchanged


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_profile_invalid_data(test_db_session):
    """Test profile update with invalid data."""
    # Create test user
    password = "TestPassword123!"
    user = User(
        email="invalid@example.com",
        password_hash=PasswordService.hash_password(password),
        first_name="Test",
        last_name="User"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create access token
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    update_data = {
        "first_name": "",  # Empty string should fail validation
        "last_name": "Valid"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.put("/api/auth/profile", json=update_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_profile_unauthorized(test_db_session):
    """Test profile update without authentication."""
    update_data = {
        "first_name": "Updated",
        "last_name": "Profile"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.put("/api/auth/profile", json=update_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 403  # No authorization header


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_permissions(test_db_session):
    """Test retrieving user permissions."""
    # Create test user
    user = User(
        email="permissions@example.com",
        password_hash=PasswordService.hash_password("password123"),
        first_name="Permissions",
        last_name="User"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create role with permissions
    role = Role(
        name="test_role",
        description="Test role",
        permissions=["read", "write", "manage_users"]
    )
    test_db_session.add(role)
    await test_db_session.commit()
    await test_db_session.refresh(role)
    
    # Assign role to user
    user_role = UserRole(user_id=user.id, role_id=role.id)
    test_db_session.add(user_role)
    await test_db_session.commit()
    
    # Create access token
    access_token = JWTService.create_access_token(user.id, ["read", "write", "manage_users"])
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/auth/permissions", headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["user_id"] == user.id
    assert "read" in response_data["permissions"]
    assert "write" in response_data["permissions"]
    assert "manage_users" in response_data["permissions"]
    assert "test_role" in response_data["roles"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_change_password_success(test_db_session):
    """Test successful password change."""
    # Create test user
    current_password = "CurrentPassword123!"
    user = User(
        email="changepass@example.com",
        password_hash=PasswordService.hash_password(current_password),
        first_name="Change",
        last_name="Password"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create access token
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    change_data = {
        "current_password": current_password,
        "new_password": "NewSecurePassword123!"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/auth/change-password", json=change_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert "success" in response_data["message"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_change_password_wrong_current(test_db_session):
    """Test password change with wrong current password."""
    # Create test user
    current_password = "CurrentPassword123!"
    user = User(
        email="wrongpass@example.com",
        password_hash=PasswordService.hash_password(current_password),
        first_name="Wrong",
        last_name="Password"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create access token
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    change_data = {
        "current_password": "WrongPassword123!",
        "new_password": "NewSecurePassword123!"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/auth/change-password", json=change_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 400
    response_data = response.json()
    assert "detail" in response_data
    assert "current password" in response_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_change_password_weak_new_password(test_db_session):
    """Test password change with weak new password."""
    # Create test user
    current_password = "CurrentPassword123!"
    user = User(
        email="weaknew@example.com",
        password_hash=PasswordService.hash_password(current_password),
        first_name="Weak",
        last_name="New"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create access token
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    change_data = {
        "current_password": current_password,
        "new_password": "weak"  # Too weak
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/auth/change-password", json=change_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
@pytest.mark.integration
async def test_change_email_success(test_db_session):
    """Test successful email change."""
    # Create test user
    password = "TestPassword123!"
    user = User(
        email="oldemail@example.com",
        password_hash=PasswordService.hash_password(password),
        first_name="Change",
        last_name="Email"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create access token
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    change_data = {
        "new_email": "newemail@example.com",
        "password": password
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/auth/change-email", json=change_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["email"] == "newemail@example.com"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_change_email_wrong_password(test_db_session):
    """Test email change with wrong password."""
    # Create test user
    password = "TestPassword123!"
    user = User(
        email="wrongemailpass@example.com",
        password_hash=PasswordService.hash_password(password),
        first_name="Wrong",
        last_name="Email"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create access token
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    change_data = {
        "new_email": "newemail@example.com",
        "password": "WrongPassword123!"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/auth/change-email", json=change_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 400
    response_data = response.json()
    assert "detail" in response_data
    assert "password" in response_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_change_email_duplicate(test_db_session):
    """Test email change to an already existing email."""
    # Create first user
    existing_user = User(
        email="existing@example.com",
        password_hash=PasswordService.hash_password("password123"),
        first_name="Existing",
        last_name="User"
    )
    test_db_session.add(existing_user)
    
    # Create test user
    password = "TestPassword123!"
    user = User(
        email="changeto@example.com",
        password_hash=PasswordService.hash_password(password),
        first_name="Change",
        last_name="To"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create access token
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    change_data = {
        "new_email": "existing@example.com",  # Already exists
        "password": password
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/auth/change-email", json=change_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 400
    response_data = response.json()
    assert "detail" in response_data
    assert "already exists" in response_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_change_email_invalid_format(test_db_session):
    """Test email change with invalid email format."""
    # Create test user
    password = "TestPassword123!"
    user = User(
        email="invalidformat@example.com",
        password_hash=PasswordService.hash_password(password),
        first_name="Invalid",
        last_name="Format"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create access token
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    change_data = {
        "new_email": "invalid-email-format",  # Invalid format
        "password": password
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post("/api/auth/change-email", json=change_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
@pytest.mark.integration
async def test_profile_endpoints_require_authentication(test_db_session):
    """Test that all profile endpoints require authentication."""
    endpoints_and_data = [
        ("PUT", "/api/auth/profile", {"first_name": "Test"}),
        ("GET", "/api/auth/permissions", None),
        ("POST", "/api/auth/change-password", {"current_password": "old", "new_password": "new"}),
        ("POST", "/api/auth/change-email", {"new_email": "test@example.com", "password": "pass"}),
    ]
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        for method, endpoint, data in endpoints_and_data:
            if method == "GET":
                response = await client.get(endpoint)
            elif method == "PUT":
                response = await client.put(endpoint, json=data)
            elif method == "POST":
                response = await client.post(endpoint, json=data)
            
            assert response.status_code == 403, f"Endpoint {method} {endpoint} should require authentication"
        
        app.dependency_overrides.clear()