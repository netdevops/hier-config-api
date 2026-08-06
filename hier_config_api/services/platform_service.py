"""Service layer for platform information and batch operations."""

from typing import Any, ClassVar

from hier_config import HConfig, Platform, WorkflowRemediation

from hier_config_api.models.platform import PlatformInfo, PlatformRules


class PlatformService:
    """Service for handling platform-related operations."""

    # Common platform definitions
    PLATFORMS: ClassVar[dict[str, PlatformInfo]] = {
        "cisco_ios": PlatformInfo(
            platform_name="cisco_ios",
            display_name="Cisco IOS",
            vendor="Cisco",
            supported=True,
        ),
        "cisco_nxos": PlatformInfo(
            platform_name="cisco_nxos",
            display_name="Cisco NX-OS",
            vendor="Cisco",
            supported=True,
        ),
        "cisco_iosxr": PlatformInfo(
            platform_name="cisco_iosxr",
            display_name="Cisco IOS-XR",
            vendor="Cisco",
            supported=True,
        ),
        "juniper_junos": PlatformInfo(
            platform_name="juniper_junos",
            display_name="Juniper Junos",
            vendor="Juniper",
            supported=True,
        ),
        "arista_eos": PlatformInfo(
            platform_name="arista_eos",
            display_name="Arista EOS",
            vendor="Arista",
            supported=True,
        ),
    }

    @staticmethod
    def list_platforms() -> list[PlatformInfo]:
        """List all supported platforms."""
        return list(PlatformService.PLATFORMS.values())

    @staticmethod
    def get_platform_rules(platform: str) -> PlatformRules:
        """Get platform-specific rules."""
        # This is a simplified version
        # In a real implementation, you'd load this from hier_config's driver options
        return PlatformRules(
            platform_name=platform,
            negation_default_when=[],
            negation_negate_with=[],
            ordering=[],
            idempotent_commands_avoid=[],
            idempotent_commands=[],
        )

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
    def validate_config(platform: str, config_text: str) -> dict[str, Any]:
        """Validate configuration for a platform."""
        warnings: list[str] = []
        errors: list[str] = []
        is_valid = True

        platform_enum = PlatformService._get_platform(platform)
        try:
            # Try to parse the configuration
            HConfig.from_text(platform_enum, config_text)
        # A validation endpoint must convert any parsing failure into a
        # validation error rather than propagate it as a server error.
        except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            errors.append(f"Configuration parsing error: {exc!s}")
            is_valid = False
        else:
            # Basic validation checks
            if not config_text.strip():
                warnings.append("Configuration is empty")
                is_valid = False

            # Platform-specific validation could be added here
            # Check for common Cisco IOS patterns
            if platform == "cisco_ios" and "hostname" not in config_text:
                warnings.append("No hostname configured")

        return {
            "platform": platform,
            "is_valid": is_valid,
            "warnings": warnings,
            "errors": errors,
        }

    @staticmethod
    def create_batch_job(device_configs: list[dict[str, Any]]) -> dict[str, Any]:
        """Create a batch remediation job."""
        return {
            "status": "pending",
            "progress": 0.0,
            "total_devices": len(device_configs),
            "completed_devices": 0,
            "failed_devices": 0,
            "device_configs": device_configs,
            "results": [],
        }

    @staticmethod
    def _remediate_device(device_config: dict[str, Any]) -> dict[str, Any]:
        """Generate remediation and rollback for a single batch device."""
        platform = device_config.get("platform", "cisco_ios")
        running_config = device_config.get("running_config", "")
        intended_config = device_config.get("intended_config", "")

        platform_enum = PlatformService._get_platform(platform)
        running_hconfig = HConfig.from_text(platform_enum, running_config)
        intended_hconfig = HConfig.from_text(platform_enum, intended_config)

        workflow = WorkflowRemediation(running_hconfig, intended_hconfig)
        remediation = workflow.remediation_config
        rollback = workflow.rollback_config

        return {
            "device_id": device_config.get("device_id"),
            "status": "success",
            "remediation": str(remediation) if remediation else "",
            "rollback": str(rollback) if rollback else "",
        }

    @staticmethod
    def _process_device(device_config: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        """Process one batch device, returning its result and success flag."""
        try:
            result = PlatformService._remediate_device(device_config)
        # Batch jobs record per-device failures instead of aborting the job,
        # so any processing error must be captured here.
        except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            return (
                {
                    "device_id": device_config.get("device_id"),
                    "status": "failed",
                    "error": str(exc),
                },
                False,
            )
        return result, True

    @staticmethod
    def process_batch_job(job_data: dict[str, Any]) -> dict[str, Any]:
        """Process a batch job (simplified synchronous version)."""
        results: list[dict[str, Any]] = []
        completed = 0
        failed = 0

        for device_config in job_data["device_configs"]:
            result, succeeded = PlatformService._process_device(device_config)
            results.append(result)
            if succeeded:
                completed += 1
            else:
                failed += 1

        # Update job data
        job_data.update(
            {
                "status": "completed",
                "progress": 100.0,
                "completed_devices": completed,
                "failed_devices": failed,
                "results": results,
            }
        )

        return job_data
