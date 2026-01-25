"""API router for platform information."""

from fastapi import APIRouter, HTTPException

from hier_config_api.models.platform import (
    PlatformInfo,
    PlatformRules,
    ValidateConfigRequest,
    ValidateConfigResponse,
)
from hier_config_api.services.platform_service import PlatformService

router = APIRouter(prefix="/api/v1/platforms", tags=["platforms"])


@router.get("", response_model=list[PlatformInfo])
async def list_platforms() -> list[PlatformInfo]:
    """List all supported platforms."""
    try:
        return PlatformService.list_platforms()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list platforms: {str(e)}"
        ) from e


@router.get("/{platform}/rules", response_model=PlatformRules)
async def get_platform_rules(platform: str) -> PlatformRules:
    """Get platform-specific rules and behaviors."""
    try:
        return PlatformService.get_platform_rules(platform)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to get platform rules: {str(e)}"
        ) from e


@router.post("/{platform}/validate", response_model=ValidateConfigResponse)
async def validate_config(platform: str, request: ValidateConfigRequest) -> ValidateConfigResponse:
    """Validate configuration for a specific platform."""
    try:
        result = PlatformService.validate_config(platform, request.config_text)
        return ValidateConfigResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to validate config: {str(e)}"
        ) from e
