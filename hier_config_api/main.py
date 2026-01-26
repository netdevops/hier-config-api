"""Main FastAPI application for hier-config-api."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hier_config_api.routers import batch, configs, platforms, remediation, reports

app = FastAPI(
    title="Hier-Config API",
    description="REST API for hier_config network configuration management",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(configs.router)
app.include_router(remediation.router)
app.include_router(reports.router)
app.include_router(platforms.router)
app.include_router(batch.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Hier-Config API",
        "version": "0.1.0",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
