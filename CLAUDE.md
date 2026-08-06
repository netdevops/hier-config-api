# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

hier-config-api is a FastAPI REST API providing an interface to the [hier_config](https://github.com/netdevops/hier_config) network configuration management library. It enables comparing, analyzing, and generating remediation commands for network device configurations across platforms (Cisco IOS, NX-OS, IOS-XR, Juniper Junos, Arista EOS).

## Commands

All commands use **poetry** (not pip):

```bash
# Install dependencies
poetry install

# Run development server (with hot reload)
poetry run uvicorn hier_config_api.main:app --reload

# Full lint + test suite (equivalent to CI)
poetry run python scripts/build.py lint-and-test

# Lint only (ruff format + check, mypy, pyright, pylint, yamllint, flynt — run in parallel)
poetry run python scripts/build.py lint

# Lint with auto-fixes (ruff --fix, ruff format, flynt)
poetry run python scripts/build.py lint --fix

# Tests with coverage (95% coverage required)
poetry run python scripts/build.py pytest --coverage

# Tests without coverage
poetry run pytest                                   # all tests
poetry run pytest tests/test_configs.py -v          # single test file
poetry run pytest tests/test_configs.py::test_parse_config -v  # single test

# Documentation
poetry run mkdocs serve            # local preview with live reload
poetry run mkdocs build --strict   # build static site (CI runs this)
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

This repo follows the hier_config lint/typing/testing standards, enforced by
`scripts/build.py` and CI:

- **Ruff**: `select = ["ALL"]` with preview rules, line length 88, target Python 3.10; formatting via `ruff format` with `docstring-code-format`
- **MyPy**: `strict = true` with the pydantic plugin
- **Pyright**: `typeCheckingMode = "strict"`
- **Pylint**: extension plugins + `pylint_pydantic`; rules already covered by ruff are disabled
- **yamllint / flynt**: YAML style (2-space indent, no document-start) and f-string enforcement
- **Pytest**: flat function-based tests with full type annotations; 95% coverage floor (`--cov=hier_config_api --cov-fail-under=95`)
- Tests use `FastAPI.TestClient` with fixtures in `tests/conftest.py`
- Never loosen lint or coverage configuration to make a change pass; do not add unjustified `# noqa` / `# type: ignore` suppressions

## CI

GitHub Actions runs on push/PR to `develop`/`next`:
- **build job** (Python 3.10–3.14 matrix): `poetry run python scripts/build.py lint` then `poetry run python scripts/build.py pytest --coverage`
- **docs job**: `poetry run mkdocs build --strict`; deploys to GitHub Pages on push to `develop`
