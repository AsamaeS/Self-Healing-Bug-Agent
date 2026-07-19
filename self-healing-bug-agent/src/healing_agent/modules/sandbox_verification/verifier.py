"""Public verification service that composes the sandbox subcomponents."""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys
from typing import Sequence

from .exceptions import (
    CommandExecutionError,
    PatchApplicationError,
    PatchValidationError,
    SandboxCreationError,
    UnsafePathError,
)
from .executor import CommandExecutor
from .models import (
    Command,
    ExecutionResult,
    LogLevel,
    VerificationAttempt,
    VerificationLog,
    VerificationReport,
    VerificationRequest,
    VerificationStatus,
)
from .retry import RetryController
from .sandbox import RepositorySandbox
from .utils import command_display, validate_patch_paths, write_generated_tests


class SandboxVerifier:
    """Verify a generated patch and regression test in fresh disposable copies.

    The synchronous ``verify`` method is suitable for worker processes. Async
    orchestrators can use ``verify_async`` to avoid blocking their event loop.
    """

    def __init__(
        self,
        *,
        executor: CommandExecutor | None = None,
        retry_controller: RetryController | None = None,
    ) -> None:
        self._executor = executor or CommandExecutor()
        self._retry_controller = retry_controller or RetryController()

    def verify(self, request: VerificationRequest) -> VerificationReport:
        """Apply and test a proposal, returning all auditable attempt evidence."""

        status, attempts = self._retry_controller.run(
            lambda number: self._verify_attempt(request, number),
            max_attempts=request.max_attempts,
        )
        logs = tuple(log for attempt in attempts for log in attempt.logs)
        terminal_log = VerificationLog(
            stage="verification",
            message=f"Verification finished with status: {status.value}.",
            level=LogLevel.INFO if status is VerificationStatus.VERIFIED else LogLevel.ERROR,
            metadata={"attempt_count": len(attempts)},
        )
        return VerificationReport(status=status, attempts=attempts, logs=(*logs, terminal_log))

    async def verify_async(self, request: VerificationRequest) -> VerificationReport:
        """Run blocking sandbox work in a thread for async workflow engines."""

        return await asyncio.to_thread(self.verify, request)

    def _verify_attempt(
        self, request: VerificationRequest, number: int
    ) -> VerificationAttempt:
        logs: list[VerificationLog] = [
            VerificationLog(
                stage="sandbox",
                message=f"Starting verification attempt {number}.",
                metadata={"attempt": number},
            )
        ]
        results: list[ExecutionResult] = []

        try:
            validate_patch_paths(request.patch_diff)
            with RepositorySandbox(request.repository_path, request.sandbox_root) as workspace:
                logs.append(
                    VerificationLog(
                        stage="sandbox",
                        message="Created isolated repository workspace.",
                    )
                )
                patch_results = self._apply_patch(workspace.path, request.patch_diff)
                results.extend(patch_results)
                logs.append(
                    VerificationLog(
                        stage="patch",
                        message="Patch applied successfully.",
                    )
                )
                test_paths = write_generated_tests(workspace.path, request.regression_tests)
                logs.append(
                    VerificationLog(
                        stage="regression_test",
                        message=f"Wrote {len(test_paths)} generated regression test file(s).",
                        metadata={"paths": [str(path.relative_to(workspace.path)) for path in test_paths]},
                    )
                )
                test_command = request.test_command or Command(
                    argv=(sys.executable, "-m", "pytest")
                )
                logs.append(
                    VerificationLog(
                        stage="test_suite",
                        message=f"Running test suite: {command_display(test_command.argv)}",
                    )
                )
                test_result = self._executor.run(test_command, workspace_path=workspace.path)
                results.append(test_result)
                if test_result.succeeded:
                    logs.append(
                        VerificationLog(
                            stage="test_suite",
                            message="Test suite passed.",
                            metadata={"duration_seconds": test_result.duration_seconds},
                        )
                    )
                    return VerificationAttempt(
                        number=number,
                        status=VerificationStatus.VERIFIED,
                        patch_applied=True,
                        test_results=tuple(results),
                        logs=tuple(logs),
                        retryable=False,
                    )

                logs.append(
                    VerificationLog(
                        stage="test_suite",
                        message="Test suite failed; a fresh retry may recover transient failures.",
                        level=LogLevel.WARNING,
                        metadata={
                            "exit_code": test_result.exit_code,
                            "timed_out": test_result.timed_out,
                            "duration_seconds": test_result.duration_seconds,
                        },
                    )
                )
                return VerificationAttempt(
                    number=number,
                    status=VerificationStatus.FAILED,
                    patch_applied=True,
                    test_results=tuple(results),
                    logs=tuple(logs),
                    error="Test suite did not pass.",
                    retryable=True,
                )
        except (PatchValidationError, UnsafePathError, PatchApplicationError) as error:
            return self._failure_attempt(
                number, logs, results, error, patch_applied=False, retryable=False
            )
        except (SandboxCreationError, CommandExecutionError) as error:
            return self._failure_attempt(
                number, logs, results, error, patch_applied=bool(results), retryable=True
            )

    def _apply_patch(self, workspace_path: Path, patch_diff: str) -> Sequence[ExecutionResult]:
        """Check and apply a validated unified diff using Git's safe patch parser."""

        commands = (
            Command(
                argv=("git", "apply", "--check", "--whitespace=error"),
                stdin=patch_diff,
            ),
            Command(argv=("git", "apply", "--whitespace=error"), stdin=patch_diff),
        )
        results: list[ExecutionResult] = []
        for command in commands:
            result = self._executor.run(command, workspace_path=workspace_path)
            results.append(result)
            if not result.succeeded:
                detail = result.stderr.strip() or result.stdout.strip() or "git apply failed"
                raise PatchApplicationError(detail)
        return tuple(results)

    @staticmethod
    def _failure_attempt(
        number: int,
        logs: list[VerificationLog],
        results: list[ExecutionResult],
        error: Exception,
        *,
        patch_applied: bool,
        retryable: bool,
    ) -> VerificationAttempt:
        logs.append(
            VerificationLog(
                stage="verification",
                message=str(error),
                level=LogLevel.ERROR,
            )
        )
        return VerificationAttempt(
            number=number,
            status=VerificationStatus.FAILED,
            patch_applied=patch_applied,
            test_results=tuple(results),
            logs=tuple(logs),
            error=str(error),
            retryable=retryable,
        )
