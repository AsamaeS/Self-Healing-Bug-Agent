"""Bounded retry policy for disposable verification attempts."""

from __future__ import annotations

from collections.abc import Callable

from .models import VerificationAttempt, VerificationStatus


class RetryController:
    """Execute a verification operation no more than five times."""

    MAX_ATTEMPTS = 5

    def run(
        self,
        operation: Callable[[int], VerificationAttempt],
        *,
        max_attempts: int = MAX_ATTEMPTS,
    ) -> tuple[VerificationStatus, tuple[VerificationAttempt, ...]]:
        """Run fresh attempts until success, a non-retryable failure, or exhaustion."""

        if not 1 <= max_attempts <= self.MAX_ATTEMPTS:
            raise ValueError(f"max_attempts must be between 1 and {self.MAX_ATTEMPTS}.")

        attempts: list[VerificationAttempt] = []
        for number in range(1, max_attempts + 1):
            attempt = operation(number)
            attempts.append(attempt)
            if attempt.status is VerificationStatus.VERIFIED:
                return VerificationStatus.VERIFIED, tuple(attempts)
            if not attempt.retryable:
                return VerificationStatus.FAILED, tuple(attempts)

        return VerificationStatus.FAILED_MAX_RETRY, tuple(attempts)
