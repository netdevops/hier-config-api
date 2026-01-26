# Development Guide

Guide for setting up a development environment and contributing to hier-config-api.

## Development Setup

### Prerequisites

- Python 3.10+
- Poetry 2.0+
- Git

### Clone and Install

```bash
# Clone repository
git clone https://github.com/netdevops/hier-config-api.git
cd hier-config-api

# Install all dependencies including dev tools
poetry install

# Activate virtual environment
poetry shell
```

## Project Structure

```
hier-config-api/
├── hier_config_api/          # Main application code
│   ├── models/               # Pydantic models
│   ├── routers/              # API route handlers
│   ├── services/             # Business logic
│   ├── utils/                # Utilities
│   └── main.py               # FastAPI application
├── tests/                    # Test suite
│   ├── conftest.py           # Pytest fixtures
│   ├── test_configs.py       # Config endpoint tests
│   ├── test_remediation.py   # Remediation tests
│   ├── test_reports.py       # Report tests
│   └── test_platforms.py     # Platform tests
├── docs/                     # Documentation
├── .github/workflows/        # CI/CD workflows
├── pyproject.toml            # Project configuration
└── mkdocs.yml                # Documentation config
```

## Running Tests

### All Tests

```bash
poetry run pytest
```

### With Coverage

```bash
poetry run pytest --cov=hier_config_api --cov-report=html
```

View coverage report at `htmlcov/index.html`.

### Specific Test File

```bash
poetry run pytest tests/test_configs.py -v
```

### Single Test

```bash
poetry run pytest tests/test_configs.py::test_parse_config -v
```

## Code Quality

### Linting

Run ruff linter:

```bash
poetry run ruff check .
```

Auto-fix issues:

```bash
poetry run ruff check . --fix
```

### Formatting

Check formatting:

```bash
poetry run ruff format --check .
```

Format code:

```bash
poetry run ruff format .
```

### Type Checking

Run mypy:

```bash
poetry run mypy hier_config_api
```

### Run All Checks

```bash
poetry run ruff check . && \
poetry run ruff format --check . && \
poetry run mypy hier_config_api && \
poetry run pytest
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Make Changes

Edit code following the project conventions:

- Use type hints for all functions
- Write docstrings for public APIs
- Follow existing code structure
- Add tests for new features

### 3. Run Tests

```bash
poetry run pytest
```

### 4. Format and Lint

```bash
poetry run ruff format .
poetry run ruff check .
poetry run mypy hier_config_api
```

### 5. Commit Changes

```bash
git add .
git commit -m "Add new feature"
```

Follow conventional commit format:

- `feat: Add new endpoint`
- `fix: Resolve bug in parser`
- `docs: Update API documentation`
- `test: Add tests for reports`
- `refactor: Improve service layer`

### 6. Push and Create PR

```bash
git push origin feature/my-new-feature
```

Then create a pull request on GitHub.

## Adding New Endpoints

### 1. Define Pydantic Models

Create request/response models in `hier_config_api/models/`:

```python
# models/myfeature.py
from pydantic import BaseModel, Field

class MyFeatureRequest(BaseModel):
    """Request model for my feature."""
    param1: str = Field(..., description="Parameter 1")
    param2: int = Field(..., description="Parameter 2")

class MyFeatureResponse(BaseModel):
    """Response model for my feature."""
    result: str = Field(..., description="Result value")
```

### 2. Implement Service Logic

Add business logic in `hier_config_api/services/`:

```python
# services/myfeature_service.py
class MyFeatureService:
    """Service for my feature."""

    @staticmethod
    def process(param1: str, param2: int) -> str:
        """Process the feature request."""
        # Implementation here
        return f"Processed: {param1} with {param2}"
```

### 3. Create Router

Add endpoints in `hier_config_api/routers/`:

```python
# routers/myfeature.py
from fastapi import APIRouter, HTTPException

from hier_config_api.models.myfeature import MyFeatureRequest, MyFeatureResponse
from hier_config_api.services.myfeature_service import MyFeatureService

router = APIRouter(prefix="/api/v1/myfeature", tags=["myfeature"])

@router.post("", response_model=MyFeatureResponse)
async def process_feature(request: MyFeatureRequest) -> MyFeatureResponse:
    """Process my feature."""
    try:
        result = MyFeatureService.process(request.param1, request.param2)
        return MyFeatureResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
```

### 4. Register Router

Add router to `hier_config_api/main.py`:

```python
from hier_config_api.routers import myfeature

app.include_router(myfeature.router)
```

### 5. Write Tests

Create tests in `tests/test_myfeature.py`:

```python
def test_process_feature(client):
    """Test my feature endpoint."""
    response = client.post(
        "/api/v1/myfeature",
        json={"param1": "test", "param2": 42}
    )
    assert response.status_code == 200
    assert "result" in response.json()
```

## Debugging

### VS Code

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "hier_config_api.main:app",
        "--reload"
      ],
      "jinja": true
    }
  ]
}
```

### PyCharm

1. Edit Configurations → Add Python
2. Script path: `uvicorn`
3. Parameters: `hier_config_api.main:app --reload`
4. Environment variables: `PYTHONUNBUFFERED=1`

## Documentation

Build documentation locally:

```bash
poetry run mkdocs serve
```

View at http://localhost:8000

Build static site:

```bash
poetry run mkdocs build
```

## Continuous Integration

The project uses GitHub Actions for CI/CD. On push or PR:

1. **Lint Job**: Runs ruff and mypy
2. **Test Job**: Runs pytest on Python 3.10, 3.11, 3.12

View workflow in `.github/workflows/ci.yml`.
