"""Service layer for configuration operations."""

import re
from typing import Any

from hier_config import Platform, WorkflowRemediation, get_hconfig


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
        hconfig = get_hconfig(platform_enum, config_text)

        # Convert HConfig tree to dictionary representation
        def config_to_dict(config_obj: Any) -> dict[str, Any]:
            result: dict[str, Any] = {
                "text": str(config_obj),
                "children": [],
            }
            if hasattr(config_obj, "children"):
                for child in config_obj.children:
                    result["children"].append(config_to_dict(child))
            return result

        return config_to_dict(hconfig)

    @staticmethod
    def compare_configs(
        platform: str, running_config: str, intended_config: str
    ) -> tuple[str, bool]:
        """Compare two configurations and return unified diff."""
        platform_enum = ConfigService._get_platform(platform)
        running_hconfig = get_hconfig(platform_enum, running_config)
        intended_hconfig = get_hconfig(platform_enum, intended_config)

        workflow = WorkflowRemediation(running_hconfig, intended_hconfig)
        remediation = workflow.remediation_config
        rollback = workflow.rollback_config

        diff_lines = []

        # Generate unified diff format
        if remediation:
            diff_lines.append("--- running_config")
            diff_lines.append("+++ intended_config")
            for line in str(remediation).splitlines():
                if line.strip():
                    diff_lines.append(f"+ {line}")

        if rollback:
            for line in str(rollback).splitlines():
                if line.strip():
                    diff_lines.append(f"- {line}")

        unified_diff = "\n".join(diff_lines) if diff_lines else "No differences found"
        has_changes = bool(diff_lines)

        return unified_diff, has_changes

    @staticmethod
    def predict_config(platform: str, current_config: str, commands_to_apply: str) -> str:
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
            running_hconfig = get_hconfig(platform_enum, merged)
            intended_hconfig = get_hconfig(platform_enum, config)

            workflow = WorkflowRemediation(running_hconfig, intended_hconfig)
            remediation = workflow.remediation_config
            if remediation:
                merged += "\n" + str(remediation)

        return merged

    @staticmethod
    def search_config(
        platform: str,
        config_text: str,
        equals: str | None = None,
        contains: str | None = None,
        startswith: str | None = None,
        regex_pattern: str | None = None,
    ) -> list[str]:
        """Search configuration for matching lines."""
        platform_enum = ConfigService._get_platform(platform)
        hconfig = get_hconfig(platform_enum, config_text)

        matches = []

        def search_recursive(config_obj: Any) -> None:
            config_line = str(config_obj).strip()

            # Check matching conditions
            is_match = False
            if equals and config_line == equals:
                is_match = True
            elif contains and contains in config_line:
                is_match = True
            elif startswith and config_line.startswith(startswith):
                is_match = True
            elif regex_pattern and re.search(regex_pattern, config_line):
                is_match = True

            if is_match:
                matches.append(config_line)

            # Recursively search children
            if hasattr(config_obj, "children"):
                for child in config_obj.children:
                    search_recursive(child)

        search_recursive(hconfig)
        return matches
