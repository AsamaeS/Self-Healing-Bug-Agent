"""
Pydantic models for the repair module.

Everything here is a PROPOSAL only, per agents.md: "Treat model output as
a proposal, never as proof that code or tests work." There is deliberately
no verdict/pass field anywhere in this file -- only the verification
module, gated by VerificationGate, is allowed to say something is correct.
"""

from typing import Optional
from pydantic import BaseModel


class BugContext(BaseModel):
    bug_report: str
    failing_test_name: str
    failing_test_output: str
    stack_trace: str
    relevant_files: dict[str, str]
    test_framework: str
    previous_attempt_failure: Optional[str] = None  # set by orchestrator on retries


class Diagnosis(BaseModel):
    root_cause: str
    file_and_line: str
    confidence: str  # "low" | "medium" | "high"
    suggested_approach: str


class PatchProposal(BaseModel):
    diff: str
    files_touched: list[str]
    explanation: str


class RepairProposal(BaseModel):
    """What this module hands back to the orchestrator for a given iteration."""
    iteration_number: int
    diagnosis: Diagnosis
    patch: PatchProposal
