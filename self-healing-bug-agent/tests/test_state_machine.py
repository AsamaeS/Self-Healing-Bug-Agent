import pytest

from healing_agent.models import RepairRun, RunStatus, TriggerType, VerificationReport
from healing_agent.orchestrator.state_machine import (
    InvalidTransition,
    VerificationGate,
    transition,
)


def new_run() -> RepairRun:
    return RepairRun(
        repo_full_name="demo/repo",
        trigger_type=TriggerType.MANUAL,
        base_sha="abcdef123456",
        bug_report="A failing test",
    )


def test_cannot_skip_directly_to_ready_for_pr() -> None:
    run = new_run()

    with pytest.raises(InvalidTransition):
        transition(run, RunStatus.READY_FOR_PR, "skip verification")


def test_gate_rejects_incomplete_verification() -> None:
    run = new_run()
    run.status = RunStatus.VERIFYING_FULL_SUITE
    run.verification = VerificationReport(full_suite_passed=True)

    with pytest.raises(InvalidTransition, match="did not pass"):
        VerificationGate.promote(run)


def test_gate_promotes_only_complete_verification() -> None:
    run = new_run()
    run.status = RunStatus.VERIFYING_FULL_SUITE
    run.verification = VerificationReport(
        original_failure_reproduced=True,
        patch_present=True,
        regression_test_added=True,
        regression_test_failed_before_fix=True,
        targeted_tests_passed=True,
        full_suite_passed=True,
    )

    VerificationGate.promote(run)

    assert run.status == RunStatus.READY_FOR_PR

