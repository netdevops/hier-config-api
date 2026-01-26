"""Pydantic models for multi-device reporting."""

from pydantic import BaseModel, Field


class DeviceRemediation(BaseModel):
    """Model for a single device's remediation data."""

    device_id: str = Field(..., description="Unique device identifier")
    platform: str = Field(..., description="Platform type (e.g., cisco_ios, juniper_junos)")
    running_config: str = Field(..., description="Current running configuration")
    intended_config: str = Field(..., description="Desired configuration state")


class CreateReportRequest(BaseModel):
    """Request model for creating a multi-device report."""

    remediations: list[DeviceRemediation] = Field(
        ..., description="List of device remediation data"
    )


class CreateReportResponse(BaseModel):
    """Response model for created report."""

    report_id: str = Field(..., description="Unique report identifier")
    total_devices: int = Field(..., description="Total number of devices in report")


class ReportSummary(BaseModel):
    """Summary statistics for a report."""

    total_devices: int = Field(..., description="Total number of devices")
    devices_with_changes: int = Field(..., description="Number of devices with changes")
    total_changes: int = Field(..., description="Total number of changes across all devices")
    changes_by_tag: dict[str, int] = Field(
        default_factory=dict, description="Count of changes by tag"
    )


class ChangeDetail(BaseModel):
    """Detailed information about a specific change."""

    change_text: str = Field(..., description="The configuration change text")
    device_count: int = Field(..., description="Number of devices with this change")
    device_ids: list[str] = Field(..., description="List of affected device IDs")
    tags: list[str] = Field(default_factory=list, description="Tags associated with this change")


class GetReportChangesResponse(BaseModel):
    """Response model for detailed change analysis."""

    report_id: str = Field(..., description="Report identifier")
    changes: list[ChangeDetail] = Field(..., description="Detailed list of changes")
    total_unique_changes: int = Field(..., description="Number of unique changes")


class ExportFormat(BaseModel):
    """Supported export formats."""

    format: str = Field("json", description="Export format (json, csv, yaml)")
