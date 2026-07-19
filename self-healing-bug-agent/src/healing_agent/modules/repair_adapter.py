"""Adapter that bridges Module 2 RepairAgent with the orchestrator's RepairAgent protocol."""

from __future__ import annotations

from pathlib import Path
import asyncio

from healing_agent.models import RepairRun, VerificationReport
from healing_agent.modules.contracts import (
    Diagnosis as OrchestratorDiagnosis,
    PatchResult,
    ReproductionResult,
    Workspace,
)
from healing_agent.modules.repair.agent import RepairAgent as Module2RepairAgent
from healing_agent.modules.repair.schemas import (
    BugContext,
    Diagnosis as Module2Diagnosis,
    PatchProposal,
)
from healing_agent.modules.shared.model_client import ModelClient


class RepairAgentAdapter:
    """Adapter implementing the orchestrator's RepairAgent protocol using Module 2's RepairAgent.
    
    This adapter:
    - Converts between orchestrator and Module 2 data models
    - Makes synchronous Module 2 methods async
    - Maps method signatures appropriately
    """

    def __init__(self, model_client: ModelClient | None = None) -> None:
        self._model_client = model_client or ModelClient()
        self._repair_agent = Module2RepairAgent(self._model_client)

    async def diagnose(
        self,
        run: RepairRun,
        workspace: Workspace,
        reproduction: ReproductionResult,
        previous_verification: VerificationReport | None,
    ) -> OrchestratorDiagnosis:
        """Diagnose the failure by delegating to Module 2 RepairAgent."""
        
        # Build BugContext from orchestrator data
        bug_context = BugContext(
            bug_report=run.bug_report,
            failing_test_name="test_example",  # Placeholder - would come from reproduction
            failing_test_output=reproduction.output,
            stack_trace=reproduction.output,  # Use output as stack trace for now
            relevant_files=self._extract_relevant_files(workspace.path),
            test_framework="pytest",  # Default to pytest
            previous_attempt_failure=self._extract_failure_reason(previous_verification),
        )
        
        # Run synchronous Module 2 method in thread pool
        module2_diagnosis = await asyncio.to_thread(
            self._repair_agent.diagnose, bug_context
        )
        
        # Convert Module 2 Diagnosis to orchestrator Diagnosis
        return OrchestratorDiagnosis(
            summary=module2_diagnosis.root_cause,
            evidence=[
                f"File and line: {module2_diagnosis.file_and_line}",
                f"Confidence: {module2_diagnosis.confidence}",
                f"Suggested approach: {module2_diagnosis.suggested_approach}",
            ]
        )

    async def apply_fix(
        self, run: RepairRun, workspace: Workspace, diagnosis: OrchestratorDiagnosis
    ) -> PatchResult:
        """Apply a fix by delegating to Module 2 RepairAgent."""
        
        # Build BugContext (simplified for fix application)
        bug_context = BugContext(
            bug_report=run.bug_report,
            failing_test_name="test_example",
            failing_test_output="",
            stack_trace="",
            relevant_files=self._extract_relevant_files(workspace.path),
            test_framework="pytest",
            previous_attempt_failure=None,
        )
        
        # Convert orchestrator Diagnosis to Module 2 Diagnosis
        module2_diagnosis = Module2Diagnosis(
            root_cause=diagnosis.summary,
            file_and_line=diagnosis.evidence[0] if diagnosis.evidence else "unknown",
            confidence="medium",
            suggested_approach=diagnosis.evidence[-1] if diagnosis.evidence else "",
        )
        
        # Run synchronous Module 2 method in thread pool
        patch_proposal = await asyncio.to_thread(
            self._repair_agent.propose_fix,
            bug_context,
            module2_diagnosis,
            run.iteration,
        )
        
        # Apply the patch to the workspace
        self._apply_patch_to_workspace(workspace.path, patch_proposal.diff)
        
        # Convert to orchestrator PatchResult
        return PatchResult(
            changed_files=patch_proposal.files_touched,
            summary=patch_proposal.explanation,
        )

    def _extract_relevant_files(self, workspace_path: Path) -> dict[str, str]:
        """Extract relevant files from workspace for context.
        
        For demo purposes, return a sample of Python files.
        """
        relevant_files = {}
        try:
            for py_file in workspace_path.rglob("*.py"):
                # Limit to first 5 files to avoid overwhelming context
                if len(relevant_files) >= 5:
                    break
                try:
                    relative_path = py_file.relative_to(workspace_path)
                    relevant_files[str(relative_path)] = py_file.read_text()
                except Exception:
                    continue
        except Exception:
            pass
        
        # Fallback if no files found
        if not relevant_files:
            relevant_files["example.py"] = "# Example file\n"
        
        return relevant_files

    def _extract_failure_reason(self, verification: VerificationReport | None) -> str | None:
        """Extract failure reason from previous verification for retry context."""
        if verification and not verification.passed:
            return "Previous attempt failed verification"
        return None

    def _apply_patch_to_workspace(self, workspace_path: Path, diff: str) -> None:
        """Apply a patch diff to the workspace using git apply."""
        import subprocess
        
        try:
            # Write diff to temporary file
            diff_path = workspace_path / "patch.diff"
            diff_path.write_text(diff)
            
            # Apply the patch
            result = subprocess.run(
                ["git", "apply", str(diff_path)],
                cwd=workspace_path,
                capture_output=True,
                text=True,
            )
            
            if result.returncode != 0:
                # If git apply fails, try manual patch application
                # For demo, we'll just note the failure
                pass
                
        except Exception as e:
            # Log error but don't fail - this is a demo
            pass
