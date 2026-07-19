from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field

from healing_agent.models import RepairRun, VerificationReport


class Workspace(BaseModel):
    path: Path
    branch_name: str


class ReproductionResult(BaseModel):
    reproduced: bool
    command: str
    exit_code: int
    output: str


class Diagnosis(BaseModel):
    summary: str
    evidence: list[str] = Field(default_factory=list)


class PatchResult(BaseModel):
    changed_files: list[str] = Field(default_factory=list)
    summary: str = ""


class RegressionTestResult(BaseModel):
    test_files: list[str] = Field(default_factory=list)
    failed_before_fix: bool = False
    command: str = ""


class TestCommandResult(BaseModel):
    command: str
    passed: bool
    exit_code: int
    output: str = ""


class PullRequestResult(BaseModel):
    url: str
    number: int


class WorkspaceManager(Protocol):
    async def prepare(self, run: RepairRun) -> Workspace: ...


class Reproducer(Protocol):
    async def reproduce(
        self, run: RepairRun, workspace: Workspace
    ) -> ReproductionResult: ...


class RepairAgent(Protocol):
    async def diagnose(
        self,
        run: RepairRun,
        workspace: Workspace,
        reproduction: ReproductionResult,
        previous_verification: VerificationReport | None,
    ) -> Diagnosis: ...

    async def apply_fix(
        self, run: RepairRun, workspace: Workspace, diagnosis: Diagnosis
    ) -> PatchResult: ...


class RegressionTestWriter(Protocol):
    async def write_test(
        self,
        run: RepairRun,
        workspace: Workspace,
        reproduction: ReproductionResult,
        patch: PatchResult,
    ) -> RegressionTestResult: ...


class TestRunner(Protocol):
    async def run_targeted(
        self, run: RepairRun, workspace: Workspace, test: RegressionTestResult
    ) -> TestCommandResult: ...

    async def run_full_suite(
        self, run: RepairRun, workspace: Workspace
    ) -> TestCommandResult: ...

    async def build_verification_report(
        self,
        run: RepairRun,
        workspace: Workspace,
        reproduction: ReproductionResult,
        patch: PatchResult,
        regression_test: RegressionTestResult,
        targeted: TestCommandResult,
        full_suite: TestCommandResult,
    ) -> VerificationReport: ...


class PullRequestPublisher(Protocol):
    async def open_pr(
        self, run: RepairRun, workspace: Workspace
    ) -> PullRequestResult: ...


@dataclass(frozen=True)
class OrchestrationModules:
    workspace_manager: WorkspaceManager
    reproducer: Reproducer
    repair_agent: RepairAgent
    regression_test_writer: RegressionTestWriter
    test_runner: TestRunner
    pr_publisher: PullRequestPublisher
