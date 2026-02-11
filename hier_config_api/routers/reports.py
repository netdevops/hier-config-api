"""API router for multi-device reporting."""

import logging

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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.post("", response_model=CreateReportResponse)
async def create_report(request: CreateReportRequest) -> CreateReportResponse:
    """Create a multi-device report."""
    try:
        report_data = ReportService.create_report(request.remediations)
        report_id = storage.store_report(report_data)

        return CreateReportResponse(report_id=report_id, total_devices=report_data["total_devices"])
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=f"Failed to create report: {str(e)}") from e


@router.get("/{report_id}/summary", response_model=ReportSummary)
async def get_report_summary(report_id: str) -> ReportSummary:
    """Get summary statistics for a report."""
    report_data = storage.get_report(report_id)
    if not report_data:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportService.get_summary(report_data)


@router.get("/{report_id}/changes", response_model=GetReportChangesResponse)
async def get_report_changes(
    report_id: str, tag: str | None = Query(None), min_devices: int = Query(1)
) -> GetReportChangesResponse:
    """Get detailed change analysis for a report."""
    report_data = storage.get_report(report_id)
    if not report_data:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        changes = ReportService.get_changes(report_data, tag_filter=tag, min_devices=min_devices)

        return GetReportChangesResponse(
            report_id=report_id, changes=changes, total_unique_changes=len(changes)
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to get report changes: {str(e)}"
        ) from e


@router.get("/{report_id}/export", response_class=PlainTextResponse)
async def export_report(report_id: str, format: str = Query("json")) -> str:
    """Export report in specified format (json, csv, yaml)."""
    report_data = storage.get_report(report_id)
    if not report_data:
        raise HTTPException(status_code=404, detail="Report not found")

    if format not in ["json", "csv", "yaml"]:
        raise HTTPException(status_code=400, detail="Format must be one of: json, csv, yaml")

    try:
        return ReportService.export_report(report_data, format_type=format)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=f"Failed to export report: {str(e)}") from e
