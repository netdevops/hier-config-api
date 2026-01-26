"""Tests for remediation endpoints."""

from fastapi.testclient import TestClient


def test_generate_remediation(
    client: TestClient, sample_cisco_ios_config: str, sample_cisco_ios_intended_config: str
) -> None:
    """Test generating remediation."""
    response = client.post(
        "/api/v1/remediation/generate",
        json={
            "platform": "cisco_ios",
            "running_config": sample_cisco_ios_config,
            "intended_config": sample_cisco_ios_intended_config,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "remediation_id" in data
    assert data["platform"] == "cisco_ios"
    assert "remediation_config" in data
    assert "rollback_config" in data
    assert "summary" in data
    assert "tags" in data


def test_generate_remediation_with_tags(
    client: TestClient, sample_cisco_ios_config: str, sample_cisco_ios_intended_config: str
) -> None:
    """Test generating remediation with tag rules."""
    response = client.post(
        "/api/v1/remediation/generate",
        json={
            "platform": "cisco_ios",
            "running_config": sample_cisco_ios_config,
            "intended_config": sample_cisco_ios_intended_config,
            "tag_rules": [{"match_rules": ["interface"], "tags": ["safe"]}],
            "include_tags": ["safe"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "remediation_id" in data
    assert "remediation_config" in data


def test_apply_tags(
    client: TestClient, sample_cisco_ios_config: str, sample_cisco_ios_intended_config: str
) -> None:
    """Test applying tags to remediation."""
    # First, generate a remediation
    gen_response = client.post(
        "/api/v1/remediation/generate",
        json={
            "platform": "cisco_ios",
            "running_config": sample_cisco_ios_config,
            "intended_config": sample_cisco_ios_intended_config,
        },
    )
    assert gen_response.status_code == 200
    remediation_id = gen_response.json()["remediation_id"]

    # Apply tags
    response = client.post(
        f"/api/v1/remediation/{remediation_id}/tags",
        json={"tag_rules": [{"match_rules": ["hostname"], "tags": ["critical"]}]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["remediation_id"] == remediation_id
    assert "tags" in data


def test_filter_remediation(
    client: TestClient, sample_cisco_ios_config: str, sample_cisco_ios_intended_config: str
) -> None:
    """Test filtering remediation by tags."""
    # First, generate a remediation
    gen_response = client.post(
        "/api/v1/remediation/generate",
        json={
            "platform": "cisco_ios",
            "running_config": sample_cisco_ios_config,
            "intended_config": sample_cisco_ios_intended_config,
        },
    )
    assert gen_response.status_code == 200
    remediation_id = gen_response.json()["remediation_id"]

    # Filter remediation
    response = client.get(
        f"/api/v1/remediation/{remediation_id}/filter", params={"include_tags": ["safe"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["remediation_id"] == remediation_id
    assert "filtered_config" in data
    assert "summary" in data
