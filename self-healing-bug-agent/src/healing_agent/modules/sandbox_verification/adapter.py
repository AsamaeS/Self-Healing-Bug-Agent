"""Adapter that bridges Module 3 (SandboxVerifier) with the orchestrator's TestRunner protocol.

This adapter allows Module 3 to integrate cleanly with the orchestrator without modifying
either the orchestrator workflow or Module 3's public API.
"""

from __future__ import annotations

import sys
import shlex
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
        self,
        run: RepairRun,
        workspace: Workspace,
        patch: PatchResult,
        test: RegressionTestResult,
    ) -> TestCommandResult:
        """Run targeted regression tests by delegating to SandboxVerifier.
        
        Since Module 3 runs everything in one call, we perform the full verification here
        and cache the results for later method calls.
        """
        # Build verification request from orchestrator data
        request = self._build_verification_request(workspace, patch, test, run)
        
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

    async def verify(
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
            regression_test_failed_before_fix=any(
                attempt.regression_failed_before_patch
                for attempt in sandbox_report.attempts
            ),
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
        self,
        workspace: Workspace,
        patch: PatchResult,
        test: RegressionTestResult,
        run: RepairRun,
    ) -> VerificationRequest:
        """Build Module 3's VerificationRequest from orchestrator data.
        
        Patch and test artifacts come from the contracts, not mutable workspace state.
        """
        regression_tests = [
            GeneratedTest(relative_path=test_file.path, content=test_file.content)
            for test_file in test.test_files
        ]
        
        # Build test command
        test_command = Command(
            argv=tuple(shlex.split(test.command))
            if test.command
            else (sys.executable, "-m", "pytest"),
            timeout_seconds=300.0,
        )
        
        return VerificationRequest(
            repository_path=workspace.path,
            patch_diff=patch.unified_diff,
            regression_tests=tuple(regression_tests),
            test_command=test_command,
            max_attempts=3,  # Use orchestrator's max_iterations
        )

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
                exit_code=1 if last_test.exit_code is None else last_test.exit_code,
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
