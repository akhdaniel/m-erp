"""
Tests for Company API endpoints.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.fixture
def mock_auth():
    """Mock authentication for testing."""
    mock_user = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True,
        "roles": ["admin"]
    }
    
    with patch("app.middleware.auth.get_current_active_user", return_value=mock_user):
        yield mock_user


@pytest.mark.asyncio
async def test_create_company(mock_auth):
    """Test creating a company via API."""
    company_data = {
        "name": "API Test Company",
        "legal_name": "API Test Company LLC",
        "code": "APITEST",
        "email": "api@test.com",
        "currency": "USD"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/companies/", json=company_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "API Test Company"
    assert data["code"] == "APITEST"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_create_company_invalid_data(mock_auth):
    """Test creating a company with invalid data."""
    company_data = {
        "name": "",  # Empty name should fail validation
        "legal_name": "Test Company LLC",
        "code": "X"  # Too short code should fail validation
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/companies/", json=company_data)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_companies(mock_auth):
    """Test listing companies via API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/companies/")
    
    assert response.status_code == 200
    data = response.json()
    assert "companies" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert "pages" in data


@pytest.mark.asyncio
async def test_list_companies_with_search(mock_auth):
    """Test listing companies with search parameter."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/companies/?search=test&limit=5")
    
    assert response.status_code == 200
    data = response.json()
    assert data["per_page"] == 5


@pytest.mark.asyncio
async def test_get_company(mock_auth):
    """Test getting a specific company via API."""
    # First create a company
    company_data = {
        "name": "Get Test Company",
        "legal_name": "Get Test Company LLC",
        "code": "GETTEST"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create company
        create_response = await client.post("/api/v1/companies/", json=company_data)
        assert create_response.status_code == 201
        company_id = create_response.json()["id"]
        
        # Get company
        get_response = await client.get(f"/api/v1/companies/{company_id}")
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == company_id
        assert data["name"] == "Get Test Company"


@pytest.mark.asyncio
async def test_get_company_not_found(mock_auth):
    """Test getting a non-existent company."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/companies/99999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_company_by_code(mock_auth):
    """Test getting a company by code via API."""
    # First create a company
    company_data = {
        "name": "Code Get Test Company",
        "legal_name": "Code Get Test Company LLC",
        "code": "CODEGET"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create company
        create_response = await client.post("/api/v1/companies/", json=company_data)
        assert create_response.status_code == 201
        
        # Get company by code
        get_response = await client.get("/api/v1/companies/code/CODEGET")
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["code"] == "CODEGET"
        assert data["name"] == "Code Get Test Company"


@pytest.mark.asyncio
async def test_update_company(mock_auth):
    """Test updating a company via API."""
    # First create a company
    company_data = {
        "name": "Update Test Company",
        "legal_name": "Update Test Company LLC",
        "code": "UPDATEAPI"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create company
        create_response = await client.post("/api/v1/companies/", json=company_data)
        assert create_response.status_code == 201
        company_id = create_response.json()["id"]
        
        # Update company
        update_data = {
            "name": "Updated Company Name",
            "email": "updated@company.com"
        }
        update_response = await client.put(f"/api/v1/companies/{company_id}", json=update_data)
        
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "Updated Company Name"
        assert data["email"] == "updated@company.com"
        assert data["legal_name"] == "Update Test Company LLC"  # Unchanged


@pytest.mark.asyncio
async def test_delete_company(mock_auth):
    """Test soft deleting a company via API."""
    # First create a company
    company_data = {
        "name": "Delete Test Company",
        "legal_name": "Delete Test Company LLC",
        "code": "DELETEAPI"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create company
        create_response = await client.post("/api/v1/companies/", json=company_data)
        assert create_response.status_code == 201
        company_id = create_response.json()["id"]
        
        # Delete company
        delete_response = await client.delete(f"/api/v1/companies/{company_id}")
        assert delete_response.status_code == 204
        
        # Verify company still exists but is inactive
        get_response = await client.get(f"/api/v1/companies/{company_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["is_active"] is False


@pytest.mark.asyncio
async def test_activate_company(mock_auth):
    """Test activating a company via API."""
    # First create and delete a company
    company_data = {
        "name": "Activate Test Company",
        "legal_name": "Activate Test Company LLC",
        "code": "ACTIVATEAPI"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create company
        create_response = await client.post("/api/v1/companies/", json=company_data)
        assert create_response.status_code == 201
        company_id = create_response.json()["id"]
        
        # Delete company
        await client.delete(f"/api/v1/companies/{company_id}")
        
        # Activate company
        activate_response = await client.post(f"/api/v1/companies/{company_id}/activate")
        assert activate_response.status_code == 200
        data = activate_response.json()
        assert data["is_active"] is True


@pytest.mark.asyncio
async def test_unauthorized_access():
    """Test that endpoints require authentication."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Try to access endpoint without authentication
        response = await client.get("/api/v1/companies/")
    
    assert response.status_code == 401