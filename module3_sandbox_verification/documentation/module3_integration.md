# Module 3 Integration Guide

## Overview

Module 3 (Sandbox & Verification) provides isolated execution environment for verifying patches and regression tests. This document explains how to integrate Module 3 with the orchestrator.

## Architecture

```
Orchestrator (expects TestRunner protocol)
    ↓
SandboxTestRunnerAdapter (adapter layer)
    ↓
SandboxVerifier (Module 3 core)
    ↓
RepositorySandbox + CommandExecutor + RetryController
```

## Integration Approach

### Problem

- **Orchestrator expects**: `TestRunner` protocol with 3 separate async methods:
  - `run_targeted()` - Run targeted regression tests
  - `run_full_suite()` - Run full test suite
  - `build_verification_report()` - Build verification report
  
- **Module 3 provides**: `SandboxVerifier.verify_async()` - Single method that:
  - Creates isolated sandbox
  - Applies patch
  - Writes regression tests
  - Runs test suite
  - Returns verification report with retry logic

### Solution: Adapter Pattern

`SandboxTestRunnerAdapter` bridges the gap by:

1. **Implementing TestRunner protocol** - Provides the 3 methods expected by orchestrator
2. **Single execution, multiple returns** - Runs verification in `run_targeted()`, caches results for `run_full_suite()` and `build_verification_report()`
3. **Model conversion** - Converts between:
   - Orchestrator models (`PatchResult`, `RegressionTestResult`, `TestCommandResult`, `VerificationReport`)
   - Module 3 models (`VerificationRequest`, `VerificationReport`, `GeneratedTest`, `Command`)

## Usage

### Step 1: Import the Adapter

```python
from healing_agent.modules.sandbox_verification import SandboxTestRunnerAdapter
```

### Step 2: Instantiate in OrchestrationModules

```python
from healing_agent.modules.contracts import OrchestrationModules
from healing_agent.modules.sandbox_verification import SandboxTestRunnerAdapter

modules = OrchestrationModules(
    workspace_manager=your_workspace_manager,
    reproducer=your_reproducer,
    repair_agent=your_repair_agent,
    regression_test_writer=your_test_writer,
    test_runner=SandboxTestRunnerAdapter(),  # ← Module 3 adapter
    pr_publisher=your_pr_publisher,
)
```

### Step 3: Use in Orchestrator

The orchestrator workflow already calls the TestRunner protocol correctly:

```python
# In ClosedLoopOrchestrator.execute()

# Run targeted tests (this triggers full verification in Module 3)
targeted = await self.modules.test_runner.run_targeted(
    run, workspace, regression_test
)

# Run full suite (returns cached results from Module 3)
full_suite = await self.modules.test_runner.run_full_suite(run, workspace)

# Build verification report (converts Module 3 report to orchestrator format)
run.verification = await self.modules.test_runner.build_verification_report(
    run, workspace, reproduction, patch, regression_test, targeted, full_suite
)
```

## Data Flow

### 1. run_targeted() Call

**Input from orchestrator:**
- `run: RepairRun` - Run metadata
- `workspace: Workspace` - Working directory
- `test: RegressionTestResult` - Test files and command

**Adapter actions:**
1. Read test files from workspace
2. Extract patch diff from git state
3. Build `VerificationRequest` for Module 3
4. Call `SandboxVerifier.verify_async()`
5. Cache `VerificationReport` for later use
6. Convert to `TestCommandResult`

**Output to orchestrator:**
- `TestCommandResult` - Test execution result

### 2. run_full_suite() Call

**Input from orchestrator:**
- `run: RepairRun`
- `workspace: Workspace`

**Adapter actions:**
1. Retrieve cached `VerificationReport` from Step 1
2. Convert to `TestCommandResult`

**Output to orchestrator:**
- `TestCommandResult` - Same test results from Module 3

### 3. build_verification_report() Call

**Input from orchestrator:**
- `run: RepairRun`
- `workspace: Workspace`
- `reproduction: ReproductionResult`
- `patch: PatchResult`
- `regression_test: RegressionTestResult`
- `targeted: TestCommandResult`
- `full_suite: TestCommandResult`

**Adapter actions:**
1. Retrieve cached Module 3 `VerificationReport`
2. Convert to orchestrator's `VerificationReport` format
3. Map fields:
   - `original_failure_reproduced` ← from reproduction
   - `patch_present` ← from patch
   - `regression_test_added` ← from regression_test
   - `targeted_tests_passed` ← from Module 3 verification
   - `full_suite_passed` ← from Module 3 verification
   - `commands` ← extract from Module 3 logs
   - `notes` ← extract from Module 3 logs
4. Clean up cache

**Output to orchestrator:**
- `VerificationReport` - Orchestrator-compatible report

## Known Limitations

### 1. Patch Diff Extraction

**Issue**: `PatchResult` doesn't preserve the patch diff content.

**Current workaround**: Adapter extracts diff from workspace git state using:
```python
git diff HEAD  # or git diff for unstaged changes
```

**Recommended fix**: Add `diff: str` field to `PatchResult` in the repair agent contract.

### 2. Verification Proofs Not Collected

Module 3 doesn't currently check:
- `regression_test_failed_before_fix` - Would require running test before patch
- `forbidden_changes_detected` - Would require allowlist/denylist
- `secrets_detected` - Would require secret scanning

**Current behavior**: Adapter sets these to `False` or uses values from other sources.

**Recommended fix**: Either:
- Accept that Module 3 has a narrower scope, OR
- Extend Module 3 to support these checks (out of scope for hackathon)

### 3. Retry Budget Mismatch

- Orchestrator: `max_iterations=3` (repair iterations)
- Module 3: `max_attempts=5` (verification retries)

These are different concepts:
- **Repair iterations**: Number of times to retry the entire repair cycle
- **Verification retries**: Number of times to retry transient failures in sandbox

**Current behavior**: Adapter uses orchestrator's `max_iterations` as Module 3's `max_attempts`.

## Testing the Integration

### Unit Test Example

```python
import pytest
from healing_agent.modules.sandbox_verification import SandboxTestRunnerAdapter
from healing_agent.models import RepairRun, TriggerType
from healing_agent.modules.contracts import Workspace, RegressionTestResult

@pytest.mark.asyncio
async def test_adapter_integration():
    adapter = SandboxTestRunnerAdapter()
    
    run = RepairRun(
        repo_full_name="test/repo",
        trigger_type=TriggerType.MANUAL,
        base_sha="abc123",
    )
    
    workspace = Workspace(
        path=Path("/tmp/test-workspace"),
        branch_name="fix-branch",
    )
    
    test_result = RegressionTestResult(
        test_files=["tests/test_bug.py"],
        failed_before_fix=False,
        command="pytest",
    )
    
    # Test the adapter
    targeted = await adapter.run_targeted(run, workspace, test_result)
    assert targeted.command == "pytest"
    
    full_suite = await adapter.run_full_suite(run, workspace)
    assert full_suite.command == "pytest"
```

## Summary

The `SandboxTestRunnerAdapter` provides a clean integration between Module 3 and the orchestrator:

✅ **Preserves Module 3's public API** - No changes to SandboxVerifier  
✅ **Implements orchestrator's protocol** - Fully compatible with existing workflow  
✅ **Minimal code changes** - Single adapter file  
✅ **Clear responsibility** - Adapter handles conversion, Module 3 handles verification  
✅ **Testable** - Both Module 3 and adapter can be tested independently

The adapter is the recommended approach for integration, keeping Module 3 independent and reusable.