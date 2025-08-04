"""
API tests for installation management endpoints
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.models.installation import InstallationStatus


@pytest.fixture
def client():
    """Test client for API testing"""
    return TestClient(app)


@pytest.fixture
def sample_installation_data():
    """Sample installation data for testing"""
    return {
        "module_id": 1,
        "company_id": 1,
        "configuration": {
            "api_key": "test_key",
            "timeout": 30,
            "debug_mode": False
        }
    }


@pytest.fixture
def mock_installation_service():
    """Mock installation service for testing"""
    with patch('app.routers.installations.get_installation_service') as mock_service:
        service_instance = AsyncMock()
        mock_service.return_value = service_instance
        yield service_instance


@pytest.fixture
def mock_current_user():
    """Mock current user for testing"""
    with patch('app.routers.installations.get_current_user') as mock_user:
        mock_user.return_value = {"id": 1, "username": "testuser"}
        yield mock_user


@pytest.fixture
def sample_installation_response():
    """Sample installation response for testing"""
    return {
        "id": 1,
        "module_id": 1,
        "company_id": 1,
        "status": "installed",
        "installed_version": "1.0.0",
        "installed_by": "testuser",
        "installed_at": "2025-08-02T17:00:00Z",
        "updated_at": "2025-08-02T17:00:00Z",
        "configuration": {
            "api_key": "test_key",
            "timeout": 30,
            "debug_mode": False
        },
        "module": {
            "id": 1,
            "name": "test-module",
            "version": "1.0.0",
            "display_name": "Test Module"
        }
    }


class TestInstallationCreation:
    """Test installation creation endpoints"""
    
    def test_create_installation_success(self, client, mock_installation_service, mock_current_user, 
                                       sample_installation_data, sample_installation_response):
        """Test successful installation creation"""
        mock_installation_service.create_installation.return_value = sample_installation_response
        
        response = client.post("/api/v1/installations/", json=sample_installation_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["module_id"] == 1
        assert response.json()["company_id"] == 1
        assert response.json()["status"] == "installed"
        mock_installation_service.create_installation.assert_called_once()
    
    def test_create_installation_invalid_data(self, client, mock_installation_service, mock_current_user):
        """Test installation creation with invalid data"""
        mock_installation_service.create_installation.side_effect = ValueError("Invalid module ID")
        
        invalid_data = {
            "module_id": -1,  # Invalid ID
            "company_id": 1,
            "configuration": {}
        }
        
        response = client.post("/api/v1/installations/", json=invalid_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid module ID" in response.json()["detail"]
    
    def test_create_installation_module_not_found(self, client, mock_installation_service, mock_current_user):
        """Test installation creation when module not found"""
        mock_installation_service.create_installation.side_effect = ValueError("Module not found")
        
        installation_data = {
            "module_id": 999,
            "company_id": 1,
            "configuration": {}
        }
        
        response = client.post("/api/v1/installations/", json=installation_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Module not found" in response.json()["detail"]
    
    def test_create_installation_already_exists(self, client, mock_installation_service, mock_current_user):
        """Test installation creation when installation already exists"""
        mock_installation_service.create_installation.side_effect = ValueError(
            "Installation already exists for this module and company"
        )
        
        installation_data = {
            "module_id": 1,
            "company_id": 1,
            "configuration": {}
        }
        
        response = client.post("/api/v1/installations/", json=installation_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]


class TestInstallationRetrieval:
    """Test installation retrieval endpoints"""
    
    def test_list_installations_success(self, client, mock_installation_service, sample_installation_response):
        """Test successful installation listing"""
        mock_installation_service.list_installations.return_value = ([sample_installation_response], 1)
        
        response = client.get("/api/v1/installations/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["installations"]) == 1
        assert data["installations"][0]["module_id"] == 1
    
    def test_list_installations_with_filters(self, client, mock_installation_service, sample_installation_response):
        """Test installation listing with filters"""
        mock_installation_service.list_installations.return_value = ([sample_installation_response], 1)
        
        response = client.get(
            "/api/v1/installations/",
            params={
                "company_id": 1,
                "module_id": 1,
                "status": "installed",
                "skip": 0,
                "limit": 10
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        mock_installation_service.list_installations.assert_called_once_with(
            company_id=1,
            module_id=1,
            status=InstallationStatus.INSTALLED,
            skip=0,
            limit=10
        )
    
    def test_get_installation_by_id_success(self, client, mock_installation_service, sample_installation_response):
        """Test successful installation retrieval by ID"""
        mock_installation_service.get_installation.return_value = sample_installation_response
        
        response = client.get("/api/v1/installations/1")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == 1
        assert response.json()["module_id"] == 1
    
    def test_get_installation_by_id_not_found(self, client, mock_installation_service):
        """Test installation retrieval when installation not found"""
        mock_installation_service.get_installation.return_value = None
        
        response = client.get("/api/v1/installations/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Installation not found" in response.json()["detail"]
    
    def test_get_company_installations_success(self, client, mock_installation_service, sample_installation_response):
        """Test successful company installations retrieval"""
        mock_installation_service.get_company_installations.return_value = [sample_installation_response]
        
        response = client.get("/api/v1/installations/company/1")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["company_id"] == 1
    
    def test_get_module_installations_success(self, client, mock_installation_service, sample_installation_response):
        """Test successful module installations retrieval"""
        mock_installation_service.get_module_installations.return_value = [sample_installation_response]
        
        response = client.get("/api/v1/installations/module/1")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["module_id"] == 1
    
    def test_check_installation_exists_true(self, client, mock_installation_service):
        """Test installation existence check when installation exists"""
        mock_installation_service.installation_exists.return_value = True
        
        response = client.get("/api/v1/installations/check/1/1")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["exists"] is True
    
    def test_check_installation_exists_false(self, client, mock_installation_service):
        """Test installation existence check when installation doesn't exist"""
        mock_installation_service.installation_exists.return_value = False
        
        response = client.get("/api/v1/installations/check/1/1")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["exists"] is False


class TestInstallationUpdate:
    """Test installation update endpoints"""
    
    def test_update_installation_success(self, client, mock_installation_service, sample_installation_response):
        """Test successful installation update"""
        updated_installation = sample_installation_response.copy()
        updated_installation["configuration"]["timeout"] = 60
        mock_installation_service.update_installation.return_value = updated_installation
        
        update_data = {
            "configuration": {
                "api_key": "test_key",
                "timeout": 60,
                "debug_mode": True
            }
        }
        
        response = client.put("/api/v1/installations/1", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["configuration"]["timeout"] == 60
    
    def test_update_installation_not_found(self, client, mock_installation_service):
        """Test installation update when installation not found"""
        mock_installation_service.update_installation.return_value = None
        
        update_data = {
            "configuration": {"timeout": 60}
        }
        
        response = client.put("/api/v1/installations/999", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Installation not found" in response.json()["detail"]
    
    def test_update_installation_invalid_config(self, client, mock_installation_service):
        """Test installation update with invalid configuration"""
        mock_installation_service.update_installation.side_effect = ValueError("Invalid configuration")
        
        update_data = {
            "configuration": {"invalid_field": "value"}
        }
        
        response = client.put("/api/v1/installations/1", json=update_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid configuration" in response.json()["detail"]
    
    def test_update_installation_status_success(self, client, mock_installation_service, sample_installation_response):
        """Test successful installation status update"""
        updated_installation = sample_installation_response.copy()
        updated_installation["status"] = "stopped"
        mock_installation_service.update_installation_status.return_value = updated_installation
        
        status_data = {
            "status": "stopped",
            "reason": "Manual stop for maintenance"
        }
        
        response = client.patch("/api/v1/installations/1/status", json=status_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "stopped"
    
    def test_update_installation_status_invalid(self, client, mock_installation_service):
        """Test installation status update with invalid status"""
        mock_installation_service.update_installation_status.side_effect = ValueError("Invalid status transition")
        
        status_data = {"status": "invalid_status"}
        
        response = client.patch("/api/v1/installations/1/status", json=status_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid status transition" in response.json()["detail"]


class TestInstallationDeletion:
    """Test installation deletion endpoints"""
    
    def test_uninstall_module_success(self, client, mock_installation_service):
        """Test successful module uninstallation"""
        mock_installation_service.uninstall_module.return_value = True
        
        response = client.delete("/api/v1/installations/1")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_installation_service.uninstall_module.assert_called_once_with(1)
    
    def test_uninstall_module_not_found(self, client, mock_installation_service):
        """Test module uninstallation when installation not found"""
        mock_installation_service.uninstall_module.return_value = False
        
        response = client.delete("/api/v1/installations/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Installation not found" in response.json()["detail"]
    
    def test_uninstall_module_with_dependencies(self, client, mock_installation_service):
        """Test module uninstallation with dependency conflicts"""
        mock_installation_service.uninstall_module.side_effect = ValueError(
            "Cannot uninstall module with active dependencies"
        )
        
        response = client.delete("/api/v1/installations/1")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "active dependencies" in response.json()["detail"]


class TestInstallationHealthCheck:
    """Test installation health check endpoints"""
    
    def test_health_check_success(self, client, mock_installation_service):
        """Test successful installation health check"""
        health_result = {
            "installation_id": 1,
            "status": "healthy",
            "checks": {
                "module_loaded": True,
                "endpoints_responding": True,
                "dependencies_available": True
            },
            "last_check": "2025-08-02T17:00:00Z",
            "response_time_ms": 45
        }
        mock_installation_service.perform_health_check.return_value = health_result
        
        response = client.post("/api/v1/installations/1/health-check")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
        assert response.json()["checks"]["module_loaded"] is True
    
    def test_health_check_unhealthy(self, client, mock_installation_service):
        """Test installation health check when unhealthy"""
        health_result = {
            "installation_id": 1,
            "status": "unhealthy",
            "checks": {
                "module_loaded": False,
                "endpoints_responding": False,
                "dependencies_available": True
            },
            "last_check": "2025-08-02T17:00:00Z",
            "response_time_ms": 1500,
            "errors": ["Module failed to load", "Endpoint timeout"]
        }
        mock_installation_service.perform_health_check.return_value = health_result
        
        response = client.post("/api/v1/installations/1/health-check")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "unhealthy"
        assert len(response.json()["errors"]) == 2
    
    def test_health_check_installation_not_found(self, client, mock_installation_service):
        """Test health check when installation not found"""
        mock_installation_service.perform_health_check.side_effect = ValueError("Installation not found")
        
        response = client.post("/api/v1/installations/999/health-check")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Installation not found" in response.json()["detail"]


class TestErrorHandling:
    """Test error handling in installation endpoints"""
    
    def test_internal_server_error(self, client, mock_installation_service):
        """Test internal server error handling"""
        mock_installation_service.get_installation.side_effect = Exception("Database connection failed")
        
        response = client.get("/api/v1/installations/1")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Database connection failed" in response.json()["detail"]
    
    def test_validation_error(self, client, mock_installation_service, mock_current_user):
        """Test validation error handling"""
        mock_installation_service.create_installation.side_effect = ValueError("Invalid installation data")
        
        installation_data = {"module_id": "invalid", "company_id": 1}
        
        response = client.post("/api/v1/installations/", json=installation_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid installation data" in response.json()["detail"]


@pytest.mark.integration
class TestInstallationAPIIntegration:
    """Integration tests for installation API workflows"""
    
    def test_installation_lifecycle_workflow(self, client, mock_installation_service, mock_current_user,
                                           sample_installation_data, sample_installation_response):
        """Test complete installation lifecycle workflow"""
        # Setup mocks for the workflow
        mock_installation_service.create_installation.return_value = sample_installation_response
        mock_installation_service.get_installation.return_value = sample_installation_response
        mock_installation_service.update_installation_status.return_value = {
            **sample_installation_response, "status": "stopped"
        }
        mock_installation_service.perform_health_check.return_value = {
            "installation_id": 1,
            "status": "healthy",
            "checks": {"module_loaded": True}
        }
        mock_installation_service.uninstall_module.return_value = True
        
        # 1. Create installation
        response = client.post("/api/v1/installations/", json=sample_installation_data)
        assert response.status_code == status.HTTP_201_CREATED
        installation_id = response.json()["id"]
        
        # 2. Get installation
        response = client.get(f"/api/v1/installations/{installation_id}")
        assert response.status_code == status.HTTP_200_OK
        
        # 3. Perform health check
        response = client.post(f"/api/v1/installations/{installation_id}/health-check")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
        
        # 4. Update installation status
        status_data = {"status": "stopped", "reason": "Maintenance"}
        response = client.patch(f"/api/v1/installations/{installation_id}/status", json=status_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "stopped"
        
        # 5. Uninstall module
        response = client.delete(f"/api/v1/installations/{installation_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_company_module_management_workflow(self, client, mock_installation_service, mock_current_user,
                                              sample_installation_response):
        """Test company-specific module management workflow"""
        company_id = 1
        
        # Setup mocks
        mock_installation_service.get_company_installations.return_value = [sample_installation_response]
        mock_installation_service.installation_exists.return_value = True
        
        # 1. Get company installations
        response = client.get(f"/api/v1/installations/company/{company_id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        
        # 2. Check if specific module is installed
        module_id = 1
        response = client.get(f"/api/v1/installations/check/{module_id}/{company_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["exists"] is True
    
    def test_module_installation_tracking_workflow(self, client, mock_installation_service, 
                                                 sample_installation_response):
        """Test module installation tracking workflow"""
        module_id = 1
        
        # Setup mocks
        mock_installation_service.get_module_installations.return_value = [sample_installation_response]
        
        # Get all installations for a specific module
        response = client.get(f"/api/v1/installations/module/{module_id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["module_id"] == module_id