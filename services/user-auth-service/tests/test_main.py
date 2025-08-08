import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.unit
async def test_health_check(test_client: AsyncClient):
  """Test the health check endpoint returns expected response."""
  response = await test_client.get("/health")
  
  assert response.status_code == 200
  data = response.json()
  
  assert data["status"] == "healthy"
  assert data["service"] == "User Authentication Service"
  assert data["version"] == "1.0.0"
  assert "environment" in data


@pytest.mark.unit
def test_app_creation():
  """Test that the FastAPI app is created correctly."""
  from app.main import app
  
  assert app.title == "User Authentication Service"
  assert app.description == "XERPIUM User Authentication Microservice"
  assert app.version == "1.0.0"