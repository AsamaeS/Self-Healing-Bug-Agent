# Load-bearing flows

## Failed CI webhook to repair run

- Actor: installed GitHub App.
- Preconditions: valid HMAC signature; event is `workflow_run.completed`; conclusion is
  `failure`; repository is authorized for the installation.
- Success outcome: one queued repair run tied to the exact failed commit.

1. GitHub sends the raw payload and signature to FastAPI.
2. The server validates HMAC before parsing or writing state.
3. The parser accepts only the configured event shape.
4. The service creates a `RECEIVED` run with the repository, SHA, and workflow ID.
5. A background worker will claim and execute it. Worker dispatch is not implemented yet.

Deny cases: invalid signature, unsupported event, non-failing workflow, unauthorized repo,
or duplicate delivery. The first three are implemented; repository authorization and
delivery deduplication are planned.

## Labeled issue to repair run

- Actor: repository maintainer through GitHub.
- Preconditions: signed `issues.labeled` event and configured `agent-fix` label.
- Success outcome: a repair run containing issue title/body and default branch.

The current parser enforces event and label shape. GitHub App repository authorization
and permission checks remain part of the GitHub adapter milestone.

## Closed verification loop

- Actor: background orchestrator.
- Preconditions: accepted run and prepared isolated workspace.
- Success outcome: a verified PR or an explicit terminal failure state.

1. Prepare an isolated workspace at the requested SHA.
2. Reproduce the original failure. Stop if it cannot be reproduced.
3. Ask the repair module for diagnosis and patch.
4. Require the regression-test module to add a test and prove it fails before the fix.
5. Run targeted tests. Feed failures into the next iteration.
6. Run the full suite and assemble a structured verification report.
7. Reject forbidden changes or detected secrets.
8. Promote to `READY_FOR_PR` only when every field passes.
9. Invoke the PR publisher and record the resulting URL.

The repair Agent owns suggestions. The application owns state transitions, command
evidence, iteration limits, safety checks, and PR creation.

