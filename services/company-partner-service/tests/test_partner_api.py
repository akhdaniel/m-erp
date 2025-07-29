"""
Tests for Partner API endpoints.
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
        with patch("app.middleware.auth.verify_company_access", return_value=mock_user):
            yield mock_user


@pytest.fixture
async def test_company():
    """Create a test company for partner tests."""
    company_data = {
        "name": "Partner Test Company",
        "legal_name": "Partner Test Company LLC",
        "code": "PARTNERTEST"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch("app.middleware.auth.get_current_active_user", return_value={"id": 1, "is_active": True}):
            response = await client.post("/api/v1/companies/", json=company_data)
            assert response.status_code == 201
            return response.json()


@pytest.mark.asyncio
async def test_create_partner(mock_auth, test_company):
    """Test creating a partner via API."""
    partner_data = {
        "company_id": test_company["id"],
        "name": "API Test Partner",
        "code": "APIPART01",
        "email": "partner@api.com",
        "partner_type": "customer",
        "is_customer": True
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/partners/", json=partner_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "API Test Partner"
    assert data["code"] == "APIPART01"
    assert data["company_id"] == test_company["id"]
    assert data["is_customer"] is True


@pytest.mark.asyncio
async def test_create_partner_invalid_data(mock_auth, test_company):
    """Test creating a partner with invalid data."""
    partner_data = {
        "company_id": test_company["id"],
        "name": "",  # Empty name should fail validation
        "partner_type": "invalid_type"  # Invalid type should fail validation
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/partners/", json=partner_data)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_partners(mock_auth, test_company):
    """Test listing partners via API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/api/v1/partners/?company_id={test_company['id']}")
    
    assert response.status_code == 200
    data = response.json()
    assert "partners" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert "pages" in data


@pytest.mark.asyncio
async def test_list_partners_with_filters(mock_auth, test_company):
    """Test listing partners with filters."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/partners/?company_id={test_company['id']}&search=test&partner_type=customer&limit=5"
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["per_page"] == 5


@pytest.mark.asyncio
async def test_get_partners_by_company(mock_auth, test_company):
    """Test getting all partners for a company."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/api/v1/partners/company/{test_company['id']}")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_partner(mock_auth, test_company):
    """Test getting a specific partner via API."""
    # First create a partner
    partner_data = {
        "company_id": test_company["id"],
        "name": "Get Test Partner",
        "code": "GETPART01",
        "partner_type": "customer"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create partner
        create_response = await client.post("/api/v1/partners/", json=partner_data)
        assert create_response.status_code == 201
        partner_id = create_response.json()["id"]
        
        # Get partner
        get_response = await client.get(f"/api/v1/partners/{partner_id}")
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == partner_id
        assert data["name"] == "Get Test Partner"


@pytest.mark.asyncio
async def test_get_partner_not_found(mock_auth):
    """Test getting a non-existent partner."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/partners/99999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_partner_by_code(mock_auth, test_company):
    """Test getting a partner by code via API."""
    # First create a partner
    partner_data = {
        "company_id": test_company["id"],
        "name": "Code Get Test Partner",
        "code": "CODEGETPART",
        "partner_type": "supplier"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create partner
        create_response = await client.post("/api/v1/partners/", json=partner_data)
        assert create_response.status_code == 201
        
        # Get partner by code
        get_response = await client.get(f"/api/v1/partners/company/{test_company['id']}/code/CODEGETPART")
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["code"] == "CODEGETPART"
        assert data["name"] == "Code Get Test Partner"


@pytest.mark.asyncio
async def test_update_partner(mock_auth, test_company):
    """Test updating a partner via API."""
    # First create a partner
    partner_data = {
        "company_id": test_company["id"],
        "name": "Update Test Partner",
        "code": "UPDATEPART",
        "partner_type": "customer"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create partner
        create_response = await client.post("/api/v1/partners/", json=partner_data)
        assert create_response.status_code == 201
        partner_id = create_response.json()["id"]
        
        # Update partner
        update_data = {
            "name": "Updated Partner Name",
            "email": "updated@partner.com",
            "is_supplier": True
        }
        update_response = await client.put(f"/api/v1/partners/{partner_id}", json=update_data)
        
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "Updated Partner Name"
        assert data["email"] == "updated@partner.com"
        assert data["is_supplier"] is True
        assert data["code"] == "UPDATEPART"  # Unchanged


@pytest.mark.asyncio
async def test_delete_partner(mock_auth, test_company):
    """Test soft deleting a partner via API."""
    # First create a partner
    partner_data = {
        "company_id": test_company["id"],
        "name": "Delete Test Partner",
        "code": "DELETEPART",
        "partner_type": "customer"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create partner
        create_response = await client.post("/api/v1/partners/", json=partner_data)
        assert create_response.status_code == 201
        partner_id = create_response.json()["id"]
        
        # Delete partner
        delete_response = await client.delete(f"/api/v1/partners/{partner_id}")
        assert delete_response.status_code == 204
        
        # Verify partner still exists but is inactive
        get_response = await client.get(f"/api/v1/partners/{partner_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["is_active"] is False


@pytest.mark.asyncio
async def test_activate_partner(mock_auth, test_company):
    """Test activating a partner via API."""
    # First create and delete a partner
    partner_data = {
        "company_id": test_company["id"],
        "name": "Activate Test Partner",
        "code": "ACTIVATEPART",
        "partner_type": "customer"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create partner
        create_response = await client.post("/api/v1/partners/", json=partner_data)
        assert create_response.status_code == 201
        partner_id = create_response.json()["id"]
        
        # Delete partner
        await client.delete(f"/api/v1/partners/{partner_id}")
        
        # Activate partner
        activate_response = await client.post(f"/api/v1/partners/{partner_id}/activate")
        assert activate_response.status_code == 200
        data = activate_response.json()
        assert data["is_active"] is True


@pytest.mark.asyncio
async def test_unauthorized_access():
    """Test that partner endpoints require authentication."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Try to access endpoint without authentication
        response = await client.get("/api/v1/partners/")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_partner_company_access_control(test_company):
    """Test that partner access is properly controlled by company."""
    # Mock user without access to test company
    mock_user = {
        "id": 2,
        "username": "otheruser", 
        "email": "other@example.com",
        "is_active": True,
        "roles": ["user"]
    }
    
    partner_data = {
        "company_id": test_company["id"],
        "name": "Access Control Test Partner",
        "code": "ACCESSPART",
        "partner_type": "customer"
    }
    
    with patch("app.middleware.auth.get_current_active_user", return_value=mock_user):
        with patch("app.middleware.auth.verify_company_access", side_effect=Exception("Access denied")):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post("/api/v1/partners/", json=partner_data)
                
                # Should fail due to company access control
                assert response.status_code == 500  # Internal server error due to exception