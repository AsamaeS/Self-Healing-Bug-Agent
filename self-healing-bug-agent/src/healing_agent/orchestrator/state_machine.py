from healing_agent.models import RepairRun, RunStatus, TERMINAL_STATUSES


class InvalidTransition(ValueError):
    """Raised when code attempts to bypass the closed-loop workflow."""


ALLOWED_TRANSITIONS: dict[RunStatus, set[RunStatus]] = {
    RunStatus.RECEIVED: {RunStatus.PREPARING, RunStatus.INFRA_FAILURE},
    RunStatus.PREPARING: {RunStatus.REPRODUCING, RunStatus.INFRA_FAILURE},
    RunStatus.REPRODUCING: {
        RunStatus.DIAGNOSING,
        RunStatus.REPRODUCTION_FAILED,
        RunStatus.INFRA_FAILURE,
    },
    RunStatus.DIAGNOSING: {
        RunStatus.PATCHING,
        RunStatus.NEEDS_HUMAN,
        RunStatus.INFRA_FAILURE,
    },
    RunStatus.PATCHING: {
        RunStatus.WRITING_TEST,
        RunStatus.DIAGNOSING,
        RunStatus.NEEDS_HUMAN,
        RunStatus.INFRA_FAILURE,
    },
    RunStatus.WRITING_TEST: {
        RunStatus.VERIFYING_TARGETED,
        RunStatus.DIAGNOSING,
        RunStatus.NEEDS_HUMAN,
        RunStatus.INFRA_FAILURE,
    },
    RunStatus.VERIFYING_TARGETED: {
        RunStatus.VERIFYING_FULL_SUITE,
        RunStatus.DIAGNOSING,
        RunStatus.ITERATION_LIMIT_REACHED,
        RunStatus.INFRA_FAILURE,
    },
    RunStatus.VERIFYING_FULL_SUITE: {
        RunStatus.READY_FOR_PR,
        RunStatus.DIAGNOSING,
        RunStatus.ITERATION_LIMIT_REACHED,
        RunStatus.INFRA_FAILURE,
    },
    RunStatus.READY_FOR_PR: {RunStatus.PR_CREATED, RunStatus.INFRA_FAILURE},
}


def transition(
    run: RepairRun,
    target: RunStatus,
    message: str,
    metadata: dict | None = None,
) -> None:
    if run.status in TERMINAL_STATUSES:
        raise InvalidTransition(f"terminal run cannot leave {run.status.value}")

    allowed = ALLOWED_TRANSITIONS.get(run.status, set())
    if target not in allowed:
        raise InvalidTransition(
            f"transition {run.status.value} -> {target.value} is not allowed"
        )
    run.add_event(target, message, metadata)


class VerificationGate:
    """The only component allowed to promote a run to READY_FOR_PR."""

    @staticmethod
    def promote(run: RepairRun) -> None:
        if run.verification is None:
            raise InvalidTransition("verification report is required before PR promotion")
        if not run.verification.passed:
            raise InvalidTransition("verification gate did not pass")
        transition(run, RunStatus.READY_FOR_PR, "All verification gates passed")

