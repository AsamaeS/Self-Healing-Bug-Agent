from __future__ import annotations

from healing_agent.models import RepairRun, RunStatus
from healing_agent.modules.contracts import OrchestrationModules
from healing_agent.orchestrator.state_machine import VerificationGate, transition
from healing_agent.orchestrator.store import InMemoryRunStore


class ClosedLoopOrchestrator:
    def __init__(
        self, modules: OrchestrationModules, store: InMemoryRunStore
    ) -> None:
        self.modules = modules
        self.store = store

    def _transition(
        self, run: RepairRun, target: RunStatus, message: str, metadata: dict | None = None
    ) -> None:
        transition(run, target, message, metadata)
        self.store.save(run)

    async def execute(self, run: RepairRun) -> RepairRun:
        self.store.save(run)
        try:
            self._transition(run, RunStatus.PREPARING, "Preparing isolated workspace")
            workspace = await self.modules.workspace_manager.prepare(run)

            self._transition(run, RunStatus.REPRODUCING, "Running original failure")
            reproduction = await self.modules.reproducer.reproduce(run, workspace)
            if not reproduction.reproduced:
                self._transition(
                    run,
                    RunStatus.REPRODUCTION_FAILED,
                    "Could not reproduce the reported failure",
                    {"command": reproduction.command, "exit_code": reproduction.exit_code},
                )
                return run

            retry_reason: str | None = None
            while run.iteration < run.max_iterations:
                run.iteration += 1
                self._transition(
                    run,
                    RunStatus.DIAGNOSING,
                    retry_reason or f"Diagnosing failure, iteration {run.iteration}",
                )
                retry_reason = None
                diagnosis = await self.modules.repair_agent.diagnose(
                    run, workspace, reproduction, run.verification
                )

                self._transition(run, RunStatus.PATCHING, "Applying proposed fix")
                patch = await self.modules.repair_agent.apply_fix(
                    run, workspace, diagnosis
                )

                self._transition(
                    run, RunStatus.WRITING_TEST, "Writing regression test"
                )
                regression_test = await self.modules.regression_test_writer.write_test(
                    run, workspace, reproduction, patch
                )

                self._transition(
                    run,
                    RunStatus.VERIFYING_TARGETED,
                    "Running targeted regression tests",
                )
                targeted = await self.modules.test_runner.run_targeted(
                    run, workspace, regression_test
                )
                if not targeted.passed:
                    if run.iteration >= run.max_iterations:
                        self._transition(
                            run,
                            RunStatus.ITERATION_LIMIT_REACHED,
                            "Targeted tests still fail at iteration limit",
                        )
                        return run
                    retry_reason = (
                        "Targeted tests failed; feeding evidence into next iteration"
                    )
                    continue

                self._transition(
                    run,
                    RunStatus.VERIFYING_FULL_SUITE,
                    "Running full repository test suite",
                )
                full_suite = await self.modules.test_runner.run_full_suite(run, workspace)
                run.verification = (
                    await self.modules.test_runner.build_verification_report(
                        run,
                        workspace,
                        reproduction,
                        patch,
                        regression_test,
                        targeted,
                        full_suite,
                    )
                )
                self.store.save(run)

                if not run.verification.passed:
                    if run.iteration >= run.max_iterations:
                        self._transition(
                            run,
                            RunStatus.ITERATION_LIMIT_REACHED,
                            "Verification gate failed at iteration limit",
                        )
                        return run
                    retry_reason = (
                        "Verification gate failed; feeding evidence into next iteration"
                    )
                    continue

                VerificationGate.promote(run)
                self.store.save(run)
                pr = await self.modules.pr_publisher.open_pr(run, workspace)
                run.pull_request_url = pr.url
                self._transition(
                    run,
                    RunStatus.PR_CREATED,
                    "Verified pull request created",
                    {"url": pr.url, "number": pr.number},
                )
                return run

            self._transition(
                run,
                RunStatus.ITERATION_LIMIT_REACHED,
                "Repair iteration limit reached",
            )
            return run
        except Exception as exc:
            if run.status not in {
                RunStatus.REPRODUCTION_FAILED,
                RunStatus.PR_CREATED,
                RunStatus.ITERATION_LIMIT_REACHED,
            }:
                self._transition(
                    run,
                    RunStatus.INFRA_FAILURE,
                    "Workflow failed because of an infrastructure or integration error",
                    {"error_type": type(exc).__name__, "error": str(exc)},
                )
            return run
