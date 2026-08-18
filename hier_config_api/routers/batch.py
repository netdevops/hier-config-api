"""API router for batch operations."""

from typing import Any

from fastapi import APIRouter, HTTPException

from hier_config_api.models.platform import (
    BatchJobRequest,
    BatchJobResponse,
    BatchJobResults,
    BatchJobStatus,
)
from hier_config_api.services.platform_service import PlatformService
from hier_config_api.utils.storage import storage

router = APIRouter(prefix="/api/v1/batch", tags=["batch"])


def _create_and_run_job(
    device_configs: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    """Create a batch job, process it, and persist the result."""
    job_data = PlatformService.create_batch_job(device_configs)
    job_id = storage.store_job(job_data)

    # Process the job (in a real implementation, this would be async/background)
    PlatformService.process_batch_job(job_data)
    storage.update_job(job_id, job_data)
    return job_id, job_data


@router.post("/remediation")
async def create_batch_remediation(request: BatchJobRequest) -> BatchJobResponse:
    """Create a batch remediation job for multiple devices."""
    try:
        job_id, job_data = _create_and_run_job(request.device_configs)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to create batch job: {e!s}"
        ) from e
    return BatchJobResponse(job_id=job_id, total_devices=job_data["total_devices"])


@router.get("/jobs/{job_id}")
async def get_batch_job_status(job_id: str) -> BatchJobStatus:
    """Get the status of a batch job."""
    job_data = storage.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        return BatchJobStatus(
            job_id=job_id,
            status=job_data["status"],
            progress=job_data["progress"],
            total_devices=job_data["total_devices"],
            completed_devices=job_data["completed_devices"],
            failed_devices=job_data["failed_devices"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to get job status: {e!s}"
        ) from e


@router.get("/jobs/{job_id}/results")
async def get_batch_job_results(job_id: str) -> BatchJobResults:
    """Get the results of a completed batch job."""
    job_data = storage.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    if job_data["status"] not in {"completed", "failed"}:
        raise HTTPException(status_code=400, detail="Job is not yet completed")

    summary = {
        "total_devices": job_data["total_devices"],
        "completed_devices": job_data["completed_devices"],
        "failed_devices": job_data["failed_devices"],
        "status": job_data["status"],
    }

    try:
        return BatchJobResults(
            job_id=job_id,
            status=job_data["status"],
            results=job_data["results"],
            summary=summary,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to get job results: {e!s}"
        ) from e
