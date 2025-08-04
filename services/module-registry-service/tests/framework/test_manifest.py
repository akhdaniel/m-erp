"""
Tests for module manifest schema and validation
"""
import pytest
from app.framework.manifest import (
    ModuleManifest, ModuleDependency, ModuleEndpoint, ModuleEventHandler,
    ModuleConfiguration, ModuleEntryPoint, ModulePermission,
    ManifestValidator, ModuleType, DependencyType, EndpointMethod, EventType
)


def test_module_dependency_validation():
    """Test module dependency validation"""
    # Valid dependency
    dep = ModuleDependency(
        name="test-dependency",
        version=">=1.0.0,<2.0.0",
        type=DependencyType.MODULE,
        optional=False,
        description="Test dependency"
    )
    assert dep.name == "test-dependency"
    assert dep.version == ">=1.0.0,<2.0.0"
    
    # Invalid version constraint
    with pytest.raises(ValueError, match="Invalid version constraint"):
        ModuleDependency(
            name="test-dependency",
            version="invalid-version"
        )


def test_module_endpoint_validation():
    """Test module endpoint validation"""
    # Valid endpoint
    endpoint = ModuleEndpoint(
        path="/test",
        method=EndpointMethod.GET,
        handler="test_module.handlers:get_test",
        description="Test endpoint",
        requires_auth=True,
        company_scoped=True
    )
    assert endpoint.path == "/test"
    assert endpoint.method == EndpointMethod.GET
    
    # Invalid path (no leading slash)
    with pytest.raises(ValueError, match="Endpoint path must start with"):
        ModuleEndpoint(
            path="test",
            method=EndpointMethod.GET,
            handler="test_module.handlers:get_test"
        )
    
    # Invalid handler format
    with pytest.raises(ValueError, match="Handler must be in format"):
        ModuleEndpoint(
            path="/test",
            method=EndpointMethod.GET,
            handler="invalid-handler"
        )


def test_module_event_handler_validation():
    """Test module event handler validation"""
    # Valid event handler
    handler = ModuleEventHandler(
        event_type=EventType.BUSINESS_OBJECT,
        event_pattern="partner\\.(created|updated)",
        handler="test_module.handlers:handle_partner_event",
        priority=100
    )
    assert handler.event_type == EventType.BUSINESS_OBJECT
    assert handler.event_pattern == "partner\\.(created|updated)"
    
    # Invalid regex pattern
    with pytest.raises(ValueError, match="Invalid regex pattern"):
        ModuleEventHandler(
            event_type=EventType.BUSINESS_OBJECT,
            event_pattern="[invalid-regex",
            handler="test_module.handlers:handle_event"
        )


def test_module_configuration_validation():
    """Test module configuration validation"""
    # Valid configuration
    config = ModuleConfiguration(
        schema={
            "type": "object",
            "properties": {
                "api_key": {"type": "string"},
                "timeout": {"type": "integer", "default": 30}
            },
            "required": ["api_key"]
        },
        default_values={"timeout": 30},
        required_fields=["api_key"]
    )
    assert config.schema["type"] == "object"
    assert config.default_values["timeout"] == 30
    
    # Invalid schema (missing type)
    with pytest.raises(ValueError, match="Configuration schema must have a type field"):
        ModuleConfiguration(
            schema={"properties": {"api_key": {"type": "string"}}}
        )


def test_module_entry_point_validation():
    """Test module entry point validation"""
    # Valid entry point
    entry_point = ModuleEntryPoint(
        name="main",
        module_path="test_module.main",
        function="main",
        description="Main entry point"
    )
    assert entry_point.name == "main"
    assert entry_point.module_path == "test_module.main"
    
    # Invalid module path
    with pytest.raises(ValueError, match="Invalid module path format"):
        ModuleEntryPoint(
            name="main",
            module_path="invalid-module-path!",
            function="main"
        )
    
    # Invalid function name
    with pytest.raises(ValueError, match="Invalid function name format"):
        ModuleEntryPoint(
            name="main",
            module_path="test_module.main",
            function="123invalid"
        )


def test_module_manifest_validation():
    """Test complete module manifest validation"""
    # Valid manifest
    manifest_data = {
        "name": "test-module",
        "version": "1.0.0",
        "description": "Test module",
        "author": "Test Author",
        "author_email": "test@example.com",
        "license": "MIT",
        "module_type": ModuleType.FULL_MODULE,
        "dependencies": [
            {
                "name": "business-object-framework",
                "version": ">=1.0.0",
                "type": DependencyType.MODULE
            }
        ],
        "entry_points": [
            {
                "name": "main",
                "module_path": "test_module.main",
                "function": "main"
            }
        ],
        "endpoints": [
            {
                "path": "/test",
                "method": EndpointMethod.GET,
                "handler": "test_module.handlers:get_test"
            }
        ]
    }
    
    manifest = ModuleManifest(**manifest_data)
    assert manifest.name == "test-module"
    assert manifest.version == "1.0.0"
    assert len(manifest.dependencies) == 1
    assert len(manifest.entry_points) == 1
    assert len(manifest.endpoints) == 1
    
    # Invalid name (not kebab-case)
    with pytest.raises(ValueError, match="Module name must be lowercase kebab-case"):
        invalid_data = manifest_data.copy()
        invalid_data["name"] = "TestModule"
        ModuleManifest(**invalid_data)
    
    # Invalid version (not semantic versioning)
    with pytest.raises(ValueError, match="Version must follow semantic versioning"):
        invalid_data = manifest_data.copy()
        invalid_data["version"] = "1.0"
        ModuleManifest(**invalid_data)
    
    # Invalid email
    with pytest.raises(ValueError, match="Invalid email format"):
        invalid_data = manifest_data.copy()
        invalid_data["author_email"] = "invalid-email"
        ModuleManifest(**invalid_data)


def test_manifest_consistency_validation():
    """Test manifest consistency validation"""
    # Business object module without main entry point
    with pytest.raises(ValueError, match="Business object modules must have a \"main\" entry point"):
        ModuleManifest(
            name="test-module",
            version="1.0.0",
            description="Test module",
            author="Test Author",
            module_type=ModuleType.BUSINESS_OBJECT,
            entry_points=[]
        )
    
    # UI component module without UI endpoints
    with pytest.raises(ValueError, match="UI component modules should have UI endpoints"):
        ModuleManifest(
            name="test-module",
            version="1.0.0",
            description="Test module",
            author="Test Author",
            module_type=ModuleType.UI_COMPONENT,
            endpoints=[
                ModuleEndpoint(
                    path="/api/test",
                    method=EndpointMethod.GET,
                    handler="test_module.handlers:get_test"
                )
            ]
        )
    
    # Workflow module without event handlers
    with pytest.raises(ValueError, match="Workflow modules should have event handlers"):
        ModuleManifest(
            name="test-module",
            version="1.0.0",
            description="Test module",
            author="Test Author",
            module_type=ModuleType.WORKFLOW,
            event_handlers=[]
        )


def test_manifest_validator():
    """Test manifest validator utility functions"""
    # Valid manifest dict
    manifest_dict = {
        "name": "test-module",
        "version": "1.0.0",
        "description": "Test module",
        "author": "Test Author"
    }
    
    is_valid, errors = ManifestValidator.validate_manifest_dict(manifest_dict)
    assert is_valid
    assert len(errors) == 0
    
    # Invalid manifest dict
    invalid_dict = {
        "name": "",  # Invalid name
        "version": "invalid"  # Invalid version
    }
    
    is_valid, errors = ManifestValidator.validate_manifest_dict(invalid_dict)
    assert not is_valid
    assert len(errors) > 0


def test_manifest_yaml_validation():
    """Test YAML manifest validation"""
    yaml_content = """
name: test-module
version: 1.0.0
description: Test module for YAML validation
author: Test Author
module_type: full_module
dependencies:
  - name: business-object-framework
    version: ">=1.0.0"
    type: module
entry_points:
  - name: main
    module_path: test_module.main
    function: main
"""
    
    is_valid, errors, manifest = ManifestValidator.validate_manifest_yaml(yaml_content)
    assert is_valid
    assert len(errors) == 0
    assert manifest is not None
    assert manifest.name == "test-module"


def test_security_requirements_check():
    """Test security requirements checking"""
    manifest = ModuleManifest(
        name="test-module",
        version="1.0.0",
        description="Test module",
        author="Test Author",
        permissions=[
            ModulePermission(
                name="admin_access",
                description="Admin access permission"
            ),
            ModulePermission(
                name="user_read",
                description="User read permission"
            )
        ],
        requires_external_services=["external-api"],
        sandbox_enabled=False
    )
    
    warnings = ManifestValidator.check_security_requirements(manifest)
    
    # Should have warnings for dangerous permission, external services, and disabled sandbox
    assert len(warnings) >= 3
    assert any("dangerous permission" in w.lower() for w in warnings)
    assert any("external services" in w.lower() for w in warnings)
    assert any("sandbox" in w.lower() for w in warnings)


def test_manifest_to_dict():
    """Test manifest serialization to dictionary"""
    manifest = ModuleManifest(
        name="test-module",
        version="1.0.0",
        description="Test module",
        author="Test Author",
        dependencies=[
            ModuleDependency(
                name="test-dep",
                type=DependencyType.MODULE
            )
        ]
    )
    
    manifest_dict = manifest.to_dict()
    assert isinstance(manifest_dict, dict)
    assert manifest_dict["name"] == "test-module"
    assert manifest_dict["version"] == "1.0.0"
    assert "dependencies" in manifest_dict
    assert len(manifest_dict["dependencies"]) == 1


def test_manifest_dependency_validation():
    """Test manifest dependency validation against available modules"""
    manifest = ModuleManifest(
        name="test-module",
        version="1.0.0",
        description="Test module",
        author="Test Author",
        dependencies=[
            ModuleDependency(
                name="available-module",
                type=DependencyType.MODULE,
                optional=False
            ),
            ModuleDependency(
                name="missing-module",
                type=DependencyType.MODULE,
                optional=False
            ),
            ModuleDependency(
                name="optional-missing",
                type=DependencyType.MODULE,
                optional=True
            )
        ]
    )
    
    available_modules = ["available-module", "other-module"]
    missing_deps = manifest.validate_dependencies(available_modules)
    
    # Should only report missing required dependencies
    assert len(missing_deps) == 1
    assert "missing-module" in missing_deps[0]


def test_manifest_required_permissions():
    """Test getting required permissions from manifest"""
    manifest = ModuleManifest(
        name="test-module",
        version="1.0.0",
        description="Test module",
        author="Test Author",
        endpoints=[
            ModuleEndpoint(
                path="/test1",
                method=EndpointMethod.GET,
                handler="test_module.handlers:get_test1",
                permissions=["read_data"]
            ),
            ModuleEndpoint(
                path="/test2",
                method=EndpointMethod.POST,
                handler="test_module.handlers:post_test2",
                permissions=["write_data", "admin"]
            )
        ],
        permissions=[
            ModulePermission(
                name="module_admin",
                description="Module admin permission"
            )
        ]
    )
    
    required_perms = manifest.get_required_permissions()
    
    # Should include permissions from endpoints and module permissions
    expected_perms = {"read_data", "write_data", "admin", "module_admin"}
    assert set(required_perms) == expected_perms