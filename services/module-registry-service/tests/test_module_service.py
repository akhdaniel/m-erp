"""
Tests for module service
"""
import pytest
from app.services.module_service import ModuleService
from app.schemas.module import ModuleCreate, ModuleUpdate, ModuleStatusUpdate
from app.models.module import ModuleStatus, ModuleType


@pytest.mark.asyncio
async def test_create_module(test_db_session, sample_module_data):
    """Test creating a module"""
    service = ModuleService(test_db_session)
    module_data = ModuleCreate(**sample_module_data)
    
    module = await service.create_module(module_data)
    
    assert module.id is not None
    assert module.name == sample_module_data["name"]
    assert module.version == sample_module_data["version"]
    assert module.status == ModuleStatus.REGISTERED
    assert module.manifest == sample_module_data["manifest"]


@pytest.mark.asyncio
async def test_get_module(test_db_session, sample_module):
    """Test getting a module by ID"""
    service = ModuleService(test_db_session)
    
    module = await service.get_module(sample_module.id)
    
    assert module is not None
    assert module.id == sample_module.id
    assert module.name == sample_module.name


@pytest.mark.asyncio
async def test_get_module_not_found(test_db_session):
    """Test getting a non-existent module"""
    service = ModuleService(test_db_session)
    
    module = await service.get_module(9999)
    
    assert module is None


@pytest.mark.asyncio
async def test_get_module_by_name_version(test_db_session, sample_module):
    """Test getting a module by name and version"""
    service = ModuleService(test_db_session)
    
    module = await service.get_module_by_name_version(sample_module.name, sample_module.version)
    
    assert module is not None
    assert module.id == sample_module.id
    assert module.name == sample_module.name
    assert module.version == sample_module.version


@pytest.mark.asyncio
async def test_list_modules(test_db_session, sample_module):
    """Test listing modules"""
    service = ModuleService(test_db_session)
    
    modules, total = await service.list_modules()
    
    assert total == 1
    assert len(modules) == 1
    assert modules[0].id == sample_module.id


@pytest.mark.asyncio
async def test_list_modules_with_filters(test_db_session, sample_module):
    """Test listing modules with filters"""
    service = ModuleService(test_db_session)
    
    # Filter by status
    modules, total = await service.list_modules(status=ModuleStatus.APPROVED)
    assert total == 1
    assert len(modules) == 1
    
    # Filter by module type
    modules, total = await service.list_modules(module_type=ModuleType.FULL_MODULE)
    assert total == 1
    assert len(modules) == 1
    
    # Filter by search term
    modules, total = await service.list_modules(search="test")
    assert total == 1
    assert len(modules) == 1
    
    # Filter with no results
    modules, total = await service.list_modules(status=ModuleStatus.REJECTED)
    assert total == 0
    assert len(modules) == 0


@pytest.mark.asyncio
async def test_update_module(test_db_session, sample_module):
    """Test updating a module"""
    service = ModuleService(test_db_session)
    update_data = ModuleUpdate(
        display_name="Updated Test Module",
        description="Updated description"
    )
    
    updated_module = await service.update_module(sample_module.id, update_data)
    
    assert updated_module is not None
    assert updated_module.display_name == "Updated Test Module"
    assert updated_module.description == "Updated description"
    assert updated_module.name == sample_module.name  # Unchanged


@pytest.mark.asyncio
async def test_update_module_status(test_db_session, sample_module):
    """Test updating module status"""
    service = ModuleService(test_db_session)
    status_data = ModuleStatusUpdate(
        status=ModuleStatus.REJECTED,
        validation_errors={"error": "Invalid manifest"}
    )
    
    updated_module = await service.update_module_status(sample_module.id, status_data)
    
    assert updated_module is not None
    assert updated_module.status == ModuleStatus.REJECTED
    assert updated_module.validation_errors == {"error": "Invalid manifest"}


@pytest.mark.asyncio
async def test_delete_module(test_db_session, sample_module):
    """Test deleting a module (soft delete)"""
    service = ModuleService(test_db_session)
    
    result = await service.delete_module(sample_module.id)
    
    assert result is True
    
    # Module should still exist but be inactive
    module = await service.get_module(sample_module.id)
    assert module is not None
    assert module.is_active is False


@pytest.mark.asyncio
async def test_get_module_dependencies(test_db_session, sample_module, sample_dependency):
    """Test getting module dependencies"""
    service = ModuleService(test_db_session)
    
    dependencies = await service.get_module_dependencies(sample_module.id)
    
    assert len(dependencies) == 1
    assert dependencies[0].id == sample_dependency.id
    assert dependencies[0].dependency_name == "business-object-framework"


@pytest.mark.asyncio
async def test_validate_module_manifest(test_db_session):
    """Test module manifest validation"""
    service = ModuleService(test_db_session)
    
    # Valid manifest
    valid_manifest = {
        "name": "test-module",
        "version": "1.0.0",
        "description": "Test module",
        "author": "Test Author",
        "dependencies": [
            {"name": "dep1", "version": ">=1.0.0"}
        ],
        "entry_points": {
            "main": "module.main:main"
        },
        "endpoints": [
            {"path": "/test", "method": "GET"}
        ]
    }
    
    result = await service.validate_module_manifest(valid_manifest)
    assert result["valid"] is True
    assert len(result["errors"]) == 0
    
    # Invalid manifest (missing required fields)
    invalid_manifest = {
        "name": "test-module"
        # Missing required fields
    }
    
    result = await service.validate_module_manifest(invalid_manifest)
    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert "version" in result["errors"]
    assert "description" in result["errors"]
    assert "author" in result["errors"]


@pytest.mark.asyncio
async def test_search_modules(test_db_session, sample_module):
    """Test searching modules"""
    service = ModuleService(test_db_session)
    
    # Search by name
    modules = await service.search_modules("test")
    assert len(modules) == 1
    assert modules[0].id == sample_module.id
    
    # Search by author
    modules = await service.search_modules("Test Author")
    assert len(modules) == 1
    assert modules[0].id == sample_module.id
    
    # Search with no results
    modules = await service.search_modules("nonexistent")
    assert len(modules) == 0