"""Tests for the application root endpoints."""

from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hier-Config API"
    assert data["docs"] == "/api/docs"


def test_health(client: TestClient) -> None:
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
