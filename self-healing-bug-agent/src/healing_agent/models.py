from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, computed_field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TriggerType(str, Enum):
    CI_FAILURE = "ci_failure"
    ISSUE_LABEL = "issue_label"
    MANUAL = "manual"


class RunStatus(str, Enum):
    RECEIVED = "received"
    PREPARING = "preparing"
    REPRODUCING = "reproducing"
    REPRODUCTION_FAILED = "reproduction_failed"
    DIAGNOSING = "diagnosing"
    PATCHING = "patching"
    WRITING_TEST = "writing_test"
    VERIFYING_TARGETED = "verifying_targeted"
    VERIFYING_FULL_SUITE = "verifying_full_suite"
    READY_FOR_PR = "ready_for_pr"
    PR_CREATED = "pr_created"
    NEEDS_HUMAN = "needs_human"
    INFRA_FAILURE = "infra_failure"
    ITERATION_LIMIT_REACHED = "iteration_limit_reached"


TERMINAL_STATUSES = {
    RunStatus.REPRODUCTION_FAILED,
    RunStatus.PR_CREATED,
    RunStatus.NEEDS_HUMAN,
    RunStatus.INFRA_FAILURE,
    RunStatus.ITERATION_LIMIT_REACHED,
}


class RunEvent(BaseModel):
    status: RunStatus
    message: str
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class VerificationReport(BaseModel):
    original_failure_reproduced: bool = False
    patch_present: bool = False
    regression_test_added: bool = False
    regression_test_failed_before_fix: bool = False
    targeted_tests_passed: bool = False
    full_suite_passed: bool = False
    forbidden_changes_detected: bool = False
    secrets_detected: bool = False
    commands: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def passed(self) -> bool:
        return all(
            (
                self.original_failure_reproduced,
                self.patch_present,
                self.regression_test_added,
                self.regression_test_failed_before_fix,
                self.targeted_tests_passed,
                self.full_suite_passed,
                not self.forbidden_changes_detected,
                not self.secrets_detected,
            )
        )


class RepairRun(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    repo_full_name: str
    trigger_type: TriggerType
    base_sha: str
    bug_report: str = ""
    issue_number: int | None = None
    workflow_run_id: int | None = None
    status: RunStatus = RunStatus.RECEIVED
    iteration: int = 0
    max_iterations: int = Field(default=3, ge=1, le=10)
    events: list[RunEvent] = Field(default_factory=list)
    verification: VerificationReport | None = None
    pull_request_url: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    def add_event(
        self,
        status: RunStatus,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.status = status
        self.updated_at = utc_now()
        self.events.append(
            RunEvent(status=status, message=message, metadata=metadata or {})
        )

