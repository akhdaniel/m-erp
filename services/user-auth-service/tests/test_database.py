import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db


@pytest.mark.asyncio
@pytest.mark.unit
async def test_database_session_creation(test_db_session: AsyncSession):
  """Test that database session is created correctly."""
  assert isinstance(test_db_session, AsyncSession)
  assert test_db_session.is_active


@pytest.mark.unit
def test_get_db_dependency():
  """Test that get_db dependency function exists and is callable."""
  assert callable(get_db)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_database_connection(test_db_session: AsyncSession):
  """Test that database connection works correctly."""
  # Execute a simple query to test connection
  from sqlalchemy import text
  result = await test_db_session.execute(text("SELECT 1 as test_value"))
  row = result.fetchone()
  
  assert row is not None
  assert row[0] == 1