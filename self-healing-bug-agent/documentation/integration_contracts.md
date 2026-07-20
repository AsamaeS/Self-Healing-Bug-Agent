# Backend module integration contract

The executable source of truth is `src/healing_agent/modules/contracts.py`.

## Runtime decision

The orchestrator calls plain asynchronous Python objects implementing `Protocol`.
It does not receive OpenAI Agents SDK `Agent` instances directly. A repair module may
use `Agent` and `Runner.run(...)` internally, but it must expose the backend-facing
`RepairAgent` methods through an adapter and return the Pydantic contract models.

`openai-agents` remains optional because the deterministic orchestrator and verifier do
not depend on a specific model runtime. The current repair module uses the standard
OpenAI Python client behind `RepairAgentAdapter`; it can later be replaced by an Agents
SDK adapter without changing the orchestrator.

## Repair

```python
class RepairAgent(Protocol):
    async def diagnose(
        self,
        run: RepairRun,
        workspace: Workspace,
        reproduction: ReproductionResult,
        previous_verification: VerificationReport | None,
    ) -> Diagnosis: ...

    async def apply_fix(
        self,
        run: RepairRun,
        workspace: Workspace,
        diagnosis: Diagnosis,
    ) -> PatchResult: ...
```

Despite the legacy `apply_fix` name, the adapter returns a patch proposal and does not
mutate the pristine source workspace. `PatchResult` carries `changed_files`, the exact
`unified_diff`, and a summary. Module 3 applies the diff only inside a disposable copy.

## Regression test writing

```python
class RegressionTestWriter(Protocol):
    async def write_test(
        self,
        run: RepairRun,
        workspace: Workspace,
        reproduction: ReproductionResult,
        patch: PatchResult,
    ) -> RegressionTestResult: ...
```

The writer returns `RegressionTestFile(path, content)` with complete file content. It
does not write into the pristine source workspace. Module 3 inserts the files in its
sandbox, first against original code and then against patched code.

## Test runner and verifier adapter

```python
class TestRunner(Protocol):
    async def run_targeted(
        self,
        run: RepairRun,
        workspace: Workspace,
        patch: PatchResult,
        test: RegressionTestResult,
    ) -> TestCommandResult: ...

    async def run_full_suite(
        self,
        run: RepairRun,
        workspace: Workspace,
    ) -> TestCommandResult: ...

class Verifier(Protocol):
    async def verify(
        self,
        run: RepairRun,
        workspace: Workspace,
        reproduction: ReproductionResult,
        patch: PatchResult,
        regression_test: RegressionTestResult,
        targeted: TestCommandResult,
        full_suite: TestCommandResult,
    ) -> healing_agent.models.VerificationReport: ...
```

`SandboxTestRunnerAdapter` implements both protocols. It maps Module 3's own dataclass
`VerificationReport` to the backend gate report, so Module 3 does not need a rewrite.
The same adapter instance is supplied as both `test_runner` and `verifier`.

## Closed verification order

1. Copy the pristine workspace.
2. Write the generated regression test.
3. Run only that test against original code and require a failure.
4. Apply the preserved unified diff.
5. Clear stale Python bytecode generated during the pre-patch run.
6. Run the complete suite and require success.
7. Normalize evidence into the backend report.
8. Only `VerificationGate` may promote the run to `READY_FOR_PR`.

