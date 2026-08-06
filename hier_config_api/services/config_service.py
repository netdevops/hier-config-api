"""Service layer for configuration operations."""

import re
from typing import Any

from hier_config import HConfig, HConfigChild, Platform, WorkflowRemediation

from hier_config_api.models.config import MatchRule


def _line_matches(config_line: str, match_rules: MatchRule) -> bool:
    """Check whether a configuration line satisfies any of the match rules."""
    if match_rules.equals and config_line == match_rules.equals:
        return True
    if match_rules.contains and match_rules.contains in config_line:
        return True
    if match_rules.startswith and config_line.startswith(match_rules.startswith):
        return True
    return bool(match_rules.regex and re.search(match_rules.regex, config_line))


class ConfigService:
    """Service for handling configuration operations."""

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
    def parse_config(platform: str, config_text: str) -> dict[str, Any]:
        """Parse configuration text into structured format."""
        platform_enum = ConfigService._get_platform(platform)
        hconfig = HConfig.from_text(platform_enum, config_text)

        # Convert HConfig tree to dictionary representation
        def config_to_dict(config_obj: HConfig | HConfigChild) -> dict[str, Any]:
            return {
                "text": str(config_obj),
                "children": [config_to_dict(child) for child in config_obj.children],
            }

        return config_to_dict(hconfig)

    @staticmethod
    def compare_configs(
        platform: str, running_config: str, intended_config: str
    ) -> tuple[str, bool]:
        """Compare two configurations and return unified diff."""
        platform_enum = ConfigService._get_platform(platform)
        running_hconfig = HConfig.from_text(platform_enum, running_config)
        intended_hconfig = HConfig.from_text(platform_enum, intended_config)

        workflow = WorkflowRemediation(running_hconfig, intended_hconfig)
        remediation = workflow.remediation_config
        rollback = workflow.rollback_config

        diff_lines: list[str] = []

        # Generate unified diff format
        if remediation:
            diff_lines.extend(("--- running_config", "+++ intended_config"))
            diff_lines.extend(
                f"+ {line}" for line in str(remediation).splitlines() if line.strip()
            )

        if rollback:
            diff_lines.extend(
                f"- {line}" for line in str(rollback).splitlines() if line.strip()
            )

        unified_diff = "\n".join(diff_lines) if diff_lines else "No differences found"
        has_changes = bool(diff_lines)

        return unified_diff, has_changes

    @staticmethod
    def predict_config(
        _platform: str, current_config: str, commands_to_apply: str
    ) -> str:
        """Predict configuration state after applying commands."""
        # Simple merge: append new commands
        config_lines = current_config.splitlines()
        command_lines = commands_to_apply.splitlines()
        predicted_lines = config_lines + command_lines

        return "\n".join(predicted_lines)

    @staticmethod
    def merge_configs(platform: str, configs: list[str]) -> str:
        """Merge multiple configurations into one."""
        if not configs:
            return ""

        if len(configs) == 1:
            return configs[0]

        platform_enum = ConfigService._get_platform(platform)

        # Use the first config as base
        merged = configs[0]

        # Merge each subsequent config
        for config in configs[1:]:
            running_hconfig = HConfig.from_text(platform_enum, merged)
            intended_hconfig = HConfig.from_text(platform_enum, config)

            workflow = WorkflowRemediation(running_hconfig, intended_hconfig)
            remediation = workflow.remediation_config
            if remediation:
                merged += f"\n{remediation!s}"

        return merged

    @staticmethod
    def search_config(
        platform: str,
        config_text: str,
        match_rules: MatchRule,
    ) -> list[str]:
        """Search configuration for matching lines."""
        platform_enum = ConfigService._get_platform(platform)
        hconfig = HConfig.from_text(platform_enum, config_text)

        matches: list[str] = []

        def search_recursive(config_obj: HConfig | HConfigChild) -> None:
            config_line = str(config_obj).strip()

            if _line_matches(config_line, match_rules):
                matches.append(config_line)

            # Recursively search children
            for child in config_obj.children:
                search_recursive(child)

        search_recursive(hconfig)
        return matches
