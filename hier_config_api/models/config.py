"""Pydantic models for configuration operations."""

from typing import Any

from pydantic import BaseModel, Field


class ParseConfigRequest(BaseModel):
    """Request model for parsing configuration."""

    platform: str = Field(..., description="Platform type (e.g., cisco_ios, juniper_junos)")
    config_text: str = Field(..., description="Raw configuration text to parse")


class ParseConfigResponse(BaseModel):
    """Response model for parsed configuration."""

    platform: str = Field(..., description="Platform type")
    structured_config: dict[str, Any] = Field(..., description="Structured configuration tree")


class CompareConfigRequest(BaseModel):
    """Request model for comparing configurations."""

    platform: str = Field(..., description="Platform type (e.g., cisco_ios, juniper_junos)")
    running_config: str = Field(..., description="Current running configuration")
    intended_config: str = Field(..., description="Desired configuration state")


class CompareConfigResponse(BaseModel):
    """Response model for configuration comparison."""

    platform: str = Field(..., description="Platform type")
    unified_diff: str = Field(..., description="Unified diff showing differences")
    has_changes: bool = Field(..., description="Whether there are any differences")


class PredictConfigRequest(BaseModel):
    """Request model for predicting future configuration state."""

    platform: str = Field(..., description="Platform type (e.g., cisco_ios, juniper_junos)")
    current_config: str = Field(..., description="Current configuration state")
    commands_to_apply: str = Field(..., description="Commands to apply to current config")


class PredictConfigResponse(BaseModel):
    """Response model for predicted configuration."""

    platform: str = Field(..., description="Platform type")
    predicted_config: str = Field(
        ..., description="Predicted configuration after applying commands"
    )


class MergeConfigRequest(BaseModel):
    """Request model for merging multiple configurations."""

    platform: str = Field(..., description="Platform type (e.g., cisco_ios, juniper_junos)")
    configs: list[str] = Field(..., description="List of configuration texts to merge")


class MergeConfigResponse(BaseModel):
    """Response model for merged configuration."""

    platform: str = Field(..., description="Platform type")
    merged_config: str = Field(..., description="Merged configuration result")


class MatchRule(BaseModel):
    """Rule for matching configuration lines."""

    equals: str | None = Field(None, description="Exact match string")
    contains: str | None = Field(None, description="Substring to match")
    startswith: str | None = Field(None, description="Prefix to match")
    regex: str | None = Field(None, description="Regular expression pattern")


class SearchConfigRequest(BaseModel):
    """Request model for searching configuration."""

    platform: str = Field(..., description="Platform type (e.g., cisco_ios, juniper_junos)")
    config_text: str = Field(..., description="Configuration text to search")
    match_rules: MatchRule = Field(..., description="Rules for matching configuration sections")


class SearchConfigResponse(BaseModel):
    """Response model for configuration search."""

    platform: str = Field(..., description="Platform type")
    matches: list[str] = Field(..., description="Matching configuration sections")
    match_count: int = Field(..., description="Number of matches found")
