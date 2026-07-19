"""Lifecycle management for disposable repository workspaces."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import tempfile

from .exceptions import SandboxCreationError


_IGNORED_COPY_NAMES = {".git", ".pytest_cache", "__pycache__", ".mypy_cache"}


@dataclass(frozen=True, slots=True)
class SandboxWorkspace:
    """A single isolated copy of a source repository."""

    path: Path


class RepositorySandbox:
    """Create and reliably remove a short-lived repository copy.

    This is filesystem isolation: the source checkout is never patched or tested
    in place. It is not a security boundary for hostile code. In production, run
    this module inside a container/VM with network, CPU, memory, and filesystem
    policies appropriate for untrusted repository code.
    """

    def __init__(self, repository_path: Path, sandbox_root: Path | None = None) -> None:
        self._repository_path = repository_path.expanduser().resolve()
        self._sandbox_root = sandbox_root.expanduser().resolve() if sandbox_root else None
        self._temporary_root: Path | None = None
        self.workspace: SandboxWorkspace | None = None

    def __enter__(self) -> SandboxWorkspace:
        """Copy the repository into a fresh directory and return that directory."""

        if not self._repository_path.is_dir():
            raise SandboxCreationError(
                f"Repository path is not a directory: {self._repository_path}"
            )

        try:
            if self._sandbox_root is not None:
                self._sandbox_root.mkdir(parents=True, exist_ok=True)
            temporary_root = Path(
                tempfile.mkdtemp(
                    prefix="repair-verification-",
                    dir=str(self._sandbox_root) if self._sandbox_root else None,
                )
            )
            destination = temporary_root / "repository"
            shutil.copytree(
                self._repository_path,
                destination,
                symlinks=True,
                ignore=shutil.ignore_patterns(*_IGNORED_COPY_NAMES),
            )
        except OSError as error:
            if "temporary_root" in locals():
                shutil.rmtree(temporary_root, ignore_errors=True)
            raise SandboxCreationError("Unable to create repository sandbox.") from error

        self._temporary_root = temporary_root
        self.workspace = SandboxWorkspace(path=destination)
        return self.workspace

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Remove the temporary workspace, even when verification fails."""

        if self._temporary_root is not None:
            shutil.rmtree(self._temporary_root, ignore_errors=True)
        self._temporary_root = None
        self.workspace = None
