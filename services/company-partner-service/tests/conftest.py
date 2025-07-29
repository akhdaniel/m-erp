import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


# Test database URL - using in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
  """Create an instance of the default event loop for the test session."""
  loop = asyncio.get_event_loop_policy().new_event_loop()
  yield loop
  loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db_engine():
  """Create a test database engine for each test function."""
  engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
  )
  
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  
  yield engine
  
  await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db_session(test_db_engine):
  """Create a test database session for each test function."""
  async_session_factory = sessionmaker(
    bind=test_db_engine,
    class_=AsyncSession,
    expire_on_commit=False,
  )
  
  async with async_session_factory() as session:
    yield session


@pytest_asyncio.fixture(scope="function")
async def test_client(test_db_session):
  """Create a test client with database dependency override."""
  
  async def override_get_db():
    yield test_db_session
  
  app.dependency_overrides[get_db] = override_get_db
  
  from httpx import ASGITransport
  async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    yield client
  
  # Clean up dependency override
  app.dependency_overrides.clear()


@pytest.fixture
def anyio_backend():
  """Configure the async backend for anyio."""
  return "asyncio"