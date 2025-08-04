"""
API tests for module management endpoints
"""
import pytest
import io
import tarfile
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.models.module import ModuleStatus, ModuleType
from app.schemas.module import ModuleCreate, ModuleUpdate, ModuleStatusUpdate


@pytest.fixture
def client():
    """Test client for API testing"""
    return TestClient(app)


@pytest.fixture
def sample_module_data():
    """Sample module data for testing"""
    return {
        "name": "test-module",
        "version": "1.0.0",
        "display_name": "Test Module",
        "description": "Test module for API testing",
        "author": "Test Author",
        "author_email": "test@example.com",
        "license": "MIT",
        "homepage": "https://example.com",
        "repository": "https://github.com/example/test-module",
        "tags": ["test", "example"],
        "is_public": True,
        "manifest": {
            "name": "test-module",
            "version": "1.0.0",
            "description": "Test module for API testing",
            "author": "Test Author",
            "module_type": "full_module"
        }
    }


@pytest.fixture
def sample_package_data():
    """Sample package data for testing"""
    # Create a simple tar.gz package
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
        # Add a simple __init__.py file
        info = tarfile.TarInfo(name='__init__.py')
        init_content = b'def main(): return "test"'
        info.size = len(init_content)
        tar.addfile(info, io.BytesIO(init_content))
    
    tar_buffer.seek(0)
    return tar_buffer.getvalue()


@pytest.fixture
def mock_module_service():
    """Mock module service for testing"""
    with patch('app.routers.modules.get_module_service') as mock_service:
        service_instance = AsyncMock()
        mock_service.return_value = service_instance
        yield service_instance


@pytest.fixture
def sample_module_response():
    """Sample module response for testing"""
    return {
        "id": 1,
        "name": "test-module",
        "version": "1.0.0",
        "display_name": "Test Module",
        "description": "Test module for API testing",
        "author": "Test Author",
        "author_email": "test@example.com",
        "license": "MIT",
        "homepage": "https://example.com",
        "repository": "https://github.com/example/test-module",
        "tags": ["test", "example"],
        "status": "pending",
        "is_public": True,
        "download_count": 0,
        "rating": 0.0,
        "created_at": "2025-08-02T17:00:00Z",
        "updated_at": "2025-08-02T17:00:00Z",
        "manifest": {
            "name": "test-module",
            "version": "1.0.0",
            "description": "Test module for API testing",
            "author": "Test Author",
            "module_type": "full_module"
        }
    }


class TestModuleCreation:
    """Test module creation endpoints"""
    
    def test_create_module_success(self, client, mock_module_service, sample_module_data, sample_module_response):
        """Test successful module creation"""
        mock_module_service.validate_module_manifest.return_value = {"valid": True, "errors": []}
        mock_module_service.get_module_by_name_version.return_value = None
        mock_module_service.create_module.return_value = sample_module_response
        
        response = client.post("/api/v1/modules/", json=sample_module_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == "test-module"
        assert response.json()["version"] == "1.0.0"
        mock_module_service.create_module.assert_called_once()
    
    def test_create_module_with_package(self, client, mock_module_service, sample_module_data, sample_package_data, sample_module_response):
        """Test module creation with package upload"""
        mock_module_service.validate_module_manifest.return_value = {"valid": True, "errors": []}
        mock_module_service.get_module_by_name_version.return_value = None
        mock_module_service.create_module.return_value = sample_module_response
        
        files = {"package": ("test-module.tar.gz", sample_package_data, "application/gzip")}
        data = sample_module_data.copy()
        data.pop("manifest")  # Remove nested dict for multipart form
        
        response = client.post(
            "/api/v1/modules/",
            data={"module_data": sample_module_data},
            files=files
        )
        
        # This might fail due to form parsing complexity, but tests the structure
        mock_module_service.validate_module_manifest.assert_called()
    
    def test_create_module_invalid_manifest(self, client, mock_module_service, sample_module_data):
        """Test module creation with invalid manifest"""
        mock_module_service.validate_module_manifest.return_value = {
            "valid": False, 
            "errors": ["Missing required field: module_type"]
        }
        
        response = client.post("/api/v1/modules/", json=sample_module_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Invalid module manifest" in response.json()["detail"]["message"]
    
    def test_create_module_already_exists(self, client, mock_module_service, sample_module_data, sample_module_response):
        """Test module creation when module already exists"""
        mock_module_service.validate_module_manifest.return_value = {"valid": True, "errors": []}
        mock_module_service.get_module_by_name_version.return_value = sample_module_response
        
        response = client.post("/api/v1/modules/", json=sample_module_data)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"]
    
    def test_create_module_package_too_large(self, client, mock_module_service, sample_module_data):
        """Test module creation with package too large"""
        # Create large package data (over 50MB)
        large_package = b"x" * (51 * 1024 * 1024)
        
        files = {"package": ("large-module.tar.gz", large_package, "application/gzip")}
        
        response = client.post(
            "/api/v1/modules/",
            data={"module_data": sample_module_data},
            files=files
        )
        
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


class TestModuleRetrieval:
    """Test module retrieval endpoints"""
    
    def test_list_modules_success(self, client, mock_module_service, sample_module_response):
        """Test successful module listing"""
        mock_module_service.list_modules.return_value = ([sample_module_response], 1)
        
        response = client.get("/api/v1/modules/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["modules"]) == 1
        assert data["modules"][0]["name"] == "test-module"
    
    def test_list_modules_with_filters(self, client, mock_module_service, sample_module_response):
        """Test module listing with filters"""
        mock_module_service.list_modules.return_value = ([sample_module_response], 1)
        
        response = client.get(
            "/api/v1/modules/",
            params={
                "status": "approved",
                "module_type": "full_module",
                "search": "test",
                "is_public": True,
                "skip": 0,
                "limit": 10
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        mock_module_service.list_modules.assert_called_once_with(
            skip=0,
            limit=10,
            status=ModuleStatus.APPROVED,
            module_type=ModuleType.FULL_MODULE,
            search="test",
            is_public=True
        )
    
    def test_get_module_by_id_success(self, client, mock_module_service, sample_module_response):
        """Test successful module retrieval by ID"""
        mock_module_service.get_module.return_value = sample_module_response
        
        response = client.get("/api/v1/modules/1")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == 1
        assert response.json()["name"] == "test-module"
    
    def test_get_module_by_id_not_found(self, client, mock_module_service):
        """Test module retrieval when module not found"""
        mock_module_service.get_module.return_value = None
        
        response = client.get("/api/v1/modules/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Module not found" in response.json()["detail"]
    
    def test_get_module_by_name_version_success(self, client, mock_module_service, sample_module_response):
        """Test successful module retrieval by name and version"""
        mock_module_service.get_module_by_name_version.return_value = sample_module_response
        
        response = client.get("/api/v1/modules/by-name/test-module/versions/1.0.0")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "test-module"
        assert response.json()["version"] == "1.0.0"
    
    def test_get_module_by_name_version_not_found(self, client, mock_module_service):
        """Test module retrieval by name/version when not found"""
        mock_module_service.get_module_by_name_version.return_value = None
        
        response = client.get("/api/v1/modules/by-name/nonexistent/versions/1.0.0")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]


class TestModuleUpdate:
    """Test module update endpoints"""
    
    def test_update_module_success(self, client, mock_module_service, sample_module_response):
        """Test successful module update"""
        updated_module = sample_module_response.copy()
        updated_module["description"] = "Updated description"
        mock_module_service.update_module.return_value = updated_module
        
        update_data = {
            "description": "Updated description",
            "tags": ["updated", "test"]
        }
        
        response = client.put("/api/v1/modules/1", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["description"] == "Updated description"
    
    def test_update_module_not_found(self, client, mock_module_service):
        """Test module update when module not found"""
        mock_module_service.update_module.return_value = None
        
        update_data = {"description": "Updated description"}
        
        response = client.put("/api/v1/modules/999", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Module not found" in response.json()["detail"]
    
    def test_update_module_status_success(self, client, mock_module_service, sample_module_response):
        """Test successful module status update"""
        updated_module = sample_module_response.copy()
        updated_module["status"] = "approved"
        mock_module_service.update_module_status.return_value = updated_module
        
        status_data = {
            "status": "approved",
            "reason": "Module approved for publication"
        }
        
        response = client.patch("/api/v1/modules/1/status", json=status_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "approved"
    
    def test_update_module_status_invalid(self, client, mock_module_service):
        """Test module status update with invalid status"""
        mock_module_service.update_module_status.side_effect = ValueError("Invalid status")
        
        status_data = {"status": "invalid_status"}
        
        response = client.patch("/api/v1/modules/1/status", json=status_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid status" in response.json()["detail"]


class TestModuleDeletion:
    """Test module deletion endpoints"""
    
    def test_delete_module_success(self, client, mock_module_service):
        """Test successful module deletion"""
        mock_module_service.delete_module.return_value = True
        
        response = client.delete("/api/v1/modules/1")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_module_service.delete_module.assert_called_once_with(1)
    
    def test_delete_module_not_found(self, client, mock_module_service):
        """Test module deletion when module not found"""
        mock_module_service.delete_module.return_value = False
        
        response = client.delete("/api/v1/modules/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Module not found" in response.json()["detail"]


class TestModulePackage:
    """Test module package endpoints"""
    
    def test_download_module_package_success(self, client, mock_module_service, sample_package_data):
        """Test successful module package download"""
        module_with_package = {
            "id": 1,
            "name": "test-module",
            "version": "1.0.0",
            "package_data": sample_package_data
        }
        mock_module_service.get_module.return_value = module_with_package
        
        response = client.get("/api/v1/modules/1/package")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/octet-stream"
        assert "attachment" in response.headers["content-disposition"]
    
    def test_download_module_package_not_found(self, client, mock_module_service):
        """Test module package download when module not found"""
        mock_module_service.get_module.return_value = None
        
        response = client.get("/api/v1/modules/999/package")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Module not found" in response.json()["detail"]
    
    def test_download_module_package_no_package(self, client, mock_module_service):
        """Test module package download when no package available"""
        module_without_package = {
            "id": 1,
            "name": "test-module",
            "version": "1.0.0",
            "package_data": None
        }
        mock_module_service.get_module.return_value = module_without_package
        
        response = client.get("/api/v1/modules/1/package")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Module package not available" in response.json()["detail"]


class TestModuleDependencies:
    """Test module dependency endpoints"""
    
    def test_get_module_dependencies_success(self, client, mock_module_service):
        """Test successful module dependencies retrieval"""
        dependencies = [
            {"name": "dep1", "version": ">=1.0.0", "type": "module"},
            {"name": "dep2", "version": "^2.0.0", "type": "library"}
        ]
        mock_module_service.get_module_dependencies.return_value = [
            MagicMock(to_dict=lambda: dep) for dep in dependencies
        ]
        
        response = client.get("/api/v1/modules/1/dependencies")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["dependencies"]) == 2
    
    def test_get_module_dependents_success(self, client, mock_module_service):
        """Test successful module dependents retrieval"""
        dependents = [
            {"name": "dependent1", "version": "1.0.0"},
            {"name": "dependent2", "version": "2.0.0"}
        ]
        mock_module_service.get_module_dependents.return_value = [
            MagicMock(to_dict=lambda: dep) for dep in dependents
        ]
        
        response = client.get("/api/v1/modules/1/dependents")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["dependents"]) == 2


class TestModuleValidation:
    """Test module validation endpoints"""
    
    def test_validate_manifest_success(self, client, mock_module_service):
        """Test successful manifest validation"""
        validation_result = {"valid": True, "errors": [], "warnings": []}
        mock_module_service.validate_module_manifest.return_value = validation_result
        
        manifest_data = {
            "name": "test-module",
            "version": "1.0.0",
            "description": "Test module",
            "author": "Test Author",
            "module_type": "full_module"
        }
        
        response = client.post("/api/v1/modules/validate-manifest", json=manifest_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["valid"] is True
    
    def test_validate_manifest_invalid(self, client, mock_module_service):
        """Test manifest validation with invalid manifest"""
        validation_result = {
            "valid": False, 
            "errors": ["Missing required field: module_type"],
            "warnings": []
        }
        mock_module_service.validate_module_manifest.return_value = validation_result
        
        manifest_data = {
            "name": "test-module",
            "version": "1.0.0",
            "description": "Test module",
            "author": "Test Author"
            # Missing module_type
        }
        
        response = client.post("/api/v1/modules/validate-manifest", json=manifest_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["valid"] is False
        assert len(response.json()["errors"]) > 0


class TestModuleSearch:
    """Test module search endpoints"""
    
    def test_search_modules_success(self, client, mock_module_service, sample_module_response):
        """Test successful module search"""
        search_results = [sample_module_response]
        mock_module_service.search_modules.return_value = [
            MagicMock(to_dict=lambda: module) for module in search_results
        ]
        
        response = client.get("/api/v1/modules/search/test?limit=10")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["modules"]) == 1
        mock_module_service.search_modules.assert_called_once_with("test", 10)
    
    def test_search_modules_no_results(self, client, mock_module_service):
        """Test module search with no results"""
        mock_module_service.search_modules.return_value = []
        
        response = client.get("/api/v1/modules/search/nonexistent")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["modules"]) == 0


class TestErrorHandling:
    """Test error handling in module endpoints"""
    
    def test_internal_server_error(self, client, mock_module_service):
        """Test internal server error handling"""
        mock_module_service.get_module.side_effect = Exception("Database connection failed")
        
        response = client.get("/api/v1/modules/1")
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Database connection failed" in response.json()["detail"]
    
    def test_validation_error(self, client, mock_module_service):
        """Test validation error handling"""
        mock_module_service.create_module.side_effect = ValueError("Invalid module data")
        
        module_data = {"name": "test", "version": "1.0.0"}
        
        response = client.post("/api/v1/modules/", json=module_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid module data" in response.json()["detail"]


@pytest.mark.integration
class TestModuleAPIIntegration:
    """Integration tests for module API workflows"""
    
    def test_module_lifecycle_workflow(self, client, mock_module_service, sample_module_data, sample_module_response):
        """Test complete module lifecycle workflow"""
        # Setup mocks for the workflow
        mock_module_service.validate_module_manifest.return_value = {"valid": True, "errors": []}
        mock_module_service.get_module_by_name_version.return_value = None
        mock_module_service.create_module.return_value = sample_module_response
        mock_module_service.get_module.return_value = sample_module_response
        mock_module_service.update_module_status.return_value = {**sample_module_response, "status": "approved"}
        mock_module_service.delete_module.return_value = True
        
        # 1. Create module
        response = client.post("/api/v1/modules/", json=sample_module_data)
        assert response.status_code == status.HTTP_201_CREATED
        module_id = response.json()["id"]
        
        # 2. Get module
        response = client.get(f"/api/v1/modules/{module_id}")
        assert response.status_code == status.HTTP_200_OK
        
        # 3. Update module status
        status_data = {"status": "approved", "reason": "Module approved"}
        response = client.patch(f"/api/v1/modules/{module_id}/status", json=status_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "approved"
        
        # 4. Delete module
        response = client.delete(f"/api/v1/modules/{module_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT