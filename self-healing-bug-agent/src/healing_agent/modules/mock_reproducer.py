"""Mock Reproducer implementation for demo purposes."""

from __future__ import annotations

import subprocess
import sys

from healing_agent.models import RepairRun
from healing_agent.modules.contracts import ReproductionResult, Workspace


class MockReproducer:
    """Mock reproducer that runs tests to reproduce the failure.
    
    In production, this would run the actual failing test from the CI logs.
    """

    async def reproduce(
        self, run: RepairRun, workspace: Workspace
    ) -> ReproductionResult:
        """Attempt to reproduce the failure by running tests."""
        
        # For demo purposes, simulate a failure to allow the workflow to continue
        # In production, this would actually run the failing test
        return ReproductionResult(
            reproduced=True,  # Simulate successful reproduction
            command=f"{sys.executable} -m pytest -v",
            exit_code=1,  # Simulate test failure
            output="Simulated test failure for demo purposes\n\nFAILED test_calculator.py::test_divide_by_zero - AssertionError: Expected ZeroDivisionError but no exception was raised",
        )
