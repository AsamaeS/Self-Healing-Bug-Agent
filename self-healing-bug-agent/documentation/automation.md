# Agent and automation contract

## Repair workflow

| Field | Contract |
| --- | --- |
| Trigger | Signed failed-CI event, signed labeled issue, or development manual request |
| Owner | Backend/Orchestration |
| Approval | Automatic inside isolated workspace; PR creation only after hard verification |
| Read access | Checked-out repository, bug report, CI logs, prior iteration evidence |
| Tool access | Workspace filesystem and allowlisted shell commands through sandbox adapter |
| Output | Structured diagnosis, patch metadata, regression-test metadata, command results |
| Side effects | App creates workspace, persists state, pushes branch, and opens PR |
| Agent suggestions | Diagnosis, file edits, test edits, candidate commands |

## Steering versus hard guardrails

Prompts steer diagnosis quality, patch scope, and test-writing behavior. Prompts do not
enforce safety. Hard guardrails live in code: legal state transitions, iteration limits,
workspace isolation, tool allowlists, forbidden-path checks, secret scans, test exit
codes, and `VerificationGate`.

## Operational controls

- Audit timeline: implemented as run events; durable storage planned.
- Retry limit: implemented through `MAX_REPAIR_ITERATIONS`.
- Rate and cost limits: planned.
- Kill switch: planned global setting plus per-run cancellation.
- Human escalation: terminal states exist; resume/approval endpoint planned.
- Trace correlation: planned across GitHub delivery, run ID, model trace, and PR.

