"""Unit tests for service and utility edge cases."""

import pytest
from fastapi.testclient import TestClient

from hier_config_api.models.platform import PlatformRules
from hier_config_api.services.config_service import ConfigService
from hier_config_api.services.remediation_service import RemediationService
from hier_config_api.services.report_service import ReportService
from hier_config_api.utils.storage import InMemoryStorage


def test_platform_rules_defaults() -> None:
    """Test that PlatformRules fields default to empty collections."""
    rules = PlatformRules(platform_name="cisco_ios")
    assert not rules.ordering
    assert not rules.negation_default_when


def test_storage_update_unknown_job() -> None:
    """Test that updating an unknown job returns False."""
    storage = InMemoryStorage()
    assert storage.update_job("unknown-id", {"status": "completed"}) is False


def test_storage_update_unknown_remediation() -> None:
    """Test that updating an unknown remediation returns False."""
    storage = InMemoryStorage()
    assert storage.update_remediation("unknown-id", {"tags": {}}) is False


def test_merge_configs_empty() -> None:
    """Test that merging an empty config list returns an empty string."""
    assert not ConfigService.merge_configs("cisco_ios", [])


def test_merge_configs_single() -> None:
    """Test that merging a single config returns it unchanged."""
    assert ConfigService.merge_configs("cisco_ios", ["hostname a"]) == "hostname a"


def test_filter_remediation_include_tags() -> None:
    """Test filtering remediation lines by include tags."""
    filtered_config, summary = RemediationService.filter_remediation(
        "line one\nline two",
        {"0": ["keep"]},
        include_tags=["keep"],
    )
    assert filtered_config == "line one"
    assert summary.additions == 1


def test_filter_remediation_exclude_tags() -> None:
    """Test filtering remediation lines by exclude tags."""
    filtered_config, summary = RemediationService.filter_remediation(
        "line one\nline two",
        {"0": ["drop"]},
        exclude_tags=["drop"],
    )
    assert filtered_config == "line two"
    assert summary.additions == 1


def test_export_report_unsupported_format() -> None:
    """Test that exporting with an unsupported format raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported format"):
        ReportService.export_report({"devices": []}, format_type="xml")


def test_search_config_contains(client: TestClient) -> None:
    """Test searching configuration lines with a contains rule."""
    response = client.post(
        "/api/v1/configs/search",
        json={
            "platform": "cisco_ios",
            "config_text": "hostname router1\ninterface GigabitEthernet0/0",
            "match_rules": {"contains": "Gigabit"},
        },
    )
    assert response.status_code == 200
    matches = response.json()["matches"]
    assert "interface GigabitEthernet0/0" in matches


def test_search_config_startswith(client: TestClient) -> None:
    """Test searching configuration lines with a startswith rule."""
    response = client.post(
        "/api/v1/configs/search",
        json={
            "platform": "cisco_ios",
            "config_text": "hostname router1\ninterface GigabitEthernet0/0",
            "match_rules": {"startswith": "hostname"},
        },
    )
    assert response.status_code == 200
    matches = response.json()["matches"]
    assert "hostname router1" in matches
