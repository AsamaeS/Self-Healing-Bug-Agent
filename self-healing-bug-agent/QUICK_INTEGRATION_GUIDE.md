# Quick Integration Guide for Jing (Orchestrator Owner)

## TL;DR

Change 1 line in your orchestrator setup to integrate Module 3.

## What You Need to Do

### Step 1: Find where you create `OrchestrationModules`

Look for code like this in your project (probably in `main.py`, `app.py`, or a setup file):

```python
modules = OrchestrationModules(
    workspace_manager=...,
    reproducer=...,
    repair_agent=...,
    regression_test_writer=...,
    test_runner=FakeTestRunner(),  # ← Currently using fake
    pr_publisher=...,
)
```

### Step 2: Replace FakeTestRunner with SandboxTestRunnerAdapter

```python
from healing_agent.modules.sandbox_verification import SandboxTestRunnerAdapter

modules = OrchestrationModules(
    workspace_manager=...,
    reproducer=...,
    repair_agent=...,
    regression_test_writer=...,
    test_runner=SandboxTestRunnerAdapter(),  # ← Real Module 3
    pr_publisher=...,
)
```

That's it! The adapter handles everything else.

## Example: Complete Integration

```python
# Example: src/healing_agent/main.py or wherever you setup the orchestrator

from healing_agent.modules.contracts import OrchestrationModules
from healing_agent.modules.sandbox_verification import SandboxTestRunnerAdapter
from healing_agent.orchestrator.workflow import ClosedLoopOrchestrator
from healing_agent.orchestrator.store import InMemoryRunStore

# Your existing modules
from your_modules import (
    YourWorkspaceManager,
    YourReproducer,
    YourRepairAgent,
    YourRegressionTestWriter,
    YourPRPublisher,
)

def create_orchestrator():
    """Create orchestrator with all modules including Module 3."""
    
    modules = OrchestrationModules(
        workspace_manager=YourWorkspaceManager(),
        reproducer=YourReproducer(),
        repair_agent=YourRepairAgent(),
        regression_test_writer=YourRegressionTestWriter(),
        test_runner=SandboxTestRunnerAdapter(),  # ← Module 3 integration
        pr_publisher=YourPRPublisher(),
    )
    
    store = InMemoryRunStore()
    
    return ClosedLoopOrchestrator(modules, store)

# Usage
orchestrator = create_orchestrator()
result = await orchestrator.execute(repair_run)
```

## What the Adapter Does Automatically

The `SandboxTestRunnerAdapter` handles:

1. **Protocol Compliance** - Implements all 3 `TestRunner` methods:
   - `run_targeted()` - Runs verification
   - `run_full_suite()` - Returns cached results  
   - `build_verification_report()` - Converts to orchestrator format

2. **Model Conversion** - Converts between:
   - Your orchestrator models (`PatchResult`, `RegressionTestResult`, etc.)
   - Module 3 models (`VerificationRequest`, `VerificationReport`, etc.)

3. **Caching** - Stores verification results between method calls

4. **Error Handling** - Gracefully handles Module 3 errors and converts them to your format

## Verification

After integration, verify it works:

```python
# Quick smoke test
import asyncio
from healing_agent.modules.sandbox_verification import SandboxTestRunnerAdapter

async def test_integration():
    adapter = SandboxTestRunnerAdapter()
    print(f"✓ Adapter created: {adapter}")
    print(f"✓ Has run_targeted: {hasattr(adapter, 'run_targeted')}")
    print(f"✓ Has run_full_suite: {hasattr(adapter, 'run_full_suite')}")
    print(f"✓ Has build_verification_report: {hasattr(adapter, 'build_verification_report')}")
    print("✓ Module 3 is ready for integration!")

asyncio.run(test_integration())
```

Expected output:
```
✓ Adapter created: <SandboxTestRunnerAdapter object at 0x...>
✓ Has run_targeted: True
✓ Has run_full_suite: True
✓ Has build_verification_report: True
✓ Module 3 is ready for integration!
```

## Troubleshooting

### Import Error

**Problem**: `ModuleNotFoundError: No module named 'healing_agent'`

**Solution**: Install the package:
```bash
cd self-healing-bug-agent
pip install -e .
```

### Missing Patch Diff

**Problem**: Adapter can't find patch diff in workspace

**Solution**: The adapter currently extracts the diff from git state. Make sure:
1. Your repair agent commits or stages changes to git
2. Or, update `PatchResult` to include a `diff: str` field (see documentation/INTEGRATION_SUMMARY.md)

### Test File Not Found

**Problem**: Adapter can't find regression test files

**Solution**: Make sure `RegressionTestResult.test_files` points to actual files that exist in the workspace

## Need Help?

See detailed documentation:
- `documentation/module3_integration.md` - Complete integration guide
- `documentation/INTEGRATION_SUMMARY.md` - What was changed and why
- `documentation/sandbox_verification.md` - Module 3 architecture

## That's It!

One import, one line change, and Module 3 is integrated. The adapter handles all the complexity.