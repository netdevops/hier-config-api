# Batch Operations

Process multiple devices in parallel for improved efficiency.

## Create Batch Remediation Job

Create a batch job to generate remediation for multiple devices.

**Endpoint:** `POST /api/v1/batch/remediation`

### Request

```json
{
  "device_configs": [
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
  "job_id": "job-abc-123-def-456",
  "total_devices": 3
}
```

---

## Get Batch Job Status

Get the current status and progress of a batch job.

**Endpoint:** `GET /api/v1/batch/jobs/{job_id}`

### Response

```json
{
  "job_id": "job-abc-123-def-456",
  "status": "completed",
  "progress": 100.0,
  "total_devices": 3,
  "completed_devices": 3,
  "failed_devices": 0
}
```

| Field | Type | Description |
|-------|------|-------------|
| job_id | string | Unique job identifier |
| status | string | Job status (pending, running, completed, failed) |
| progress | float | Progress percentage (0-100) |
| total_devices | integer | Total number of devices |
| completed_devices | integer | Successfully processed devices |
| failed_devices | integer | Failed devices |

### Status Values

- `pending` - Job created, not yet started
- `running` - Job is currently processing
- `completed` - Job finished successfully
- `failed` - Job encountered fatal error

---

## Get Batch Job Results

Get the results of a completed batch job.

**Endpoint:** `GET /api/v1/batch/jobs/{job_id}/results`

### Response

```json
{
  "job_id": "job-abc-123-def-456",
  "status": "completed",
  "results": [
    {
      "device_id": "router1",
      "status": "success",
      "remediation": "no hostname router1\nhostname router1-new",
      "rollback": "no hostname router1-new\nhostname router1"
    },
    {
      "device_id": "router2",
      "status": "success",
      "remediation": "no hostname router2\nhostname router2-new",
      "rollback": "no hostname router2-new\nhostname router2"
    },
    {
      "device_id": "switch1",
      "status": "failed",
      "error": "Configuration parsing error"
    }
  ],
  "summary": {
    "total_devices": 3,
    "completed_devices": 2,
    "failed_devices": 1,
    "status": "completed"
  }
}
```

## Workflow Example

### 1. Submit Batch Job

```python
import requests
import time

# Prepare device list
devices = []
for i in range(100):
    devices.append({
        "device_id": f"router{i}",
        "platform": "cisco_ios",
        "running_config": f"hostname router{i}",
        "intended_config": f"hostname router{i}-new"
    })

# Create batch job
response = requests.post(
    "http://localhost:8000/api/v1/batch/remediation",
    json={"device_configs": devices}
)

job_id = response.json()["job_id"]
print(f"Job created: {job_id}")
```

### 2. Monitor Progress

```python
# Poll for completion
while True:
    status = requests.get(
        f"http://localhost:8000/api/v1/batch/jobs/{job_id}"
    ).json()

    print(f"Progress: {status['progress']:.1f}% "
          f"({status['completed_devices']}/{status['total_devices']})")

    if status['status'] in ['completed', 'failed']:
        break

    time.sleep(2)
```

### 3. Get Results

```python
# Fetch results
results = requests.get(
    f"http://localhost:8000/api/v1/batch/jobs/{job_id}/results"
).json()

# Process successful remediations
for result in results['results']:
    if result['status'] == 'success':
        print(f"{result['device_id']}: Ready for deployment")
        print(result['remediation'])
    else:
        print(f"{result['device_id']}: FAILED - {result['error']}")
```

## Performance Considerations

### Batch Size

Optimal batch size depends on:

- Server resources (CPU, memory)
- Configuration complexity
- Network latency

Recommended batch sizes:

- Small configs (<100 lines): 100-500 devices
- Medium configs (100-1000 lines): 50-100 devices
- Large configs (>1000 lines): 10-50 devices

### Timeouts

For large batches, consider:

- Increasing server timeout settings
- Splitting into smaller batches
- Using asynchronous processing

### Error Handling

Batch jobs continue processing even if individual devices fail. Always check the `failed_devices` count and review the error messages in the results.
