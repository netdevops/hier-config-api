"""In-memory storage for reports and batch jobs."""

import uuid
from typing import Any


class InMemoryStorage:
    """Simple in-memory storage for reports and jobs."""

    def __init__(self) -> None:
        """Initialize storage."""
        self._reports: dict[str, dict[str, Any]] = {}
        self._jobs: dict[str, dict[str, Any]] = {}
        self._remediations: dict[str, dict[str, Any]] = {}

    def store_report(self, report_data: dict[str, Any]) -> str:
        """Store a report and return its ID."""
        report_id = str(uuid.uuid4())
        self._reports[report_id] = report_data
        return report_id

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        """Retrieve a report by ID."""
        return self._reports.get(report_id)

    def store_job(self, job_data: dict[str, Any]) -> str:
        """Store a batch job and return its ID."""
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = job_data
        return job_id

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        """Retrieve a batch job by ID."""
        return self._jobs.get(job_id)

    def update_job(self, job_id: str, updates: dict[str, Any]) -> bool:
        """Update a batch job."""
        if job_id in self._jobs:
            self._jobs[job_id].update(updates)
            return True
        return False

    def store_remediation(self, remediation_data: dict[str, Any]) -> str:
        """Store a remediation and return its ID."""
        remediation_id = str(uuid.uuid4())
        self._remediations[remediation_id] = remediation_data
        return remediation_id

    def get_remediation(self, remediation_id: str) -> dict[str, Any] | None:
        """Retrieve a remediation by ID."""
        return self._remediations.get(remediation_id)

    def update_remediation(self, remediation_id: str, updates: dict[str, Any]) -> bool:
        """Update a remediation."""
        if remediation_id in self._remediations:
            self._remediations[remediation_id].update(updates)
            return True
        return False


# Global storage instance
storage = InMemoryStorage()
