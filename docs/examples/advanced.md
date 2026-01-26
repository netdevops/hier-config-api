# Advanced Workflows

Complex use cases and advanced patterns.

## Tag-Based Remediation Filtering

Generate remediation with selective deployment based on tags:

```python
import requests

# Define tag rules
tag_rules = [
    {
        "match_rules": ["hostname"],
        "tags": ["safe", "non-service-impacting"]
    },
    {
        "match_rules": ["interface.*shutdown"],
        "tags": ["risky", "service-impacting"]
    },
    {
        "match_rules": ["ntp server"],
        "tags": ["safe", "infrastructure"]
    }
]

# Generate remediation with tags
response = requests.post(
    "http://localhost:8000/api/v1/remediation/generate",
    json={
        "platform": "cisco_ios",
        "running_config": open("current.cfg").read(),
        "intended_config": open("desired.cfg").read(),
        "tag_rules": tag_rules,
        "include_tags": ["safe"],  # Only safe changes
        "exclude_tags": ["risky"]  # Exclude risky changes
    }
)

result = response.json()
print("Safe remediation commands:")
print(result["remediation_config"])
```

## Fleet-Wide Configuration Drift Analysis

Identify common drift across your network:

```python
import requests
from collections import defaultdict

# Load device configs from your inventory
devices = load_device_inventory()

# Create report
response = requests.post(
    "http://localhost:8000/api/v1/reports",
    json={
        "remediations": [
            {
                "device_id": device["name"],
                "platform": device["platform"],
                "running_config": device["running_config"],
                "intended_config": device["intended_config"]
            }
            for device in devices
        ]
    }
)

report_id = response.json()["report_id"]

# Find common changes appearing on many devices
changes = requests.get(
    f"http://localhost:8000/api/v1/reports/{report_id}/changes",
    params={"min_devices": 10}  # Changes on 10+ devices
).json()

# Group by change type
drift_analysis = defaultdict(list)
for change in changes["changes"]:
    change_type = categorize_change(change["change_text"])
    drift_analysis[change_type].append({
        "change": change["change_text"],
        "device_count": change["device_count"],
        "devices": change["device_ids"]
    })

# Report findings
for change_type, items in drift_analysis.items():
    print(f"\n{change_type}:")
    for item in items:
        print(f"  {item['device_count']} devices: {item['change']}")
```

## Incremental Deployment Pipeline

Deploy changes incrementally with validation:

```python
import requests
import time

class DeploymentPipeline:
    def __init__(self, api_url):
        self.api_url = api_url

    def generate_remediation(self, device, running_config, intended_config):
        """Generate remediation for a device."""
        response = requests.post(
            f"{self.api_url}/api/v1/remediation/generate",
            json={
                "platform": device["platform"],
                "running_config": running_config,
                "intended_config": intended_config,
                "tag_rules": [
                    {"match_rules": ["hostname"], "tags": ["stage1"]},
                    {"match_rules": ["interface"], "tags": ["stage2"]},
                    {"match_rules": ["routing"], "tags": ["stage3"]}
                ]
            }
        )
        return response.json()

    def deploy_stage(self, remediation_id, stage_tags):
        """Get remediation for a specific deployment stage."""
        response = requests.get(
            f"{self.api_url}/api/v1/remediation/{remediation_id}/filter",
            params={"include_tags": ",".join(stage_tags)}
        )
        return response.json()

    def execute(self, devices):
        """Execute multi-stage deployment."""
        stages = [
            {"name": "Stage 1: Non-impacting", "tags": ["stage1"]},
            {"name": "Stage 2: Interface changes", "tags": ["stage2"]},
            {"name": "Stage 3: Routing changes", "tags": ["stage3"]}
        ]

        for device in devices:
            print(f"\n=== Deploying to {device['name']} ===")

            # Generate full remediation
            remediation = self.generate_remediation(
                device,
                device["running_config"],
                device["intended_config"]
            )

            # Deploy in stages
            for stage in stages:
                print(f"\n{stage['name']}:")

                # Get stage-specific commands
                stage_config = self.deploy_stage(
                    remediation["remediation_id"],
                    stage["tags"]
                )

                if not stage_config["filtered_config"]:
                    print("  No changes in this stage")
                    continue

                # Show what will be deployed
                print(f"  Commands:\n{stage_config['filtered_config']}")

                # Wait for confirmation
                if not self.confirm_deployment():
                    print("  Deployment cancelled")
                    break

                # Deploy to device
                self.apply_to_device(device, stage_config["filtered_config"])

                # Verify
                if self.verify_deployment(device):
                    print("  ✓ Deployment successful")
                else:
                    print("  ✗ Deployment failed, rolling back")
                    self.rollback(device, remediation["rollback_config"])
                    break

                # Wait before next stage
                time.sleep(30)

# Usage
pipeline = DeploymentPipeline("http://localhost:8000")
pipeline.execute(devices)
```

## Configuration Compliance Checking

Check compliance across devices:

```python
import requests

class ComplianceChecker:
    def __init__(self, api_url, compliance_config):
        self.api_url = api_url
        self.compliance_config = compliance_config

    def check_device(self, device):
        """Check a single device for compliance."""
        response = requests.post(
            f"{self.api_url}/api/v1/remediation/generate",
            json={
                "platform": device["platform"],
                "running_config": device["config"],
                "intended_config": self.compliance_config
            }
        )

        result = response.json()
        violations = []

        if result["summary"]["additions"] > 0:
            violations.append({
                "type": "missing_config",
                "severity": "high",
                "remediation": result["remediation_config"]
            })

        return {
            "device_id": device["id"],
            "compliant": len(violations) == 0,
            "violations": violations
        }

    def check_fleet(self, devices):
        """Check compliance for entire fleet."""
        results = []

        # Create batch job
        response = requests.post(
            f"{self.api_url}/api/v1/batch/remediation",
            json={
                "device_configs": [
                    {
                        "device_id": d["id"],
                        "platform": d["platform"],
                        "running_config": d["config"],
                        "intended_config": self.compliance_config
                    }
                    for d in devices
                ]
            }
        )

        job_id = response.json()["job_id"]

        # Wait for completion
        while True:
            status = requests.get(
                f"{self.api_url}/api/v1/batch/jobs/{job_id}"
            ).json()

            if status["status"] == "completed":
                break

            time.sleep(1)

        # Get results
        job_results = requests.get(
            f"{self.api_url}/api/v1/batch/jobs/{job_id}/results"
        ).json()

        # Analyze compliance
        for result in job_results["results"]:
            compliant = not result.get("remediation", "").strip()
            results.append({
                "device_id": result["device_id"],
                "compliant": compliant,
                "remediation": result.get("remediation", "")
            })

        return results

# Usage
checker = ComplianceChecker(
    "http://localhost:8000",
    compliance_config=open("compliance_baseline.cfg").read()
)

results = checker.check_fleet(devices)

# Generate compliance report
compliant = [r for r in results if r["compliant"]]
non_compliant = [r for r in results if not r["compliant"]]

print(f"Compliance Rate: {len(compliant)}/{len(results)} ({len(compliant)/len(results)*100:.1f}%)")
print(f"\nNon-compliant devices:")
for device in non_compliant:
    print(f"  - {device['device_id']}")
```

## Change Approval Workflow

Implement approval workflow for changes:

```python
import requests
from dataclasses import dataclass
from enum import Enum

class ChangeStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPLOYED = "deployed"

@dataclass
class ChangeRequest:
    device_id: str
    remediation_id: str
    remediation_config: str
    rollback_config: str
    status: ChangeStatus
    approver: str = None

class ChangeManagement:
    def __init__(self, api_url):
        self.api_url = api_url
        self.changes = {}

    def submit_change(self, device, running_config, intended_config):
        """Submit a change for approval."""
        response = requests.post(
            f"{self.api_url}/api/v1/remediation/generate",
            json={
                "platform": device["platform"],
                "running_config": running_config,
                "intended_config": intended_config
            }
        )

        result = response.json()
        change_id = result["remediation_id"]

        self.changes[change_id] = ChangeRequest(
            device_id=device["id"],
            remediation_id=change_id,
            remediation_config=result["remediation_config"],
            rollback_config=result["rollback_config"],
            status=ChangeStatus.PENDING
        )

        return change_id

    def approve_change(self, change_id, approver):
        """Approve a change."""
        if change_id not in self.changes:
            raise ValueError("Change not found")

        self.changes[change_id].status = ChangeStatus.APPROVED
        self.changes[change_id].approver = approver

    def deploy_approved_changes(self):
        """Deploy all approved changes."""
        for change_id, change in self.changes.items():
            if change.status == ChangeStatus.APPROVED:
                print(f"Deploying {change.device_id}...")
                # Deploy to device
                # ...
                change.status = ChangeStatus.DEPLOYED

# Usage
cm = ChangeManagement("http://localhost:8000")

# Submit changes
change_id = cm.submit_change(device, current_config, desired_config)

# Approve
cm.approve_change(change_id, "john.doe@example.com")

# Deploy
cm.deploy_approved_changes()
```
