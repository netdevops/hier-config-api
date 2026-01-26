# API Overview

The hier-config-api provides a comprehensive REST API for network configuration management.

## Base URL

All API endpoints are prefixed with `/api/v1/`:

```
http://localhost:8000/api/v1/
```

## Authentication

Currently, the API does not require authentication. For production deployments, consider adding:

- API keys
- OAuth2/JWT tokens
- IP allowlisting

## Response Format

All responses are in JSON format with appropriate HTTP status codes.

### Success Response

```json
{
  "field1": "value1",
  "field2": "value2"
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request - Invalid input |
| 404  | Not Found - Resource doesn't exist |
| 422  | Validation Error - Invalid request body |
| 500  | Internal Server Error |

## API Categories

### Configuration Operations

Endpoints for parsing, comparing, and manipulating configurations:

- `POST /api/v1/configs/parse` - Parse configuration
- `POST /api/v1/configs/compare` - Compare configurations
- `POST /api/v1/configs/predict` - Predict future state
- `POST /api/v1/configs/merge` - Merge configurations
- `POST /api/v1/configs/search` - Search configuration

[Learn more →](configurations.md)

### Remediation Workflows

Generate and manage remediation configurations:

- `POST /api/v1/remediation/generate` - Generate remediation
- `POST /api/v1/remediation/{id}/tags` - Apply tags
- `GET /api/v1/remediation/{id}/filter` - Filter by tags

[Learn more →](remediation.md)

### Multi-Device Reports

Create and analyze fleet-wide configuration reports:

- `POST /api/v1/reports` - Create report
- `GET /api/v1/reports/{id}/summary` - Get summary
- `GET /api/v1/reports/{id}/changes` - Get changes
- `GET /api/v1/reports/{id}/export` - Export report

[Learn more →](reports.md)

### Platform Information

Platform-specific information and validation:

- `GET /api/v1/platforms` - List platforms
- `GET /api/v1/platforms/{platform}/rules` - Get rules
- `POST /api/v1/platforms/{platform}/validate` - Validate config

[Learn more →](platforms.md)

### Batch Operations

Process multiple devices in parallel:

- `POST /api/v1/batch/remediation` - Create batch job
- `GET /api/v1/batch/jobs/{id}` - Get job status
- `GET /api/v1/batch/jobs/{id}/results` - Get results

[Learn more →](batch.md)

## Interactive Documentation

The API provides automatic interactive documentation:

- **Swagger UI**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **ReDoc**: [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc)

These interfaces allow you to:

- Browse all available endpoints
- View request/response schemas
- Test endpoints directly from the browser
- Generate example requests

## Rate Limiting

Currently, there is no rate limiting. For production deployments, consider implementing rate limiting at:

- Application level (using FastAPI middleware)
- Reverse proxy level (Nginx, Traefik)
- API gateway level (Kong, Tyk)

## Pagination

Currently, endpoints return all results. Future versions will support pagination for large result sets:

```
GET /api/v1/reports/{id}/changes?page=1&page_size=50
```

## Versioning

The API uses URL-based versioning (`/api/v1/`). Breaking changes will result in a new version (`/api/v2/`), while the old version remains available for backward compatibility.
