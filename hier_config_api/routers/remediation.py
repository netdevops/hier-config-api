"""API router for remediation operations."""

from fastapi import APIRouter, HTTPException, Query

from hier_config_api.models.remediation import (
    ApplyTagsRequest,
    ApplyTagsResponse,
    FilterRemediationResponse,
    GenerateRemediationRequest,
    GenerateRemediationResponse,
)
from hier_config_api.services.remediation_service import RemediationService
from hier_config_api.utils.storage import storage

router = APIRouter(prefix="/api/v1/remediation", tags=["remediation"])


@router.post("/generate", response_model=GenerateRemediationResponse)
async def generate_remediation(request: GenerateRemediationRequest) -> GenerateRemediationResponse:
    """Generate remediation and rollback configurations."""
    try:
        result = RemediationService.generate_remediation(
            platform=request.platform,
            running_config=request.running_config,
            intended_config=request.intended_config,
            tag_rules=request.tag_rules,
            include_tags=request.include_tags,
            exclude_tags=request.exclude_tags,
        )

        # Store remediation
        remediation_id = storage.store_remediation(result)
        result["remediation_id"] = remediation_id

        return GenerateRemediationResponse(
            remediation_id=remediation_id,
            platform=result["platform"],
            remediation_config=result["remediation_config"],
            rollback_config=result["rollback_config"],
            summary=result["summary"],
            tags=result["tags"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to generate remediation: {str(e)}"
        ) from e


@router.post("/{remediation_id}/tags", response_model=ApplyTagsResponse)
async def apply_tags(remediation_id: str, request: ApplyTagsRequest) -> ApplyTagsResponse:
    """Apply tags to an existing remediation."""
    remediation_data = storage.get_remediation(remediation_id)
    if not remediation_data:
        raise HTTPException(status_code=404, detail="Remediation not found")

    try:
        remediation_config = remediation_data["remediation_config"]
        tagged_config, tags = RemediationService.apply_tags(
            remediation_config, request.tag_rules
        )

        # Update stored remediation
        storage.update_remediation(remediation_id, {"tags": tags})

        return ApplyTagsResponse(
            remediation_id=remediation_id, remediation_config=tagged_config, tags=tags
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to apply tags: {str(e)}") from e


@router.get("/{remediation_id}/filter", response_model=FilterRemediationResponse)
async def filter_remediation(
    remediation_id: str,
    include_tags: list[str] = Query(None),
    exclude_tags: list[str] = Query(None),
) -> FilterRemediationResponse:
    """Filter remediation by tags."""
    remediation_data = storage.get_remediation(remediation_id)
    if not remediation_data:
        raise HTTPException(status_code=404, detail="Remediation not found")

    try:
        remediation_config = remediation_data["remediation_config"]
        tags = remediation_data.get("tags", {})

        filtered_config, summary = RemediationService.filter_remediation(
            remediation_config, tags, include_tags, exclude_tags
        )

        return FilterRemediationResponse(
            remediation_id=remediation_id, filtered_config=filtered_config, summary=summary
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to filter remediation: {str(e)}"
        ) from e
