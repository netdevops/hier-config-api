"""Pydantic models for platform information."""

from typing import Any

from pydantic import BaseModel, Field


class PlatformInfo(BaseModel):
    """Information about a supported platform."""

    platform_name: str = Field(..., description="Platform identifier")
    display_name: str = Field(..., description="Human-readable platform name")
    vendor: str = Field(..., description="Vendor name")
    supported: bool = Field(True, description="Whether platform is currently supported")


class PlatformRules(BaseModel):
    """Platform-specific rules and behaviors."""

    platform_name: str = Field(..., description="Platform identifier")
    negation_default_when: list[str] = Field(
        default_factory=list, description="Default negation patterns for when conditions"
    )
    negation_negate_with: list[str] = Field(
        default_factory=list, description="How to negate specific commands"
    )
    ordering: list[dict[str, Any]] = Field(
        default_factory=list, description="Command ordering rules"
    )
    idempotent_commands_avoid: list[str] = Field(
        default_factory=list, description="Commands to avoid in idempotent configs"
    )
    idempotent_commands: list[str] = Field(
        default_factory=list, description="Commands that are idempotent"
    )


class ValidateConfigRequest(BaseModel):
    """Request model for validating configuration."""

    config_text: str = Field(..., description="Configuration text to validate")


class ValidateConfigResponse(BaseModel):
    """Response model for configuration validation."""

    platform: str = Field(..., description="Platform type")
    is_valid: bool = Field(..., description="Whether configuration is valid")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
    errors: list[str] = Field(default_factory=list, description="Validation errors")


class BatchJobRequest(BaseModel):
    """Request model for batch job."""

    device_configs: list[dict[str, Any]] = Field(..., description="List of device configurations")


class BatchJobResponse(BaseModel):
    """Response model for batch job creation."""

    job_id: str = Field(..., description="Unique job identifier")
    total_devices: int = Field(..., description="Total number of devices in batch")


class BatchJobStatus(BaseModel):
    """Status of a batch job."""

    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Job status (pending, running, completed, failed)")
    progress: float = Field(0.0, description="Progress percentage (0.0 to 100.0)", ge=0.0, le=100.0)
    total_devices: int = Field(..., description="Total number of devices")
    completed_devices: int = Field(0, description="Number of completed devices")
    failed_devices: int = Field(0, description="Number of failed devices")


class BatchJobResults(BaseModel):
    """Results of a completed batch job."""

    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Job status")
    results: list[dict[str, Any]] = Field(..., description="Results for each device")
    summary: dict[str, Any] = Field(..., description="Summary statistics")
