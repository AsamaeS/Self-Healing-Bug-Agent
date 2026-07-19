from __future__ import annotations

from pathlib import Path
import sys

from healing_agent.modules.sandbox_verification import (
    Command,
    GeneratedTest,
    SandboxVerifier,
    VerificationRequest,
    VerificationStatus,
)


PATCH = """--- a/calculator.py
+++ b/calculator.py
@@ -1 +1 @@
-def answer(): return 1
+def answer(): return 2
"""


def _repository(tmp_path: Path) -> Path:
    repository = tmp_path / "source-repository"
    repository.mkdir()
    (repository / "calculator.py").write_text("def answer(): return 1\n", encoding="utf-8")
    return repository


def _request(repository: Path, **overrides: object) -> VerificationRequest:
    values: dict[str, object] = {
        "repository_path": repository,
        "patch_diff": PATCH,
        "regression_tests": [
            GeneratedTest(
                relative_path=Path("tests/test_calculator.py"),
                content="from calculator import answer\n\ndef test_answer():\n    assert answer() == 2\n",
            )
        ],
        "test_command": Command(
            argv=(sys.executable, "-c", "from calculator import answer; assert answer() == 2")
        ),
    }
    values.update(overrides)
    return VerificationRequest(**values)  # type: ignore[arg-type]


def test_verifier_applies_patch_runs_test_and_preserves_source(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    report = SandboxVerifier().verify(_request(repository))

    assert report.status is VerificationStatus.VERIFIED
    assert report.attempts[0].patch_applied is True
    assert report.attempts[0].test_results[-1].succeeded is True
    assert (repository / "calculator.py").read_text(encoding="utf-8") == "def answer(): return 1\n"
    assert report.to_dict()["status"] == "verified"


def test_unsafe_patch_is_rejected_without_retry(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    unsafe_patch = PATCH.replace("a/calculator.py", "a/../../outside.py")

    report = SandboxVerifier().verify(_request(repository, patch_diff=unsafe_patch))

    assert report.status is VerificationStatus.FAILED
    assert len(report.attempts) == 1
    assert report.attempts[0].retryable is False


def test_failed_test_suite_returns_max_retry_status(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    failing_command = Command(argv=(sys.executable, "-c", "raise SystemExit(1)"))

    report = SandboxVerifier().verify(
        _request(repository, test_command=failing_command, max_attempts=2)
    )

    assert report.status is VerificationStatus.FAILED_MAX_RETRY
    assert len(report.attempts) == 2
    assert all(attempt.patch_applied for attempt in report.attempts)
