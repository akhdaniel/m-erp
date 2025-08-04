"""
Tests for dependency resolution API endpoints
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.services.dependency_resolution_service import (
    DependencyConflict, ResolutionPlan, ConflictType
)


@pytest.fixture
def client():
    """Test client for API testing"""
    return TestClient(app)


@pytest.fixture
def mock_dependency_resolution_service():
    """Mock dependency resolution service"""
    with patch('app.routers.dependency_resolution.get_dependency_resolution_service') as mock_service:
        service_instance = AsyncMock()
        mock_service.return_value = service_instance
        yield service_instance


@pytest.fixture
def sample_conflicts():
    """Sample dependency conflicts for testing"""
    return [
        DependencyConflict(
            conflict_type=ConflictType.MISSING_DEPENDENCY,
            module_name="test-module",
            conflicting_module="missing-dependency",
            description="Required dependency 'missing-dependency' is not available",
            severity="critical",
            resolution_suggestions=["Install missing-dependency first"]
        ),
        DependencyConflict(
            conflict_type=ConflictType.VERSION_MISMATCH,
            module_name="test-module",
            conflicting_module="other-module",
            description="Version conflict between modules",
            severity="major",
            resolution_suggestions=["Update to compatible version"]
        )
    ]


@pytest.fixture
def sample_resolution_plan(sample_conflicts):
    """Sample resolution plan for testing"""
    return ResolutionPlan(
        install_order=[1, 2, 3],
        conflicts=sample_conflicts,
        warnings=["Module 'optional-dep' not found but marked as optional"],
        is_resolvable=False  # Due to critical conflict
    )


class TestDependencyAnalysis:
    """Test dependency analysis endpoint"""
    
    def test_analyze_dependencies_success(self, client, mock_dependency_resolution_service, sample_resolution_plan):
        """Test successful dependency analysis"""
        mock_dependency_resolution_service.analyze_module_dependencies.return_value = sample_resolution_plan
        
        request_data = {
            "module_id": 1,
            "company_id": 1,
            "target_modules": [2, 3]
        }
        
        response = client.post("/api/v2/dependencies/analyze", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert response_data["install_order"] == [1, 2, 3]
        assert len(response_data["conflicts"]) == 2
        assert response_data["conflicts"][0]["conflict_type"] == "missing_dependency"
        assert response_data["conflicts"][0]["severity"] == "critical"
        assert response_data["is_resolvable"] is False
        assert len(response_data["warnings"]) == 1
        
        mock_dependency_resolution_service.analyze_module_dependencies.assert_called_once_with(
            module_id=1,
            company_id=1,
            target_modules=[2, 3]
        )
    
    def test_analyze_dependencies_resolvable(self, client, mock_dependency_resolution_service):
        """Test dependency analysis with resolvable conflicts"""
        resolvable_plan = ResolutionPlan(
            install_order=[1, 2, 3],
            conflicts=[],
            warnings=[],
            is_resolvable=True
        )
        mock_dependency_resolution_service.analyze_module_dependencies.return_value = resolvable_plan
        
        request_data = {
            "module_id": 1,
            "company_id": 1
        }
        
        response = client.post("/api/v2/dependencies/analyze", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert response_data["is_resolvable"] is True
        assert len(response_data["conflicts"]) == 0
        assert len(response_data["install_order"]) == 3
    
    def test_analyze_dependencies_service_error(self, client, mock_dependency_resolution_service):
        """Test dependency analysis with service error"""
        mock_dependency_resolution_service.analyze_module_dependencies.side_effect = Exception("Database error")
        
        request_data = {
            "module_id": 1,
            "company_id": 1
        }
        
        response = client.post("/api/v2/dependencies/analyze", json=request_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Dependency analysis failed" in response.json()["detail"]


class TestConflictDetection:
    """Test conflict detection endpoint"""
    
    def test_detect_conflicts_success(self, client, mock_dependency_resolution_service, sample_conflicts):
        """Test successful conflict detection"""
        mock_dependency_resolution_service.detect_installation_conflicts.return_value = sample_conflicts
        
        request_data = {
            "module_ids": [1, 2, 3],
            "company_id": 1
        }
        
        response = client.post("/api/v2/dependencies/conflicts", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert len(response_data) == 2
        assert response_data[0]["conflict_type"] == "missing_dependency"
        assert response_data[0]["module_name"] == "test-module"
        assert response_data[0]["severity"] == "critical"
        assert response_data[1]["conflict_type"] == "version_mismatch"
        
        mock_dependency_resolution_service.detect_installation_conflicts.assert_called_once_with(
            module_ids=[1, 2, 3],
            company_id=1
        )
    
    def test_detect_conflicts_no_conflicts(self, client, mock_dependency_resolution_service):
        """Test conflict detection with no conflicts"""
        mock_dependency_resolution_service.detect_installation_conflicts.return_value = []
        
        request_data = {
            "module_ids": [1, 2],
            "company_id": 1
        }
        
        response = client.post("/api/v2/dependencies/conflicts", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert len(response_data) == 0
    
    def test_detect_conflicts_service_error(self, client, mock_dependency_resolution_service):
        """Test conflict detection with service error"""
        mock_dependency_resolution_service.detect_installation_conflicts.side_effect = Exception("Analysis error")
        
        request_data = {
            "module_ids": [1, 2, 3],
            "company_id": 1
        }
        
        response = client.post("/api/v2/dependencies/conflicts", json=request_data)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Conflict detection failed" in response.json()["detail"]


class TestResolutionSuggestions:
    """Test resolution suggestion endpoint"""
    
    def test_suggest_resolution_success(self, client, mock_dependency_resolution_service):
        """Test successful resolution suggestions"""
        suggestions = {
            "test-module": [
                "Install missing-dependency first",
                "Update to compatible version",
                "Check for alternative modules"
            ],
            "other-module": [
                "Update to compatible version",
                "Use version pinning in manifest"
            ]
        }
        mock_dependency_resolution_service.suggest_dependency_resolution.return_value = suggestions
        
        request_data = [
            {
                "conflict_type": "missing_dependency",
                "module_name": "test-module",
                "conflicting_module": "missing-dependency",
                "description": "Required dependency missing",
                "severity": "critical",
                "resolution_suggestions": ["Install missing-dependency first"]
            }
        ]
        
        response = client.post("/api/v2/dependencies/resolve", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert "test-module" in response_data
        assert len(response_data["test-module"]) == 3
        assert "Install missing-dependency first" in response_data["test-module"]
    
    def test_suggest_resolution_empty_conflicts(self, client, mock_dependency_resolution_service):
        """Test resolution suggestions with empty conflicts"""
        mock_dependency_resolution_service.suggest_dependency_resolution.return_value = {}
        
        response = client.post("/api/v2/dependencies/resolve", json=[])
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert response_data == {}


class TestUpgradeCompatibility:
    """Test upgrade compatibility endpoint"""
    
    def test_validate_upgrade_compatibility_success(self, client, mock_dependency_resolution_service):
        """Test successful upgrade compatibility check"""
        conflicts = [
            DependencyConflict(
                conflict_type=ConflictType.VERSION_MISMATCH,
                module_name="dependent-module",
                conflicting_module="target-module",
                description="Upgrade may break dependent module",
                severity="minor",
                resolution_suggestions=["Test dependent module with new version"]
            )
        ]
        mock_dependency_resolution_service.validate_upgrade_compatibility.return_value = conflicts
        
        request_data = {
            "module_id": 1,
            "new_version": "2.0.0",
            "company_id": 1
        }
        
        response = client.post("/api/v2/dependencies/upgrade-compatibility", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert len(response_data) == 1
        assert response_data[0]["conflict_type"] == "version_mismatch"
        assert response_data[0]["module_name"] == "dependent-module"
        assert response_data[0]["severity"] == "minor"
        
        mock_dependency_resolution_service.validate_upgrade_compatibility.assert_called_once_with(
            module_id=1,
            new_version="2.0.0",
            company_id=1
        )
    
    def test_validate_upgrade_compatibility_no_conflicts(self, client, mock_dependency_resolution_service):
        """Test upgrade compatibility with no conflicts"""
        mock_dependency_resolution_service.validate_upgrade_compatibility.return_value = []
        
        request_data = {
            "module_id": 1,
            "new_version": "1.1.0",
            "company_id": 1
        }
        
        response = client.post("/api/v2/dependencies/upgrade-compatibility", json=request_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert len(response_data) == 0


class TestDependencyGraph:
    """Test dependency graph endpoint"""
    
    def test_get_dependency_graph_success(self, client, mock_dependency_resolution_service):
        """Test successful dependency graph retrieval"""
        from app.services.dependency_resolution_service import DependencyNode
        
        # Mock dependency graph
        dependency_graph = {
            "module-a": DependencyNode(
                name="module-a",
                version="1.0.0",
                module_id=1,
                dependencies=["module-b"],
                optional_dependencies=[],
                conflicts_with=[],
                provides=["module-a", "feature-x"]
            ),
            "module-b": DependencyNode(
                name="module-b",
                version="1.0.0",
                module_id=2,
                dependencies=[],
                optional_dependencies=["module-c"],
                conflicts_with=[],
                provides=["module-b"]
            )
        }
        
        mock_dependency_resolution_service._build_dependency_graph.return_value = dependency_graph
        
        response = client.get("/api/v2/dependencies/graph/1")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert response_data["company_id"] == 1
        assert "graph" in response_data
        assert "statistics" in response_data
        
        graph = response_data["graph"]
        assert len(graph["nodes"]) == 2
        assert len(graph["edges"]) == 1
        
        # Check node structure
        nodes = {node["name"]: node for node in graph["nodes"]}
        assert "module-a" in nodes
        assert nodes["module-a"]["id"] == 1
        assert "feature-x" in nodes["module-a"]["provides"]
        
        # Check edge structure
        edge = graph["edges"][0]
        assert edge["from"] == 1
        assert edge["to"] == 2
        assert edge["type"] == "required"
        assert edge["dependency_name"] == "module-b"
        
        # Check statistics
        stats = response_data["statistics"]
        assert stats["total_modules"] == 2
        assert stats["total_dependencies"] == 1
        assert stats["modules_with_dependencies"] == 1
    
    def test_get_dependency_graph_with_optional(self, client, mock_dependency_resolution_service):
        """Test dependency graph with optional dependencies"""
        from app.services.dependency_resolution_service import DependencyNode
        
        dependency_graph = {
            "module-a": DependencyNode(
                name="module-a",
                version="1.0.0",
                module_id=1,
                dependencies=[],
                optional_dependencies=["module-b"],
                conflicts_with=[],
                provides=["module-a"]
            ),
            "module-b": DependencyNode(
                name="module-b",
                version="1.0.0",
                module_id=2,
                dependencies=[],
                optional_dependencies=[],
                conflicts_with=[],
                provides=["module-b"]
            )
        }
        
        mock_dependency_resolution_service._build_dependency_graph.return_value = dependency_graph
        
        response = client.get("/api/v2/dependencies/graph/1?include_optional=true")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        graph = response_data["graph"]
        assert len(graph["edges"]) == 1
        
        edge = graph["edges"][0]
        assert edge["type"] == "optional"


class TestDependencyValidation:
    """Test quick dependency validation endpoint"""
    
    def test_validate_module_dependencies_success(self, client, mock_dependency_resolution_service):
        """Test successful module dependency validation"""
        resolution_plan = ResolutionPlan(
            install_order=[1, 2, 3],
            conflicts=[
                DependencyConflict(
                    ConflictType.VERSION_MISMATCH,
                    "test-module",
                    "other-module",
                    "Minor version conflict",
                    "minor",
                    []
                )
            ],
            warnings=[],
            is_resolvable=True
        )
        mock_dependency_resolution_service.analyze_module_dependencies.return_value = resolution_plan
        
        response = client.get("/api/v2/dependencies/validate/1?company_id=1")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert response_data["module_id"] == 1
        assert response_data["is_installable"] is True
        assert response_data["critical_conflicts"] == 0
        assert response_data["total_conflicts"] == 1
        assert response_data["dependencies_resolved"] is True
    
    def test_validate_module_dependencies_critical_conflicts(self, client, mock_dependency_resolution_service):
        """Test module validation with critical conflicts"""
        resolution_plan = ResolutionPlan(
            install_order=[],
            conflicts=[
                DependencyConflict(
                    ConflictType.MISSING_DEPENDENCY,
                    "test-module",
                    "missing-dep",
                    "Critical dependency missing",
                    "critical",
                    []
                )
            ],
            warnings=[],
            is_resolvable=False
        )
        mock_dependency_resolution_service.analyze_module_dependencies.return_value = resolution_plan
        
        response = client.get("/api/v2/dependencies/validate/1?company_id=1")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        
        assert response_data["is_installable"] is False
        assert response_data["critical_conflicts"] == 1
        assert response_data["dependencies_resolved"] is False