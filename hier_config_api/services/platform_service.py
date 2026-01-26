"""Service layer for platform information and batch operations."""

from typing import Any

from hier_config import Platform, WorkflowRemediation, get_hconfig

from hier_config_api.models.platform import PlatformInfo, PlatformRules


class PlatformService:
    """Service for handling platform-related operations."""

    # Common platform definitions
    PLATFORMS = {
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
        warnings = []
        errors = []
        is_valid = True

        try:
            # Try to parse the configuration
            platform_enum = PlatformService._get_platform(platform)
            get_hconfig(platform_enum, config_text)

            # Basic validation checks
            if not config_text.strip():
                warnings.append("Configuration is empty")
                is_valid = False

            # Platform-specific validation could be added here
            if platform == "cisco_ios":
                # Check for common Cisco IOS patterns
                if "hostname" not in config_text:
                    warnings.append("No hostname configured")

        except Exception as e:
            errors.append(f"Configuration parsing error: {str(e)}")
            is_valid = False

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
    def process_batch_job(job_data: dict[str, Any]) -> dict[str, Any]:
        """Process a batch job (simplified synchronous version)."""
        results = []
        completed = 0
        failed = 0

        for device_config in job_data["device_configs"]:
            try:
                # Process each device
                platform = device_config.get("platform", "cisco_ios")
                running_config = device_config.get("running_config", "")
                intended_config = device_config.get("intended_config", "")

                platform_enum = PlatformService._get_platform(platform)
                running_hconfig = get_hconfig(platform_enum, running_config)
                intended_hconfig = get_hconfig(platform_enum, intended_config)

                workflow = WorkflowRemediation(running_hconfig, intended_hconfig)
                remediation = workflow.remediation_config
                rollback = workflow.rollback_config

                results.append(
                    {
                        "device_id": device_config.get("device_id"),
                        "status": "success",
                        "remediation": str(remediation) if remediation else "",
                        "rollback": str(rollback) if rollback else "",
                    }
                )
                completed += 1

            except Exception as e:
                results.append(
                    {
                        "device_id": device_config.get("device_id"),
                        "status": "failed",
                        "error": str(e),
                    }
                )
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
