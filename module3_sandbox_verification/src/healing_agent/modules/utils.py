"""Safety-focused helpers for paths, diffs, and generated test files."""

from __future__ import annotations

from pathlib import Path, PurePosixPath, PureWindowsPath
import re
from typing import Iterable

from .exceptions import PatchValidationError, UnsafePathError
from .models import GeneratedTest


_PATCH_HEADER = re.compile(r"^(?:---|\+\+\+) ([^\t\r\n]+)", re.MULTILINE)


def validate_relative_path(path: Path) -> Path:
    """Return a safe relative path or reject attempts to escape the workspace."""

    raw_path = str(path)
    posix_path = PurePosixPath(raw_path.replace("\\", "/"))
    windows_path = PureWindowsPath(raw_path)
    if (
        not raw_path
        or "\x00" in raw_path
        or posix_path.is_absolute()
        or windows_path.is_absolute()
        or windows_path.drive
        or any(part in {"", ".", ".."} for part in posix_path.parts)
    ):
        raise UnsafePathError(f"Unsafe relative path: {raw_path!r}")
    return Path(*posix_path.parts)


def validate_patch_paths(patch_diff: str) -> None:
    """Reject unified-diff paths that could write outside the sandbox.

    Git still performs syntax and context validation before the patch is applied;
    this check specifically guards the trust boundary before invoking Git.
    """

    headers = _PATCH_HEADER.findall(patch_diff)
    if not headers:
        raise PatchValidationError("Patch does not contain unified-diff file headers.")

    for raw_path in headers:
        if raw_path == "/dev/null":
            continue
        normalized = raw_path[2:] if raw_path.startswith(("a/", "b/")) else raw_path
        try:
            validate_relative_path(Path(normalized))
        except UnsafePathError as error:
            raise PatchValidationError(f"Unsafe path in patch: {raw_path!r}") from error


def write_generated_tests(workspace_path: Path, tests: Iterable[GeneratedTest]) -> tuple[Path, ...]:
    """Write generated tests only below ``workspace_path`` and return their paths."""

    root = workspace_path.resolve()
    written_paths: list[Path] = []
    for test in tests:
        relative_path = validate_relative_path(test.relative_path)
        target = (root / relative_path).resolve()
        if not target.is_relative_to(root):
            raise UnsafePathError(f"Test path escapes workspace: {test.relative_path!s}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(test.content, encoding="utf-8", newline="\n")
        written_paths.append(target)
    return tuple(written_paths)


def command_display(argv: tuple[str, ...]) -> str:
    """Render an argument vector for logs without ever executing a shell."""

    return " ".join(repr(argument) if any(char.isspace() for char in argument) else argument for argument in argv)
