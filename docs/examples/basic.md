# Basic Usage Examples

Common use cases and examples for hier-config-api.

## Simple Configuration Comparison

Compare two configurations to see what changed:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/configs/compare",
    json={
        "platform": "cisco_ios",
        "running_config": """
hostname router1
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
""",
        "intended_config": """
hostname router2
interface GigabitEthernet0/0
 ip address 192.168.1.2 255.255.255.0
 description WAN Link
 no shutdown
"""
    }
)

result = response.json()
print(result["unified_diff"])
print(f"Has changes: {result['has_changes']}")
```

## Generate Remediation Commands

Get commands to achieve desired state:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/remediation/generate",
    json={
        "platform": "cisco_ios",
        "running_config": "hostname router1",
        "intended_config": "hostname router2"
    }
)

result = response.json()
print("Remediation:")
print(result["remediation_config"])
print("\nRollback:")
print(result["rollback_config"])
print(f"\nSummary: {result['summary']}")
```

## Parse Configuration

Parse configuration into structured format:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/configs/parse",
    json={
        "platform": "cisco_ios",
        "config_text": """
hostname router1
!
interface GigabitEthernet0/0
 description WAN Link
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 description LAN Link
 ip address 10.0.0.1 255.255.255.0
 no shutdown
"""
    }
)

config = response.json()["structured_config"]
print(f"Root: {config['text']}")
for child in config['children']:
    print(f"  - {child['text']}")
```

## Search Configuration

Find specific configuration lines:

```python
import requests

# Search for all interface configurations
response = requests.post(
    "http://localhost:8000/api/v1/configs/search",
    json={
        "platform": "cisco_ios",
        "config_text": "...",
        "match_rules": {
            "startswith": "interface"
        }
    }
)

matches = response.json()["matches"]
for match in matches:
    print(match)
```

## Multi-Device Analysis

Analyze changes across multiple devices:

```python
import requests

# Create report for multiple devices
response = requests.post(
    "http://localhost:8000/api/v1/reports",
    json={
        "remediations": [
            {
                "device_id": "router1",
                "platform": "cisco_ios",
                "running_config": "hostname router1",
                "intended_config": "hostname router1-new"
            },
            {
                "device_id": "router2",
                "platform": "cisco_ios",
                "running_config": "hostname router2",
                "intended_config": "hostname router2-new"
            },
            {
                "device_id": "switch1",
                "platform": "cisco_nxos",
                "running_config": "hostname switch1",
                "intended_config": "hostname switch1-new"
            }
        ]
    }
)

report_id = response.json()["report_id"]

# Get summary
summary = requests.get(
    f"http://localhost:8000/api/v1/reports/{report_id}/summary"
).json()

print(f"Total devices: {summary['total_devices']}")
print(f"Devices with changes: {summary['devices_with_changes']}")
print(f"Total changes: {summary['total_changes']}")

# Export to CSV
csv_data = requests.get(
    f"http://localhost:8000/api/v1/reports/{report_id}/export",
    params={"format": "csv"}
).text

with open("report.csv", "w") as f:
    f.write(csv_data)
```

## Batch Processing

Process multiple devices in parallel:

```python
import requests
import time

# Prepare device list
devices = []
for i in range(10):
    devices.append({
        "device_id": f"router{i}",
        "platform": "cisco_ios",
        "running_config": f"hostname router{i}",
        "intended_config": f"hostname router{i}-new"
    })

# Submit batch job
response = requests.post(
    "http://localhost:8000/api/v1/batch/remediation",
    json={"device_configs": devices}
)

job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")

# Monitor progress
while True:
    status = requests.get(
        f"http://localhost:8000/api/v1/batch/jobs/{job_id}"
    ).json()

    print(f"Progress: {status['progress']:.1f}%")

    if status['status'] in ['completed', 'failed']:
        break

    time.sleep(1)

# Get results
results = requests.get(
    f"http://localhost:8000/api/v1/batch/jobs/{job_id}/results"
).json()

for result in results['results']:
    if result['status'] == 'success':
        print(f"{result['device_id']}: Success")
    else:
        print(f"{result['device_id']}: Failed - {result['error']}")
```

## Platform Information

Get supported platforms:

```python
import requests

platforms = requests.get(
    "http://localhost:8000/api/v1/platforms"
).json()

for platform in platforms:
    print(f"{platform['display_name']} ({platform['platform_name']})")
```

## Validate Configuration

Validate configuration syntax:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/platforms/cisco_ios/validate",
    json={
        "config_text": """
hostname router1
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
"""
    }
)

result = response.json()
if result["is_valid"]:
    print("Configuration is valid")
else:
    print("Configuration has errors:")
    for error in result["errors"]:
        print(f"  - {error}")
```
