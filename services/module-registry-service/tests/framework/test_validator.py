"""
Tests for module validation system
"""
import pytest
import tempfile
import ast
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from app.framework.validator import (
    ModuleValidator, SecurityValidator, DependencyValidator,
    ModuleValidationError, SecurityViolationError, DependencyValidationError
)
from app.framework.manifest import ModuleManifest, ModuleDependency, DependencyType
from app.models.module import Module


@pytest.fixture
def sample_manifest():
    """Sample module manifest for testing"""
    return {
        "name": "test-module",
        "version": "1.0.0",
        "description": "Test module for validation testing",
        "author": "Test Author",
        "dependencies": [
            {
                "name": "business-object-framework",
                "version": ">=1.0.0",
                "type": DependencyType.MODULE
            }
        ]
    }


@pytest.fixture
def sample_module(sample_manifest):
    """Sample module for testing"""
    return Module(
        id=1,
        name="test-module",
        version="1.0.0",
        display_name="Test Module",
        description="Test module for validation testing",
        author="Test Author",
        manifest=sample_manifest
    )


@pytest.fixture
def security_validator():
    """Security validator instance"""
    return SecurityValidator()


@pytest.fixture
def dependency_validator():
    """Dependency validator instance"""
    return DependencyValidator()


@pytest.fixture
def module_validator():
    """Module validator instance"""
    return ModuleValidator()


def test_security_validator_safe_code(security_validator):
    """Test security validation with safe code"""
    safe_code = """
def hello_world():
    return "Hello, World!"

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
"""
    
    issues = security_validator.analyze_python_code(safe_code)
    assert len(issues) == 0


def test_security_validator_dangerous_imports(security_validator):
    """Test security validation with dangerous imports"""
    dangerous_code = """
import os
import subprocess
import sys
from shutil import rmtree

def dangerous_function():
    os.system("rm -rf /")
    subprocess.call(["echo", "test"])
"""
    
    issues = security_validator.analyze_python_code(dangerous_code)
    assert len(issues) > 0
    
    # Check for specific dangerous imports
    import_issues = [issue for issue in issues if issue['type'] == 'dangerous_import']
    assert len(import_issues) >= 3  # os, subprocess, shutil


def test_security_validator_dangerous_functions(security_validator):
    """Test security validation with dangerous function calls"""
    dangerous_code = """
def bad_function():
    exec("print('hello')")
    eval("1 + 1")
    open("/etc/passwd", "r")
    compile("test", "test", "exec")
"""
    
    issues = security_validator.analyze_python_code(dangerous_code)
    assert len(issues) > 0
    
    # Check for dangerous function calls
    function_issues = [issue for issue in issues if issue['type'] == 'dangerous_function']
    assert len(function_issues) >= 4


def test_security_validator_file_operations(security_validator):
    """Test security validation with file operations"""
    file_code = """
def file_operations():
    with open("/tmp/test.txt", "w") as f:
        f.write("test")
    
    import pathlib
    pathlib.Path("/tmp/test").unlink()
"""
    
    issues = security_validator.analyze_python_code(file_code)
    file_issues = [issue for issue in issues if issue['type'] == 'file_operation']
    assert len(file_issues) >= 1


def test_security_validator_network_operations(security_validator):
    """Test security validation with network operations"""
    network_code = """
import socket
import urllib.request
import requests

def network_ops():
    socket.socket()
    urllib.request.urlopen("http://example.com")
    requests.get("http://example.com")
"""
    
    issues = security_validator.analyze_python_code(network_code)
    network_issues = [issue for issue in issues if issue['type'] == 'network_operation']
    assert len(network_issues) >= 3


def test_security_validator_invalid_syntax(security_validator):
    """Test security validation with invalid Python syntax"""
    invalid_code = """
def broken_function(
    # Missing closing parenthesis and colon
    return "test"
"""
    
    with pytest.raises(SecurityViolationError, match="Failed to parse Python code"):
        security_validator.analyze_python_code(invalid_code)


def test_security_validator_check_package_structure(security_validator):
    """Test package structure validation"""
    with tempfile.TemporaryDirectory() as temp_dir:
        module_dir = Path(temp_dir)
        
        # Create valid structure
        (module_dir / "__init__.py").write_text("# Init file")
        (module_dir / "main.py").write_text("def main(): pass")
        (module_dir / "handlers.py").write_text("def handle(): pass")
        
        issues = security_validator.check_package_structure(module_dir)
        assert len(issues) == 0
        
        # Add suspicious file
        (module_dir / "suspicious.exe").write_text("binary content")
        
        issues = security_validator.check_package_structure(module_dir)
        assert len(issues) > 0
        assert any("suspicious file" in issue['message'].lower() for issue in issues)


def test_dependency_validator_check_dependencies(dependency_validator):
    """Test dependency validation"""
    manifest = ModuleManifest(
        name="test-module",
        version="1.0.0",
        description="Test module",
        author="Test Author",
        dependencies=[
            ModuleDependency(
                name="available-module",
                type=DependencyType.MODULE
            ),
            ModuleDependency(
                name="missing-module",
                type=DependencyType.MODULE
            )
        ]
    )
    
    available_modules = ["available-module", "other-module"]
    
    missing_deps = dependency_validator.check_dependencies(manifest, available_modules)
    assert len(missing_deps) == 1
    assert missing_deps[0].name == "missing-module"


def test_dependency_validator_validate_version_constraints(dependency_validator):
    """Test version constraint validation"""
    # Valid constraints
    valid_constraints = [">=1.0.0", "~1.2.0", "^2.0.0", ">=1.0.0,<2.0.0"]
    
    for constraint in valid_constraints:
        assert dependency_validator.validate_version_constraint(constraint)
    
    # Invalid constraints
    invalid_constraints = ["invalid", ">>1.0.0", "~"]
    
    for constraint in invalid_constraints:
        assert not dependency_validator.validate_version_constraint(constraint)


def test_dependency_validator_check_circular_dependencies(dependency_validator):
    """Test circular dependency detection"""
    modules_with_deps = {
        "module-a": ["module-b"],
        "module-b": ["module-c"],
        "module-c": ["module-a"]  # Creates circular dependency
    }
    
    circular_deps = dependency_validator.check_circular_dependencies(modules_with_deps)
    assert len(circular_deps) > 0
    assert "module-a" in circular_deps[0]


@pytest.mark.asyncio
async def test_module_validator_validate_complete_module(module_validator, sample_module):
    """Test complete module validation"""
    with tempfile.TemporaryDirectory() as temp_dir:
        module_dir = Path(temp_dir)
        
        # Create valid module structure
        (module_dir / "__init__.py").write_text("""
def main(config):
    return "initialized"

def cleanup():
    return "cleaned"
""")
        (module_dir / "handlers.py").write_text("""
def get_test(request):
    return {"message": "test"}
""")
        
        available_modules = ["business-object-framework"]
        
        result = await module_validator.validate_module(
            sample_module, module_dir, available_modules
        )
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.security_issues) == 0


@pytest.mark.asyncio
async def test_module_validator_validation_with_security_issues(module_validator, sample_module):
    """Test module validation with security issues"""
    with tempfile.TemporaryDirectory() as temp_dir:
        module_dir = Path(temp_dir)
        
        # Create module with security issues
        (module_dir / "__init__.py").write_text("""
import os
import subprocess

def main(config):
    os.system("echo hello")
    return "initialized"
""")
        
        available_modules = ["business-object-framework"]
        
        result = await module_validator.validate_module(
            sample_module, module_dir, available_modules
        )
        
        assert not result.is_valid
        assert len(result.security_issues) > 0


@pytest.mark.asyncio
async def test_module_validator_validation_with_missing_dependencies(module_validator, sample_module):
    """Test module validation with missing dependencies"""
    with tempfile.TemporaryDirectory() as temp_dir:
        module_dir = Path(temp_dir)
        
        # Create valid module structure
        (module_dir / "__init__.py").write_text("def main(config): pass")
        
        # Empty available modules (missing dependency)
        available_modules = []
        
        result = await module_validator.validate_module(
            sample_module, module_dir, available_modules
        )
        
        assert not result.is_valid
        assert len(result.dependency_errors) > 0


@pytest.mark.asyncio
async def test_module_validator_validation_without_package(module_validator):
    """Test module validation without package data"""
    module = Module(
        id=1,
        name="config-only-module",
        version="1.0.0",
        display_name="Config Only Module",
        manifest={
            "name": "config-only-module",
            "version": "1.0.0",
            "description": "Configuration only module",
            "author": "Test Author"
        }
    )
    
    result = await module_validator.validate_module(module, None, [])
    
    assert result.is_valid
    assert len(result.errors) == 0


def test_security_validator_analyze_requirements():
    """Test requirements.txt analysis"""
    validator = SecurityValidator()
    
    requirements_content = """
requests==2.28.0
django>=3.2,<4.0
numpy
suspicious-package==999.0.0
"""
    
    issues = validator.analyze_requirements(requirements_content)
    
    # Should find issues with suspicious package or version patterns
    assert isinstance(issues, list)


@pytest.mark.asyncio
async def test_module_validator_validate_manifest_only(module_validator):
    """Test manifest-only validation"""
    manifest = ModuleManifest(
        name="test-module",
        version="1.0.0",
        description="Test module",
        author="Test Author"
    )
    
    available_modules = []
    
    result = await module_validator.validate_manifest(manifest, available_modules)
    
    assert result.is_valid
    assert len(result.errors) == 0


def test_security_validator_check_suspicious_patterns():
    """Test detection of suspicious code patterns"""
    validator = SecurityValidator()
    
    suspicious_code = """
import base64
import pickle

def decode_data(data):
    decoded = base64.b64decode(data)
    return pickle.loads(decoded)  # Dangerous deserialization

def execute_command():
    __import__('os').system('whoami')  # Dynamic import
"""
    
    issues = validator.analyze_python_code(suspicious_code)
    
    # Should detect pickle usage and dynamic imports
    dangerous_issues = [issue for issue in issues if 'pickle' in issue['message'].lower() or 'dynamic' in issue['message'].lower()]
    assert len(dangerous_issues) > 0


def test_dependency_validator_complex_version_checking():
    """Test complex version constraint validation"""
    validator = DependencyValidator()
    
    # Test complex version ranges
    complex_constraints = [
        ">=1.0.0,<2.0.0,!=1.5.0",
        "~=1.4.2",
        "==1.0.*",
        ">=2.2,==2.2.*"
    ]
    
    for constraint in complex_constraints:
        result = validator.validate_version_constraint(constraint)
        # These should be considered valid or at least not crash
        assert isinstance(result, bool)