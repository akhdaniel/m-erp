"""
Tests for API endpoints
"""
import pytest
from httpx import AsyncClient
from app.models.module import ModuleStatus


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint"""
    response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Module Registry Service"
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Module Registry Service"


@pytest.mark.asyncio
async def test_service_info(client: AsyncClient):
    """Test service info endpoint"""
    response = await client.get("/info")
    
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Module Registry Service"
    assert "endpoints" in data
    assert "configuration" in data


@pytest.mark.asyncio
async def test_create_module(client: AsyncClient, sample_module_data):
    """Test creating a module via API"""
    response = await client.post("/api/v1/modules/", json=sample_module_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_module_data["name"]
    assert data["version"] == sample_module_data["version"]
    assert data["status"] == ModuleStatus.REGISTERED


@pytest.mark.asyncio
async def test_create_module_invalid_data(client: AsyncClient):
    """Test creating a module with invalid data"""
    invalid_data = {
        "name": "",  # Invalid: empty name
        "version": "invalid-version",  # Invalid: not semantic version
        # Missing required fields
    }
    
    response = await client.post("/api/v1/modules/", json=invalid_data)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_module(client: AsyncClient, sample_module):
    """Test getting a module via API"""
    response = await client.get(f"/api/v1/modules/{sample_module.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_module.id
    assert data["name"] == sample_module.name


@pytest.mark.asyncio
async def test_get_module_not_found(client: AsyncClient):
    """Test getting a non-existent module"""
    response = await client.get("/api/v1/modules/9999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_modules(client: AsyncClient, sample_module):
    """Test listing modules via API"""
    response = await client.get("/api/v1/modules/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["modules"]) == 1
    assert data["modules"][0]["id"] == sample_module.id


@pytest.mark.asyncio
async def test_list_modules_with_pagination(client: AsyncClient, sample_module):
    """Test listing modules with pagination"""
    response = await client.get("/api/v1/modules/?skip=0&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_update_module(client: AsyncClient, sample_module):
    """Test updating a module via API"""
    update_data = {
        "display_name": "Updated Test Module",
        "description": "Updated description"
    }
    
    response = await client.put(f"/api/v1/modules/{sample_module.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "Updated Test Module"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_module_status(client: AsyncClient, sample_module):
    """Test updating module status via API"""
    status_data = {
        "status": ModuleStatus.REJECTED,
        "validation_errors": {"error": "Invalid manifest"}
    }
    
    response = await client.patch(f"/api/v1/modules/{sample_module.id}/status", json=status_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == ModuleStatus.REJECTED


@pytest.mark.asyncio
async def test_delete_module(client: AsyncClient, sample_module):
    """Test deleting a module via API"""
    response = await client.delete(f"/api/v1/modules/{sample_module.id}")
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_module_dependencies(client: AsyncClient, sample_module, sample_dependency):
    """Test getting module dependencies via API"""
    response = await client.get(f"/api/v1/modules/{sample_module.id}/dependencies")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["dependencies"]) == 1
    assert data["dependencies"][0]["dependency_name"] == "business-object-framework"


@pytest.mark.asyncio
async def test_validate_module_manifest(client: AsyncClient):
    """Test validating module manifest via API"""
    manifest_data = {
        "name": "test-module",
        "version": "1.0.0",
        "description": "Test module",
        "author": "Test Author",
        "dependencies": [],
        "entry_points": {},
        "endpoints": [],
        "event_handlers": {},
        "metadata": {}
    }
    
    response = await client.post("/api/v1/modules/validate-manifest", json=manifest_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True


@pytest.mark.asyncio
async def test_search_modules(client: AsyncClient, sample_module):
    """Test searching modules via API"""
    response = await client.get("/api/v1/modules/search/test")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["modules"]) == 1
    assert data["modules"][0]["id"] == sample_module.id


@pytest.mark.asyncio
async def test_create_installation(client: AsyncClient, sample_module, sample_installation_data):
    """Test creating an installation via API"""
    response = await client.post("/api/v1/installations/", json=sample_installation_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["module_id"] == sample_installation_data["module_id"]
    assert data["company_id"] == sample_installation_data["company_id"]


@pytest.mark.asyncio
async def test_list_installations(client: AsyncClient, sample_installation):
    """Test listing installations via API"""
    response = await client.get("/api/v1/installations/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["installations"]) == 1


@pytest.mark.asyncio
async def test_get_installation(client: AsyncClient, sample_installation):
    """Test getting an installation via API"""
    response = await client.get(f"/api/v1/installations/{sample_installation.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_installation.id


@pytest.mark.asyncio
async def test_update_installation(client: AsyncClient, sample_installation):
    """Test updating an installation via API"""
    update_data = {
        "configuration": {"api_key": "updated-key"},
        "is_enabled": False
    }
    
    response = await client.put(f"/api/v1/installations/{sample_installation.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["configuration"]["api_key"] == "updated-key"
    assert data["is_enabled"] is False


@pytest.mark.asyncio
async def test_uninstall_module(client: AsyncClient, sample_installation):
    """Test uninstalling a module via API"""
    response = await client.delete(f"/api/v1/installations/{sample_installation.id}")
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_perform_health_check(client: AsyncClient, sample_installation):
    """Test performing health check via API"""
    response = await client.post(f"/api/v1/installations/{sample_installation.id}/health-check")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"