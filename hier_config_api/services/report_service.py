"""Service layer for multi-device reporting."""

import csv
import io
import json
from collections import defaultdict
from typing import Any

import yaml

from hier_config_api.models.report import ChangeDetail, DeviceRemediation, ReportSummary
from hier_config_api.services.remediation_service import RemediationService


class ReportService:
    """Service for handling multi-device reports."""

    @staticmethod
    def create_report(remediations: list[DeviceRemediation]) -> dict[str, Any]:
        """Create a report from multiple device remediations."""
        report_data: dict[str, Any] = {
            "devices": [],
            "total_devices": len(remediations),
            "devices_with_changes": 0,
            "total_changes": 0,
            "changes_by_tag": {},
            "change_details": [],
        }

        # Track changes across devices
        change_tracker: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"count": 0, "devices": [], "tags": []}
        )

        for device_rem in remediations:
            # Generate remediation for this device
            remediation_result = RemediationService.generate_remediation(
                platform=device_rem.platform,
                running_config=device_rem.running_config,
                intended_config=device_rem.intended_config,
            )

            remediation_config = remediation_result["remediation_config"]
            has_changes = bool(remediation_config.strip())

            if has_changes:
                report_data["devices_with_changes"] += 1

            # Track changes
            changes = remediation_config.splitlines()
            report_data["total_changes"] += len(changes)

            # Store device data
            device_data = {
                "device_id": device_rem.device_id,
                "platform": device_rem.platform,
                "has_changes": has_changes,
                "change_count": len(changes),
                "remediation": remediation_config,
                "rollback": remediation_result["rollback_config"],
            }
            report_data["devices"].append(device_data)

            # Track individual changes
            for change in changes:
                if change.strip():
                    change_tracker[change]["count"] += 1
                    change_tracker[change]["devices"].append(device_rem.device_id)

        # Convert change tracker to change details
        report_data["change_details"] = [
            {
                "change_text": change_text,
                "device_count": data["count"],
                "device_ids": data["devices"],
                "tags": data["tags"],
            }
            for change_text, data in change_tracker.items()
        ]

        return report_data

    @staticmethod
    def get_summary(report_data: dict[str, Any]) -> ReportSummary:
        """Get summary statistics from report."""
        return ReportSummary(
            total_devices=report_data["total_devices"],
            devices_with_changes=report_data["devices_with_changes"],
            total_changes=report_data["total_changes"],
            changes_by_tag=report_data.get("changes_by_tag", {}),
        )

    @staticmethod
    def get_changes(
        report_data: dict[str, Any],
        tag_filter: str | None = None,
        min_devices: int = 1,
    ) -> list[ChangeDetail]:
        """Get detailed change analysis."""
        changes = report_data.get("change_details", [])

        # Filter by tag if specified
        if tag_filter:
            changes = [c for c in changes if tag_filter in c.get("tags", [])]

        # Filter by minimum devices
        changes = [c for c in changes if c["device_count"] >= min_devices]

        # Convert to ChangeDetail objects
        return [
            ChangeDetail(
                change_text=c["change_text"],
                device_count=c["device_count"],
                device_ids=c["device_ids"],
                tags=c.get("tags", []),
            )
            for c in changes
        ]

    @staticmethod
    def export_report(report_data: dict[str, Any], format_type: str = "json") -> str:
        """Export report in specified format."""
        if format_type == "json":
            return json.dumps(report_data, indent=2)

        elif format_type == "yaml":
            return yaml.dump(report_data, default_flow_style=False)

        elif format_type == "csv":
            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(
                ["Device ID", "Platform", "Has Changes", "Change Count", "Remediation Summary"]
            )

            # Write device rows
            for device in report_data.get("devices", []):
                writer.writerow(
                    [
                        device["device_id"],
                        device["platform"],
                        device["has_changes"],
                        device["change_count"],
                        (
                            device["remediation"][:50] + "..."
                            if len(device["remediation"]) > 50
                            else device["remediation"]
                        ),
                    ]
                )

            return output.getvalue()

        else:
            raise ValueError(f"Unsupported format: {format_type}")
