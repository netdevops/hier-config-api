# hier-config-api

[![CI](https://github.com/netdevops/hier-config-api/workflows/CI/badge.svg)](https://github.com/netdevops/hier-config-api/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/netdevops/hier-config-api/branch/main/graph/badge.svg)](https://codecov.io/gh/netdevops/hier-config-api)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A comprehensive REST API for [hier_config](https://github.com/netdevops/hier_config) network configuration management.

## Overview

hier-config-api provides a FastAPI-based REST interface to the powerful hier_config library, enabling network engineers and automation tools to:

- **Compare and Diff**: Analyze differences between running and intended configurations
- **Generate Remediation**: Automatically create commands to achieve desired state
- **Multi-Device Analysis**: Aggregate and analyze changes across device fleets
- **Platform Support**: Work with Cisco IOS/NX-OS/IOS-XR, Juniper Junos, Arista EOS, and more
- **Batch Processing**: Handle multiple devices in parallel for efficiency
- **Flexible Export**: Output results in JSON, CSV, or YAML formats

## Key Features

### Configuration Operations
Parse, compare, merge, and search network configurations across different platforms.

### Remediation Workflows
Generate precise remediation and rollback configurations with tag-based filtering for safe, incremental deployments.

### Multi-Device Reporting
Create comprehensive reports showing configuration drift and changes across your entire network infrastructure.

### RESTful Architecture
Clean, well-documented REST API with automatic OpenAPI/Swagger documentation.

## Quick Example

```bash
# Generate remediation for a configuration change
curl -X POST http://localhost:8000/api/v1/remediation/generate \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "cisco_ios",
    "running_config": "hostname router1\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0",
    "intended_config": "hostname router2\ninterface GigabitEthernet0/0\n ip address 192.168.1.2 255.255.255.0"
  }'
```

## Getting Started

Check out the [Installation Guide](getting-started/installation.md) to get up and running quickly, or jump to the [Quick Start](getting-started/quickstart.md) for a hands-on introduction.

## Architecture

hier-config-api follows a clean, layered architecture:

```
┌─────────────────────────────────────┐
│         REST API Layer              │
│      (FastAPI Routers)              │
├─────────────────────────────────────┤
│       Service Layer                 │
│    (Business Logic)                 │
├─────────────────────────────────────┤
│      Pydantic Models                │
│  (Validation & Serialization)       │
├─────────────────────────────────────┤
│      hier_config Library            │
│  (Core Configuration Logic)         │
└─────────────────────────────────────┘
```

## Supported Platforms

- Cisco IOS
- Cisco NX-OS
- Cisco IOS-XR
- Juniper Junos
- Arista EOS
- Generic

## Why hier-config-api?

- **Production Ready**: Comprehensive test suite, type hints, and linting
- **Well Documented**: Automatic API docs, examples, and guides
- **Flexible**: RESTful design works with any programming language or tool
- **Scalable**: Stateless design with batch processing for large deployments
- **Standards-Based**: OpenAPI/Swagger for easy integration

## Contributing

We welcome contributions! See the [Contributing Guide](guides/contributing.md) for details on how to get involved.

## License

See [LICENSE](https://github.com/netdevops/hier-config-api/blob/main/LICENSE) for details.
