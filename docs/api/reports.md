# Multi-Device Reports

Create and analyze configuration reports across multiple devices.

## Create Report

Create a multi-device configuration report.

**Endpoint:** `POST /api/v1/reports`

### Request

```json
{
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
```

### Response

```json
{
  "report_id": "report-abc-123",
  "total_devices": 3
}
```

---

## Get Report Summary

Get aggregated statistics for a report.

**Endpoint:** `GET /api/v1/reports/{report_id}/summary`

### Response

```json
{
  "total_devices": 3,
  "devices_with_changes": 3,
  "total_changes": 6,
  "changes_by_tag": {
    "safe": 3,
    "hostname-change": 3
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| total_devices | integer | Total number of devices |
| devices_with_changes | integer | Devices with configuration changes |
| total_changes | integer | Total configuration changes |
| changes_by_tag | object | Count of changes by tag |

---

## Get Report Changes

Get detailed change analysis showing common changes across devices.

**Endpoint:** `GET /api/v1/reports/{report_id}/changes`

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| tag | string | Filter by specific tag |
| min_devices | integer | Minimum devices with this change |

### Example

```bash
# Get changes appearing on at least 2 devices
curl "http://localhost:8000/api/v1/reports/report-123/changes?min_devices=2"
```

### Response

```json
{
  "report_id": "report-abc-123",
  "changes": [
    {
      "change_text": "no hostname router1",
      "device_count": 2,
      "device_ids": ["router1", "router2"],
      "tags": ["hostname-change"]
    },
    {
      "change_text": "hostname router1-new",
      "device_count": 1,
      "device_ids": ["router1"],
      "tags": ["hostname-change", "safe"]
    }
  ],
  "total_unique_changes": 2
}
```

---

## Export Report

Export report in different formats.

**Endpoint:** `GET /api/v1/reports/{report_id}/export`

### Query Parameters

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| format | string | json, csv, yaml | Export format |

### Examples

**Export as JSON:**

```bash
curl "http://localhost:8000/api/v1/reports/report-123/export?format=json"
```

**Export as CSV:**

```bash
curl "http://localhost:8000/api/v1/reports/report-123/export?format=csv" > report.csv
```

**Export as YAML:**

```bash
curl "http://localhost:8000/api/v1/reports/report-123/export?format=yaml" > report.yaml
```

### CSV Format

```csv
Device ID,Platform,Has Changes,Change Count,Remediation Summary
router1,cisco_ios,True,2,no hostname router1...
router2,cisco_ios,True,2,no hostname router2...
switch1,cisco_nxos,True,2,no hostname switch1...
```

## Use Cases

### Fleet-Wide Analysis

Identify common misconfigurations:

```python
import requests

# Create report for 100 devices
devices = [...]  # List of device configs

response = requests.post(
    "http://localhost:8000/api/v1/reports",
    json={"remediations": devices}
)

report_id = response.json()["report_id"]

# Find changes appearing on 10+ devices
changes = requests.get(
    f"http://localhost:8000/api/v1/reports/{report_id}/changes",
    params={"min_devices": 10}
).json()

for change in changes["changes"]:
    print(f"{change['change_text']}: {change['device_count']} devices")
```

### Change Impact Assessment

Understand scope of a planned change:

```python
# Create report
report = requests.post(...).json()

# Get summary
summary = requests.get(
    f"http://localhost:8000/api/v1/reports/{report['report_id']}/summary"
).json()

print(f"Total devices affected: {summary['devices_with_changes']}")
print(f"Total changes: {summary['total_changes']}")
```
