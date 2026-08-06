"""Tests for API error handling paths."""

from typing import NoReturn

import pytest
from fastapi.testclient import TestClient
from hier_config import HConfig


def _raise_parse_error(*_args: object, **_kwargs: object) -> NoReturn:
    """Stand-in for HConfig.from_text that always fails."""
    message = "simulated parse failure"
    raise ValueError(message)


def test_parse_config_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that a parsing failure returns a 400 error."""
    monkeypatch.setattr(HConfig, "from_text", _raise_parse_error)
    response = client.post(
        "/api/v1/configs/parse",
        json={"platform": "cisco_ios", "config_text": "hostname router1"},
    )
    assert response.status_code == 400
    assert "Failed to parse config" in response.json()["detail"]


def test_compare_configs_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that a comparison failure returns a 400 error."""
    monkeypatch.setattr(HConfig, "from_text", _raise_parse_error)
    response = client.post(
        "/api/v1/configs/compare",
        json={
            "platform": "cisco_ios",
            "running_config": "hostname a",
            "intended_config": "hostname b",
        },
    )
    assert response.status_code == 400
    assert "Failed to compare configs" in response.json()["detail"]


def test_merge_configs_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that a merge failure returns a 400 error."""
    monkeypatch.setattr(HConfig, "from_text", _raise_parse_error)
    response = client.post(
        "/api/v1/configs/merge",
        json={"platform": "cisco_ios", "configs": ["hostname a", "hostname b"]},
    )
    assert response.status_code == 400
    assert "Failed to merge configs" in response.json()["detail"]


def test_search_config_invalid_regex(client: TestClient) -> None:
    """Test that an invalid regex pattern returns a 400 error."""
    response = client.post(
        "/api/v1/configs/search",
        json={
            "platform": "cisco_ios",
            "config_text": "hostname router1",
            "match_rules": {"regex": "["},
        },
    )
    assert response.status_code == 400
    assert "Failed to search config" in response.json()["detail"]


def test_generate_remediation_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that a remediation generation failure returns a 400 error."""
    monkeypatch.setattr(HConfig, "from_text", _raise_parse_error)
    response = client.post(
        "/api/v1/remediation/generate",
        json={
            "platform": "cisco_ios",
            "running_config": "hostname a",
            "intended_config": "hostname b",
        },
    )
    assert response.status_code == 400
    assert "Failed to generate remediation" in response.json()["detail"]


def test_apply_tags_unknown_remediation(client: TestClient) -> None:
    """Test that applying tags to an unknown remediation returns 404."""
    response = client.post(
        "/api/v1/remediation/unknown-id/tags",
        json={"tag_rules": [{"match_rules": ["interface"], "tags": ["intf"]}]},
    )
    assert response.status_code == 404


def test_filter_unknown_remediation(client: TestClient) -> None:
    """Test that filtering an unknown remediation returns 404."""
    response = client.get("/api/v1/remediation/unknown-id/filter")
    assert response.status_code == 404


def test_create_report_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that a report creation failure returns a 400 error."""
    monkeypatch.setattr(HConfig, "from_text", _raise_parse_error)
    response = client.post(
        "/api/v1/reports",
        json={
            "remediations": [
                {
                    "device_id": "router1",
                    "platform": "cisco_ios",
                    "running_config": "hostname a",
                    "intended_config": "hostname b",
                }
            ]
        },
    )
    assert response.status_code == 400
    assert "Failed to create report" in response.json()["detail"]


def test_get_summary_unknown_report(client: TestClient) -> None:
    """Test that requesting a summary for an unknown report returns 404."""
    response = client.get("/api/v1/reports/unknown-id/summary")
    assert response.status_code == 404


def test_get_changes_unknown_report(client: TestClient) -> None:
    """Test that requesting changes for an unknown report returns 404."""
    response = client.get("/api/v1/reports/unknown-id/changes")
    assert response.status_code == 404


def test_export_unknown_report(client: TestClient) -> None:
    """Test that exporting an unknown report returns 404."""
    response = client.get("/api/v1/reports/unknown-id/export")
    assert response.status_code == 404


def test_export_report_invalid_format(
    client: TestClient,
    sample_cisco_ios_config: str,
    sample_cisco_ios_intended_config: str,
) -> None:
    """Test that exporting a report with an unsupported format returns 400."""
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

    response = client.get(f"/api/v1/reports/{report_id}/export?format=xml")
    assert response.status_code == 400


def test_get_status_unknown_batch_job(client: TestClient) -> None:
    """Test that requesting the status of an unknown batch job returns 404."""
    response = client.get("/api/v1/batch/jobs/unknown-id")
    assert response.status_code == 404


def test_get_results_unknown_batch_job(client: TestClient) -> None:
    """Test that requesting the results of an unknown batch job returns 404."""
    response = client.get("/api/v1/batch/jobs/unknown-id/results")
    assert response.status_code == 404


def test_validate_config_parse_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that validation reports parsing failures as validation errors."""
    monkeypatch.setattr(HConfig, "from_text", _raise_parse_error)
    response = client.post(
        "/api/v1/platforms/cisco_ios/validate",
        json={"config_text": "hostname router1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert any("parsing error" in error for error in data["errors"])


def test_batch_job_with_failing_device(
    client: TestClient,
    sample_cisco_ios_config: str,
    sample_cisco_ios_intended_config: str,
) -> None:
    """Test that a batch job records per-device failures without aborting."""
    response = client.post(
        "/api/v1/batch/remediation",
        json={
            "device_configs": [
                {
                    "device_id": "good-router",
                    "platform": "cisco_ios",
                    "running_config": sample_cisco_ios_config,
                    "intended_config": sample_cisco_ios_intended_config,
                },
                {
                    "device_id": "bad-router",
                    "platform": "cisco_ios",
                    "running_config": 123,
                    "intended_config": 456,
                },
            ]
        },
    )
    assert response.status_code == 200
    job_id = response.json()["job_id"]

    results_response = client.get(f"/api/v1/batch/jobs/{job_id}/results")
    assert results_response.status_code == 200
    data = results_response.json()
    statuses = {result["device_id"]: result["status"] for result in data["results"]}
    assert statuses == {"good-router": "success", "bad-router": "failed"}
    assert data["summary"]["failed_devices"] == 1
