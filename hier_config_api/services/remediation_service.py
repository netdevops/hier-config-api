"""Service layer for remediation operations."""

from typing import Any

from hier_config import Platform, WorkflowRemediation, get_hconfig

from hier_config_api.models.remediation import RemediationSummary, TagRule


class RemediationService:
    """Service for handling remediation operations."""

    @staticmethod
    def _get_platform(platform_str: str) -> Platform:
        """Convert platform string to Platform enum."""
        platform_map = {
            "cisco_ios": Platform.CISCO_IOS,
            "cisco_nxos": Platform.CISCO_NXOS,
            "cisco_iosxr": Platform.CISCO_XR,
            "juniper_junos": Platform.JUNIPER_JUNOS,
            "arista_eos": Platform.ARISTA_EOS,
            "generic": Platform.GENERIC,
        }
        return platform_map.get(platform_str.lower(), Platform.GENERIC)

    @staticmethod
    def generate_remediation(
        platform: str,
        running_config: str,
        intended_config: str,
        tag_rules: list[TagRule] | None = None,
        include_tags: list[str] | None = None,
        exclude_tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Generate remediation and rollback configurations."""
        platform_enum = RemediationService._get_platform(platform)
        running_hconfig = get_hconfig(platform_enum, running_config)
        intended_hconfig = get_hconfig(platform_enum, intended_config)

        # Load tag rules if provided
        if tag_rules:
            # Convert tag rules to hier_config format
            # This is simplified - actual implementation would need proper tag loading
            pass

        # Generate remediation and rollback
        workflow = WorkflowRemediation(running_hconfig, intended_hconfig)
        remediation = workflow.remediation_config
        rollback = workflow.rollback_config

        # Calculate summary
        remediation_lines = str(remediation).splitlines() if remediation else []
        rollback_lines = str(rollback).splitlines() if rollback else []

        # Count additions, deletions, modifications
        additions = len([line for line in remediation_lines if line.strip()])
        deletions = len([line for line in rollback_lines if line.strip()])
        modifications = 0  # Simplified - would need more logic to detect modifications

        summary = RemediationSummary(
            additions=additions, deletions=deletions, modifications=modifications
        )

        # Apply tag filtering if specified
        filtered_remediation = str(remediation) if remediation else ""
        if include_tags or exclude_tags:
            # Simplified tag filtering
            # In a real implementation, you'd filter based on tags
            pass

        result = {
            "remediation_config": filtered_remediation,
            "rollback_config": str(rollback) if rollback else "",
            "summary": summary,
            "tags": {},
            "platform": platform,
        }

        return result

    @staticmethod
    def apply_tags(
        remediation_config: str, tag_rules: list[TagRule]
    ) -> tuple[str, dict[str, list[str]]]:
        """Apply tags to remediation configuration."""
        # Simplified implementation
        # In a real implementation, you'd apply tags based on patterns
        tags: dict[str, list[str]] = {}

        # For each line in remediation, check if it matches any tag rules
        for rule in tag_rules:
            for _match_pattern in rule.match_rules:
                # Check if pattern matches any lines
                # Add tags to matching lines
                pass

        return remediation_config, tags

    @staticmethod
    def filter_remediation(
        remediation_config: str,
        tags: dict[str, list[str]],
        include_tags: list[str] | None = None,
        exclude_tags: list[str] | None = None,
    ) -> tuple[str, RemediationSummary]:
        """Filter remediation configuration by tags."""
        lines = remediation_config.splitlines()
        filtered_lines = []

        for i, line in enumerate(lines):
            line_tags = tags.get(str(i), [])

            # Check include/exclude logic
            if include_tags and not any(tag in line_tags for tag in include_tags):
                continue
            if exclude_tags and any(tag in line_tags for tag in exclude_tags):
                continue

            filtered_lines.append(line)

        filtered_config = "\n".join(filtered_lines)

        # Calculate summary
        summary = RemediationSummary(
            additions=len(filtered_lines),
            deletions=0,
            modifications=0,
        )

        return filtered_config, summary
