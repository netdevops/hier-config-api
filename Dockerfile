FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir "poetry>=2.0,<3.0"

WORKDIR /app

# README.md is required because pyproject.toml declares it as the readme
COPY pyproject.toml poetry.lock README.md ./


# Development image: full toolchain; source is bind-mounted by docker compose
FROM base AS development

RUN poetry install --no-root --with dev

COPY . .

RUN poetry install --with dev

EXPOSE 8000

CMD ["uvicorn", "hier_config_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# Production image: runtime dependencies only
FROM base AS production

RUN poetry install --no-root --only main

COPY hier_config_api ./hier_config_api

RUN poetry install --only main

EXPOSE 8000

CMD ["uvicorn", "hier_config_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
