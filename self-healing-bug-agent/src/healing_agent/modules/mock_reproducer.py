"""Mock Reproducer implementation for demo purposes."""

from __future__ import annotations

import asyncio
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
        """Reproduce the demo bug by executing the checked-out code."""

        command = [
            sys.executable,
            "-c",
            (
                "from calculator import divide\n"
                "try:\n"
                "    divide(10, 0)\n"
                "except ValueError:\n"
                "    pass\n"
                "else:\n"
                "    raise AssertionError('expected ValueError')\n"
            ),
        ]
        completed = await asyncio.to_thread(
            subprocess.run,
            command,
            cwd=workspace.path,
            capture_output=True,
            text=True,
        )
        return ReproductionResult(
            reproduced=completed.returncode != 0,
            command=" ".join(command[:2]) + " <reproduction-script>",
            exit_code=completed.returncode,
            output=(completed.stdout + completed.stderr).strip(),
        )
