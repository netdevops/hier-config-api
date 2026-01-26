"""Pydantic models for remediation operations."""

from pydantic import BaseModel, Field


class TagRule(BaseModel):
    """Rule for tagging configuration lines."""

    match_rules: list[str] = Field(..., description="List of match patterns")
    tags: list[str] = Field(..., description="Tags to apply to matching lines")


class RemediationSummary(BaseModel):
    """Summary of remediation changes."""

    additions: int = Field(0, description="Number of configuration additions")
    deletions: int = Field(0, description="Number of configuration deletions")
    modifications: int = Field(0, description="Number of configuration modifications")


class GenerateRemediationRequest(BaseModel):
    """Request model for generating remediation."""

    platform: str = Field(..., description="Platform type (e.g., cisco_ios, juniper_junos)")
    running_config: str = Field(..., description="Current running configuration")
    intended_config: str = Field(..., description="Desired configuration state")
    tag_rules: list[TagRule] | None = Field(None, description="Optional tag rules to apply")
    include_tags: list[str] | None = Field(None, description="Only include these tags")
    exclude_tags: list[str] | None = Field(None, description="Exclude these tags")


class GenerateRemediationResponse(BaseModel):
    """Response model for generated remediation."""

    remediation_id: str = Field(..., description="Unique identifier for this remediation")
    platform: str = Field(..., description="Platform type")
    remediation_config: str = Field(..., description="Commands to achieve desired state")
    rollback_config: str = Field(..., description="Commands to rollback changes")
    summary: RemediationSummary = Field(..., description="Summary of changes")
    tags: dict[str, list[str]] = Field(default_factory=dict, description="Tags applied to commands")


class ApplyTagsRequest(BaseModel):
    """Request model for applying tags to remediation."""

    tag_rules: list[TagRule] = Field(..., description="Tag rules to apply")


class ApplyTagsResponse(BaseModel):
    """Response model for tagged remediation."""

    remediation_id: str = Field(..., description="Remediation identifier")
    remediation_config: str = Field(..., description="Tagged remediation configuration")
    tags: dict[str, list[str]] = Field(..., description="Tags applied to commands")


class FilterRemediationRequest(BaseModel):
    """Request model for filtering remediation by tags."""

    include_tags: list[str] | None = Field(None, description="Only include these tags")
    exclude_tags: list[str] | None = Field(None, description="Exclude these tags")


class FilterRemediationResponse(BaseModel):
    """Response model for filtered remediation."""

    remediation_id: str = Field(..., description="Remediation identifier")
    filtered_config: str = Field(..., description="Filtered remediation commands")
    summary: RemediationSummary = Field(..., description="Summary of filtered changes")
