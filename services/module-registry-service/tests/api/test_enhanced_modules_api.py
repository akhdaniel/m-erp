"""
Tests for enhanced module registration endpoints
"""
import pytest
import io
import json
import tarfile
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.services.enhanced_module_service import ModuleRegistrationError, PackageValidationError


@pytest.fixture
def client():
    """Test client for API testing"""
    return TestClient(app)


@pytest.fixture
def sample_module_data():
    """Complete sample module data for enhanced registration"""
    return {
        "name": "enhanced-test-module",
        "version": "1.0.0",
        "display_name": "Enhanced Test Module",
        "description": "A comprehensive test module for enhanced API endpoints",
        "author": "Test Author",
        "author_email": "test@example.com",
        "license": "MIT",
        "homepage_url": "https://example.com/enhanced-module",
        "repository_url": "https://github.com/example/enhanced-module",
        "module_type": "full_module",
        "minimum_framework_version": "1.0.0",
        "python_version": ">=3.8",
        "config_schema": {
            "type": "object",
            "properties": {
                "api_key": {"type": "string"},
                "timeout": {"type": "integer", "default": 30}
            },
            "required": ["api_key"]
        },
        "default_config": {"timeout": 30},
        "is_public": True,
        "requires_approval": True,
        "manifest": {
            "name": "enhanced-test-module",
            "version": "1.0.0",
            "description": "A comprehensive test module for enhanced API endpoints",
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
                    "handler": "enhanced_test_module.handlers:get_test",
                    "description": "Enhanced test endpoint"
                }
            ],
            "event_handlers": [
                {
                    "event_type": "business_object",
                    "event_pattern": "partner\\.(created|updated)",
                    "handler": "enhanced_test_module.handlers:handle_partner_event"
                }
            ]
        }
    }


@pytest.fixture
def sample_package_data():
    """Sample package data with proper structure"""
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
        # Create a proper module structure
        files = {
            "enhanced_test_module/__init__.py": b'''
def main(config):
    """Main entry point"""
    return "Enhanced module loaded"

def initialize(config):
    """Initialize module"""
    return "Enhanced module initialized"

def cleanup():
    """Cleanup module"""
    return "Enhanced module cleaned up"
''',
            "enhanced_test_module/handlers.py": b'''
def get_test(request):
    """Test endpoint handler"""
    return {"message": "Enhanced test response"}

def handle_partner_event(event):
    """Partner event handler"""
    return f"Handled partner event: {event.event_type}"
''',
            "enhanced_test_module/models.py": b'''
class TestModel:
    """Test model for enhanced module"""
    
    def __init__(self, name: str):
        self.name = name
    
    def get_name(self) -> str:
        return self.name
''',
            "requirements.txt": b'''
requests>=2.25.0
pydantic>=1.8.0
'''
        }
        
        for filename, content in files.items():
            info = tarfile.TarInfo(name=filename)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    
    tar_buffer.seek(0)
    return tar_buffer.getvalue()


@pytest.fixture
def mock_enhanced_module_service():
    """Mock enhanced module service"""
    with patch('app.routers.enhanced_modules.get_enhanced_module_service') as mock_service:
        service_instance = AsyncMock()
        mock_service.return_value = service_instance
        yield service_instance


class TestModuleRegistrationWithValidation:
    """Test enhanced module registration with comprehensive validation"""
    
    def test_register_module_with_package_success(self, client, mock_enhanced_module_service, 
                                                sample_module_data, sample_package_data):
        """Test successful module registration with package"""
        # Mock validation result
        validation_result = MagicMock()
        validation_result.is_valid = True
        validation_result.security_issues = []
        validation_result.dependency_errors = []
        validation_result.validation_timestamp = None
        
        # Mock module response
        module_response = MagicMock()
        module_response.id = 1
        module_response.name = "enhanced-test-module"
        module_response.version = "1.0.0"
        module_response.display_name = "Enhanced Test Module"
        module_response.description = "A comprehensive test module"
        module_response.author = "Test Author"
        module_response.author_email = "test@example.com"
        module_response.license = "MIT"
        module_response.homepage_url = "https://example.com/enhanced-module"
        module_response.repository_url = "https://github.com/example/enhanced-module"
        module_response.status.value = "registered"
        module_response.is_public = True
        module_response.package_size = len(sample_package_data)
        module_response.package_hash = "abc123def456"
        module_response.created_at.isoformat.return_value = "2025-08-02T17:00:00Z"
        module_response.manifest = sample_module_data["manifest"]
        module_response.validation_summary = {}
        
        mock_enhanced_module_service.register_module_with_validation.return_value = (
            module_response, validation_result
        )
        
        # Prepare multipart form data
        files = {"package": ("enhanced-test-module.tar.gz", sample_package_data, "application/gzip")}
        data = {"module_data": json.dumps(sample_module_data)}
        
        response = client.post("/api/v2/modules/register", data=data, files=files)
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["name"] == "enhanced-test-module"
        assert response_data["version"] == "1.0.0"
        assert response_data["validation_summary"]["is_valid"] is True
        assert response_data["validation_summary"]["has_package"] is True
        
        mock_enhanced_module_service.register_module_with_validation.assert_called_once()
    
    def test_register_module_without_package_success(self, client, mock_enhanced_module_service, sample_module_data):
        """Test successful module registration without package (configuration only)"""
        # Mock validation result
        validation_result = MagicMock()
        validation_result.is_valid = True
        validation_result.security_issues = []
        validation_result.dependency_errors = []
        validation_result.validation_timestamp = None
        
        # Mock module response
        module_response = MagicMock()
        module_response.id = 2
        module_response.name = "config-only-module"
        module_response.version = "1.0.0"
        module_response.display_name = "Config Only Module"
        module_response.description = "Configuration only module"
        module_response.author = "Test Author"
        module_response.author_email = "test@example.com"
        module_response.license = "MIT"
        module_response.homepage_url = None
        module_response.repository_url = None
        module_response.status.value = "registered"
        module_response.is_public = True
        module_response.package_size = None
        module_response.package_hash = None
        module_response.created_at.isoformat.return_value = "2025-08-02T17:00:00Z"
        module_response.manifest = sample_module_data["manifest"]
        module_response.validation_summary = {}
        
        mock_enhanced_module_service.register_module_with_validation.return_value = (
            module_response, validation_result
        )
        
        data = {"module_data": json.dumps(sample_module_data)}
        
        response = client.post("/api/v2/modules/register", data=data)
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["validation_summary"]["has_package"] is False
    
    def test_register_module_invalid_json(self, client, mock_enhanced_module_service):
        """Test module registration with invalid JSON"""
        data = {"module_data": "invalid json {"}
        
        response = client.post("/api/v2/modules/register", data=data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Invalid module data format" in response.json()["detail"]
    
    def test_register_module_package_too_large(self, client, mock_enhanced_module_service, sample_module_data):
        """Test module registration with package too large"""
        # Create large package data
        large_package = b"x" * (51 * 1024 * 1024)  # 51MB
        
        files = {"package": ("large-module.tar.gz", large_package, "application/gzip")}
        data = {"module_data": json.dumps(sample_module_data)}
        
        response = client.post("/api/v2/modules/register", data=data, files=files)
        
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert "Package file too large" in response.json()["detail"]
    
    def test_register_module_validation_failure(self, client, mock_enhanced_module_service, 
                                              sample_module_data, sample_package_data):
        """Test module registration with validation failure"""
        mock_enhanced_module_service.register_module_with_validation.side_effect = ModuleRegistrationError(
            "Module validation failed: Missing required field: module_type"
        )
        
        files = {"package": ("test-module.tar.gz", sample_package_data, "application/gzip")}
        data = {"module_data": json.dumps(sample_module_data)}
        
        response = client.post("/api/v2/modules/register", data=data, files=files)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Module validation failed" in response.json()["detail"]
    
    def test_register_module_package_validation_error(self, client, mock_enhanced_module_service, 
                                                    sample_module_data, sample_package_data):
        """Test module registration with package validation error"""
        mock_enhanced_module_service.register_module_with_validation.side_effect = PackageValidationError(
            "Package must contain __init__.py file"
        )
        
        files = {"package": ("invalid-module.tar.gz", sample_package_data, "application/gzip")}
        data = {"module_data": json.dumps(sample_module_data)}
        
        response = client.post("/api/v2/modules/register", data=data, files=files)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Package validation error" in response.json()["detail"]


class TestPackageValidation:
    """Test package validation endpoints"""
    
    def test_validate_package_success(self, client, mock_enhanced_module_service, sample_package_data):
        """Test successful package validation"""
        mock_enhanced_module_service._extract_and_validate_package.return_value = "/tmp/test_module"
        mock_enhanced_module_service._validate_package_structure.return_value = None
        mock_enhanced_module_service._cleanup_extracted_package.return_value = None
        
        files = {"package": ("test-module.tar.gz", sample_package_data, "application/gzip")}
        data = {"module_name": "test-module"}
        
        response = client.post("/api/v2/modules/validate-package", data=data, files=files)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["valid"] is True
        assert response_data["structure_valid"] is True
        assert "Package structure is valid" in response_data["message"]
    
    def test_validate_package_invalid_structure(self, client, mock_enhanced_module_service, sample_package_data):
        """Test package validation with invalid structure"""
        mock_enhanced_module_service._extract_and_validate_package.side_effect = PackageValidationError(
            "Package must contain __init__.py file"
        )
        
        files = {"package": ("invalid-module.tar.gz", sample_package_data, "application/gzip")}
        data = {"module_name": "invalid-module"}
        
        response = client.post("/api/v2/modules/validate-package", data=data, files=files)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["valid"] is False
        assert "Package must contain __init__.py file" in response_data["error"]
    
    def test_validate_package_too_large(self, client, mock_enhanced_module_service):
        """Test package validation with package too large"""
        large_package = b"x" * (51 * 1024 * 1024)  # 51MB
        
        files = {"package": ("large-module.tar.gz", large_package, "application/gzip")}
        data = {"module_name": "large-module"}
        
        response = client.post("/api/v2/modules/validate-package", data=data, files=files)
        
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert "Package file too large" in response.json()["detail"]


class TestManifestValidation:
    """Test enhanced manifest validation"""
    
    def test_validate_manifest_success(self, client, mock_enhanced_module_service):
        """Test successful manifest validation"""
        mock_enhanced_module_service.validate_module_manifest.return_value = {
            "valid": True,
            "errors": [],
            "warnings": ["Consider adding more detailed documentation"]
        }
        mock_enhanced_module_service._get_available_module_names.return_value = ["business-object-framework"]
        
        manifest_data = {
            "name": "test-module",
            "version": "1.0.0",
            "description": "Test module",
            "author": "Test Author",
            "module_type": "full_module",
            "dependencies": [
                {
                    "name": "business-object-framework",
                    "version": ">=1.0.0",
                    "type": "module"
                }
            ]
        }
        
        response = client.post("/api/v2/modules/validate-manifest", json=manifest_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["valid"] is True
        assert len(response_data["warnings"]) >= 1
    
    def test_validate_manifest_with_missing_dependencies(self, client, mock_enhanced_module_service):
        """Test manifest validation with missing dependencies"""
        mock_enhanced_module_service.validate_module_manifest.return_value = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        mock_enhanced_module_service._get_available_module_names.return_value = []  # No available modules
        
        manifest_data = {
            "name": "test-module",
            "version": "1.0.0",
            "description": "Test module",
            "author": "Test Author",
            "module_type": "full_module",
            "dependencies": [
                {
                    "name": "missing-dependency",
                    "version": ">=1.0.0",
                    "type": "module"
                }
            ]
        }
        
        response = client.post("/api/v2/modules/validate-manifest", json=manifest_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["valid"] is True
        assert any("Missing dependencies" in warning for warning in response_data["warnings"])
        assert "dependency_info" in response_data
    
    def test_validate_manifest_invalid(self, client, mock_enhanced_module_service):
        """Test manifest validation with invalid manifest"""
        mock_enhanced_module_service.validate_module_manifest.return_value = {
            "valid": False,
            "errors": ["Missing required field: module_type"],
            "warnings": []
        }
        
        manifest_data = {
            "name": "test-module",
            "version": "1.0.0",
            "description": "Test module",
            "author": "Test Author"
            # Missing module_type
        }
        
        response = client.post("/api/v2/modules/validate-manifest", json=manifest_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["valid"] is False
        assert "Missing required field: module_type" in response_data["errors"]


class TestModuleValidationDetails:
    """Test module validation details endpoints"""
    
    def test_get_module_validation_details_success(self, client, mock_enhanced_module_service):
        """Test successful retrieval of module validation details"""
        validation_details = {
            "module_id": 1,
            "validation_summary": {
                "security_issues_count": 0,
                "dependency_errors_count": 0,
                "validation_timestamp": "2025-08-02T17:00:00Z"
            },
            "status": "approved",
            "package_hash": "abc123def456",
            "package_size": 1024,
            "created_at": "2025-08-02T16:00:00Z",
            "dependencies": [
                {
                    "name": "business-object-framework",
                    "type": "module",
                    "version_constraint": ">=1.0.0",
                    "is_optional": False
                }
            ]
        }
        
        mock_enhanced_module_service.get_module_validation_details.return_value = validation_details
        
        response = client.get("/api/v2/modules/1/validation")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["module_id"] == 1
        assert response_data["status"] == "approved"
        assert len(response_data["dependencies"]) == 1
    
    def test_get_module_validation_details_not_found(self, client, mock_enhanced_module_service):
        """Test module validation details when module not found"""
        mock_enhanced_module_service.get_module_validation_details.return_value = None
        
        response = client.get("/api/v2/modules/999/validation")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Module not found" in response.json()["detail"]


class TestModuleStatusUpdate:
    """Test enhanced module status update"""
    
    def test_update_module_status_success(self, client, mock_enhanced_module_service):
        """Test successful module status update"""
        updated_module = MagicMock()
        updated_module.id = 1
        updated_module.name = "test-module"
        updated_module.version = "1.0.0"
        updated_module.status.value = "approved"
        updated_module.status_reason = "Module approved after review"
        updated_module.updated_at.isoformat.return_value = "2025-08-02T17:00:00Z"
        updated_module.validation_summary = {"security_issues_count": 0}
        
        mock_enhanced_module_service.update_module_status.return_value = updated_module
        
        status_data = {
            "status": "approved",
            "reason": "Module approved after review"
        }
        
        response = client.patch("/api/v2/modules/1/status", json=status_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "approved"
        assert response_data["status_reason"] == "Module approved after review"
    
    def test_update_module_status_invalid_transition(self, client, mock_enhanced_module_service):
        """Test module status update with invalid transition"""
        mock_enhanced_module_service.update_module_status.side_effect = ValueError(
            "Invalid status transition from published to pending"
        )
        
        status_data = {
            "status": "pending",
            "reason": "Reverting status"
        }
        
        response = client.patch("/api/v2/modules/1/status", json=status_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid status transition" in response.json()["detail"]


class TestSecurityAndMonitoring:
    """Test security scanning and monitoring endpoints"""
    
    def test_trigger_security_scan_success(self, client, mock_enhanced_module_service):
        """Test triggering security scan"""
        module = MagicMock()
        module.id = 1
        module.name = "test-module"
        
        mock_enhanced_module_service.get_module.return_value = module
        
        response = client.post("/api/v2/modules/1/security-scan")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["module_id"] == 1
        assert response_data["scan_requested"] is True
    
    def test_trigger_security_scan_module_not_found(self, client, mock_enhanced_module_service):
        """Test triggering security scan for non-existent module"""
        mock_enhanced_module_service.get_module.return_value = None
        
        response = client.post("/api/v2/modules/999/security-scan")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Module not found" in response.json()["detail"]
    
    def test_get_registration_statistics(self, client, mock_enhanced_module_service):
        """Test getting registration statistics"""
        response = client.get("/api/v2/modules/stats/registration?days=30")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "period_days" in response_data
        assert "total_registrations" in response_data
        assert "successful_registrations" in response_data