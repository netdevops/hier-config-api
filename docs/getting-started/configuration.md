# Configuration

hier-config-api can be configured through environment variables and command-line options.

## Server Configuration

### Host and Port

By default, the server runs on `127.0.0.1:8000`. Configure this with uvicorn options:

```bash
# Custom host and port
poetry run uvicorn hier_config_api.main:app --host 0.0.0.0 --port 8080

# Listen on all interfaces
poetry run uvicorn hier_config_api.main:app --host 0.0.0.0
```

### Workers

For production, use multiple workers:

```bash
poetry run uvicorn hier_config_api.main:app --workers 4
```

### SSL/TLS

For HTTPS support:

```bash
poetry run uvicorn hier_config_api.main:app \
  --ssl-keyfile=/path/to/key.pem \
  --ssl-certfile=/path/to/cert.pem
```

## Environment Variables

Currently, hier-config-api uses minimal configuration. Future versions will support:

- `API_PREFIX` - Custom API path prefix
- `LOG_LEVEL` - Logging verbosity
- `CORS_ORIGINS` - Allowed CORS origins

## CORS Configuration

By default, CORS is enabled for all origins. In production, modify `hier_config_api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Logging

Configure logging level with uvicorn:

```bash
poetry run uvicorn hier_config_api.main:app --log-level debug
```

Available levels:

- `critical`
- `error`
- `warning`
- `info` (default)
- `debug`
- `trace`

## Performance Tuning

### Worker Processes

Rule of thumb: `(2 * CPU cores) + 1`

```bash
# For a 4-core machine
poetry run uvicorn hier_config_api.main:app --workers 9
```

### Worker Class

For async workloads, use uvloop:

```bash
poetry run uvicorn hier_config_api.main:app --loop uvloop
```

### Timeout

Adjust timeout for long-running operations:

```bash
poetry run uvicorn hier_config_api.main:app --timeout-keep-alive 30
```

## Storage Configuration

Currently, hier-config-api uses in-memory storage for reports and batch jobs. For production deployments with multiple workers, consider:

1. **Redis** - For distributed caching
2. **PostgreSQL** - For persistent storage
3. **File-based** - For simple single-server deployments

These options are planned for future releases.

## Production Deployment

See the [Deployment Guide](../guides/deployment.md) for comprehensive production setup including:

- Nginx reverse proxy
- Systemd service
- Docker containers
- Kubernetes deployments
