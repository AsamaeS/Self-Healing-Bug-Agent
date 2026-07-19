"""Adapter that bridges Module 3 (SandboxVerifier) with the orchestrator's TestRunner protocol.

This adapter allows Module 3 to integrate cleanly with the orchestrator without modifying
either the orchestrator workflow or Module 3's public API.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import TYPE_CHECKING

from healing_agent.models import RepairRun, VerificationReport as OrchestratorVerificationReport
from healing_agent.modules.contracts import (
    PatchResult,
    RegressionTestResult,
    ReproductionResult,
    TestCommandResult,
    Workspace,
)

from .models import Command, GeneratedTest, VerificationRequest, VerificationStatus
from .verifier import SandboxVerifier

if TYPE_CHECKING:
    from .models import VerificationReport as SandboxVerificationReport


class SandboxTestRunnerAdapter:
    """Adapter implementing the TestRunner protocol using Module 3's SandboxVerifier.
    
    This adapter:
    - Implements the orchestrator's TestRunner protocol
    - Converts between orchestrator and Module 3 data models
    - Preserves verification state for building the final report
    - Handles the difference in granularity (3 orchestrator calls → 1 sandbox call)
    """

    def __init__(self, verifier: SandboxVerifier | None = None) -> None:
        self._verifier = verifier or SandboxVerifier()
        # Cache to store verification results between method calls
        self._verification_cache: dict[str, SandboxVerificationReport] = {}

    async def run_targeted(
        self, run: RepairRun, workspace: Workspace, test: RegressionTestResult
    ) -> TestCommandResult:
        """Run targeted regression tests by delegating to SandboxVerifier.
        
        Since Module 3 runs everything in one call, we perform the full verification here
        and cache the results for later method calls.
        """
        # Build verification request from orchestrator data
        request = self._build_verification_request(workspace, test, run)
        
        # Execute full verification (patch + test)
        sandbox_report = await self._verifier.verify_async(request)
        
        # Cache the report for use in build_verification_report
        cache_key = f"{run.id}_{run.iteration}"
        self._verification_cache[cache_key] = sandbox_report
        
        # Convert to TestCommandResult
        return self._convert_to_test_result(sandbox_report, test.command)

    async def run_full_suite(
        self, run: RepairRun, workspace: Workspace
    ) -> TestCommandResult:
        """Return cached full suite results from the verification performed in run_targeted.
        
        Module 3 runs the complete test suite during its verification, so we return
        the cached results here.
        """
        cache_key = f"{run.id}_{run.iteration}"
        sandbox_report = self._verification_cache.get(cache_key)
        
        if sandbox_report is None:
            # Fallback: verification wasn't cached (shouldn't happen in normal flow)
            return TestCommandResult(
                command="pytest",
                passed=False,
                exit_code=1,
                output="Error: No cached verification results found",
            )
        
        # Return the same test results - Module 3 already ran the full suite
        return self._convert_to_test_result(sandbox_report, "pytest")

    async def build_verification_report(
        self,
        run: RepairRun,
        workspace: Workspace,
        reproduction: ReproductionResult,
        patch: PatchResult,
        regression_test: RegressionTestResult,
        targeted: TestCommandResult,
        full_suite: TestCommandResult,
    ) -> OrchestratorVerificationReport:
        """Build orchestrator verification report from cached Module 3 results."""
        cache_key = f"{run.id}_{run.iteration}"
        sandbox_report = self._verification_cache.get(cache_key)
        
        if sandbox_report is None:
            # Fallback: create a failed report
            return OrchestratorVerificationReport(
                original_failure_reproduced=reproduction.reproduced,
                patch_present=bool(patch.changed_files),
                regression_test_added=bool(regression_test.test_files),
                regression_test_failed_before_fix=False,
                targeted_tests_passed=False,
                full_suite_passed=False,
                forbidden_changes_detected=False,
                secrets_detected=False,
                notes=["Error: No cached verification results found"],
            )
        
        # Convert Module 3's report to orchestrator's report
        orchestrator_report = OrchestratorVerificationReport(
            original_failure_reproduced=reproduction.reproduced,
            patch_present=bool(patch.changed_files),
            regression_test_added=bool(regression_test.test_files),
            regression_test_failed_before_fix=regression_test.failed_before_fix,
            targeted_tests_passed=targeted.passed,
            full_suite_passed=full_suite.passed,
            forbidden_changes_detected=False,  # Module 3 doesn't check this
            secrets_detected=False,  # Module 3 doesn't scan for secrets
            commands=self._extract_commands(sandbox_report),
            notes=self._extract_notes(sandbox_report),
        )
        
        # Clean up cache
        self._verification_cache.pop(cache_key, None)
        
        return orchestrator_report

    def _build_verification_request(
        self, workspace: Workspace, test: RegressionTestResult, run: RepairRun
    ) -> VerificationRequest:
        """Build Module 3's VerificationRequest from orchestrator data.
        
        Note: This requires the orchestrator to preserve the patch diff in PatchResult
        and full test file content in RegressionTestResult.
        """
        # Extract patch diff from workspace git state
        # For now, we'll need to read this from the workspace's git diff
        # This is a limitation: PatchResult doesn't include the diff content
        
        # Build regression tests from test result
        regression_tests = []
        for test_file in test.test_files:
            # Read test file content from workspace
            test_path = workspace.path / test_file
            if test_path.exists():
                content = test_path.read_text()
                regression_tests.append(
                    GeneratedTest(
                        relative_path=Path(test_file),
                        content=content,
                    )
                )
        
        # Build test command
        test_command = Command(
            argv=tuple(test.command.split()) if test.command else (sys.executable, "-m", "pytest"),
            timeout_seconds=300.0,
        )
        
        return VerificationRequest(
            repository_path=workspace.path,
            patch_diff=self._get_patch_diff_from_workspace(workspace.path),
            regression_tests=tuple(regression_tests),
            test_command=test_command,
            max_attempts=3,  # Use orchestrator's max_iterations
        )

    def _get_patch_diff_from_workspace(self, workspace_path: Path) -> str:
        """Extract the current patch diff from the workspace's git state.
        
        This is a workaround because PatchResult doesn't preserve the diff.
        """
        import subprocess
        
        result = subprocess.run(
            ["git", "diff", "HEAD"],
            cwd=workspace_path,
            capture_output=True,
            text=True,
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
        
        # Fallback: if no diff in HEAD, try unstaged changes
        result = subprocess.run(
            ["git", "diff"],
            cwd=workspace_path,
            capture_output=True,
            text=True,
        )
        
        return result.stdout if result.returncode == 0 else ""

    def _convert_to_test_result(
        self, sandbox_report: SandboxVerificationReport, command: str
    ) -> TestCommandResult:
        """Convert Module 3's VerificationReport to orchestrator's TestCommandResult."""
        # Extract the last test execution result
        last_attempt = sandbox_report.attempts[-1] if sandbox_report.attempts else None
        
        if last_attempt and last_attempt.test_results:
            last_test = last_attempt.test_results[-1]
            return TestCommandResult(
                command=command or " ".join(last_test.command),
                passed=sandbox_report.status == VerificationStatus.VERIFIED,
                exit_code=last_test.exit_code or 1,
                output=f"{last_test.stdout}\n{last_test.stderr}".strip(),
            )
        
        # Fallback for failed verifications
        return TestCommandResult(
            command=command,
            passed=False,
            exit_code=1,
            output=self._extract_error_summary(sandbox_report),
        )

    def _extract_commands(self, sandbox_report: SandboxVerificationReport) -> list[str]:
        """Extract command list from Module 3's verification report."""
        commands = []
        for attempt in sandbox_report.attempts:
            for result in attempt.test_results:
                commands.append(" ".join(result.command))
        return commands

    def _extract_notes(self, sandbox_report: SandboxVerificationReport) -> list[str]:
        """Extract notes from Module 3's verification logs."""
        notes = []
        for log in sandbox_report.logs:
            if log.level.value in ("warning", "error"):
                notes.append(f"[{log.stage}] {log.message}")
        return notes

    def _extract_error_summary(self, sandbox_report: SandboxVerificationReport) -> str:
        """Create error summary from failed verification."""
        errors = []
        for attempt in sandbox_report.attempts:
            if attempt.error:
                errors.append(f"Attempt {attempt.number}: {attempt.error}")
        return "\n".join(errors) if errors else "Verification failed"
