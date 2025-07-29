"""
Tests for auth service client integration.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx
from fastapi import HTTPException

from app.services.auth_client import AuthClient, AuthServiceError


@pytest.fixture
def auth_client():
    """Create AuthClient instance for testing."""
    return AuthClient(auth_service_url="http://test-auth-service:8000")


@pytest.mark.unit
async def test_auth_client_initialization(auth_client):
    """Test AuthClient initialization."""
    assert auth_client.auth_service_url == "http://test-auth-service:8000"
    assert auth_client.service_token is None
    assert auth_client.timeout == 30.0


@pytest.mark.unit
async def test_validate_user_token_success(auth_client):
    """Test successful user token validation."""
    # Mock successful response
    mock_response = {
        "valid": True,
        "user_id": 123,
        "email": "test@example.com",
        "permissions": ["read_users", "manage_profile"],
        "is_active": True
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value=mock_response)
        )
        
        result = await auth_client.validate_user_token("test_token_123")
        
        assert result is not None
        assert result["valid"] is True
        assert result["user_id"] == 123
        assert result["email"] == "test@example.com"
        assert "read_users" in result["permissions"]
        assert result["is_active"] is True
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "/api/validate/user-token" in str(call_args)


@pytest.mark.unit
async def test_validate_user_token_invalid(auth_client):
    """Test validation of invalid user token."""
    mock_response = {
        "valid": False,
        "user_id": 0,
        "email": "",
        "permissions": [],
        "is_active": False
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value=mock_response)
        )
        
        result = await auth_client.validate_user_token("invalid_token")
        
        assert result is not None
        assert result["valid"] is False
        assert result["user_id"] == 0


@pytest.mark.unit
async def test_validate_user_token_auth_service_error(auth_client):
    """Test handling of auth service errors during token validation."""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock(
            status_code=500,
            text="Internal Server Error"
        )
        
        with pytest.raises(AuthServiceError) as exc_info:
            await auth_client.validate_user_token("test_token")
        
        assert "Auth service error" in str(exc_info.value)
        assert "500" in str(exc_info.value)


@pytest.mark.unit
async def test_validate_user_token_network_error(auth_client):
    """Test handling of network errors during token validation."""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.side_effect = httpx.RequestError("Connection failed")
        
        with pytest.raises(AuthServiceError) as exc_info:
            await auth_client.validate_user_token("test_token")
        
        assert "Failed to connect to auth service" in str(exc_info.value)


@pytest.mark.unit
async def test_get_user_info_success(auth_client):
    """Test successful user info retrieval."""
    mock_response = {
        "user_id": 456,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": True
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value=mock_response)
        )
        
        result = await auth_client.get_user_info(456)
        
        assert result is not None
        assert result["user_id"] == 456
        assert result["email"] == "user@example.com"
        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["is_active"] is True


@pytest.mark.unit
async def test_get_user_info_not_found(auth_client):
    """Test user info retrieval for non-existent user."""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock(
            status_code=404,
            text="User not found"
        )
        
        with pytest.raises(AuthServiceError) as exc_info:
            await auth_client.get_user_info(999999)
        
        assert "User not found" in str(exc_info.value) or "404" in str(exc_info.value)


@pytest.mark.unit
async def test_get_user_companies_success(auth_client):
    """Test successful retrieval of user's companies."""
    mock_response = {
        "companies": [
            {
                "company_id": 1,
                "company_name": "Company A",
                "role": "admin",
                "is_default": True
            },
            {
                "company_id": 2,
                "company_name": "Company B", 
                "role": "user",
                "is_default": False
            }
        ]
    }
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = Mock(
            status_code=200,
            json=Mock(return_value=mock_response)
        )
        
        result = await auth_client.get_user_companies(123)
        
        assert result is not None
        assert "companies" in result
        assert len(result["companies"]) == 2
        assert result["companies"][0]["company_id"] == 1
        assert result["companies"][0]["is_default"] is True


@pytest.mark.unit
async def test_authenticate_service_success(auth_client):
    """Test successful service authentication."""
    mock_response = {
        "access_token": "service_token_123",
        "token_type": "bearer",
        "expires_in": 3600
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value=mock_response)
        )
        
        result = await auth_client.authenticate_service("company-partner-service", "secret_key")
        
        assert result is not None
        assert result["access_token"] == "service_token_123"
        assert result["token_type"] == "bearer"
        assert result["expires_in"] == 3600
        
        # Verify service token is stored
        assert auth_client.service_token == "service_token_123"


@pytest.mark.unit
async def test_authenticate_service_invalid_credentials(auth_client):
    """Test service authentication with invalid credentials."""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock(
            status_code=401,
            text="Invalid credentials"
        )
        
        with pytest.raises(AuthServiceError) as exc_info:
            await auth_client.authenticate_service("invalid-service", "wrong_key")
        
        assert "Invalid credentials" in str(exc_info.value) or "401" in str(exc_info.value)


@pytest.mark.unit
async def test_service_headers_without_token(auth_client):
    """Test service headers when no service token is set."""
    headers = auth_client._get_service_headers()
    
    assert "Authorization" not in headers
    assert headers["Content-Type"] == "application/json"


@pytest.mark.unit
async def test_service_headers_with_token(auth_client):
    """Test service headers when service token is set."""
    auth_client.service_token = "test_service_token"
    
    headers = auth_client._get_service_headers()
    
    assert headers["Authorization"] == "Bearer test_service_token"
    assert headers["Content-Type"] == "application/json"


@pytest.mark.unit
async def test_validate_company_access_success(auth_client):
    """Test successful company access validation."""
    mock_response = {
        "has_access": True,
        "role": "admin",
        "permissions": ["manage_partners", "view_data"]
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value=mock_response)
        )
        
        result = await auth_client.validate_company_access(123, 1)
        
        assert result is not None
        assert result["has_access"] is True
        assert result["role"] == "admin"
        assert "manage_partners" in result["permissions"]


@pytest.mark.unit
async def test_validate_company_access_denied(auth_client):
    """Test company access validation when access is denied."""
    mock_response = {
        "has_access": False,
        "role": None,
        "permissions": []
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value=mock_response)
        )
        
        result = await auth_client.validate_company_access(123, 999)
        
        assert result is not None
        assert result["has_access"] is False
        assert result["role"] is None
        assert result["permissions"] == []


@pytest.mark.unit
async def test_timeout_configuration(auth_client):
    """Test that timeout is properly configured."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"valid": True, "user_id": 1, "email": "test@test.com", "permissions": [], "is_active": True})
        )
        
        await auth_client.validate_user_token("test_token")
        
        # Verify client was created with correct timeout
        mock_client_class.assert_called_with(timeout=30.0)


@pytest.mark.unit
def test_auth_service_error_creation():
    """Test AuthServiceError exception creation."""
    error = AuthServiceError("Test error message")
    assert str(error) == "Test error message"
    
    error_with_details = AuthServiceError("Error", status_code=500, details="Server error")
    assert "Error" in str(error_with_details)
    assert hasattr(error_with_details, 'status_code')
    assert hasattr(error_with_details, 'details')