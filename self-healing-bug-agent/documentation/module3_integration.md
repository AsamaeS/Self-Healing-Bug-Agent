# Module 3 integration

`SandboxTestRunnerAdapter` wraps Module 3 without changing Module 3's internal
dataclass report. It implements the backend `TestRunner` and `Verifier` protocols and
maps Module 3 evidence into `healing_agent.models.VerificationReport`.

See [`integration_contracts.md`](integration_contracts.md) for the current method
signatures and composition example.

The verification sequence is:

1. copy pristine repository into a disposable directory;
2. write the generated regression test;
3. require that test to fail on original code;
4. apply the preserved patch diff;
5. remove stale Python bytecode from the pre-patch run;
6. run the full test suite and require success;
7. return structured evidence for the backend PR gate.

The current local sandbox is filesystem isolation for the demo, not a security boundary
for hostile code. A container or hosted sandbox remains required for production.
