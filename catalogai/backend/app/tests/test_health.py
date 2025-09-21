"""Tests for health check endpoint."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ..main import app
from ..db import get_session


# Create test database
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_health_check(client: TestClient):
    """Test health check endpoint returns 200."""
    response = client.get("/health/")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "model_loaded" in data
    assert "database_connected" in data
    assert "version" in data
    
    # Database should be connected in test
    assert data["database_connected"] is True


def test_health_check_structure(client: TestClient):
    """Test health check response structure."""
    response = client.get("/health/")
    data = response.json()
    
    # Check required fields
    required_fields = ["status", "timestamp", "model_loaded", "database_connected", "version"]
    for field in required_fields:
        assert field in data
    
    # Check data types
    assert isinstance(data["status"], str)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["model_loaded"], bool)
    assert isinstance(data["database_connected"], bool)
    assert isinstance(data["version"], str)


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "description" in data


def test_status_endpoint(client: TestClient):
    """Test status endpoint."""
    response = client.get("/status")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "model_available" in data
    assert data["status"] == "running"