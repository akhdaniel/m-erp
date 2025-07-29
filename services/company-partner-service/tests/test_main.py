"""
Tests for main application health checks and basic functionality.
"""

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint():
    """Test the health check endpoint returns correct status."""
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "company-partner-service"
    assert "timestamp" in data
    assert "version" in data


def test_health_endpoint_includes_dependencies():
    """Test health check includes database and auth service status."""
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "dependencies" in data
    assert "database" in data["dependencies"]


def test_root_endpoint():
    """Test the root endpoint returns service information."""
    from app.main import app
    
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Company & Partner Management Service"
    assert data["version"] is not None


def test_app_startup():
    """Test that the FastAPI app can be created and started."""
    from app.main import app
    
    assert app is not None
    assert app.title == "Company & Partner Management Service"