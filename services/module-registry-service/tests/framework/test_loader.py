"""
Tests for plugin loader functionality
"""
import pytest
import tempfile
import tarfile
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from app.framework.loader import PluginLoader, LoadedModule, ModuleLoadError, ModuleValidationError
from app.framework.manifest import ModuleManifest, ModuleEntryPoint, ModuleType
from app.models.module import Module
from app.models.installation import ModuleInstallation, InstallationStatus


@pytest.fixture
def sample_module_package():
    """Create a sample module package for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        module_dir = Path(temp_dir) / "test_module"
        module_dir.mkdir()
        
        # Create __init__.py
        init_file = module_dir / "__init__.py"
        init_file.write_text("""
# Test module
def main(config):
    return "Module initialized"

def initialize(config):
    return "Module initialized"

def cleanup():
    return "Module cleaned up"

def health_check():
    return {"status": "healthy"}
""")
        
        # Create main.py
        main_file = module_dir / "main.py"
        main_file.write_text("""
def test_function():
    return "test_result"

class TestHandler:
    def handle_event(self, event):
        return f"Handled: {event}"
""")
        
        # Create tar.gz package
        package_path = Path(temp_dir) / "test_module.tar.gz"
        with tarfile.open(package_path, "w:gz") as tar:
            tar.add(module_dir, arcname="test_module")
        
        with open(package_path, "rb") as f:
            package_data = f.read()
        
        yield package_data


@pytest.fixture
def sample_manifest():
    """Sample module manifest for testing"""
    return {
        "name": "test-module",
        "version": "1.0.0",
        "description": "Test module for loader testing",
        "author": "Test Author",
        "module_type": ModuleType.FULL_MODULE,
        "entry_points": [
            {
                "name": "main",
                "module_path": "test_module",
                "function": "main"
            },
            {
                "name": "initialize",
                "module_path": "test_module",
                "function": "initialize"
            },
            {
                "name": "cleanup",
                "module_path": "test_module",
                "function": "cleanup"
            },
            {
                "name": "health_check",
                "module_path": "test_module",
                "function": "health_check"
            }
        ]
    }


@pytest.fixture
def sample_module(sample_manifest, sample_module_package):
    """Sample module for testing"""
    module = Module(
        id=1,
        name="test-module",
        version="1.0.0",
        display_name="Test Module",
        description="Test module for loader testing",
        author="Test Author",
        manifest=sample_manifest,
        package_data=sample_module_package
    )
    return module


@pytest.fixture
def sample_installation():
    """Sample installation for testing"""
    installation = ModuleInstallation(
        id=1,
        module_id=1,
        company_id=1,
        status=InstallationStatus.INSTALLED,
        installed_version="1.0.0",
        installed_by="test_user",
        configuration={"test_config": "test_value"}
    )
    return installation


@pytest.fixture
def plugin_loader_instance():
    """Plugin loader instance for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        loader = PluginLoader(storage_path=temp_dir)
        yield loader


@pytest.mark.asyncio
async def test_extract_module_package(plugin_loader_instance, sample_module):
    """Test module package extraction"""
    module_dir = await plugin_loader_instance.extract_module_package(sample_module)
    
    assert module_dir.exists()
    assert module_dir.is_dir()
    assert (module_dir / "test_module" / "__init__.py").exists()
    assert (module_dir / "test_module" / "main.py").exists()


@pytest.mark.asyncio
async def test_extract_module_package_no_data(plugin_loader_instance):
    """Test module package extraction with no package data"""
    module = Module(
        id=1,
        name="test-module",
        version="1.0.0",
        manifest={}
    )
    
    with pytest.raises(ModuleLoadError, match="has no package data"):
        await plugin_loader_instance.extract_module_package(module)


def test_validate_module_structure(plugin_loader_instance, sample_manifest):
    """Test module structure validation"""
    with tempfile.TemporaryDirectory() as temp_dir:
        module_dir = Path(temp_dir)
        
        # Create valid structure
        (module_dir / "__init__.py").touch()
        
        manifest = ModuleManifest(**sample_manifest)
        assert plugin_loader_instance.validate_module_structure(module_dir, manifest)
        
        # Test with no Python files
        (module_dir / "__init__.py").unlink()
        
        with pytest.raises(ModuleValidationError, match="must contain __init__.py or Python files"):
            plugin_loader_instance.validate_module_structure(module_dir, manifest)


@pytest.mark.asyncio
async def test_load_module_python(plugin_loader_instance, sample_manifest):
    """Test Python module loading"""
    with tempfile.TemporaryDirectory() as temp_dir:
        module_dir = Path(temp_dir)
        
        # Create test module
        init_file = module_dir / "__init__.py"
        init_file.write_text("""
def test_function():
    return "success"
""")
        
        manifest = ModuleManifest(**sample_manifest)
        python_module = await plugin_loader_instance.load_module_python(module_dir, manifest)
        
        assert python_module is not None
        assert hasattr(python_module, "test_function")
        assert python_module.test_function() == "success"


def test_resolve_entry_points(plugin_loader_instance, sample_manifest):
    """Test entry point resolution"""
    # Create mock Python module
    mock_module = MagicMock()
    mock_module.main = MagicMock(return_value="main_result")
    mock_module.initialize = MagicMock(return_value="init_result")
    
    manifest = ModuleManifest(**sample_manifest)
    entry_points = plugin_loader_instance.resolve_entry_points(mock_module, manifest)
    
    assert "main" in entry_points
    assert "initialize" in entry_points
    assert callable(entry_points["main"])
    assert callable(entry_points["initialize"])


def test_resolve_entry_points_missing_function(plugin_loader_instance, sample_manifest):
    """Test entry point resolution with missing function"""
    mock_module = MagicMock()
    # Don't add the main function
    
    manifest = ModuleManifest(**sample_manifest)
    
    with pytest.raises(ModuleLoadError, match="Could not resolve entry point"):
        plugin_loader_instance.resolve_entry_points(mock_module, manifest)


@pytest.mark.asyncio
async def test_initialize_module(plugin_loader_instance, sample_installation):
    """Test module initialization"""
    # Create mock loaded module
    mock_python_module = MagicMock()
    mock_main = AsyncMock(return_value="initialized")
    mock_init = MagicMock(return_value="initialized")
    
    loaded_module = LoadedModule(
        module_id=1,
        module_name="test-module",
        module_version="1.0.0",
        manifest=ModuleManifest(
            name="test-module",
            version="1.0.0",
            description="Test",
            author="Test"
        ),
        python_module=mock_python_module,
        installation=sample_installation
    )
    
    loaded_module.entry_points = {
        "main": mock_main,
        "initialize": mock_init
    }
    
    result = await plugin_loader_instance.initialize_module(loaded_module)
    
    assert result is True
    assert loaded_module.is_initialized is True
    mock_main.assert_called_once_with(sample_installation.configuration)
    mock_init.assert_called_once_with(sample_installation.configuration)


@pytest.mark.asyncio
async def test_initialize_module_error(plugin_loader_instance, sample_installation):
    """Test module initialization with error"""
    mock_python_module = MagicMock()
    mock_main = AsyncMock(side_effect=Exception("Initialization failed"))
    
    loaded_module = LoadedModule(
        module_id=1,
        module_name="test-module",
        module_version="1.0.0",
        manifest=ModuleManifest(
            name="test-module",
            version="1.0.0",
            description="Test",
            author="Test"
        ),
        python_module=mock_python_module,
        installation=sample_installation
    )
    
    loaded_module.entry_points = {"main": mock_main}
    
    with pytest.raises(ModuleLoadError, match="Module initialization failed"):
        await plugin_loader_instance.initialize_module(loaded_module)


@pytest.mark.asyncio
async def test_load_module_complete(plugin_loader_instance, sample_module, sample_installation):
    """Test complete module loading process"""
    loaded_module = await plugin_loader_instance.load_module(sample_module, sample_installation)
    
    assert loaded_module.module_id == sample_module.id
    assert loaded_module.module_name == sample_module.name
    assert loaded_module.module_version == sample_module.version
    assert loaded_module.python_module is not None
    assert len(loaded_module.entry_points) > 0
    assert "main" in loaded_module.entry_points


@pytest.mark.asyncio
async def test_load_module_without_package(plugin_loader_instance, sample_installation):
    """Test loading module without package (configuration only)"""
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
    
    loaded_module = await plugin_loader_instance.load_module(module, sample_installation)
    
    assert loaded_module.python_module is None
    assert len(loaded_module.entry_points) == 0


@pytest.mark.asyncio
async def test_unload_module(plugin_loader_instance, sample_module, sample_installation):
    """Test module unloading"""
    # Load module first
    loaded_module = await plugin_loader_instance.load_module(sample_module, sample_installation)
    module_id = loaded_module.module_id
    
    # Unload module
    result = await plugin_loader_instance.unload_module(module_id)
    
    assert result is True
    assert module_id not in plugin_loader_instance.loaded_modules
    assert sample_module.name not in plugin_loader_instance.module_paths


@pytest.mark.asyncio
async def test_unload_module_not_loaded(plugin_loader_instance):
    """Test unloading module that's not loaded"""
    result = await plugin_loader_instance.unload_module(999)
    
    assert result is False


@pytest.mark.asyncio
async def test_reload_module(plugin_loader_instance, sample_module, sample_installation):
    """Test module reloading"""
    # Load module first
    loaded_module = await plugin_loader_instance.load_module(sample_module, sample_installation)
    module_id = loaded_module.module_id
    
    # Create new version
    new_module = Module(
        id=module_id,
        name=sample_module.name,
        version="2.0.0",
        display_name=sample_module.display_name,
        manifest=sample_module.manifest,
        package_data=sample_module.package_data
    )
    
    new_installation = ModuleInstallation(
        id=sample_installation.id,
        module_id=module_id,
        company_id=sample_installation.company_id,
        status=InstallationStatus.INSTALLED,
        installed_version="2.0.0",
        installed_by=sample_installation.installed_by,
        configuration={"updated_config": "new_value"}
    )
    
    # Reload module
    reloaded_module = await plugin_loader_instance.reload_module(module_id, new_module, new_installation)
    
    assert reloaded_module.module_version == "2.0.0"
    assert reloaded_module.installation.configuration["updated_config"] == "new_value"


def test_get_loaded_module(plugin_loader_instance):
    """Test getting loaded module"""
    # Add mock loaded module
    mock_loaded_module = MagicMock()
    plugin_loader_instance.loaded_modules[1] = mock_loaded_module
    
    result = plugin_loader_instance.get_loaded_module(1)
    assert result == mock_loaded_module
    
    result = plugin_loader_instance.get_loaded_module(999)
    assert result is None


def test_is_module_loaded(plugin_loader_instance):
    """Test checking if module is loaded"""
    plugin_loader_instance.loaded_modules[1] = MagicMock()
    
    assert plugin_loader_instance.is_module_loaded(1) is True
    assert plugin_loader_instance.is_module_loaded(999) is False


@pytest.mark.asyncio
async def test_health_check_module(plugin_loader_instance, sample_installation):
    """Test module health check"""
    # Test module not loaded
    result = await plugin_loader_instance.health_check_module(999)
    assert result["status"] == "not_loaded"
    
    # Test module with health check entry point
    mock_python_module = MagicMock()
    mock_health_check = AsyncMock(return_value={"status": "healthy", "custom": "data"})
    
    loaded_module = LoadedModule(
        module_id=1,
        module_name="test-module",
        module_version="1.0.0",
        manifest=ModuleManifest(
            name="test-module",
            version="1.0.0",
            description="Test",
            author="Test"
        ),
        python_module=mock_python_module,
        installation=sample_installation
    )
    
    loaded_module.entry_points = {"health_check": mock_health_check}
    loaded_module.is_initialized = True
    plugin_loader_instance.loaded_modules[1] = loaded_module
    
    result = await plugin_loader_instance.health_check_module(1)
    assert result["status"] == "healthy"
    assert result["custom"] == "data"
    
    # Test module without health check entry point
    loaded_module.entry_points = {}
    result = await plugin_loader_instance.health_check_module(1)
    assert result["status"] == "healthy"
    assert result["initialized"] is True


@pytest.mark.asyncio
async def test_shutdown(plugin_loader_instance, sample_module, sample_installation):
    """Test plugin loader shutdown"""
    # Load a module first
    await plugin_loader_instance.load_module(sample_module, sample_installation)
    
    assert len(plugin_loader_instance.loaded_modules) > 0
    
    # Shutdown
    await plugin_loader_instance.shutdown()
    
    assert len(plugin_loader_instance.loaded_modules) == 0