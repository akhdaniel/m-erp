"""
Integration tests for complete API workflows
"""
import pytest
import io
import tarfile
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app


@pytest.fixture
def client():
    """Test client for API testing"""
    return TestClient(app)


@pytest.fixture
def mock_services():
    """Mock all services for integration testing"""
    with patch('app.routers.modules.get_module_service') as mock_module_service, \
         patch('app.routers.installations.get_installation_service') as mock_installation_service, \
         patch('app.routers.installations.get_current_user') as mock_current_user:
        
        module_service = AsyncMock()
        installation_service = AsyncMock()
        current_user = {"id": 1, "username": "testuser"}
        
        mock_module_service.return_value = module_service
        mock_installation_service.return_value = installation_service
        mock_current_user.return_value = current_user
        
        yield {
            "module_service": module_service,
            "installation_service": installation_service,
            "current_user": current_user
        }


@pytest.fixture
def sample_module_package():
    """Sample module package for testing"""
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
        # Add module files
        files = {
            "__init__.py": b'def main(config): return "Module loaded"',
            "handlers.py": b'def get_test(request): return {"message": "test"}',
            "manifest.yaml": b'''
name: test-module
version: 1.0.0
description: Test module
author: Test Author
module_type: full_module
'''
        }
        
        for filename, content in files.items():
            info = tarfile.TarInfo(name=filename)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    
    tar_buffer.seek(0)
    return tar_buffer.getvalue()


@pytest.fixture
def sample_module_data():
    """Complete sample module data"""
    return {
        "name": "test-module",
        "version": "1.0.0",
        "display_name": "Test Module",
        "description": "A comprehensive test module for API workflows",
        "author": "Test Author",
        "author_email": "test@example.com",
        "license": "MIT",
        "homepage": "https://example.com/test-module",
        "repository": "https://github.com/example/test-module",
        "tags": ["test", "example", "workflow"],
        "is_public": True,
        "manifest": {
            "name": "test-module",
            "version": "1.0.0",
            "description": "A comprehensive test module for API workflows",
            "author": "Test Author",
            "module_type": "full_module",
            "dependencies": [
                {
                    "name": "business-object-framework",
                    "version": ">=1.0.0",
                    "type": "module"
                }
            ],
            "endpoints": [
                {
                    "path": "/test",
                    "method": "GET",
                    "handler": "test_module.handlers:get_test",
                    "description": "Test endpoint"
                }
            ]
        }
    }


class TestCompleteModuleWorkflow:
    """Test complete module development and deployment workflow"""
    
    def test_module_development_to_deployment_workflow(self, client, mock_services, sample_module_data, sample_module_package):
        """Test complete workflow from module development to deployment"""
        module_service = mock_services["module_service"]
        installation_service = mock_services["installation_service"]
        
        # Step 1: Validate manifest during development
        module_service.validate_module_manifest.return_value = {
            "valid": True,
            "errors": [],
            "warnings": ["Consider adding more detailed documentation"]
        }
        
        response = client.post("/api/v1/modules/validate-manifest", json=sample_module_data["manifest"])
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["valid"] is True
        
        # Step 2: Submit module for registration
        module_response = {
            "id": 1,
            "name": "test-module",
            "version": "1.0.0",
            "status": "pending",
            **sample_module_data
        }
        
        module_service.get_module_by_name_version.return_value = None
        module_service.create_module.return_value = module_response
        
        response = client.post("/api/v1/modules/", json=sample_module_data)
        assert response.status_code == status.HTTP_201_CREATED
        module_id = response.json()["id"]
        
        # Step 3: Module review and approval
        approved_module = {**module_response, "status": "approved"}
        module_service.update_module_status.return_value = approved_module
        
        approval_data = {
            "status": "approved",
            "reason": "Module passes all security and quality checks"
        }
        
        response = client.patch(f"/api/v1/modules/{module_id}/status", json=approval_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "approved"
        
        # Step 4: Module discovery by companies
        module_service.search_modules.return_value = [MagicMock(to_dict=lambda: approved_module)]
        
        response = client.get("/api/v1/modules/search/test?limit=10")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["modules"]) == 1
        
        # Step 5: Module installation by company
        installation_response = {
            "id": 1,
            "module_id": module_id,
            "company_id": 1,
            "status": "installed",
            "installed_version": "1.0.0",
            "configuration": {"api_key": "company_key"}
        }
        
        installation_service.create_installation.return_value = installation_response
        
        installation_data = {
            "module_id": module_id,
            "company_id": 1,
            "configuration": {"api_key": "company_key"}
        }
        
        response = client.post("/api/v1/installations/", json=installation_data)
        assert response.status_code == status.HTTP_201_CREATED
        installation_id = response.json()["id"]
        
        # Step 6: Health check after installation
        health_result = {
            "installation_id": installation_id,
            "status": "healthy",
            "checks": {
                "module_loaded": True,
                "endpoints_responding": True,
                "dependencies_available": True
            }
        }
        
        installation_service.perform_health_check.return_value = health_result
        
        response = client.post(f"/api/v1/installations/{installation_id}/health-check")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
    
    def test_module_update_and_migration_workflow(self, client, mock_services, sample_module_data):
        """Test module update and migration workflow"""
        module_service = mock_services["module_service"]
        installation_service = mock_services["installation_service"]
        
        # Existing module v1.0.0
        existing_module = {
            "id": 1,
            "name": "test-module",
            "version": "1.0.0",
            "status": "approved"
        }
        
        # Step 1: Submit new version v1.1.0
        new_version_data = {**sample_module_data, "version": "1.1.0"}
        new_version_response = {
            "id": 2,
            "name": "test-module",
            "version": "1.1.0",
            "status": "pending"
        }
        
        module_service.validate_module_manifest.return_value = {"valid": True, "errors": []}
        module_service.get_module_by_name_version.return_value = None
        module_service.create_module.return_value = new_version_response
        
        response = client.post("/api/v1/modules/", json=new_version_data)
        assert response.status_code == status.HTTP_201_CREATED
        new_module_id = response.json()["id"]
        
        # Step 2: Approve new version
        approved_new_version = {**new_version_response, "status": "approved"}
        module_service.update_module_status.return_value = approved_new_version
        
        response = client.patch(f"/api/v1/modules/{new_module_id}/status", json={"status": "approved"})
        assert response.status_code == status.HTTP_200_OK
        
        # Step 3: Check existing installations
        existing_installation = {
            "id": 1,
            "module_id": 1,
            "company_id": 1,
            "installed_version": "1.0.0",
            "status": "installed"
        }
        
        installation_service.get_company_installations.return_value = [existing_installation]
        
        response = client.get("/api/v1/installations/company/1")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()[0]["installed_version"] == "1.0.0"
        
        # Step 4: Update installation to new version
        updated_installation = {
            **existing_installation,
            "module_id": new_module_id,
            "installed_version": "1.1.0"
        }
        
        installation_service.update_installation.return_value = updated_installation
        
        update_data = {
            "module_id": new_module_id,
            "configuration": {"api_key": "updated_key"}
        }
        
        response = client.put("/api/v1/installations/1", json=update_data)
        assert response.status_code == status.HTTP_200_OK


class TestMultiCompanyModuleManagement:
    """Test multi-company module management scenarios"""
    
    def test_multi_company_installation_workflow(self, client, mock_services, sample_module_data):
        """Test module installation across multiple companies"""
        module_service = mock_services["module_service"]
        installation_service = mock_services["installation_service"]
        
        # Single approved module
        module_response = {
            "id": 1,
            "name": "shared-module",
            "version": "1.0.0",
            "status": "approved",
            "is_public": True
        }
        
        module_service.get_module.return_value = module_response
        
        # Company 1 installation
        company1_installation = {
            "id": 1,
            "module_id": 1,
            "company_id": 1,
            "status": "installed",
            "configuration": {"company_name": "Company 1"}
        }
        
        installation_service.create_installation.return_value = company1_installation
        
        response = client.post("/api/v1/installations/", json={
            "module_id": 1,
            "company_id": 1,
            "configuration": {"company_name": "Company 1"}
        })
        assert response.status_code == status.HTTP_201_CREATED
        
        # Company 2 installation with different config
        company2_installation = {
            "id": 2,
            "module_id": 1,
            "company_id": 2,
            "status": "installed",
            "configuration": {"company_name": "Company 2", "custom_setting": True}
        }
        
        installation_service.create_installation.return_value = company2_installation
        
        response = client.post("/api/v1/installations/", json={
            "module_id": 1,
            "company_id": 2,
            "configuration": {"company_name": "Company 2", "custom_setting": True}
        })
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify module has multiple installations
        installation_service.get_module_installations.return_value = [
            company1_installation, company2_installation
        ]
        
        response = client.get("/api/v1/installations/module/1")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2
    
    def test_company_isolation_verification(self, client, mock_services):
        """Test that company data is properly isolated"""
        installation_service = mock_services["installation_service"]
        
        # Company 1 installations
        company1_installations = [
            {"id": 1, "module_id": 1, "company_id": 1},
            {"id": 2, "module_id": 2, "company_id": 1}
        ]
        
        installation_service.get_company_installations.return_value = company1_installations
        
        response = client.get("/api/v1/installations/company/1")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2
        assert all(inst["company_id"] == 1 for inst in response.json())
        
        # Company 2 installations (different set)
        company2_installations = [
            {"id": 3, "module_id": 1, "company_id": 2}
        ]
        
        installation_service.get_company_installations.return_value = company2_installations
        
        response = client.get("/api/v1/installations/company/2")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["company_id"] == 2


class TestModuleDependencyWorkflow:
    """Test module dependency management workflows"""
    
    def test_dependency_resolution_workflow(self, client, mock_services):
        """Test module dependency resolution during installation"""
        module_service = mock_services["module_service"]
        installation_service = mock_services["installation_service"]
        
        # Base module (dependency)
        base_module = {
            "id": 1,
            "name": "base-framework",
            "version": "1.0.0",
            "status": "approved"
        }
        
        # Dependent module
        dependent_module = {
            "id": 2,
            "name": "dependent-module",
            "version": "1.0.0",
            "status": "approved"
        }
        
        # Get module dependencies
        module_service.get_module_dependencies.return_value = [
            MagicMock(to_dict=lambda: {
                "name": "base-framework",
                "version": ">=1.0.0",
                "type": "module"
            })
        ]
        
        response = client.get("/api/v1/modules/2/dependencies")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["dependencies"]) == 1
        
        # Check base module dependents
        module_service.get_module_dependents.return_value = [
            MagicMock(to_dict=lambda: {
                "name": "dependent-module",
                "version": "1.0.0"
            })
        ]
        
        response = client.get("/api/v1/modules/1/dependents")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["dependents"]) == 1
        
        # Install base module first
        base_installation = {
            "id": 1,
            "module_id": 1,
            "company_id": 1,
            "status": "installed"
        }
        
        installation_service.create_installation.return_value = base_installation
        
        response = client.post("/api/v1/installations/", json={
            "module_id": 1,
            "company_id": 1,
            "configuration": {}
        })
        assert response.status_code == status.HTTP_201_CREATED
        
        # Install dependent module
        dependent_installation = {
            "id": 2,
            "module_id": 2,
            "company_id": 1,
            "status": "installed"
        }
        
        installation_service.create_installation.return_value = dependent_installation
        
        response = client.post("/api/v1/installations/", json={
            "module_id": 2,
            "company_id": 1,
            "configuration": {}
        })
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_dependency_conflict_resolution(self, client, mock_services):
        """Test handling of dependency conflicts"""
        installation_service = mock_services["installation_service"]
        
        # Attempt to uninstall module with active dependents
        installation_service.uninstall_module.side_effect = ValueError(
            "Cannot uninstall module with active dependencies: dependent-module"
        )
        
        response = client.delete("/api/v1/installations/1")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "active dependencies" in response.json()["detail"]


class TestModuleHealthAndMonitoring:
    """Test module health monitoring workflows"""
    
    def test_comprehensive_health_monitoring_workflow(self, client, mock_services):
        """Test comprehensive health monitoring across installations"""
        installation_service = mock_services["installation_service"]
        
        # Multiple installations with different health states
        installations = [
            {
                "id": 1,
                "module_id": 1,
                "company_id": 1,
                "status": "installed"
            },
            {
                "id": 2,
                "module_id": 2,
                "company_id": 1,
                "status": "installed"
            }
        ]
        
        installation_service.list_installations.return_value = (installations, 2)
        
        response = client.get("/api/v1/installations/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["installations"]) == 2
        
        # Health check for healthy installation
        healthy_result = {
            "installation_id": 1,
            "status": "healthy",
            "checks": {
                "module_loaded": True,
                "endpoints_responding": True,
                "dependencies_available": True
            },
            "response_time_ms": 45
        }
        
        installation_service.perform_health_check.return_value = healthy_result
        
        response = client.post("/api/v1/installations/1/health-check")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
        
        # Health check for unhealthy installation
        unhealthy_result = {
            "installation_id": 2,
            "status": "unhealthy",
            "checks": {
                "module_loaded": True,
                "endpoints_responding": False,
                "dependencies_available": True
            },
            "response_time_ms": 2000,
            "errors": ["Endpoint timeout after 2000ms"]
        }
        
        installation_service.perform_health_check.return_value = unhealthy_result
        
        response = client.post("/api/v1/installations/2/health-check")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "unhealthy"
        assert len(response.json()["errors"]) == 1


class TestErrorRecoveryWorkflows:
    """Test error recovery and rollback workflows"""
    
    def test_installation_failure_recovery(self, client, mock_services):
        """Test recovery from installation failures"""
        installation_service = mock_services["installation_service"]
        
        # Simulate installation failure
        installation_service.create_installation.side_effect = ValueError(
            "Module validation failed: Missing required dependencies"
        )
        
        response = client.post("/api/v1/installations/", json={
            "module_id": 1,
            "company_id": 1,
            "configuration": {}
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "validation failed" in response.json()["detail"]
        
        # Verify no installation was created
        installation_service.installation_exists.return_value = False
        
        response = client.get("/api/v1/installations/check/1/1")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["exists"] is False
    
    def test_module_rollback_workflow(self, client, mock_services):
        """Test module version rollback workflow"""
        installation_service = mock_services["installation_service"]
        
        # Current installation with v2.0.0 (problematic)
        current_installation = {
            "id": 1,
            "module_id": 2,
            "company_id": 1,
            "installed_version": "2.0.0",
            "status": "error"
        }
        
        installation_service.get_installation.return_value = current_installation
        
        # Rollback to v1.0.0
        rolled_back_installation = {
            **current_installation,
            "module_id": 1,
            "installed_version": "1.0.0",
            "status": "installed"
        }
        
        installation_service.update_installation.return_value = rolled_back_installation
        
        rollback_data = {
            "module_id": 1,  # Previous working version
            "configuration": {"rollback_reason": "Version 2.0.0 causing issues"}
        }
        
        response = client.put("/api/v1/installations/1", json=rollback_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["installed_version"] == "1.0.0"
        assert response.json()["status"] == "installed"