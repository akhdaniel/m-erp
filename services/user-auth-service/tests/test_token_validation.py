import pytest
import json
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.user import User
from app.models.role import Role, UserRole
from app.services.service_auth import ServiceAuthService
from app.services.password_service import PasswordService
from app.services.jwt_service import JWTService
from app.core.database import get_db


async def create_test_service_with_validation_scope(test_db_session):
    """Create a test service with token validation scope."""
    import uuid
    service_name = f"validation-service-{str(uuid.uuid4())[:8]}"
    
    service, secret = await ServiceAuthService.register_service(
        test_db_session,
        service_name,
        "Token validation test service",
        ["validate:tokens"]
    )
    return service, secret


async def create_test_user_with_permissions(test_db_session, permissions=None):
    """Create a test user with specific permissions."""
    import uuid
    unique_suffix = str(uuid.uuid4())[:8]
    
    if permissions is None:
        permissions = ["read", "write"]
    
    user = User(
        email=f"user-{unique_suffix}@example.com",
        password_hash=PasswordService.hash_password("UserPassword123!"),
        first_name="Test",
        last_name="User"
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Create role with permissions
    role = Role(
        name=f"role-{unique_suffix}",
        description="Test role",
        permissions=permissions
    )
    test_db_session.add(role)
    await test_db_session.commit()
    await test_db_session.refresh(role)
    
    # Assign role to user
    user_role = UserRole(user_id=user.id, role_id=role.id)
    test_db_session.add(user_role)
    await test_db_session.commit()
    
    return user


# User Token Validation Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_user_token_success(test_db_session):
    """Test successful user token validation."""
    # Create test service with validation scope
    service, service_secret = await create_test_service_with_validation_scope(test_db_session)
    
    # Create test user
    user = await create_test_user_with_permissions(test_db_session, ["read", "write"])
    
    # Get service token
    service_obj, service_token, scopes = await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, service_secret, ["validate:tokens"]
    )
    
    # Create user token
    user_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    validation_data = {
        "token": user_token,
        "required_permissions": ["read"]
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {service_token}"}
        response = await client.post("/api/validate/user-token", json=validation_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["valid"] is True
    assert response_data["user_id"] == user.id
    assert response_data["email"] == user.email
    assert "read" in response_data["permissions"]
    assert "write" in response_data["permissions"]
    assert response_data["is_active"] is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_user_token_invalid(test_db_session):
    """Test validation of invalid user token."""
    # Create test service with validation scope
    service, service_secret = await create_test_service_with_validation_scope(test_db_session)
    
    # Get service token
    service_obj, service_token, scopes = await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, service_secret, ["validate:tokens"]
    )
    
    validation_data = {
        "token": "invalid-user-token"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {service_token}"}
        response = await client.post("/api/validate/user-token", json=validation_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_user_token_insufficient_permissions(test_db_session):
    """Test user token validation with insufficient permissions."""
    # Create test service with validation scope
    service, service_secret = await create_test_service_with_validation_scope(test_db_session)
    
    # Create test user with limited permissions
    user = await create_test_user_with_permissions(test_db_session, ["read"])
    
    # Get service token
    service_obj, service_token, scopes = await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, service_secret, ["validate:tokens"]
    )
    
    # Create user token
    user_token = JWTService.create_access_token(user.id, ["read"])
    
    validation_data = {
        "token": user_token,
        "required_permissions": ["write"]  # User doesn't have this permission
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {service_token}"}
        response = await client.post("/api/validate/user-token", json=validation_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 403
    response_data = response.json()
    assert "missing required permissions" in response_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_user_token_nonexistent_user(test_db_session):
    """Test validation of token for nonexistent user."""
    # Create test service with validation scope
    service, service_secret = await create_test_service_with_validation_scope(test_db_session)
    
    # Get service token
    service_obj, service_token, scopes = await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, service_secret, ["validate:tokens"]
    )
    
    # Create user token with nonexistent user ID
    fake_user_token = JWTService.create_access_token(99999, ["read", "write"])
    
    validation_data = {
        "token": fake_user_token
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {service_token}"}
        response = await client.post("/api/validate/user-token", json=validation_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 404


# User Info Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_info_success(test_db_session):
    """Test successful user info retrieval."""
    # Create test service with validation scope
    service, service_secret = await create_test_service_with_validation_scope(test_db_session)
    
    # Create test user
    user = await create_test_user_with_permissions(test_db_session, ["read", "write"])
    
    # Get service token
    service_obj, service_token, scopes = await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, service_secret, ["validate:tokens"]
    )
    
    user_info_data = {
        "user_id": user.id,
        "include_roles": True
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {service_token}"}
        response = await client.post("/api/validate/user-info", json=user_info_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["user_id"] == user.id
    assert response_data["email"] == user.email
    assert response_data["first_name"] == user.first_name
    assert response_data["last_name"] == user.last_name
    assert response_data["is_active"] is True
    assert "read" in response_data["permissions"]
    assert "write" in response_data["permissions"]
    assert response_data["roles"] is not None
    assert len(response_data["roles"]) > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_info_without_roles(test_db_session):
    """Test user info retrieval without role information."""
    # Create test service with validation scope
    service, service_secret = await create_test_service_with_validation_scope(test_db_session)
    
    # Create test user
    user = await create_test_user_with_permissions(test_db_session, ["read"])
    
    # Get service token
    service_obj, service_token, scopes = await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, service_secret, ["validate:tokens"]
    )
    
    user_info_data = {
        "user_id": user.id,
        "include_roles": False
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {service_token}"}
        response = await client.post("/api/validate/user-info", json=user_info_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["user_id"] == user.id
    assert response_data["roles"] is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_info_nonexistent_user(test_db_session):
    """Test user info retrieval for nonexistent user."""
    # Create test service with validation scope
    service, service_secret = await create_test_service_with_validation_scope(test_db_session)
    
    # Get service token
    service_obj, service_token, scopes = await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, service_secret, ["validate:tokens"]
    )
    
    user_info_data = {
        "user_id": 99999,
        "include_roles": False
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {service_token}"}
        response = await client.post("/api/validate/user-info", json=user_info_data, headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 404


# User Permissions Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_permissions_success(test_db_session):
    """Test successful user permissions retrieval."""
    # Create test service with validation scope
    service, service_secret = await create_test_service_with_validation_scope(test_db_session)
    
    # Create test user
    user = await create_test_user_with_permissions(test_db_session, ["read", "write", "manage_users"])
    
    # Get service token
    service_obj, service_token, scopes = await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, service_secret, ["validate:tokens"]
    )
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {service_token}"}
        response = await client.get(f"/api/validate/permissions/{user.id}", headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    permissions = response.json()
    
    assert isinstance(permissions, list)
    assert "read" in permissions
    assert "write" in permissions
    assert "manage_users" in permissions


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_permissions_inactive_user(test_db_session):
    """Test permissions retrieval for inactive user."""
    # Create test service with validation scope
    service, service_secret = await create_test_service_with_validation_scope(test_db_session)
    
    # Create inactive user
    user = User(
        email="inactive@example.com",
        password_hash=PasswordService.hash_password("password123"),
        first_name="Inactive",
        last_name="User",
        is_active=False
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    # Get service token
    service_obj, service_token, scopes = await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, service_secret, ["validate:tokens"]
    )
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {service_token}"}
        response = await client.get(f"/api/validate/permissions/{user.id}", headers=headers)
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 403
    response_data = response.json()
    assert "inactive" in response_data["detail"].lower()


# Health Check Test

@pytest.mark.asyncio
@pytest.mark.integration
async def test_health_check(test_db_session):
    """Test token validation service health check."""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        response = await client.get("/api/validate/health")
        
        app.dependency_overrides.clear()
    
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["status"] == "healthy"
    assert response_data["service"] == "token-validation"
    assert "available_endpoints" in response_data


# Authorization Tests

@pytest.mark.asyncio
@pytest.mark.integration
async def test_validation_endpoints_require_service_auth(test_db_session):
    """Test that validation endpoints require service authentication."""
    # Create test user
    user = await create_test_user_with_permissions(test_db_session, ["read"])
    
    # Create user token (not service token)
    user_token = JWTService.create_access_token(user.id, ["read", "write"])
    
    endpoints_and_data = [
        ("POST", "/api/validate/user-token", {"token": "some-token"}),
        ("POST", "/api/validate/user-info", {"user_id": 1}),
        ("GET", f"/api/validate/permissions/{user.id}", None),
    ]
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {user_token}"}
        
        for method, endpoint, data in endpoints_and_data:
            if method == "GET":
                response = await client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await client.post(endpoint, json=data, headers=headers)
            
            # Should fail because user token is not a service token
            assert response.status_code == 401, f"Endpoint {method} {endpoint} should require service authentication"
        
        app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validation_endpoints_require_validate_scope(test_db_session):
    """Test that validation endpoints require validate:tokens scope."""
    # Create service without validation scope
    service, secret = await ServiceAuthService.register_service(
        test_db_session,
        "no-validation-service",
        "Service without validation scope",
        ["read:users"]  # No validate:tokens scope
    )
    
    # Get service token
    service_obj, service_token, scopes = await ServiceAuthService.authenticate_service(
        test_db_session, service.service_name, secret
    )
    
    endpoints_and_data = [
        ("POST", "/api/validate/user-token", {"token": "some-token"}),
        ("POST", "/api/validate/user-info", {"user_id": 1}),
        ("GET", "/api/validate/permissions/1", None),
    ]
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        app.dependency_overrides[get_db] = lambda: test_db_session
        
        headers = {"Authorization": f"Bearer {service_token}"}
        
        for method, endpoint, data in endpoints_and_data:
            if method == "GET":
                response = await client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await client.post(endpoint, json=data, headers=headers)
            
            # Should fail because service doesn't have validate:tokens scope
            assert response.status_code == 403, f"Endpoint {method} {endpoint} should require validate:tokens scope"
        
        app.dependency_overrides.clear()