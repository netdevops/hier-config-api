# Quick Start

Get up and running with hier-config-api in minutes.

## Starting the Server

### Development Mode

Start the server with auto-reload enabled for development:

```bash
poetry run uvicorn hier_config_api.main:app --reload
```

You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Production Mode

For production deployments:

```bash
poetry run uvicorn hier_config_api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Accessing the API

### Interactive Documentation

Once the server is running, open your browser to:

- **Swagger UI**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **ReDoc**: [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc)

These provide interactive documentation where you can test endpoints directly.

### API Endpoints

The API is available at: `http://localhost:8000/api/v1/`

## Your First API Call

Let's compare two configurations to see what changes are needed.

### Using curl

```bash
curl -X POST http://localhost:8000/api/v1/configs/compare \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "cisco_ios",
    "running_config": "hostname router1",
    "intended_config": "hostname router2"
  }'
```

Response:

```json
{
  "platform": "cisco_ios",
  "unified_diff": "--- running_config\n+++ intended_config\n+ no hostname router1\n+ hostname router2\n- no hostname router2\n- hostname router1",
  "has_changes": true
}
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/configs/compare",
    json={
        "platform": "cisco_ios",
        "running_config": "hostname router1",
        "intended_config": "hostname router2"
    }
)

print(response.json())
```

## Generate Remediation

Now let's generate remediation commands:

```bash
curl -X POST http://localhost:8000/api/v1/remediation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "cisco_ios",
    "running_config": "hostname router1\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0",
    "intended_config": "hostname router2\ninterface GigabitEthernet0/0\n ip address 192.168.1.2 255.255.255.0"
  }'
```

Response:

```json
{
  "remediation_id": "abc-123-def-456",
  "platform": "cisco_ios",
  "remediation_config": "no hostname router1\nhostname router2\ninterface GigabitEthernet0/0\n no ip address 192.168.1.1 255.255.255.0\n ip address 192.168.1.2 255.255.255.0",
  "rollback_config": "no hostname router2\nhostname router1\ninterface GigabitEthernet0/0\n no ip address 192.168.1.2 255.255.255.0\n ip address 192.168.1.1 255.255.255.0",
  "summary": {
    "additions": 4,
    "deletions": 4,
    "modifications": 0
  },
  "tags": {}
}
```

## Multi-Device Report

Create a report for multiple devices:

```bash
curl -X POST http://localhost:8000/api/v1/reports \
  -H "Content-Type: application/json" \
  -d '{
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
      }
    ]
  }'
```

Response:

```json
{
  "report_id": "report-123",
  "total_devices": 2
}
```

Get the report summary:

```bash
curl http://localhost:8000/api/v1/reports/report-123/summary
```

## Health Check

Verify the API is running:

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "healthy"
}
```

## Next Steps

- Explore the [API Reference](../api/overview.md) for detailed endpoint documentation
- Check out [Examples](../examples/basic.md) for more use cases
- Learn about [Configuration](configuration.md) options
