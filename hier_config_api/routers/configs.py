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


@router.post("/parse", response_model=ParseConfigResponse)
async def parse_config(request: ParseConfigRequest) -> ParseConfigResponse:
    """Parse configuration text into structured format."""
    try:
        structured_config = ConfigService.parse_config(request.platform, request.config_text)
        return ParseConfigResponse(platform=request.platform, structured_config=structured_config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse config: {str(e)}") from e


@router.post("/compare", response_model=CompareConfigResponse)
async def compare_configs(request: CompareConfigRequest) -> CompareConfigResponse:
    """Compare two configurations and return differences."""
    try:
        unified_diff, has_changes = ConfigService.compare_configs(
            request.platform, request.running_config, request.intended_config
        )
        return CompareConfigResponse(
            platform=request.platform, unified_diff=unified_diff, has_changes=has_changes
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to compare configs: {str(e)}") from e


@router.post("/predict", response_model=PredictConfigResponse)
async def predict_config(request: PredictConfigRequest) -> PredictConfigResponse:
    """Predict future configuration state after applying commands."""
    try:
        predicted_config = ConfigService.predict_config(
            request.platform, request.current_config, request.commands_to_apply
        )
        return PredictConfigResponse(platform=request.platform, predicted_config=predicted_config)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to predict config: {str(e)}"
        ) from e


@router.post("/merge", response_model=MergeConfigResponse)
async def merge_configs(request: MergeConfigRequest) -> MergeConfigResponse:
    """Merge multiple configurations into one."""
    try:
        merged_config = ConfigService.merge_configs(request.platform, request.configs)
        return MergeConfigResponse(platform=request.platform, merged_config=merged_config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to merge configs: {str(e)}") from e


@router.post("/search", response_model=SearchConfigResponse)
async def search_config(request: SearchConfigRequest) -> SearchConfigResponse:
    """Search configuration for matching sections."""
    try:
        matches = ConfigService.search_config(
            platform=request.platform,
            config_text=request.config_text,
            equals=request.match_rules.equals,
            contains=request.match_rules.contains,
            startswith=request.match_rules.startswith,
            regex_pattern=request.match_rules.regex,
        )
        return SearchConfigResponse(
            platform=request.platform, matches=matches, match_count=len(matches)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to search config: {str(e)}") from e
