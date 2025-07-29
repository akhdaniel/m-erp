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


# Authentication API Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_registration_success(test_db_session):
    """Test successful user registration."""
    registration_data = {
        "email": "newuser@example.com",
        "password": "SecurePass123!",
        "first_name": "New",
        "last_name": "User"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        # Override dependency
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/auth/register", json=registration_data)
        
        # Clean up override
        app.dependency_overrides.clear()
    
    assert response.status_code == 201
    response_data = response.json()
    
    assert "user" in response_data
    assert "access_token" in response_data
    assert "refresh_token" in response_data
    assert response_data["user"]["email"] == registration_data["email"]
    assert response_data["user"]["first_name"] == registration_data["first_name"]
    assert response_data["user"]["last_name"] == registration_data["last_name"]
    assert "password" not in response_data["user"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_registration_duplicate_email(test_db_session):
    """Test user registration with duplicate email address."""
    # Create existing user
    existing_user = User(
        email="existing@example.com",
        password_hash=PasswordService.hash_password("password123"),
        first_name="Existing",
        last_name="User"
    )
    test_db_session.add(existing_user)
    await test_db_session.commit()
    
    registration_data = {
        "email": "existing@example.com",
        "password": "NewPass123!",
        "first_name": "New",
        "last_name": "User"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/auth/register", json=registration_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 400
    response_data = response.json()
    assert "detail" in response_data
    assert "already registered" in response_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_registration_weak_password(test_db_session):
    """Test user registration with weak password."""
    registration_data = {
        "email": "weakpass@example.com",
        "password": "123",  # Too weak
        "first_name": "Weak",
        "last_name": "Password"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/auth/register", json=registration_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 422  # Pydantic validation error
    response_data = response.json()
    assert "detail" in response_data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_registration_invalid_email(test_db_session):
    """Test user registration with invalid email format."""
    registration_data = {
        "email": "invalid-email",
        "password": "SecurePass123!",
        "first_name": "Invalid",
        "last_name": "Email"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/auth/register", json=registration_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_registration_missing_fields(test_db_session):
    """Test user registration with missing required fields."""
    registration_data = {
        "email": "incomplete@example.com",
        # Missing password, first_name, last_name
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/auth/register", json=registration_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_login_success(test_db_session):
    """Test successful user login."""
    # Create test user
    password = "LoginPass123!"
    user = User(
        email="login@example.com",
        password_hash=PasswordService.hash_password(password),
        first_name="Login",
        last_name="User"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    login_data = {
        "email": "login@example.com",
        "password": password
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/auth/login", json=login_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert "user" in response_data
    assert "access_token" in response_data
    assert "refresh_token" in response_data
    assert response_data["user"]["email"] == user.email
    assert "password" not in response_data["user"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_login_invalid_credentials(test_db_session):
    """Test user login with invalid credentials."""
    # Create test user
    user = User(
        email="wrongpass@example.com",
        password_hash=PasswordService.hash_password("correct_password"),
        first_name="Wrong",
        last_name="Password"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    
    login_data = {
        "email": "wrongpass@example.com",
        "password": "wrong_password"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/auth/login", json=login_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 401
    response_data = response.json()
    assert "detail" in response_data
    assert "invalid" in response_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_login_nonexistent_user(test_db_session):
    """Test user login with non-existent email."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "SomePassword123!"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/auth/login", json=login_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 401
    response_data = response.json()
    assert "detail" in response_data
    assert "invalid" in response_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_login_inactive_user(test_db_session):
    """Test login with inactive user account."""
    user = User(
        email="inactive@example.com",
        password_hash=PasswordService.hash_password("password123"),
        first_name="Inactive",
        last_name="User",
        is_active=False
    )
    test_db_session.add(user)
    await test_db_session.commit()
    
    login_data = {
        "email": "inactive@example.com",
        "password": "password123"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/auth/login", json=login_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 401
    response_data = response.json()
    assert "detail" in response_data
    assert "inactive" in response_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_token_refresh_success(test_db_session):
    """Test successful token refresh."""
    # Create test user
    user = User(
        email="refresh@example.com",
        password_hash=PasswordService.hash_password("password123"),
        first_name="Refresh",
        last_name="User"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Login first to get a proper session
    login_data = {
        "email": "refresh@example.com",
        "password": "password123"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        # Login to get tokens
        login_response = await client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200
        login_data_response = login_response.json()
        refresh_token = login_data_response["refresh_token"]
        
        # Now test refresh
        refresh_data = {
            "refresh_token": refresh_token
        }
        
        response = await client.post("/api/auth/refresh", json=refresh_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert "access_token" in response_data
    assert "refresh_token" in response_data
    assert response_data["access_token"] != refresh_token  # New access token


@pytest.mark.asyncio
@pytest.mark.integration
async def test_token_refresh_invalid_token(test_db_session):
    """Test token refresh with invalid refresh token."""
    refresh_data = {
        "refresh_token": "invalid.refresh.token"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/auth/refresh", json=refresh_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 401
    response_data = response.json()
    assert "detail" in response_data
    assert "invalid" in response_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_token_refresh_expired_token(test_db_session):
    """Test token refresh with expired refresh token."""
    # Create test user
    user = User(
        email="expired@example.com",
        password_hash=PasswordService.hash_password("password123"),
        first_name="Expired",
        last_name="User"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create expired refresh token
    expired_token = JWTService.create_refresh_token(
        user.id, 
        expires_delta=timedelta(seconds=-1)
    )
    
    refresh_data = {
        "refresh_token": expired_token
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/auth/refresh", json=refresh_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 401
    response_data = response.json()
    assert "detail" in response_data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_logout_success(test_db_session):
    """Test successful user logout."""
    # Create test user
    user = User(
        email="logout@example.com",
        password_hash=PasswordService.hash_password("password123"),
        first_name="Logout",
        last_name="User"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create valid refresh token
    refresh_token = JWTService.create_refresh_token(user.id)
    
    logout_data = {
        "refresh_token": refresh_token
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/auth/logout", json=logout_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert "logged out" in response_data["message"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_logout_invalid_token(test_db_session):
    """Test logout with invalid refresh token."""
    logout_data = {
        "refresh_token": "invalid.token.here"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/auth/logout", json=logout_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 401
    response_data = response.json()
    assert "detail" in response_data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_protected_endpoint_with_valid_token(test_db_session):
    """Test accessing protected endpoint with valid access token."""
    # Create test user with permissions
    user = User(
        email="protected@example.com",
        password_hash=PasswordService.hash_password("password123"),
        first_name="Protected",
        last_name="User"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create access token
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/auth/me", headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["email"] == user.email


@pytest.mark.asyncio
@pytest.mark.integration
async def test_protected_endpoint_without_token(test_db_session):
    """Test accessing protected endpoint without token."""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.get("/api/auth/me")
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 403  # HTTPBearer returns 403 when no Authorization header


@pytest.mark.asyncio
@pytest.mark.integration
async def test_protected_endpoint_with_invalid_token(test_db_session):
    """Test accessing protected endpoint with invalid token."""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = await client.get("/api/auth/me", headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 401