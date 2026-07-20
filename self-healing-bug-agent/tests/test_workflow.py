from pathlib import Path

from healing_agent.models import RepairRun, RunStatus, TriggerType, VerificationReport
from healing_agent.modules.contracts import (
    Diagnosis,
    OrchestrationModules,
    PatchResult,
    PullRequestResult,
    RegressionTestFile,
    RegressionTestResult,
    ReproductionResult,
    TestCommandResult as CommandResult,
    Workspace,
)
from healing_agent.orchestrator.store import InMemoryRunStore
from healing_agent.orchestrator.workflow import ClosedLoopOrchestrator


class FakeWorkspaceManager:
    async def prepare(self, run):
        return Workspace(path=Path("/tmp/demo"), branch_name=f"agent/{run.id}")


class FakeReproducer:
    async def reproduce(self, run, workspace):
        return ReproductionResult(
            reproduced=True,
            command="pytest tests/test_bug.py",
            exit_code=1,
            output="expected 80, got 100",
        )


class FakeRepairAgent:
    def __init__(self):
        self.diagnoses = 0

    async def diagnose(self, run, workspace, reproduction, previous_verification):
        self.diagnoses += 1
        return Diagnosis(summary="discount boundary is not handled")

    async def apply_fix(self, run, workspace, diagnosis):
        return PatchResult(
            changed_files=["src/discount.py"],
            unified_diff=(
                "--- a/src/discount.py\n"
                "+++ b/src/discount.py\n"
                "@@ -1 +1 @@\n"
                "-return price\n"
                "+return price * 0.8\n"
            ),
            summary="fix boundary",
        )


class FakeRegressionTestWriter:
    async def write_test(self, run, workspace, reproduction, patch):
        return RegressionTestResult(
            test_files=[
                RegressionTestFile(
                    path="tests/test_discount.py",
                    content="def test_discount():\n    assert discount(100) == 80\n",
                )
            ],
            failed_before_fix=False,
            command="pytest tests/test_discount.py",
        )


class FakeTestRunner:
    def __init__(self, targeted_results: list[bool]):
        self.targeted_results = iter(targeted_results)

    async def run_targeted(self, run, workspace, patch, test):
        passed = next(self.targeted_results)
        return CommandResult(
            command=test.command,
            passed=passed,
            exit_code=0 if passed else 1,
        )

    async def run_full_suite(self, run, workspace):
        return CommandResult(command="pytest", passed=True, exit_code=0)


class FakeVerifier:
    async def verify(
        self, run, workspace, reproduction, patch, regression_test, targeted, full_suite
    ):
        return VerificationReport(
            original_failure_reproduced=reproduction.reproduced,
            patch_present=bool(patch.changed_files and patch.unified_diff),
            regression_test_added=bool(regression_test.test_files),
            regression_test_failed_before_fix=True,
            targeted_tests_passed=targeted.passed,
            full_suite_passed=full_suite.passed,
            commands=[reproduction.command, targeted.command, full_suite.command],
        )


class FakePublisher:
    def __init__(self):
        self.calls = 0

    async def open_pr(self, run, workspace):
        self.calls += 1
        assert run.status == RunStatus.READY_FOR_PR
        assert run.verification and run.verification.passed
        return PullRequestResult(url="https://github.test/demo/repo/pull/1", number=1)


def make_run(max_iterations: int = 3) -> RepairRun:
    return RepairRun(
        repo_full_name="demo/repo",
        trigger_type=TriggerType.MANUAL,
        base_sha="abcdef123456",
        bug_report="discount test fails",
        max_iterations=max_iterations,
    )


async def test_green_loop_opens_pr() -> None:
    publisher = FakePublisher()
    modules = OrchestrationModules(
        workspace_manager=FakeWorkspaceManager(),
        reproducer=FakeReproducer(),
        repair_agent=FakeRepairAgent(),
        regression_test_writer=FakeRegressionTestWriter(),
        test_runner=FakeTestRunner([True]),
        verifier=FakeVerifier(),
        pr_publisher=publisher,
    )
    orchestrator = ClosedLoopOrchestrator(modules, InMemoryRunStore())

    result = await orchestrator.execute(make_run())

    assert result.status == RunStatus.PR_CREATED
    assert result.verification and result.verification.passed
    assert publisher.calls == 1


async def test_failed_targeted_test_retries_before_pr() -> None:
    repair_agent = FakeRepairAgent()
    publisher = FakePublisher()
    modules = OrchestrationModules(
        workspace_manager=FakeWorkspaceManager(),
        reproducer=FakeReproducer(),
        repair_agent=repair_agent,
        regression_test_writer=FakeRegressionTestWriter(),
        test_runner=FakeTestRunner([False, True]),
        verifier=FakeVerifier(),
        pr_publisher=publisher,
    )
    orchestrator = ClosedLoopOrchestrator(modules, InMemoryRunStore())

    result = await orchestrator.execute(make_run())

    assert result.status == RunStatus.PR_CREATED
    assert result.iteration == 2
    assert repair_agent.diagnoses == 2
    assert publisher.calls == 1


async def test_iteration_limit_never_opens_pr() -> None:
    publisher = FakePublisher()
    modules = OrchestrationModules(
        workspace_manager=FakeWorkspaceManager(),
        reproducer=FakeReproducer(),
        repair_agent=FakeRepairAgent(),
        regression_test_writer=FakeRegressionTestWriter(),
        test_runner=FakeTestRunner([False, False]),
        verifier=FakeVerifier(),
        pr_publisher=publisher,
    )
    orchestrator = ClosedLoopOrchestrator(modules, InMemoryRunStore())

    result = await orchestrator.execute(make_run(max_iterations=2))

    assert result.status == RunStatus.ITERATION_LIMIT_REACHED
    assert publisher.calls == 0
