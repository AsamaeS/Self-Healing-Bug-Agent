# Sandbox & Verification module

`healing_agent.modules.sandbox_verification` is a standalone execution-plane
adapter. It does not implement workflow order, repair generation, GitHub access,
or UI behavior.

## Public API

```python
from pathlib import Path
from healing_agent.modules.sandbox_verification import (
    GeneratedTest,
    SandboxVerifier,
    VerificationRequest,
)

report = SandboxVerifier().verify(
    VerificationRequest(
        repository_path=Path("/workspace/repository"),
        patch_diff=generated_patch,
        regression_tests=[GeneratedTest(Path("tests/test_bug.py"), generated_test)],
    )
)
```

`report.status` is one of `verified`, `failed`, or `failed_max_retry`. The report
contains each command's stdout, stderr, exit code, duration, timeout indicator,
and timestamped frontend-displayable logs. `report.to_dict()` is JSON-ready.

The default test command is `python -m pytest`; non-Python repositories must pass
an explicit `Command` argument vector. The command is never sent through a shell.

## Isolation and trust boundary

The module copies the repository into a temporary workspace for each attempt and
deletes the copy afterwards. The input checkout is never patched in place. It
rejects generated test paths and patch paths that could escape that workspace,
then checks each diff with `git apply --check` before applying it.

This filesystem copy is not a hostile-code security sandbox. Production deployment
must run it inside a container or VM with a repository allowlist, resource limits,
network policy, and no user credentials. Do not pass secrets through `Command`
environment values, generated patch content, test content, or displayed logs.

## Retry behavior

Every retry uses a newly copied workspace. Test failures and transient process or
sandbox-start failures can retry; unsafe or non-applicable patches fail immediately.
The public request accepts 1–5 attempts and the implementation enforces an upper
limit of five. Exhaustion returns `failed_max_retry`.
