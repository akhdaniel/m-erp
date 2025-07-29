import pytest
import json
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.service import Service, ServiceToken
from app.models.user import User
from app.models.role import Role, UserRole
from app.services.service_auth import ServiceAuthService
from app.services.password_service import PasswordService
from app.services.jwt_service import JWTService
from app.core.database import get_db


# Helper function to create admin user with service management permissions
async def create_admin_user_with_service_perms(test_db_session):
    """Create an admin user with service management permissions."""
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
    
    # Create admin role with service management permissions
    admin_role = Role(
        name=f"admin-{unique_suffix}",
        description="Administrator role",
        permissions=["read", "write", "manage_users", "manage_roles", "admin:services"]
    )
    test_db_session.add(admin_role)
    await test_db_session.commit()
    await test_db_session.refresh(admin_role)
    
    # Assign admin role to user
    user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
    test_db_session.add(user_role)
    await test_db_session.commit()
    
    return admin_user


async def create_test_service(test_db_session, service_name=None):
    """Create a test service for testing."""
    import uuid
    if service_name is None:
        service_name = f"test-service-{str(uuid.uuid4())[:8]}"
    
    service, secret = await ServiceAuthService.register_service(
        test_db_session,
        service_name,
        "Test service for testing",
        ["read:users", "validate:tokens"]
    )
    return service, secret


# Service Registration Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_register_service_success(test_db_session):
    """Test successful service registration."""
    admin_user = await create_admin_user_with_service_perms(test_db_session)
    
    # Create admin access token
    admin_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users", "admin:services"]
    )
    
    service_data = {
        "service_name": "inventory-service",
        "service_description": "Inventory management service",
        "allowed_scopes": ["read:users", "validate:tokens"]
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post("/api/services/register", json=service_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 201
    response_data = response.json()
    
    assert response_data["service_name"] == service_data["service_name"]
    assert "service_secret" in response_data
    assert response_data["allowed_scopes"] == service_data["allowed_scopes"]
    assert "service_id" in response_data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_register_service_duplicate_name(test_db_session):
    """Test service registration with duplicate name."""
    admin_user = await create_admin_user_with_service_perms(test_db_session)
    
    # Create existing service
    await create_test_service(test_db_session, "duplicate-service")
    
    # Create admin access token
    admin_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users", "admin:services"]
    )
    
    service_data = {
        "service_name": "duplicate-service",
        "service_description": "Another service with same name",
        "allowed_scopes": ["read:users"]
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post("/api/services/register", json=service_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 400
    response_data = response.json()
    assert "already exists" in response_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_register_service_invalid_scopes(test_db_session):
    """Test service registration with invalid scopes."""
    admin_user = await create_admin_user_with_service_perms(test_db_session)
    
    # Create admin access token
    admin_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users", "admin:services"]
    )
    
    service_data = {
        "service_name": "invalid-scopes-service",
        "service_description": "Service with invalid scopes",
        "allowed_scopes": ["invalid:scope", "another:invalid"]
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post("/api/services/register", json=service_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 400
    response_data = response.json()
    assert "invalid scopes" in response_data["detail"].lower()


# Service Authentication Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_service_token_success(test_db_session):
    """Test successful service token generation."""
    service, secret = await create_test_service(test_db_session)
    
    token_data = {
        "service_name": service.service_name,
        "service_secret": secret,
        "scopes": ["read:users"]
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/services/token", json=token_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"
    assert response_data["expires_in"] > 0
    assert "read:users" in response_data["scopes"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_service_token_invalid_secret(test_db_session):
    """Test service token generation with invalid secret."""
    service, secret = await create_test_service(test_db_session)
    
    token_data = {
        "service_name": service.service_name,
        "service_secret": "invalid-secret",
        "scopes": ["read:users"]
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/services/token", json=token_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 401
    response_data = response.json()
    assert "invalid" in response_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_service_token_nonexistent_service(test_db_session):
    """Test service token generation for nonexistent service."""
    token_data = {
        "service_name": "nonexistent-service",
        "service_secret": "some-secret",
        "scopes": ["read:users"]
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/services/token", json=token_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 401
    response_data = response.json()
    assert "not found" in response_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_service_token_scope_filtering(test_db_session):
    """Test that only allowed scopes are granted."""
    service, secret = await create_test_service(test_db_session)
    
    # Request more scopes than allowed
    token_data = {
        "service_name": service.service_name,
        "service_secret": secret,
        "scopes": ["read:users", "validate:tokens", "admin:users"]  # admin:users not allowed
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/services/token", json=token_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    # Should only get the allowed scopes
    assert "read:users" in response_data["scopes"]
    assert "validate:tokens" in response_data["scopes"]
    assert "admin:users" not in response_data["scopes"]


# Service Token Validation Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_service_token_success(test_db_session):
    """Test successful service token validation."""
    service, secret = await create_test_service(test_db_session)
    
    # Get service token
    service_obj, token, scopes = await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, secret, ["read:users"]
    )
    
    validation_data = {
        "token": token,
        "required_scopes": ["read:users"]
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/services/validate", json=validation_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["valid"] is True
    assert response_data["service_name"] == service.service_name
    assert "read:users" in response_data["scopes"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_service_token_invalid(test_db_session):
    """Test validation of invalid service token."""
    validation_data = {
        "token": "invalid-token",
        "required_scopes": ["read:users"]
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/services/validate", json=validation_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_service_token_insufficient_scopes(test_db_session):
    """Test validation with insufficient scopes."""
    service, secret = await create_test_service(test_db_session)
    
    # Get service token with limited scopes
    service_obj, token, scopes = await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, secret, ["read:users"]
    )
    
    validation_data = {
        "token": token,
        "required_scopes": ["admin:users"]  # Scope not granted
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.post("/api/services/validate", json=validation_data)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 401


# Service Management Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_services(test_db_session):
    """Test listing registered services."""
    admin_user = await create_admin_user_with_service_perms(test_db_session)
    
    # Create some test services
    await create_test_service(test_db_session, "service1")
    await create_test_service(test_db_session, "service2")
    
    # Create admin service token
    admin_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users", "admin:services"]
    )
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get("/api/services/list", headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert "services" in response_data
    assert "total" in response_data
    assert response_data["total"] >= 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_service_info(test_db_session):
    """Test getting service information."""
    admin_user = await create_admin_user_with_service_perms(test_db_session)
    service, secret = await create_test_service(test_db_session)
    
    # Create admin service token
    admin_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users", "admin:services"]
    )
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.get(f"/api/services/{service.id}", headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["service_id"] == service.id
    assert response_data["service_name"] == service.service_name
    assert response_data["is_active"] is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_service_status(test_db_session):
    """Test updating service status."""
    admin_user = await create_admin_user_with_service_perms(test_db_session)
    service, secret = await create_test_service(test_db_session)
    
    # Create admin service token
    admin_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users", "admin:services"]
    )
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post(
            f"/api/services/{service.id}/status?is_active=false", 
            headers=headers
        )
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["service_id"] == service.id
    assert response_data["is_active"] is False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_revoke_service_tokens(test_db_session):
    """Test revoking all service tokens."""
    admin_user = await create_admin_user_with_service_perms(test_db_session)
    service, secret = await create_test_service(test_db_session)
    
    # Create a service token
    await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, secret
    )
    
    # Create admin service token
    admin_token = JWTService.create_access_token(
        admin_user.id, 
        ["read", "write", "manage_users", "admin:services"]
    )
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await client.post(
            f"/api/services/{service.id}/revoke-tokens", 
            headers=headers
        )
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert "revoked" in response_data["message"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_current_service_info(test_db_session):
    """Test getting current service information."""
    service, secret = await create_test_service(test_db_session)
    
    # Get service token
    service_obj, token, scopes = await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, secret
    )
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/api/services/me", headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["service_id"] == service.id
    assert response_data["service_name"] == service.service_name


@pytest.mark.asyncio
@pytest.mark.integration
async def test_service_endpoints_require_permission(test_db_session):
    """Test that service management endpoints require proper permissions."""
    # Create regular user without admin permissions
    user = User(
        email="regular@example.com",
        password_hash=PasswordService.hash_password("password123"),
        first_name="Regular",
        last_name="User"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create access token with regular permissions
    access_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    endpoints = [
        ("POST", "/api/services/register", {"service_name": "test", "service_description": "test", "allowed_scopes": []}),
        ("GET", "/api/services/list", None),
        ("GET", "/api/services/1", None),
        ("POST", "/api/services/1/status?is_active=false", None),
        ("POST", "/api/services/1/revoke-tokens", None),
    ]
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        for method, endpoint, data in endpoints:
            if method == "GET":
                response = await client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await client.post(endpoint, json=data, headers=headers)
            
            assert response.status_code == 403, f"Endpoint {method} {endpoint} should require admin permission"
        
        app.dependency_overrides.clear()