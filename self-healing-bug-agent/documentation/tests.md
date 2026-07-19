# Verification map

## Existing coverage

| Use case | Rule | Expected behavior | Evidence | Status |
| --- | --- | --- | --- | --- |
| PR gate bypass | A run cannot skip verification | Illegal transition raises | `state_machine.py`, `test_state_machine.py` | Existing unit |
| Incomplete evidence | Every gate field must pass | Promotion is rejected | `VerificationReport`, `test_state_machine.py` | Existing unit |
| Green repair loop | Verified run may publish | State reaches `PR_CREATED` once | `workflow.py`, `test_workflow.py` | Existing integration |
| Failed targeted test | Failure returns to diagnosis | Second iteration runs before PR | `workflow.py`, `test_workflow.py` | Existing integration |
| Iteration budget | A stuck run cannot publish | Terminal limit state and zero PR calls | `workflow.py`, `test_workflow.py` | Existing integration |
| Signed webhook | Only valid GitHub signature is accepted | Valid 202; invalid 401 | `github_webhook.py`, `test_webhook.py` | Existing API |
| Sandbox verification | Source checkout stays untouched and evidence is captured | Patch and tests run in a disposable workspace | `test_sandbox_verification.py` | Existing integration |

All existing tests are intended to be CI-required for `main`.

## Proposed tests

| Use case | Rule | Test type |
| --- | --- | --- |
| Duplicate webhook | One GitHub delivery creates one run | Automated integration |
| GitHub authorization | Installation may touch only allowed repo | Guarded live |
| Sandbox escape | Commands cannot reach host or other runs | Automated integration |
| Secret scan | Credential-like diff blocks PR | Automated integration |
| Forbidden paths | Workflow and security files require approval | Automated integration |
| Real repair | Demo bug is reproduced, fixed, and regression-tested | End-to-end |
| Restart recovery | Active run resumes from durable state | Automated integration |
| Kill switch | New actions stop without corrupting state | Automated integration |

## Gaps

1. No real sandbox or command runner is connected, so execution isolation is unverified.
2. No GitHub App authorization or real PR publishing is connected.
3. No durable database, queue, idempotency key, cancellation, or resume behavior exists.
4. No OpenAI Agents SDK repair adapter or structured-output validation exists.
5. No cost, token, or wall-clock budget enforcement exists.
