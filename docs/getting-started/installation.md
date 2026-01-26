# Installation

This guide will help you install and set up hier-config-api.

## Prerequisites

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- Git (for cloning the repository)

## From Source

### 1. Clone the Repository

```bash
git clone https://github.com/netdevops/hier-config-api.git
cd hier-config-api
```

### 2. Install Dependencies

Using Poetry (recommended):

```bash
poetry install
```

This will:

- Create a virtual environment
- Install all dependencies from `pyproject.toml`
- Install hier-config-api in development mode

### 3. Verify Installation

Run the tests to ensure everything is working:

```bash
poetry run pytest
```

You should see output indicating all tests passed:

```
============================== 21 passed in 0.19s ==============================
```

## Development Setup

If you're planning to develop or contribute, install the development dependencies:

```bash
poetry install --with dev
```

This includes additional tools:

- `pytest` - Testing framework
- `ruff` - Linter and formatter
- `mypy` - Type checker
- `mkdocs` - Documentation builder

## Docker Setup (Optional)

A Docker setup is planned for future releases. For now, use the Poetry installation method.

## Next Steps

Once installed, proceed to the [Quick Start](quickstart.md) guide to run your first API server.
