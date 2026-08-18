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


@router.get("")
async def list_platforms() -> list[PlatformInfo]:
    """List all supported platforms."""
    try:
        return PlatformService.list_platforms()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list platforms: {e!s}"
        ) from e


@router.get("/{platform}/rules")
async def get_platform_rules(platform: str) -> PlatformRules:
    """Get platform-specific rules and behaviors."""
    try:
        return PlatformService.get_platform_rules(platform)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to get platform rules: {e!s}"
        ) from e


@router.post("/{platform}/validate")
async def validate_config(
    platform: str, request: ValidateConfigRequest
) -> ValidateConfigResponse:
    """Validate configuration for a specific platform."""
    try:
        result = PlatformService.validate_config(platform, request.config_text)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to validate config: {e!s}"
        ) from e
    return ValidateConfigResponse(**result)
