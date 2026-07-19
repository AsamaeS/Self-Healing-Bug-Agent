"""Controlled subprocess execution inside a prepared sandbox workspace."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
from time import perf_counter

from .exceptions import CommandExecutionError
from .models import Command, ExecutionResult


class CommandExecutor:
    """Run argument-vector commands and capture complete process evidence."""

    def run(self, command: Command, *, workspace_path: Path) -> ExecutionResult:
        """Execute ``command`` without a shell and return its captured outcome."""

        environment = os.environ.copy()
        environment.update(command.environment)
        start = perf_counter()
        try:
            completed = subprocess.run(
                command.argv,
                cwd=workspace_path,
                env=environment,
                shell=False,
                text=True,
                encoding="utf-8",
                errors="replace",
                input=command.stdin,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=command.timeout_seconds,
            )
        except (FileNotFoundError, NotADirectoryError, PermissionError, OSError) as error:
            raise CommandExecutionError(
                f"Unable to start command {command.argv[0]!r}."
            ) from error
        except subprocess.TimeoutExpired as timeout:
            return ExecutionResult(
                command=command.argv,
                stdout=_text(timeout.stdout),
                stderr=_text(timeout.stderr),
                exit_code=None,
                duration_seconds=perf_counter() - start,
                timed_out=True,
            )
        return ExecutionResult(
            command=command.argv,
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
            duration_seconds=perf_counter() - start,
        )


def _text(value: str | bytes | None) -> str:
    """Normalize timeout output returned by different Python subprocess paths."""

    if value is None:
        return ""
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value
