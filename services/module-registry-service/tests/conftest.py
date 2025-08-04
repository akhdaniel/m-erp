"""
Test configuration and fixtures
"""
import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient
from app.core.database import Base, get_db_session
from app.main import app
from app.models.module import Module, ModuleStatus, ModuleType
from app.models.installation import ModuleInstallation, InstallationStatus
from app.models.dependency import ModuleDependency, DependencyType


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db_session(test_engine):
    """Create test database session"""
    TestSessionLocal = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_db_session):
    """Create test HTTP client"""
    
    # Override database dependency
    async def override_get_db():
        yield test_db_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up dependency override
    app.dependency_overrides.clear()


@pytest.fixture
def sample_module_data():
    """Sample module data for testing"""
    return {
        "name": "test-module",
        "display_name": "Test Module",
        "description": "A test module for unit testing",
        "version": "1.0.0",
        "author": "Test Author",
        "author_email": "test@example.com",
        "license": "MIT",
        "homepage_url": "https://example.com",
        "documentation_url": "https://docs.example.com",
        "repository_url": "https://github.com/example/test-module",
        "module_type": ModuleType.FULL_MODULE,
        "minimum_framework_version": "1.0.0",
        "python_version": ">=3.12",
        "manifest": {
            "name": "test-module",
            "version": "1.0.0",
            "description": "A test module",
            "author": "Test Author",
            "dependencies": [
                {
                    "name": "business-object-framework",
                    "version": ">=1.0.0",
                    "type": "module"
                }
            ],
            "entry_points": {
                "main": "test_module.main:main"
            },
            "endpoints": [
                {
                    "path": "/test",
                    "method": "GET",
                    "handler": "test_module.handlers:get_test"
                }
            ]
        },
        "config_schema": {
            "type": "object",
            "properties": {
                "api_key": {
                    "type": "string",
                    "description": "API key for external service"
                },
                "timeout": {
                    "type": "integer",
                    "default": 30,
                    "description": "Request timeout in seconds"
                }
            },
            "required": ["api_key"]
        },
        "default_config": {
            "timeout": 30
        },
        "is_public": False,
        "requires_approval": True
    }


@pytest.fixture
def sample_installation_data():
    """Sample installation data for testing"""
    return {
        "module_id": 1,
        "company_id": 1,
        "configuration": {
            "api_key": "test-api-key",
            "timeout": 60
        }
    }


@pytest_asyncio.fixture
async def sample_module(test_db_session, sample_module_data):
    """Create a sample module in the database"""
    module = Module(
        name=sample_module_data["name"],
        display_name=sample_module_data["display_name"],
        description=sample_module_data["description"],
        version=sample_module_data["version"],
        author=sample_module_data["author"],
        author_email=sample_module_data["author_email"],
        license=sample_module_data["license"],
        homepage_url=sample_module_data["homepage_url"],
        documentation_url=sample_module_data["documentation_url"],
        repository_url=sample_module_data["repository_url"],
        module_type=sample_module_data["module_type"],
        minimum_framework_version=sample_module_data["minimum_framework_version"],
        python_version=sample_module_data["python_version"],
        manifest=sample_module_data["manifest"],
        config_schema=sample_module_data["config_schema"],
        default_config=sample_module_data["default_config"],
        is_public=sample_module_data["is_public"],
        requires_approval=sample_module_data["requires_approval"],
        status=ModuleStatus.APPROVED
    )
    
    test_db_session.add(module)
    await test_db_session.commit()
    await test_db_session.refresh(module)
    
    return module


@pytest_asyncio.fixture
async def sample_installation(test_db_session, sample_module, sample_installation_data):
    """Create a sample installation in the database"""
    installation = ModuleInstallation(
        module_id=sample_module.id,
        company_id=sample_installation_data["company_id"],
        installed_version=sample_module.version,
        installed_by="test-user",
        configuration=sample_installation_data["configuration"],
        status=InstallationStatus.INSTALLED
    )
    
    test_db_session.add(installation)
    await test_db_session.commit()
    await test_db_session.refresh(installation)
    
    return installation


@pytest_asyncio.fixture
async def sample_dependency(test_db_session, sample_module):
    """Create a sample dependency in the database"""
    dependency = ModuleDependency(
        module_id=sample_module.id,
        dependency_type=DependencyType.MODULE,
        dependency_name="business-object-framework",
        version_constraint=">=1.0.0",
        is_optional=False,
        description="Core business object framework"
    )
    
    test_db_session.add(dependency)
    await test_db_session.commit()
    await test_db_session.refresh(dependency)
    
    return dependency


# Event loop fixture for pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()