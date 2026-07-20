"""Tests for the SandboxTestRunnerAdapter integration layer."""

from pathlib import Path
from uuid import uuid4

import pytest

from healing_agent.models import RepairRun, TriggerType
from healing_agent.modules.contracts import (
    PatchResult,
    RegressionTestFile,
    RegressionTestResult,
    ReproductionResult,
    Workspace,
)
from healing_agent.modules.sandbox_verification import (
    SandboxTestRunnerAdapter,
    SandboxVerifier,
    VerificationReport,
    VerificationStatus,
    VerificationAttempt,
    LogLevel,
    VerificationLog,
)


class FakeSandboxVerifier:
    """Fake verifier for testing the adapter without real sandbox execution."""

    def __init__(self, status: VerificationStatus = VerificationStatus.VERIFIED):
        self.status = status
        self.called_with = None

    async def verify_async(self, request):
        """Simulate verification."""
        self.called_with = request

        # Create a fake verification report
        attempt = VerificationAttempt(
            number=1,
            status=self.status,
            patch_applied=True,
            regression_failed_before_patch=True,
            test_results=(),
            logs=(
                VerificationLog(
                    stage="test",
                    message="Test completed",
                    level=LogLevel.INFO,
                ),
            ),
            error=None if self.status == VerificationStatus.VERIFIED else "Test failed",
            retryable=False,
        )

        return VerificationReport(
            status=self.status,
            attempts=(attempt,),
            logs=attempt.logs,
        )


@pytest.fixture
def adapter_with_fake_verifier():
    """Create adapter with fake verifier for testing."""
    fake_verifier = FakeSandboxVerifier()
    adapter = SandboxTestRunnerAdapter(verifier=fake_verifier)
    return adapter, fake_verifier


@pytest.fixture
def sample_run():
    """Create a sample repair run."""
    return RepairRun(
        id=uuid4(),
        repo_full_name="test/repo",
        trigger_type=TriggerType.MANUAL,
        base_sha="abc123",
        iteration=1,
    )


@pytest.fixture
def sample_workspace(tmp_path):
    """Create a sample workspace with git repo and sample diff."""
    import subprocess
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True, capture_output=True)
    
    # Create a sample file
    sample_file = tmp_path / "calculator.py"
    sample_file.write_text("def add(a, b): return a + b\n")
    
    # Commit initial version
    subprocess.run(["git", "add", "calculator.py"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmp_path, check=True, capture_output=True)
    
    # Make a change to create a diff
    sample_file.write_text("def add(a, b): return a + b\n\ndef divide(a, b): return a / b\n")
    
    return Workspace(
        path=tmp_path,
        branch_name="fix-branch",
    )


@pytest.fixture
def sample_test_result():
    """Create a sample regression test result."""
    return RegressionTestResult(
        test_files=[
            RegressionTestFile(
                path="tests/test_bug.py",
                content="def test_example(): assert True\n",
            )
        ],
        failed_before_fix=False,
        command="pytest",
    )


@pytest.fixture
def sample_reproduction():
    """Create a sample reproduction result."""
    return ReproductionResult(
        reproduced=True,
        command="pytest tests/",
        exit_code=1,
        output="Test failed",
    )


@pytest.fixture
def sample_patch():
    """Create a sample patch result."""
    return PatchResult(
        changed_files=["src/main.py"],
        unified_diff=(
            "--- a/calculator.py\n+++ b/calculator.py\n"
            "@@ -1 +1 @@\n-def add(a, b): return a + b\n"
            "+def add(a, b): return a - b\n"
        ),
        summary="Fixed the bug",
    )


class TestSandboxTestRunnerAdapter:
    """Test suite for the adapter."""

    @pytest.mark.asyncio
    async def test_adapter_implements_protocol(
        self, adapter_with_fake_verifier, sample_run, sample_workspace, sample_test_result
    ):
        """Test that adapter has all required TestRunner protocol methods."""
        adapter, _ = adapter_with_fake_verifier

        # Check that adapter has the required methods
        assert hasattr(adapter, "run_targeted")
        assert hasattr(adapter, "run_full_suite")
        assert hasattr(adapter, "verify")

    @pytest.mark.asyncio
    async def test_run_targeted_returns_test_command_result(
        self,
        adapter_with_fake_verifier,
        sample_run,
        sample_workspace,
        sample_test_result,
        sample_patch,
    ):
        """Test that run_targeted returns a TestCommandResult."""
        adapter, fake_verifier = adapter_with_fake_verifier

        # Setup: Create test file in workspace
        test_file = sample_workspace.path / "tests" / "test_bug.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_example(): assert True")

        result = await adapter.run_targeted(
            sample_run, sample_workspace, sample_patch, sample_test_result
        )

        # Verify result structure
        assert result.command == "pytest"
        assert isinstance(result.passed, bool)
        assert isinstance(result.exit_code, int)

    @pytest.mark.asyncio
    async def test_run_full_suite_uses_cached_results(
        self, adapter_with_fake_verifier, sample_run, sample_workspace, sample_test_result, sample_patch
    ):
        """Test that run_full_suite returns cached results from run_targeted."""
        adapter, _ = adapter_with_fake_verifier

        # Setup: Create test file in workspace
        test_file = sample_workspace.path / "tests" / "test_bug.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_example(): assert True")

        # First call run_targeted (this populates cache)
        await adapter.run_targeted(sample_run, sample_workspace, sample_patch, sample_test_result)

        # Then call run_full_suite (should use cache)
        result = await adapter.run_full_suite(sample_run, sample_workspace)

        # Verify result structure
        assert result.command == "pytest"
        assert isinstance(result.passed, bool)

    @pytest.mark.asyncio
    async def test_build_verification_report_converts_models(
        self,
        adapter_with_fake_verifier,
        sample_run,
        sample_workspace,
        sample_test_result,
        sample_reproduction,
        sample_patch,
    ):
        """Test that build_verification_report converts Module 3 report to orchestrator format."""
        adapter, _ = adapter_with_fake_verifier

        # Setup: Create test file in workspace
        test_file = sample_workspace.path / "tests" / "test_bug.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_example(): assert True")

        # Run verification to populate cache
        targeted = await adapter.run_targeted(
            sample_run, sample_workspace, sample_patch, sample_test_result
        )
        full_suite = await adapter.run_full_suite(sample_run, sample_workspace)

        # Build verification report
        report = await adapter.verify(
            sample_run,
            sample_workspace,
            sample_reproduction,
            sample_patch,
            sample_test_result,
            targeted,
            full_suite,
        )

        # Verify report structure (orchestrator's VerificationReport)
        assert hasattr(report, "original_failure_reproduced")
        assert hasattr(report, "patch_present")
        assert hasattr(report, "regression_test_added")
        assert hasattr(report, "targeted_tests_passed")
        assert hasattr(report, "full_suite_passed")
        assert hasattr(report, "forbidden_changes_detected")
        assert hasattr(report, "secrets_detected")
        assert hasattr(report, "commands")
        assert hasattr(report, "notes")

        # Verify values
        assert report.original_failure_reproduced == True
        assert report.patch_present == True
        assert report.regression_test_added == True

    @pytest.mark.asyncio
    async def test_adapter_handles_verification_failure(
        self, sample_run, sample_workspace, sample_test_result, sample_patch
    ):
        """Test that adapter correctly handles Module 3 verification failures."""
        # Create adapter with failing verifier
        fake_verifier = FakeSandboxVerifier(status=VerificationStatus.FAILED)
        adapter = SandboxTestRunnerAdapter(verifier=fake_verifier)

        # Setup: Create test file
        test_file = sample_workspace.path / "tests" / "test_bug.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_example(): assert True")

        # Run targeted test
        result = await adapter.run_targeted(
            sample_run, sample_workspace, sample_patch, sample_test_result
        )

        # Verify failure is reflected
        assert result.passed == False

    @pytest.mark.asyncio
    async def test_cache_cleanup_after_build_report(
        self,
        adapter_with_fake_verifier,
        sample_run,
        sample_workspace,
        sample_test_result,
        sample_reproduction,
        sample_patch,
    ):
        """Test that cache is cleaned up after building verification report."""
        adapter, _ = adapter_with_fake_verifier

        # Setup: Create test file
        test_file = sample_workspace.path / "tests" / "test_bug.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_example(): assert True")

        # Run full cycle
        targeted = await adapter.run_targeted(
            sample_run, sample_workspace, sample_patch, sample_test_result
        )
        full_suite = await adapter.run_full_suite(sample_run, sample_workspace)

        # Verify cache exists
        cache_key = f"{sample_run.id}_{sample_run.iteration}"
        assert cache_key in adapter._verification_cache

        # Build report (should clean cache)
        await adapter.verify(
            sample_run,
            sample_workspace,
            sample_reproduction,
            sample_patch,
            sample_test_result,
            targeted,
            full_suite,
        )

        # Verify cache is cleaned
        assert cache_key not in adapter._verification_cache


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
