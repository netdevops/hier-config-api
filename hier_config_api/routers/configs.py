"""API router for configuration operations."""

from fastapi import APIRouter, HTTPException

from hier_config_api.models.config import (
    CompareConfigRequest,
    CompareConfigResponse,
    MergeConfigRequest,
    MergeConfigResponse,
    ParseConfigRequest,
    ParseConfigResponse,
    PredictConfigRequest,
    PredictConfigResponse,
    SearchConfigRequest,
    SearchConfigResponse,
)
from hier_config_api.services.config_service import ConfigService

router = APIRouter(prefix="/api/v1/configs", tags=["configurations"])


@router.post("/parse")
async def parse_config(request: ParseConfigRequest) -> ParseConfigResponse:
    """Parse configuration text into structured format."""
    try:
        structured_config = ConfigService.parse_config(
            request.platform, request.config_text
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to parse config: {e!s}"
        ) from e
    return ParseConfigResponse(
        platform=request.platform, structured_config=structured_config
    )


@router.post("/compare")
async def compare_configs(request: CompareConfigRequest) -> CompareConfigResponse:
    """Compare two configurations and return differences."""
    try:
        unified_diff, has_changes = ConfigService.compare_configs(
            request.platform, request.running_config, request.intended_config
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to compare configs: {e!s}"
        ) from e
    return CompareConfigResponse(
        platform=request.platform,
        unified_diff=unified_diff,
        has_changes=has_changes,
    )


@router.post("/predict")
async def predict_config(request: PredictConfigRequest) -> PredictConfigResponse:
    """Predict future configuration state after applying commands."""
    try:
        predicted_config = ConfigService.predict_config(
            request.platform, request.current_config, request.commands_to_apply
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to predict config: {e!s}"
        ) from e
    return PredictConfigResponse(
        platform=request.platform, predicted_config=predicted_config
    )


@router.post("/merge")
async def merge_configs(request: MergeConfigRequest) -> MergeConfigResponse:
    """Merge multiple configurations into one."""
    try:
        merged_config = ConfigService.merge_configs(request.platform, request.configs)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to merge configs: {e!s}"
        ) from e
    return MergeConfigResponse(platform=request.platform, merged_config=merged_config)


@router.post("/search")
async def search_config(request: SearchConfigRequest) -> SearchConfigResponse:
    """Search configuration for matching sections."""
    try:
        matches = ConfigService.search_config(
            platform=request.platform,
            config_text=request.config_text,
            match_rules=request.match_rules,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to search config: {e!s}"
        ) from e
    return SearchConfigResponse(
        platform=request.platform, matches=matches, match_count=len(matches)
    )
