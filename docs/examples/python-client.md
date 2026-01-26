# Python Client

Example Python client library for hier-config-api.

## Simple Client Implementation

```python
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class RemediationResult:
    """Remediation result container."""
    remediation_id: str
    platform: str
    remediation_config: str
    rollback_config: str
    summary: Dict[str, int]
    tags: Dict[str, List[str]]

class HierConfigAPIClient:
    """Client for hier-config-api."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize client.

        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def compare_configs(
        self,
        platform: str,
        running_config: str,
        intended_config: str
    ) -> Dict[str, Any]:
        """Compare two configurations.

        Args:
            platform: Platform type
            running_config: Current configuration
            intended_config: Desired configuration

        Returns:
            Comparison result with diff
        """
        return self._post("/api/v1/configs/compare", {
            "platform": platform,
            "running_config": running_config,
            "intended_config": intended_config
        })

    def generate_remediation(
        self,
        platform: str,
        running_config: str,
        intended_config: str,
        tag_rules: Optional[List[Dict[str, Any]]] = None,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None
    ) -> RemediationResult:
        """Generate remediation configuration.

        Args:
            platform: Platform type
            running_config: Current configuration
            intended_config: Desired configuration
            tag_rules: Optional tag rules
            include_tags: Tags to include
            exclude_tags: Tags to exclude

        Returns:
            Remediation result
        """
        data = {
            "platform": platform,
            "running_config": running_config,
            "intended_config": intended_config
        }

        if tag_rules:
            data["tag_rules"] = tag_rules
        if include_tags:
            data["include_tags"] = include_tags
        if exclude_tags:
            data["exclude_tags"] = exclude_tags

        result = self._post("/api/v1/remediation/generate", data)

        return RemediationResult(
            remediation_id=result["remediation_id"],
            platform=result["platform"],
            remediation_config=result["remediation_config"],
            rollback_config=result["rollback_config"],
            summary=result["summary"],
            tags=result["tags"]
        )

    def create_report(
        self,
        devices: List[Dict[str, str]]
    ) -> str:
        """Create multi-device report.

        Args:
            devices: List of device configs

        Returns:
            Report ID
        """
        result = self._post("/api/v1/reports", {
            "remediations": devices
        })
        return result["report_id"]

    def get_report_summary(self, report_id: str) -> Dict[str, Any]:
        """Get report summary.

        Args:
            report_id: Report identifier

        Returns:
            Report summary
        """
        return self._get(f"/api/v1/reports/{report_id}/summary")

    def get_report_changes(
        self,
        report_id: str,
        tag: Optional[str] = None,
        min_devices: int = 1
    ) -> Dict[str, Any]:
        """Get detailed changes from report.

        Args:
            report_id: Report identifier
            tag: Filter by tag
            min_devices: Minimum device count

        Returns:
            Change details
        """
        params = {"min_devices": min_devices}
        if tag:
            params["tag"] = tag

        return self._get(f"/api/v1/reports/{report_id}/changes", params)

    def export_report(
        self,
        report_id: str,
        format: str = "json"
    ) -> str:
        """Export report in specified format.

        Args:
            report_id: Report identifier
            format: Export format (json, csv, yaml)

        Returns:
            Report content
        """
        url = f"{self.base_url}/api/v1/reports/{report_id}/export"
        response = self.session.get(url, params={"format": format})
        response.raise_for_status()
        return response.text

    def list_platforms(self) -> List[Dict[str, Any]]:
        """List supported platforms.

        Returns:
            List of platform information
        """
        return self._get("/api/v1/platforms")

    def validate_config(
        self,
        platform: str,
        config_text: str
    ) -> Dict[str, Any]:
        """Validate configuration.

        Args:
            platform: Platform type
            config_text: Configuration to validate

        Returns:
            Validation result
        """
        return self._post(f"/api/v1/platforms/{platform}/validate", {
            "config_text": config_text
        })

    def create_batch_job(
        self,
        devices: List[Dict[str, str]]
    ) -> str:
        """Create batch remediation job.

        Args:
            devices: List of device configs

        Returns:
            Job ID
        """
        result = self._post("/api/v1/batch/remediation", {
            "device_configs": devices
        })
        return result["job_id"]

    def get_batch_status(self, job_id: str) -> Dict[str, Any]:
        """Get batch job status.

        Args:
            job_id: Job identifier

        Returns:
            Job status
        """
        return self._get(f"/api/v1/batch/jobs/{job_id}")

    def get_batch_results(self, job_id: str) -> Dict[str, Any]:
        """Get batch job results.

        Args:
            job_id: Job identifier

        Returns:
            Job results
        """
        return self._get(f"/api/v1/batch/jobs/{job_id}/results")
```

## Usage Examples

### Basic Usage

```python
from hier_config_client import HierConfigAPIClient

# Initialize client
client = HierConfigAPIClient("http://localhost:8000")

# Compare configs
result = client.compare_configs(
    platform="cisco_ios",
    running_config="hostname router1",
    intended_config="hostname router2"
)

print(result["unified_diff"])
```

### Generate Remediation

```python
# Generate remediation
remediation = client.generate_remediation(
    platform="cisco_ios",
    running_config=open("current.cfg").read(),
    intended_config=open("desired.cfg").read()
)

print("Remediation:")
print(remediation.remediation_config)

print("\nRollback:")
print(remediation.rollback_config)

print(f"\nSummary: {remediation.summary}")
```

### Multi-Device Report

```python
# Create report
devices = [
    {
        "device_id": "router1",
        "platform": "cisco_ios",
        "running_config": "...",
        "intended_config": "..."
    },
    {
        "device_id": "router2",
        "platform": "cisco_ios",
        "running_config": "...",
        "intended_config": "..."
    }
]

report_id = client.create_report(devices)

# Get summary
summary = client.get_report_summary(report_id)
print(f"Devices with changes: {summary['devices_with_changes']}")

# Export to CSV
csv_data = client.export_report(report_id, format="csv")
with open("report.csv", "w") as f:
    f.write(csv_data)
```

### Batch Processing

```python
import time

# Create batch job
job_id = client.create_batch_job(devices)
print(f"Job ID: {job_id}")

# Monitor progress
while True:
    status = client.get_batch_status(job_id)
    print(f"Progress: {status['progress']:.1f}%")

    if status['status'] in ['completed', 'failed']:
        break

    time.sleep(2)

# Get results
results = client.get_batch_results(job_id)
for result in results['results']:
    print(f"{result['device_id']}: {result['status']}")
```

### Context Manager

```python
class HierConfigAPIClient:
    # ... previous code ...

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

# Usage with context manager
with HierConfigAPIClient("http://localhost:8000") as client:
    result = client.compare_configs(...)
```

### Async Client

```python
import httpx
from typing import List, Dict, Any

class AsyncHierConfigAPIClient:
    """Async client for hier-config-api."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient()

    async def compare_configs(
        self,
        platform: str,
        running_config: str,
        intended_config: str
    ) -> Dict[str, Any]:
        """Compare configurations asynchronously."""
        url = f"{self.base_url}/api/v1/configs/compare"
        response = await self.client.post(url, json={
            "platform": platform,
            "running_config": running_config,
            "intended_config": intended_config
        })
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close client."""
        await self.client.aclose()

# Usage
import asyncio

async def main():
    client = AsyncHierConfigAPIClient()
    try:
        result = await client.compare_configs(...)
        print(result)
    finally:
        await client.close()

asyncio.run(main())
```
