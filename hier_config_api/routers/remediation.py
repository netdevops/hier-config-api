"""API router for remediation operations."""

from typing import Annotated, Any

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


def _generate_and_store(request: GenerateRemediationRequest) -> dict[str, Any]:
    """Generate a remediation, persist it, and stamp it with its ID."""
    result = RemediationService.generate_remediation(request)
    remediation_id = storage.store_remediation(result)
    result["remediation_id"] = remediation_id
    return result


@router.post("/generate")
async def generate_remediation(
    request: GenerateRemediationRequest,
) -> GenerateRemediationResponse:
    """Generate remediation and rollback configurations."""
    try:
        result = _generate_and_store(request)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to generate remediation: {e!s}"
        ) from e
    return GenerateRemediationResponse(
        remediation_id=result["remediation_id"],
        platform=result["platform"],
        remediation_config=result["remediation_config"],
        rollback_config=result["rollback_config"],
        summary=result["summary"],
        tags=result["tags"],
    )


def _apply_and_store_tags(
    remediation_id: str,
    remediation_data: dict[str, Any],
    request: ApplyTagsRequest,
) -> tuple[str, dict[str, list[str]]]:
    """Apply tag rules to a stored remediation and persist the tags."""
    remediation_config = remediation_data["remediation_config"]
    tagged_config, tags = RemediationService.apply_tags(
        remediation_config, request.tag_rules
    )
    storage.update_remediation(remediation_id, {"tags": tags})
    return tagged_config, tags


@router.post("/{remediation_id}/tags")
async def apply_tags(
    remediation_id: str, request: ApplyTagsRequest
) -> ApplyTagsResponse:
    """Apply tags to an existing remediation."""
    remediation_data = storage.get_remediation(remediation_id)
    if not remediation_data:
        raise HTTPException(status_code=404, detail="Remediation not found")

    try:
        tagged_config, tags = _apply_and_store_tags(
            remediation_id, remediation_data, request
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to apply tags: {e!s}"
        ) from e
    return ApplyTagsResponse(
        remediation_id=remediation_id, remediation_config=tagged_config, tags=tags
    )


@router.get("/{remediation_id}/filter")
async def filter_remediation(
    remediation_id: str,
    include_tags: Annotated[list[str] | None, Query()] = None,
    exclude_tags: Annotated[list[str] | None, Query()] = None,
) -> FilterRemediationResponse:
    """Filter remediation by tags."""
    remediation_data = storage.get_remediation(remediation_id)
    if not remediation_data:
        raise HTTPException(status_code=404, detail="Remediation not found")

    remediation_config = remediation_data["remediation_config"]
    tags = remediation_data.get("tags", {})

    try:
        filtered_config, summary = RemediationService.filter_remediation(
            remediation_config, tags, include_tags, exclude_tags
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to filter remediation: {e!s}"
        ) from e
    return FilterRemediationResponse(
        remediation_id=remediation_id,
        filtered_config=filtered_config,
        summary=summary,
    )
