"""Tests for platform and batch endpoints."""

from fastapi.testclient import TestClient


def test_list_platforms(client: TestClient) -> None:
    """Test listing all platforms."""
    response = client.get("/api/v1/platforms")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check that cisco_ios is in the list
    platform_names = [p["platform_name"] for p in data]
    assert "cisco_ios" in platform_names


def test_get_platform_rules(client: TestClient) -> None:
    """Test getting platform-specific rules."""
    response = client.get("/api/v1/platforms/cisco_ios/rules")
    assert response.status_code == 200
    data = response.json()
    assert data["platform_name"] == "cisco_ios"
    assert "negation_default_when" in data
    assert "ordering" in data


def test_validate_config(client: TestClient, sample_cisco_ios_config: str) -> None:
    """Test validating configuration."""
    response = client.post(
        "/api/v1/platforms/cisco_ios/validate", json={"config_text": sample_cisco_ios_config}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "cisco_ios"
    assert "is_valid" in data
    assert "warnings" in data
    assert "errors" in data


def test_validate_empty_config(client: TestClient) -> None:
    """Test validating empty configuration."""
    response = client.post("/api/v1/platforms/cisco_ios/validate", json={"config_text": ""})
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "cisco_ios"
    # Empty config should have warnings
    assert len(data["warnings"]) > 0 or not data["is_valid"]


def test_create_batch_job(
    client: TestClient, sample_cisco_ios_config: str, sample_cisco_ios_intended_config: str
) -> None:
    """Test creating a batch remediation job."""
    response = client.post(
        "/api/v1/batch/remediation",
        json={
            "device_configs": [
                {
                    "device_id": "router1",
                    "platform": "cisco_ios",
                    "running_config": sample_cisco_ios_config,
                    "intended_config": sample_cisco_ios_intended_config,
                },
                {
                    "device_id": "router2",
                    "platform": "cisco_ios",
                    "running_config": sample_cisco_ios_config,
                    "intended_config": sample_cisco_ios_intended_config,
                },
            ]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["total_devices"] == 2


def test_get_batch_job_status(
    client: TestClient, sample_cisco_ios_config: str, sample_cisco_ios_intended_config: str
) -> None:
    """Test getting batch job status."""
    # First, create a batch job
    create_response = client.post(
        "/api/v1/batch/remediation",
        json={
            "device_configs": [
                {
                    "device_id": "router1",
                    "platform": "cisco_ios",
                    "running_config": sample_cisco_ios_config,
                    "intended_config": sample_cisco_ios_intended_config,
                }
            ]
        },
    )
    assert create_response.status_code == 200
    job_id = create_response.json()["job_id"]

    # Get job status
    response = client.get(f"/api/v1/batch/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "status" in data
    assert "progress" in data


def test_get_batch_job_results(
    client: TestClient, sample_cisco_ios_config: str, sample_cisco_ios_intended_config: str
) -> None:
    """Test getting batch job results."""
    # First, create a batch job
    create_response = client.post(
        "/api/v1/batch/remediation",
        json={
            "device_configs": [
                {
                    "device_id": "router1",
                    "platform": "cisco_ios",
                    "running_config": sample_cisco_ios_config,
                    "intended_config": sample_cisco_ios_intended_config,
                }
            ]
        },
    )
    assert create_response.status_code == 200
    job_id = create_response.json()["job_id"]

    # Get job results
    response = client.get(f"/api/v1/batch/jobs/{job_id}/results")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "status" in data
    assert "results" in data
    assert "summary" in data
