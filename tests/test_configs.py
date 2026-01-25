"""Tests for configuration endpoints."""

from fastapi.testclient import TestClient


def test_parse_config(client: TestClient, sample_cisco_ios_config: str) -> None:
    """Test parsing configuration."""
    response = client.post(
        "/api/v1/configs/parse",
        json={"platform": "cisco_ios", "config_text": sample_cisco_ios_config},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "cisco_ios"
    assert "structured_config" in data


def test_compare_configs(
    client: TestClient, sample_cisco_ios_config: str, sample_cisco_ios_intended_config: str
) -> None:
    """Test comparing configurations."""
    response = client.post(
        "/api/v1/configs/compare",
        json={
            "platform": "cisco_ios",
            "running_config": sample_cisco_ios_config,
            "intended_config": sample_cisco_ios_intended_config,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "cisco_ios"
    assert "unified_diff" in data
    assert "has_changes" in data


def test_predict_config(client: TestClient, sample_cisco_ios_config: str) -> None:
    """Test predicting future configuration."""
    response = client.post(
        "/api/v1/configs/predict",
        json={
            "platform": "cisco_ios",
            "current_config": sample_cisco_ios_config,
            "commands_to_apply": "hostname router2\ninterface GigabitEthernet0/2",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "cisco_ios"
    assert "predicted_config" in data


def test_merge_configs(client: TestClient, sample_cisco_ios_config: str) -> None:
    """Test merging configurations."""
    config2 = "interface GigabitEthernet0/2\n ip address 172.16.0.1 255.255.255.0"
    response = client.post(
        "/api/v1/configs/merge",
        json={"platform": "cisco_ios", "configs": [sample_cisco_ios_config, config2]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "cisco_ios"
    assert "merged_config" in data


def test_search_config(client: TestClient, sample_cisco_ios_config: str) -> None:
    """Test searching configuration."""
    response = client.post(
        "/api/v1/configs/search",
        json={
            "platform": "cisco_ios",
            "config_text": sample_cisco_ios_config,
            "match_rules": {"contains": "interface"},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "cisco_ios"
    assert "matches" in data
    assert "match_count" in data
