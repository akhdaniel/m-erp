"""
Tests for installation service
"""
import pytest
from app.services.installation_service import InstallationService
from app.schemas.installation import InstallationCreate, InstallationUpdate, InstallationStatusUpdate
from app.models.installation import InstallationStatus


@pytest.mark.asyncio
async def test_create_installation(test_db_session, sample_module, sample_installation_data):
    """Test creating an installation"""
    service = InstallationService(test_db_session)
    installation_data = InstallationCreate(**sample_installation_data)
    
    installation = await service.create_installation(installation_data, "test-user")
    
    assert installation.id is not None
    assert installation.module_id == sample_module.id
    assert installation.company_id == sample_installation_data["company_id"]
    assert installation.installed_by == "test-user"
    assert installation.status == InstallationStatus.PENDING
    assert installation.configuration == sample_installation_data["configuration"]


@pytest.mark.asyncio
async def test_create_installation_unapproved_module(test_db_session, sample_module_data, sample_installation_data):
    """Test creating installation for unapproved module"""
    from app.models.module import Module, ModuleStatus
    
    # Create unapproved module
    unapproved_module = Module(
        name="unapproved-module",
        display_name="Unapproved Module",
        version="1.0.0",
        author="Test Author",
        manifest=sample_module_data["manifest"],
        status=ModuleStatus.REGISTERED,  # Not approved
        requires_approval=True
    )
    test_db_session.add(unapproved_module)
    await test_db_session.commit()
    await test_db_session.refresh(unapproved_module)
    
    service = InstallationService(test_db_session)
    installation_data = InstallationCreate(
        module_id=unapproved_module.id,
        company_id=1,
        configuration={}
    )
    
    with pytest.raises(ValueError, match="Module must be approved"):
        await service.create_installation(installation_data, "test-user")


@pytest.mark.asyncio
async def test_get_installation(test_db_session, sample_installation):
    """Test getting an installation by ID"""
    service = InstallationService(test_db_session)
    
    installation = await service.get_installation(sample_installation.id)
    
    assert installation is not None
    assert installation.id == sample_installation.id
    assert installation.module_id == sample_installation.module_id


@pytest.mark.asyncio
async def test_get_installation_not_found(test_db_session):
    """Test getting a non-existent installation"""
    service = InstallationService(test_db_session)
    
    installation = await service.get_installation(9999)
    
    assert installation is None


@pytest.mark.asyncio
async def test_get_installation_by_module_company(test_db_session, sample_installation):
    """Test getting installation by module and company"""
    service = InstallationService(test_db_session)
    
    installation = await service.get_installation_by_module_company(
        sample_installation.module_id,
        sample_installation.company_id
    )
    
    assert installation is not None
    assert installation.id == sample_installation.id


@pytest.mark.asyncio
async def test_list_installations(test_db_session, sample_installation):
    """Test listing installations"""
    service = InstallationService(test_db_session)
    
    installations, total = await service.list_installations()
    
    assert total == 1
    assert len(installations) == 1
    assert installations[0].id == sample_installation.id


@pytest.mark.asyncio
async def test_list_installations_with_filters(test_db_session, sample_installation):
    """Test listing installations with filters"""
    service = InstallationService(test_db_session)
    
    # Filter by company
    installations, total = await service.list_installations(company_id=sample_installation.company_id)
    assert total == 1
    assert len(installations) == 1
    
    # Filter by module
    installations, total = await service.list_installations(module_id=sample_installation.module_id)
    assert total == 1
    assert len(installations) == 1
    
    # Filter by status
    installations, total = await service.list_installations(status=InstallationStatus.INSTALLED)
    assert total == 1
    assert len(installations) == 1
    
    # Filter with no results
    installations, total = await service.list_installations(company_id=9999)
    assert total == 0
    assert len(installations) == 0


@pytest.mark.asyncio
async def test_update_installation(test_db_session, sample_installation):
    """Test updating an installation"""
    service = InstallationService(test_db_session)
    update_data = InstallationUpdate(
        configuration={"api_key": "updated-key", "timeout": 120},
        is_enabled=False
    )
    
    updated_installation = await service.update_installation(sample_installation.id, update_data)
    
    assert updated_installation is not None
    assert updated_installation.configuration["api_key"] == "updated-key"
    assert updated_installation.configuration["timeout"] == 120
    assert updated_installation.is_enabled is False


@pytest.mark.asyncio
async def test_update_installation_status(test_db_session, sample_installation):
    """Test updating installation status"""
    service = InstallationService(test_db_session)
    status_data = InstallationStatusUpdate(
        status=InstallationStatus.FAILED,
        error_message="Installation failed due to missing dependencies",
        installation_log={"error": "Dependency not found"}
    )
    
    updated_installation = await service.update_installation_status(sample_installation.id, status_data)
    
    assert updated_installation is not None
    assert updated_installation.status == InstallationStatus.FAILED
    assert updated_installation.error_message == "Installation failed due to missing dependencies"
    assert "error" in updated_installation.installation_log


@pytest.mark.asyncio
async def test_uninstall_module(test_db_session, sample_installation):
    """Test uninstalling a module"""
    service = InstallationService(test_db_session)
    
    result = await service.uninstall_module(sample_installation.id)
    
    assert result is True
    
    # Installation should be marked as uninstalled
    installation = await service.get_installation(sample_installation.id)
    assert installation is not None
    assert installation.status == InstallationStatus.UNINSTALLED
    assert installation.is_active is False
    assert installation.uninstalled_at is not None


@pytest.mark.asyncio
async def test_perform_health_check(test_db_session, sample_installation):
    """Test performing health check"""
    service = InstallationService(test_db_session)
    
    result = await service.perform_health_check(sample_installation.id)
    
    assert result.status == "healthy"
    assert result.details["message"] == "Installation is active and enabled"
    assert result.last_check is not None
    
    # Check that installation was updated
    installation = await service.get_installation(sample_installation.id)
    assert installation.health_status == "healthy"
    assert installation.last_health_check is not None


@pytest.mark.asyncio
async def test_get_company_installations(test_db_session, sample_installation):
    """Test getting company installations"""
    service = InstallationService(test_db_session)
    
    installations = await service.get_company_installations(sample_installation.company_id)
    
    assert len(installations) == 1
    assert installations[0].id == sample_installation.id


@pytest.mark.asyncio
async def test_get_module_installations(test_db_session, sample_installation):
    """Test getting module installations"""
    service = InstallationService(test_db_session)
    
    installations = await service.get_module_installations(sample_installation.module_id)
    
    assert len(installations) == 1
    assert installations[0].id == sample_installation.id


@pytest.mark.asyncio
async def test_installation_exists(test_db_session, sample_installation):
    """Test checking if installation exists"""
    service = InstallationService(test_db_session)
    
    # Should exist
    exists = await service.installation_exists(
        sample_installation.module_id,
        sample_installation.company_id
    )
    assert exists is True
    
    # Should not exist
    exists = await service.installation_exists(9999, 9999)
    assert exists is False