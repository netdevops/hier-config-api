# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

hier-config-api is a FastAPI REST API providing an interface to the [hier_config](https://github.com/netdevops/hier_config) network configuration management library. It enables comparing, analyzing, and generating remediation commands for network device configurations across platforms (Cisco IOS, NX-OS, IOS-XR, Juniper Junos, Arista EOS).

## Commands

```bash
# Install dependencies
poetry install              # production deps
poetry install --with dev   # include dev deps

# Run development server (with hot reload)
poetry run uvicorn hier_config_api.main:app --reload

# Linting & formatting
poetry run ruff check .             # lint
poetry run ruff check . --fix       # lint with auto-fix
poetry run ruff format .            # format
poetry run ruff format --check .    # check formatting

# Type checking
poetry run mypy hier_config_api

# Tests
poetry run pytest                                   # all tests (includes coverage)
poetry run pytest tests/test_configs.py -v          # single test file
poetry run pytest tests/test_configs.py::test_parse_config -v  # single test

# Documentation
poetry run mkdocs serve    # local preview with live reload
poetry run mkdocs build    # build static site
```

## Architecture

**Layered design:** Routers → Services → hier_config library, with Pydantic models for request/response validation.

- `hier_config_api/main.py` — FastAPI app setup, CORS middleware, router registration. Custom doc URLs at `/api/docs`, `/api/redoc`, `/api/openapi.json`.
- `hier_config_api/routers/` — API endpoint definitions. Each router uses `prefix="/api/v1/{domain}"`. Routers delegate to service classes and wrap errors in `HTTPException`.
- `hier_config_api/services/` — Business logic as classes with **static methods**. Each service maps to a router: `ConfigService`, `RemediationService`, `ReportService`, `PlatformService`.
- `hier_config_api/models/` — Pydantic `BaseModel` classes for request/response validation, organized by domain (`config.py`, `remediation.py`, `report.py`, `platform.py`). All fields use `Field()` with descriptions.
- `hier_config_api/utils/storage.py` — In-memory dictionary storage (no persistence). Global `storage` singleton used by services for reports, jobs, and remediations.

**API endpoint groups** (all under `/api/v1/`):
- `/configs` — parse, compare, predict, merge, search configurations
- `/remediation` — generate remediation/rollback, apply tags, filter by tags
- `/reports` — multi-device reports with summary, changes, export (JSON/CSV/YAML)
- `/platforms` — list platforms, get rules, validate configs
- `/batch` — batch remediation jobs with status tracking

## Code Quality

- **Ruff**: linter and formatter, line length 100, target Python 3.10
- **MyPy**: strict mode enabled; `hier_config.*` has `ignore_missing_imports`
- **Pytest**: asyncio_mode="auto", coverage configured via `--cov=hier_config_api`
- Tests use `FastAPI.TestClient` with fixtures in `tests/conftest.py`

## CI

GitHub Actions runs on push/PR to `main`/`develop`:
- **Lint job**: ruff check, ruff format --check, mypy
- **Test job**: pytest across Python 3.10, 3.11, 3.12
