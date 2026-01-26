# hier-config-api

[![CI](https://github.com/netdevops/hier-config-api/workflows/CI/badge.svg)](https://github.com/netdevops/hier-config-api/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/netdevops/hier-config-api/branch/main/graph/badge.svg)](https://codecov.io/gh/netdevops/hier-config-api)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

REST API for [hier_config](https://github.com/netdevops/hier_config) network configuration management.

## Overview

This FastAPI-based REST API provides a comprehensive interface to the hier_config library, enabling network engineers to:
- Compare and diff network configurations
- Generate remediation and rollback commands
- Analyze configuration changes across multiple devices
- Validate configurations for different network platforms

## Features

- **Configuration Operations**: Parse, compare, merge, and search network configurations
- **Remediation Workflows**: Generate remediation and rollback configurations with tag-based filtering
- **Multi-Device Reporting**: Aggregate and analyze configuration changes across device fleets
- **Platform Support**: Cisco IOS, Cisco NX-OS, Cisco IOS-XR, Juniper Junos, Arista EOS
- **Batch Processing**: Process multiple devices in parallel
- **Export Formats**: JSON, CSV, YAML

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/netdevops/hier-config-api.git
cd hier-config-api

# Install dependencies with poetry
poetry install

# Run the API server
poetry run uvicorn hier_config_api.main:app --reload
```

### Access the API Documentation

Once the server is running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## API Endpoints

### Configuration Operations

#### Parse Configuration
```bash
POST /api/v1/configs/parse
```
Parse raw configuration text into structured format.

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/configs/parse \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "cisco_ios",
    "config_text": "hostname router1\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0"
  }'
```

#### Compare Configurations
```bash
POST /api/v1/configs/compare
```
Compare running and intended configurations to show differences.

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/configs/compare \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "cisco_ios",
    "running_config": "hostname old-router",
    "intended_config": "hostname new-router"
  }'
```

#### Predict Future Configuration
```bash
POST /api/v1/configs/predict
```
Predict configuration state after applying commands.

#### Merge Configurations
```bash
POST /api/v1/configs/merge
```
Merge multiple configuration snippets into one.

#### Search Configuration
```bash
POST /api/v1/configs/search
```
Search configuration using pattern matching.

### Remediation Workflows

#### Generate Remediation
```bash
POST /api/v1/remediation/generate
```
Generate remediation and rollback configurations.

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/remediation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "cisco_ios",
    "running_config": "hostname router1\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0",
    "intended_config": "hostname router2\ninterface GigabitEthernet0/0\n ip address 192.168.1.2 255.255.255.0"
  }'
```

**Response:**
```json
{
  "remediation_id": "abc-123",
  "platform": "cisco_ios",
  "remediation_config": "no hostname router1\nhostname router2\ninterface GigabitEthernet0/0\n no ip address 192.168.1.1 255.255.255.0\n ip address 192.168.1.2 255.255.255.0",
  "rollback_config": "...",
  "summary": {
    "additions": 3,
    "deletions": 2,
    "modifications": 0
  },
  "tags": {}
}
```

#### Apply Tags to Remediation
```bash
POST /api/v1/remediation/{remediation_id}/tags
```
Apply tag rules to an existing remediation.

#### Filter Remediation by Tags
```bash
GET /api/v1/remediation/{remediation_id}/filter?include_tags=safe&exclude_tags=risky
```
Filter remediation commands by tags.

### Multi-Device Reporting

#### Create Report
```bash
POST /api/v1/reports
```
Create a multi-device configuration report.

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/reports \
  -H "Content-Type: application/json" \
  -d '{
    "remediations": [
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
  }'
```

#### Get Report Summary
```bash
GET /api/v1/reports/{report_id}/summary
```
Get aggregated statistics for a report.

#### Get Report Changes
```bash
GET /api/v1/reports/{report_id}/changes?tag=safe&min_devices=2
```
Get detailed change analysis showing which changes appear across multiple devices.

#### Export Report
```bash
GET /api/v1/reports/{report_id}/export?format=json|csv|yaml
```
Export report in specified format.

### Platform Information

#### List Platforms
```bash
GET /api/v1/platforms
```
List all supported network platforms.

#### Get Platform Rules
```bash
GET /api/v1/platforms/{platform}/rules
```
Get platform-specific configuration rules.

#### Validate Configuration
```bash
POST /api/v1/platforms/{platform}/validate
```
Validate configuration for a specific platform.

### Batch Operations

#### Create Batch Job
```bash
POST /api/v1/batch/remediation
```
Create a batch remediation job for multiple devices.

#### Get Batch Job Status
```bash
GET /api/v1/batch/jobs/{job_id}
```
Get the status and progress of a batch job.

#### Get Batch Job Results
```bash
GET /api/v1/batch/jobs/{job_id}/results
```
Get the results of a completed batch job.

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=hier_config_api --cov-report=html

# Run specific test file
poetry run pytest tests/test_configs.py -v
```

### Code Quality

```bash
# Run ruff linter
poetry run ruff check .

# Run ruff formatter
poetry run ruff format .

# Run mypy type checker
poetry run mypy hier_config_api

# Run all linters
poetry run ruff check . && poetry run mypy hier_config_api
```

## Supported Platforms

- Cisco IOS (`cisco_ios`)
- Cisco NX-OS (`cisco_nxos`)
- Cisco IOS-XR (`cisco_iosxr`)
- Juniper Junos (`juniper_junos`)
- Arista EOS (`arista_eos`)
- Generic (`generic`)

## Architecture

```
hier-config-api/
├── hier_config_api/
│   ├── models/          # Pydantic models for request/response validation
│   ├── routers/         # API endpoint definitions
│   ├── services/        # Business logic layer
│   ├── utils/           # Utility functions (storage, etc.)
│   └── main.py          # FastAPI application entry point
├── tests/               # Pytest test suite
└── pyproject.toml       # Project configuration
```

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Related Projects

- [hier_config](https://github.com/netdevops/hier_config) - The core library powering this API
