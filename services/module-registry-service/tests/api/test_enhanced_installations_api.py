"""
Tests for enhanced installation workflow endpoints
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.services.enhanced_installation_service import InstallationError, UninstallationError
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
            "api_key": "test_key_123",
            "timeout": 30,
            "debug_mode": False,
            "max_connections": 10
        }
    }


@pytest.fixture
def mock_enhanced_installation_service():
    """Mock enhanced installation service"""
    with patch('app.routers.enhanced_installations.get_enhanced_installation_service') as mock_service:
        service_instance = AsyncMock()
        mock_service.return_value = service_instance
        yield service_instance


@pytest.fixture
def mock_current_user():
    """Mock current user for testing"""
    with patch('app.routers.enhanced_installations.get_current_user') as mock_user:
        mock_user.return_value = {"id": 1, "username": "testuser"}
        yield mock_user


@pytest.fixture
def sample_installation_response():
    """Sample installation response with loaded module"""
    installation = MagicMock()
    installation.id = 1
    installation.module_id = 1
    installation.company_id = 1
    installation.status = InstallationStatus.INSTALLED
    installation.installed_version = "1.0.0"
    installation.installed_by = "testuser"
    installation.installed_at = datetime.utcnow()
    installation.configuration = {"api_key": "test_key_123"}
    installation.health_status = "healthy"
    installation.installation_log = {
        "created": "2025-08-02T16:00:00Z",
        "framework_loaded": "2025-08-02T16:00:01Z",
        "loaded": "2025-08-02T16:00:02Z"
    }
    
    loaded_module = MagicMock()
    loaded_module.module_name = "test-module"
    loaded_module.module_version = "1.0.0"
    loaded_module.full_name = "test-module@1.0.0"
    loaded_module.is_initialized = True
    
    return installation, loaded_module


class TestModuleInstallationWithFramework:
    """Test enhanced module installation with plugin framework integration"""
    
    def test_install_module_success(self, client, mock_enhanced_installation_service, 
                                   mock_current_user, sample_installation_data, sample_installation_response):
        """Test successful module installation with framework integration"""
        installation, loaded_module = sample_installation_response
        mock_enhanced_installation_service.install_module.return_value = (installation, loaded_module)
        
        response = client.post("/api/v2/installations/install", json=sample_installation_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["id"] == 1
        assert response_data["status"] == "installed"
        assert response_data["module_info"]["name"] == "test-module"
        assert response_data["module_info"]["initialized"] is True
        assert "installation_log" in response_data
        
        mock_enhanced_installation_service.install_module.assert_called_once()
    
    def test_install_module_validation_error(self, client, mock_enhanced_installation_service, 
                                           mock_current_user, sample_installation_data):
        """Test module installation with validation error"""
        mock_enhanced_installation_service.install_module.side_effect = ValueError(
            "Module must be approved before installation"
        )
        
        response = client.post("/api/v2/installations/install", json=sample_installation_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "approved before installation" in response.json()["detail"]
    
    def test_install_module_installation_error(self, client, mock_enhanced_installation_service, 
                                             mock_current_user, sample_installation_data):
        """Test module installation with installation error"""
        mock_enhanced_installation_service.install_module.side_effect = InstallationError(
            "Failed to load module with framework: Module validation failed"
        )
        
        response = client.post("/api/v2/installations/install", json=sample_installation_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Failed to load module with framework" in response.json()["detail"]
    
    def test_install_module_dependency_error(self, client, mock_enhanced_installation_service, 
                                           mock_current_user, sample_installation_data):
        """Test module installation with missing dependencies"""
        mock_enhanced_installation_service.install_module.side_effect = InstallationError(
            "Required dependency 'business-object-framework' is not installed for this company"
        )
        
        response = client.post("/api/v2/installations/install", json=sample_installation_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "business-object-framework" in response.json()["detail"]
        assert "not installed" in response.json()["detail"]
    
    def test_install_module_already_installed(self, client, mock_enhanced_installation_service, 
                                            mock_current_user, sample_installation_data):
        """Test module installation when already installed"""
        mock_enhanced_installation_service.install_module.side_effect = ValueError(
            "Module is already installed for this company"
        )
        
        response = client.post("/api/v2/installations/install", json=sample_installation_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "already installed" in response.json()["detail"]


class TestModuleUninstallationWithFramework:
    """Test enhanced module uninstallation with proper cleanup"""
    
    def test_uninstall_module_success(self, client, mock_enhanced_installation_service):
        """Test successful module uninstallation"""
        mock_enhanced_installation_service.uninstall_module.return_value = True
        
        response = client.delete("/api/v2/installations/1/uninstall")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["installation_id"] == 1
        assert response_data["status"] == "uninstalled"
        assert "uninstalled successfully" in response_data["message"]
        
        mock_enhanced_installation_service.uninstall_module.assert_called_once_with(1)
    
    def test_uninstall_module_with_dependencies(self, client, mock_enhanced_installation_service):
        """Test module uninstallation with active dependencies"""
        mock_enhanced_installation_service.uninstall_module.side_effect = UninstallationError(
            "Cannot uninstall module with active dependencies: dependent-module"
        )
        
        response = client.delete("/api/v2/installations/1/uninstall")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "active dependencies" in response.json()["detail"]
        assert "dependent-module" in response.json()["detail"]
    
    def test_uninstall_module_force_flag(self, client, mock_enhanced_installation_service):
        """Test module uninstallation with force flag"""
        mock_enhanced_installation_service.uninstall_module.return_value = True
        
        response = client.delete("/api/v2/installations/1/uninstall?force=true")
        
        assert response.status_code == status.HTTP_200_OK
        # Force flag is logged but not yet implemented in the service
        mock_enhanced_installation_service.uninstall_module.assert_called_once_with(1)
    
    def test_uninstall_module_not_found(self, client, mock_enhanced_installation_service):
        """Test module uninstallation when installation not found"""
        mock_enhanced_installation_service.uninstall_module.side_effect = UninstallationError(
            "Installation not found"
        )
        
        response = client.delete("/api/v2/installations/999/uninstall")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Installation not found" in response.json()["detail"]


class TestModuleReloading:
    """Test module hot reloading functionality"""
    
    def test_reload_module_success(self, client, mock_enhanced_installation_service, sample_installation_response):
        """Test successful module reload"""
        installation, loaded_module = sample_installation_response
        installation.installation_log["reloaded"] = "2025-08-02T17:00:00Z"
        
        mock_enhanced_installation_service.reload_module.return_value = (installation, loaded_module)
        
        response = client.post("/api/v2/installations/1/reload")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["installation_id"] == 1
        assert response_data["status"] == "reloaded"
        assert response_data["module_info"]["name"] == "test-module"
        assert response_data["module_info"]["initialized"] is True
        assert "reloaded successfully" in response_data["message"]
    
    def test_reload_module_failure(self, client, mock_enhanced_installation_service):
        """Test module reload failure"""
        mock_enhanced_installation_service.reload_module.side_effect = InstallationError(
            "Module initialization failed during reload"
        )
        
        response = client.post("/api/v2/installations/1/reload")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "initialization failed" in response.json()["detail"]


class TestConfigurationManagement:
    """Test module configuration management with hot reload"""
    
    def test_update_configuration_success(self, client, mock_enhanced_installation_service):
        """Test successful configuration update with hot reload"""
        installation = MagicMock()
        installation.id = 1
        installation.configuration = {"api_key": "new_key", "timeout": 60}
        installation.installation_log = {
            "config_updated": "2025-08-02T17:00:00Z",
            "config_hot_reloaded": "2025-08-02T17:00:01Z"
        }
        
        mock_enhanced_installation_service.update_module_configuration.return_value = installation
        
        new_config = {"api_key": "new_key", "timeout": 60}
        
        response = client.put("/api/v2/installations/1/configuration", json=new_config)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["installation_id"] == 1
        assert response_data["configuration"]["api_key"] == "new_key"
        assert response_data["hot_reload"] is True
        assert response_data["hot_reload_status"] == "success"
    
    def test_update_configuration_without_hot_reload(self, client, mock_enhanced_installation_service):
        """Test configuration update without hot reload"""
        installation = MagicMock()
        installation.id = 1
        installation.configuration = {"api_key": "new_key"}
        installation.installation_log = {"config_updated": "2025-08-02T17:00:00Z"}
        
        mock_enhanced_installation_service.update_module_configuration.return_value = installation
        
        new_config = {"api_key": "new_key"}
        
        response = client.put("/api/v2/installations/1/configuration?hot_reload=false", json=new_config)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["hot_reload"] is False
        assert response_data["hot_reload_status"] == "skipped"
    
    def test_update_configuration_validation_error(self, client, mock_enhanced_installation_service):
        """Test configuration update with validation error"""
        mock_enhanced_installation_service.update_module_configuration.side_effect = ValueError(
            "Required configuration field missing: api_key"
        )
        
        invalid_config = {"timeout": 60}  # Missing required api_key
        
        response = client.put("/api/v2/installations/1/configuration", json=invalid_config)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Required configuration field missing" in response.json()["detail"]


class TestHealthChecking:
    """Test comprehensive health checking functionality"""
    
    def test_health_check_success(self, client, mock_enhanced_installation_service):
        """Test successful comprehensive health check"""
        from app.schemas.installation import HealthCheckResult
        
        health_result = HealthCheckResult(
            installation_id=1,
            status="healthy",
            checks={
                "installation_active": True,
                "module_loaded": True,
                "module_health": True,
                "endpoints_registered": True,
                "dependencies_available": True
            },
            last_check=datetime.utcnow(),
            response_time_ms=45,
            errors=[]
        )
        
        mock_enhanced_installation_service.perform_health_check.return_value = health_result
        
        response = client.post("/api/v2/installations/1/health-check")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "healthy"
        assert response_data["checks"]["module_loaded"] is True
        assert response_data["response_time_ms"] == 45
        assert len(response_data["errors"]) == 0
    
    def test_health_check_unhealthy(self, client, mock_enhanced_installation_service):
        """Test health check with unhealthy module"""
        from app.schemas.installation import HealthCheckResult
        
        health_result = HealthCheckResult(
            installation_id=1,
            status="unhealthy",
            checks={
                "installation_active": True,
                "module_loaded": False,
                "module_health": False,
                "endpoints_registered": False,
                "dependencies_available": True
            },
            last_check=datetime.utcnow(),
            response_time_ms=150,
            errors=["Module not loaded in framework", "Endpoints not responding"]
        )
        
        mock_enhanced_installation_service.perform_health_check.return_value = health_result
        
        response = client.post("/api/v2/installations/1/health-check")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "unhealthy"
        assert response_data["checks"]["module_loaded"] is False
        assert len(response_data["errors"]) == 2
    
    def test_health_check_installation_not_found(self, client, mock_enhanced_installation_service):
        """Test health check for non-existent installation"""
        mock_enhanced_installation_service.perform_health_check.side_effect = ValueError(
            "Installation not found"
        )
        
        response = client.post("/api/v2/installations/999/health-check")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Installation not found" in response.json()["detail"]


class TestInstallationStatusAndMonitoring:
    """Test installation status and monitoring endpoints"""
    
    def test_get_detailed_status_success(self, client, mock_enhanced_installation_service):
        """Test getting detailed installation status"""
        installation = MagicMock()
        installation.id = 1
        installation.module_id = 1
        installation.company_id = 1
        installation.status = InstallationStatus.INSTALLED
        installation.health_status = "healthy"
        installation.installed_version = "1.0.0"
        installation.installed_by = "testuser"
        installation.installed_at = datetime.utcnow()
        installation.last_health_check = datetime.utcnow()
        installation.error_message = None
        installation.configuration = {"api_key": "test_key"}
        installation.installation_log = {"created": "2025-08-02T16:00:00Z"}
        installation.module.name = "test-module"
        installation.module.version = "1.0.0"
        installation.module.display_name = "Test Module"
        
        mock_enhanced_installation_service.get_installation.return_value = installation
        
        # Mock framework components
        with patch('app.routers.enhanced_installations.plugin_loader') as mock_loader, \
             patch('app.routers.enhanced_installations.get_endpoint_manager') as mock_endpoint_mgr:
            
            mock_loader.is_module_loaded.return_value = True
            mock_loaded_module = MagicMock()
            mock_loaded_module.is_initialized = True
            mock_loaded_module.full_name = "test-module@1.0.0"
            mock_loader.get_loaded_module.return_value = mock_loaded_module
            
            mock_endpoint_manager = MagicMock()
            mock_endpoint_manager.get_module_endpoints.return_value = [{"path": "/test", "method": "GET"}]
            mock_endpoint_mgr.return_value = mock_endpoint_manager
            
            response = client.get("/api/v2/installations/1/status")
            
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["status"] == "installed"
            assert response_data["framework_status"]["module_loaded"] is True
            assert response_data["framework_status"]["module_initialized"] is True
            assert response_data["framework_status"]["endpoints_registered"] == 1
    
    def test_get_active_company_installations(self, client, mock_enhanced_installation_service):
        """Test getting active installations for a company"""
        installations = []
        for i in range(3):
            installation = MagicMock()
            installation.id = i + 1
            installation.module_id = i + 1
            installation.status = InstallationStatus.INSTALLED
            installation.health_status = "healthy"
            installation.installed_version = "1.0.0"
            installation.installed_at = datetime.utcnow()
            installation.module.name = f"module-{i+1}"
            installation.module.display_name = f"Module {i+1}"
            installations.append(installation)
        
        mock_enhanced_installation_service.list_installations.return_value = (installations, 3)
        
        with patch('app.routers.enhanced_installations.plugin_loader') as mock_loader:
            mock_loader.is_module_loaded.return_value = True
            mock_loaded_module = MagicMock()
            mock_loaded_module.is_initialized = True
            mock_loader.get_loaded_module.return_value = mock_loaded_module
            
            response = client.get("/api/v2/installations/company/1/active")
            
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert len(response_data) == 3
            assert all(inst["status"] == "installed" for inst in response_data)
            assert all("framework_status" in inst for inst in response_data)
    
    def test_get_framework_status(self, client):
        """Test getting overall framework status"""
        with patch('app.routers.enhanced_installations.plugin_loader') as mock_loader, \
             patch('app.routers.enhanced_installations.get_endpoint_manager') as mock_endpoint_mgr, \
             patch('app.routers.enhanced_installations.event_bus') as mock_event_bus:
            
            mock_loader.loaded_modules = {1: MagicMock(), 2: MagicMock()}
            
            mock_endpoint_manager = MagicMock()
            mock_endpoint_manager.get_all_endpoints.return_value = {
                1: [{"path": "/test1", "method": "GET"}],
                2: [{"path": "/test2", "method": "POST"}, {"path": "/test3", "method": "GET"}]
            }
            mock_endpoint_mgr.return_value = mock_endpoint_manager
            
            mock_event_bus.running = True
            
            response = client.get("/api/v2/installations/framework/status")
            
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["framework_status"] == "operational"
            assert response_data["loaded_modules"] == 2
            assert response_data["registered_endpoints"] == 3
            assert response_data["event_bus_running"] is True
    
    def test_bulk_health_check(self, client, mock_enhanced_installation_service):
        """Test bulk health check for multiple installations"""
        installations = []
        for i in range(2):
            installation = MagicMock()
            installation.id = i + 1
            installation.company_id = 1
            installation.module.name = f"module-{i+1}"
            installations.append(installation)
        
        mock_enhanced_installation_service.list_installations.return_value = (installations, 2)
        
        # Mock health check results
        health_results = [
            MagicMock(status="healthy", response_time_ms=45, errors=[]),
            MagicMock(status="degraded", response_time_ms=120, errors=["Slow response"])
        ]
        
        mock_enhanced_installation_service.perform_health_check.side_effect = health_results
        
        response = client.post("/api/v2/installations/bulk-health-check?company_id=1")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 2
        assert response_data[0]["health_status"] == "healthy"
        assert response_data[1]["health_status"] == "degraded"
        assert response_data[1]["error_count"] == 1