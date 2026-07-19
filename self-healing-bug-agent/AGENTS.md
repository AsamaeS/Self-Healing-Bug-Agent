# Repository guidance

## Scope

This repository owns the Backend/Orchestration layer for the self-healing bug agent.
Keep UI-only work and unrelated product features out of this repository.

## Non-negotiable behavior

- Never open a pull request unless `VerificationGate` passes.
- Treat model output as a proposal, never as proof that code or tests work.
- Run repository code only through a workspace/sandbox adapter.
- Never put credentials in prompts, logs, committed files, or sandbox artifacts.
- Preserve an audit event for every workflow state transition.
- All new behavior needs an automated test or an explicit entry in `documentation/tests.md`.

## Local verification

```bash
python -m pytest
```

## Documentation

Update `/documentation` whenever a trust boundary, side effect, permission, secret,
workflow state, or PR gate changes.

