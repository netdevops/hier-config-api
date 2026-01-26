"""API router for batch operations."""

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


@router.post("/remediation", response_model=BatchJobResponse)
async def create_batch_remediation(request: BatchJobRequest) -> BatchJobResponse:
    """Create a batch remediation job for multiple devices."""
    try:
        job_data = PlatformService.create_batch_job(request.device_configs)
        job_id = storage.store_job(job_data)

        # Process the job (in a real implementation, this would be async/background)
        PlatformService.process_batch_job(job_data)
        storage.update_job(job_id, job_data)

        return BatchJobResponse(job_id=job_id, total_devices=job_data["total_devices"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create batch job: {str(e)}") from e


@router.get("/jobs/{job_id}", response_model=BatchJobStatus)
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
        raise HTTPException(status_code=400, detail=f"Failed to get job status: {str(e)}") from e


@router.get("/jobs/{job_id}/results", response_model=BatchJobResults)
async def get_batch_job_results(job_id: str) -> BatchJobResults:
    """Get the results of a completed batch job."""
    job_data = storage.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    if job_data["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Job is not yet completed")

    try:
        summary = {
            "total_devices": job_data["total_devices"],
            "completed_devices": job_data["completed_devices"],
            "failed_devices": job_data["failed_devices"],
            "status": job_data["status"],
        }

        return BatchJobResults(
            job_id=job_id,
            status=job_data["status"],
            results=job_data["results"],
            summary=summary,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get job results: {str(e)}") from e
