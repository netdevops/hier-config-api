"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from hier_config_api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_cisco_ios_config() -> str:
    """Sample Cisco IOS configuration."""
    return """hostname router1
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 ip address 10.0.0.1 255.255.255.0
 no shutdown
!
router bgp 65001
 neighbor 192.168.1.2 remote-as 65002
!
end"""


@pytest.fixture
def sample_cisco_ios_intended_config() -> str:
    """Sample intended Cisco IOS configuration."""
    return """hostname router1-updated
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 ip address 10.0.0.1 255.255.255.0
 description WAN Link
 no shutdown
!
router bgp 65001
 neighbor 192.168.1.2 remote-as 65002
 neighbor 192.168.1.3 remote-as 65003
!
end"""
