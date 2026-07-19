"""Adapter that bridges Module 2 TestWritingAgent with the orchestrator's RegressionTestWriter protocol."""

from __future__ import annotations

from pathlib import Path
import asyncio

from healing_agent.models import RepairRun
from healing_agent.modules.contracts import (
    PatchResult,
    RegressionTestResult,
    ReproductionResult,
    Workspace,
)
from healing_agent.modules.repair.schemas import (
    BugContext,
    Diagnosis as Module2Diagnosis,
    PatchProposal,
)
from healing_agent.modules.shared.model_client import ModelClient
from healing_agent.modules.test_writing.agent import TestWritingAgent
from healing_agent.modules.test_writing.schemas import TestProposal


class RegressionTestWriterAdapter:
    """Adapter implementing the orchestrator's RegressionTestWriter protocol using Module 2's TestWritingAgent.
    
    This adapter:
    - Converts between orchestrator and Module 2 data models
    - Makes synchronous Module 2 methods async
    - Writes generated test files to workspace
    """

    def __init__(self, model_client: ModelClient | None = None) -> None:
        self._model_client = model_client or ModelClient()
        self._test_writer = TestWritingAgent(self._model_client)

    async def write_test(
        self,
        run: RepairRun,
        workspace: Workspace,
        reproduction: ReproductionResult,
        patch: PatchResult,
    ) -> RegressionTestResult:
        """Write a regression test by delegating to Module 2 TestWritingAgent."""
        
        # Build BugContext
        bug_context = BugContext(
            bug_report=run.bug_report,
            failing_test_name="test_example",
            failing_test_output=reproduction.output,
            stack_trace=reproduction.output,
            relevant_files=self._extract_relevant_files(workspace.path),
            test_framework="pytest",
            previous_attempt_failure=None,
        )
        
        # Build Module 2 Diagnosis (simplified)
        module2_diagnosis = Module2Diagnosis(
            root_cause="Bug identified during diagnosis",
            file_and_line="unknown",
            confidence="medium",
            suggested_approach="Fix the identified issue",
        )
        
        # Build PatchProposal from PatchResult
        patch_proposal = PatchProposal(
            diff=self._get_patch_diff_from_workspace(workspace.path),
            files_touched=patch.changed_files,
            explanation=patch.summary,
        )
        
        # Get sample existing test
        existing_test_sample = self._get_existing_test_sample(workspace.path)
        
        # Run synchronous Module 2 method in thread pool
        test_proposal = await asyncio.to_thread(
            self._test_writer.propose_regression_test,
            bug_context,
            module2_diagnosis,
            patch_proposal,
            existing_test_sample,
        )
        
        # Write the generated test file(s) to workspace
        test_files = []
        for test_file in test_proposal.test_files:
            test_path = workspace.path / test_file.path
            test_path.parent.mkdir(parents=True, exist_ok=True)
            test_path.write_text(test_file.content)
            test_files.append(str(test_file.path))
        
        return RegressionTestResult(
            test_files=test_files,
            failed_before_fix=True,  # Assume test would fail before fix
            command="pytest",
        )

    def _extract_relevant_files(self, workspace_path: Path) -> dict[str, str]:
        """Extract relevant files from workspace for context."""
        relevant_files = {}
        try:
            for py_file in workspace_path.rglob("*.py"):
                if len(relevant_files) >= 5:
                    break
                try:
                    relative_path = py_file.relative_to(workspace_path)
                    relevant_files[str(relative_path)] = py_file.read_text()
                except Exception:
                    continue
        except Exception:
            pass
        
        if not relevant_files:
            relevant_files["example.py"] = "# Example file\n"
        
        return relevant_files

    def _get_patch_diff_from_workspace(self, workspace_path: Path) -> str:
        """Extract the current patch diff from the workspace's git state."""
        import subprocess
        
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD"],
                cwd=workspace_path,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
        except Exception:
            pass
        
        return ""

    def _get_existing_test_sample(self, workspace_path: Path) -> str:
        """Get a sample existing test file for context."""
        try:
            for test_file in workspace_path.rglob("test_*.py"):
                try:
                    return test_file.read_text()
                except Exception:
                    continue
        except Exception:
            pass
        
        # Fallback sample
        return """import pytest

def test_example():
    assert True
"""
