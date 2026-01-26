"""Tests for multi-device reporting endpoints."""

from fastapi.testclient import TestClient


def test_create_report(
    client: TestClient, sample_cisco_ios_config: str, sample_cisco_ios_intended_config: str
) -> None:
    """Test creating a multi-device report."""
    response = client.post(
        "/api/v1/reports",
        json={
            "remediations": [
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
    assert "report_id" in data
    assert data["total_devices"] == 2


def test_get_report_summary(
    client: TestClient, sample_cisco_ios_config: str, sample_cisco_ios_intended_config: str
) -> None:
    """Test getting report summary."""
    # First, create a report
    create_response = client.post(
        "/api/v1/reports",
        json={
            "remediations": [
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
    report_id = create_response.json()["report_id"]

    # Get summary
    response = client.get(f"/api/v1/reports/{report_id}/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_devices" in data
    assert "devices_with_changes" in data
    assert "total_changes" in data


def test_get_report_changes(
    client: TestClient, sample_cisco_ios_config: str, sample_cisco_ios_intended_config: str
) -> None:
    """Test getting detailed change analysis."""
    # First, create a report
    create_response = client.post(
        "/api/v1/reports",
        json={
            "remediations": [
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
    report_id = create_response.json()["report_id"]

    # Get changes
    response = client.get(f"/api/v1/reports/{report_id}/changes")
    assert response.status_code == 200
    data = response.json()
    assert data["report_id"] == report_id
    assert "changes" in data
    assert "total_unique_changes" in data


def test_export_report_json(
    client: TestClient, sample_cisco_ios_config: str, sample_cisco_ios_intended_config: str
) -> None:
    """Test exporting report as JSON."""
    # First, create a report
    create_response = client.post(
        "/api/v1/reports",
        json={
            "remediations": [
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
    report_id = create_response.json()["report_id"]

    # Export as JSON
    response = client.get(f"/api/v1/reports/{report_id}/export?format=json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"


def test_export_report_csv(
    client: TestClient, sample_cisco_ios_config: str, sample_cisco_ios_intended_config: str
) -> None:
    """Test exporting report as CSV."""
    # First, create a report
    create_response = client.post(
        "/api/v1/reports",
        json={
            "remediations": [
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
    report_id = create_response.json()["report_id"]

    # Export as CSV
    response = client.get(f"/api/v1/reports/{report_id}/export?format=csv")
    assert response.status_code == 200
    assert "Device ID" in response.text
