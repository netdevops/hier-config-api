"""API router for multi-device reporting."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from hier_config_api.models.report import (
    CreateReportRequest,
    CreateReportResponse,
    GetReportChangesResponse,
    ReportSummary,
)
from hier_config_api.services.report_service import ReportService
from hier_config_api.utils.storage import storage

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.post("")
async def create_report(request: CreateReportRequest) -> CreateReportResponse:
    """Create a multi-device report."""
    try:
        report_data = ReportService.create_report(request.remediations)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to create report: {e!s}"
        ) from e
    report_id = storage.store_report(report_data)
    return CreateReportResponse(
        report_id=report_id, total_devices=report_data["total_devices"]
    )


@router.get("/{report_id}/summary")
async def get_report_summary(report_id: str) -> ReportSummary:
    """Get summary statistics for a report."""
    report_data = storage.get_report(report_id)
    if not report_data:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        return ReportService.get_summary(report_data)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to get report summary: {e!s}"
        ) from e


@router.get("/{report_id}/changes")
async def get_report_changes(
    report_id: str,
    tag: Annotated[str | None, Query()] = None,
    min_devices: Annotated[int, Query()] = 1,
) -> GetReportChangesResponse:
    """Get detailed change analysis for a report."""
    report_data = storage.get_report(report_id)
    if not report_data:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        changes = ReportService.get_changes(
            report_data, tag_filter=tag, min_devices=min_devices
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to get report changes: {e!s}"
        ) from e
    return GetReportChangesResponse(
        report_id=report_id, changes=changes, total_unique_changes=len(changes)
    )


@router.get("/{report_id}/export", response_class=PlainTextResponse)
async def export_report(
    report_id: str,
    export_format: Annotated[str, Query(alias="format")] = "json",
) -> str:
    """Export report in specified format (json, csv, yaml)."""
    report_data = storage.get_report(report_id)
    if not report_data:
        raise HTTPException(status_code=404, detail="Report not found")

    if export_format not in {"json", "csv", "yaml"}:
        raise HTTPException(
            status_code=400, detail="Format must be one of: json, csv, yaml"
        )

    try:
        return ReportService.export_report(report_data, format_type=export_format)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to export report: {e!s}"
        ) from e
