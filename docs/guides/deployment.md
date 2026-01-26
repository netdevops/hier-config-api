# Deployment Guide

Production deployment strategies for hier-config-api.

## Systemd Service

### 1. Create Service File

Create `/etc/systemd/system/hier-config-api.service`:

```ini
[Unit]
Description=hier-config-api
After=network.target

[Service]
Type=simple
User=api
Group=api
WorkingDirectory=/opt/hier-config-api
Environment="PATH=/opt/hier-config-api/.venv/bin"
ExecStart=/opt/hier-config-api/.venv/bin/uvicorn hier_config_api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Install and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable hier-config-api
sudo systemctl start hier-config-api
sudo systemctl status hier-config-api
```

## Nginx Reverse Proxy

### Configuration

Create `/etc/nginx/sites-available/hier-config-api`:

```nginx
upstream hier_config_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://hier_config_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for long-running operations
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

### Enable HTTPS with Let's Encrypt

```bash
sudo certbot --nginx -d api.example.com
```

## Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry==2.3.1

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# Copy application
COPY hier_config_api ./hier_config_api

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "hier_config_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run

```bash
# Build image
docker build -t hier-config-api:latest .

# Run container
docker run -d \
  --name hier-config-api \
  -p 8000:8000 \
  hier-config-api:latest
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    restart: always
    environment:
      - LOG_LEVEL=info
    command: uvicorn hier_config_api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Run:

```bash
docker-compose up -d
```

## Kubernetes Deployment

### Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hier-config-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hier-config-api
  template:
    metadata:
      labels:
        app: hier-config-api
    spec:
      containers:
      - name: api
        image: hier-config-api:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

### Service

Create `k8s/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: hier-config-api
spec:
  selector:
    app: hier-config-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Deploy

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## Production Checklist

### Security

- [ ] Enable HTTPS/TLS
- [ ] Implement authentication (API keys, OAuth)
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Use security headers
- [ ] Keep dependencies updated

### Performance

- [ ] Configure appropriate worker count
- [ ] Enable caching where applicable
- [ ] Monitor resource usage
- [ ] Set up auto-scaling
- [ ] Configure timeouts

### Monitoring

- [ ] Set up logging (structured logs)
- [ ] Configure metrics collection
- [ ] Set up health checks
- [ ] Configure alerting
- [ ] Monitor error rates

### Reliability

- [ ] Implement graceful shutdown
- [ ] Configure restart policies
- [ ] Set up backups (if using persistent storage)
- [ ] Test disaster recovery
- [ ] Document runbook procedures

## Environment Variables

Future versions will support configuration via environment variables:

```bash
export API_PREFIX=/api/v1
export LOG_LEVEL=info
export CORS_ORIGINS=https://app.example.com
export MAX_WORKERS=4
```

## Monitoring and Logging

### Structured Logging

Configure JSON logging for better parsing:

```python
import logging
import json

logging.basicConfig(
    format='%(message)s',
    level=logging.INFO
)
```

### Prometheus Metrics

Add prometheus-fastapi-instrumentator:

```bash
poetry add prometheus-fastapi-instrumentator
```

### Health Checks

The `/health` endpoint provides basic health status. Extend it for deeper checks:

```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "uptime": get_uptime()
    }
```
