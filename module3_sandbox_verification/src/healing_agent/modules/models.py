"""Public data contracts for the sandbox verification module.

The module deliberately uses standard-library dataclasses so it can be called from
LangGraph nodes, OpenAI Agents SDK tools, HTTP handlers, or a worker without
coupling to any of those runtimes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence


def utc_now() -> datetime:
    """Return a timezone-aware timestamp suitable for audit records."""

    return datetime.now(timezone.utc)


class VerificationStatus(str, Enum):
    """Terminal or intermediate state returned by verification."""

    VERIFIED = "verified"
    FAILED = "failed"
    FAILED_MAX_RETRY = "failed_max_retry"


class LogLevel(str, Enum):
    """Severity of a frontend-displayable verification event."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class GeneratedTest:
    """A regression-test file produced by the repair/test-writing agent."""

    relative_path: Path
    content: str


@dataclass(frozen=True, slots=True)
class Command:
    """A command executed in the isolated workspace.

    ``argv`` is intentionally an argument sequence rather than a shell string,
    preventing shell interpolation of agent-produced content.
    """

    argv: tuple[str, ...]
    timeout_seconds: float = 300.0
    environment: Mapping[str, str] = field(default_factory=dict)
    stdin: str | None = None

    def __post_init__(self) -> None:
        if not self.argv:
            raise ValueError("Command argv must contain at least one argument.")
        if self.timeout_seconds <= 0:
            raise ValueError("Command timeout_seconds must be greater than zero.")


@dataclass(frozen=True, slots=True)
class VerificationRequest:
    """All inputs needed to verify one proposed repair independently.

    ``test_command`` is optional. When omitted, the verifier uses its documented
    Python default: ``python -m pytest``. Callers for non-Python repositories can
    provide an explicit command such as ``("npm", "test", "--", "--runInBand")``.
    """

    repository_path: Path
    patch_diff: str
    regression_tests: Sequence[GeneratedTest]
    test_command: Command | None = None
    max_attempts: int = 5
    sandbox_root: Path | None = None

    def __post_init__(self) -> None:
        if not self.patch_diff.strip():
            raise ValueError("patch_diff must not be empty.")
        if not self.regression_tests:
            raise ValueError("At least one regression test is required.")
        if not 1 <= self.max_attempts <= 5:
            raise ValueError("max_attempts must be between 1 and 5.")


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """Captured evidence from one executed command."""

    command: tuple[str, ...]
    stdout: str
    stderr: str
    exit_code: int | None
    duration_seconds: float
    timed_out: bool = False

    @property
    def succeeded(self) -> bool:
        """Whether the process completed successfully before its timeout."""

        return not self.timed_out and self.exit_code == 0


@dataclass(frozen=True, slots=True)
class VerificationLog:
    """An audit event that can be rendered directly by a dashboard."""

    stage: str
    message: str
    level: LogLevel = LogLevel.INFO
    timestamp: datetime = field(default_factory=utc_now)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class VerificationAttempt:
    """Evidence collected from one fresh sandbox attempt."""

    number: int
    status: VerificationStatus
    patch_applied: bool
    test_results: Sequence[ExecutionResult] = field(default_factory=tuple)
    logs: Sequence[VerificationLog] = field(default_factory=tuple)
    error: str | None = None
    retryable: bool = True


@dataclass(frozen=True, slots=True)
class VerificationReport:
    """Structured module output for an orchestrator and the demo dashboard."""

    status: VerificationStatus
    attempts: Sequence[VerificationAttempt]
    logs: Sequence[VerificationLog]

    @property
    def verified(self) -> bool:
        """Return true only for a fully successful verification result."""

        return self.status is VerificationStatus.VERIFIED

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-ready data without tying the module to a web framework."""

        return _serialize(asdict(self))


def _serialize(value: Any) -> Any:
    """Convert standard dataclass output into JSON-compatible primitives."""

    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    return value
