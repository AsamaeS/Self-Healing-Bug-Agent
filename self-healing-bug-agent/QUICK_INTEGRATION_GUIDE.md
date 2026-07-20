# Quick integration guide

The authoritative interface is in `src/healing_agent/modules/contracts.py`; the
explanation and adapter examples are in `documentation/integration_contracts.md`.

## Runtime shape

- The orchestrator calls plain async Python protocol implementations.
- OpenAI Agents SDK `Agent` objects, if used, stay inside a repair adapter.
- `PatchResult` must include the real `unified_diff`.
- `RegressionTestResult` must include full `RegressionTestFile` contents.
- Repair and test-writing modules return proposals; they do not mutate the pristine
  workspace.
- Module 3 writes artifacts and runs commands only in a disposable copy.

## Composition

```python
from healing_agent.modules.contracts import OrchestrationModules
from healing_agent.modules.sandbox_verification import SandboxTestRunnerAdapter

sandbox_adapter = SandboxTestRunnerAdapter()

modules = OrchestrationModules(
    workspace_manager=workspace_manager,
    reproducer=reproducer,
    repair_agent=repair_agent,
    regression_test_writer=regression_test_writer,
    test_runner=sandbox_adapter,
    verifier=sandbox_adapter,
    pr_publisher=pr_publisher,
)
```

The same Module 3 adapter is supplied twice because it implements two small backend
interfaces: command-level test results and final report normalization.

## Required proof before PR

1. Original bug was reproduced by executing code.
2. Generated regression test failed against original code.
3. Preserved diff applied cleanly in the sandbox.
4. Generated regression test and full suite passed after the patch.
5. Backend `VerificationGate` accepted the normalized evidence.

Run the backend checks with:

```bash
python -m pytest
```
