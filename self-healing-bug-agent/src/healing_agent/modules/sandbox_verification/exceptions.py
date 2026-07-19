"""Domain-specific exceptions for sandbox verification."""


class SandboxVerificationError(Exception):
    """Base class for expected verification-domain failures."""


class SandboxCreationError(SandboxVerificationError):
    """Raised when a disposable repository workspace cannot be created."""


class UnsafePathError(SandboxVerificationError):
    """Raised when generated content tries to access a path outside the sandbox."""


class PatchValidationError(SandboxVerificationError):
    """Raised when a generated patch is malformed or unsafe to apply."""


class PatchApplicationError(SandboxVerificationError):
    """Raised when a validated patch cannot be applied to the sandbox."""


class CommandExecutionError(SandboxVerificationError):
    """Raised when a command cannot be started by the operating system."""
