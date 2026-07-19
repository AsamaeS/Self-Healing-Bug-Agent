# Architecture

## Product overview

The service turns a GitHub bug signal into a verified repair attempt. It receives a
failed CI event or labeled issue, prepares a repository workspace, reproduces the
failure, lets specialist modules diagnose and patch it, requires a new regression
test, runs targeted and full verification, and opens a PR only after hard gates pass.

The current milestone implements the control-plane skeleton and contracts. Real GitHub
checkout, sandbox command execution, OpenAI Agents SDK repair, background jobs, and PR
publishing remain adapters to implement.

## Tech stack

| Layer | Choice | Current state |
| --- | --- | --- |
| HTTP API | FastAPI | Implemented |
| Schemas | Pydantic v2 | Implemented |
| Orchestration | Explicit Python state machine | Implemented |
| Agent runtime | OpenAI Agents SDK | Planned adapter |
| Execution plane | Local process first, Docker/hosted sandbox next | Planned adapter |
| Run persistence | In-memory store | Implemented MVP |
| Durable persistence | PostgreSQL | Planned |
| GitHub auth | GitHub App | Planned |
| Streaming timeline | SSE | Planned |

## Control plane versus execution plane

The control plane owns webhook verification, run state, retries, budgets, audit events,
secrets, and the PR gate. The execution plane receives narrow repository credentials and
runs model-directed file and shell operations in an isolated workspace. Secrets must not
be copied into prompts or committed artifacts.

```text
GitHub -> FastAPI -> Run store -> ClosedLoopOrchestrator
                                  |-> Workspace/Sandbox
                                  |-> Repair Agent
                                  |-> Test Runner
                                  `-> VerificationGate -> PR Publisher
```

## State ownership

`ClosedLoopOrchestrator` owns workflow order. Specialist modules return structured
evidence but cannot advance state. `VerificationGate` is the only path to
`READY_FOR_PR`; `PullRequestPublisher` is called only after that promotion.

## Trust boundaries

| Boundary | Risk | Enforcement |
| --- | --- | --- |
| GitHub -> webhook | Forged or replayed event | HMAC signature now; delivery dedupe planned |
| Control plane -> sandbox | Model-directed arbitrary execution | Adapter boundary now; isolation planned |
| Agent -> tools | Excessive side effects | Narrow module contracts and future tool allowlist |
| Sandbox -> GitHub | Credential or branch misuse | App-scoped token and branch policy planned |
| Verification -> PR | False claim of success | Deterministic `VerificationGate` implemented |

## Known risks and assumptions

- The in-memory store loses runs on restart and is not suitable for production.
- Webhook delivery deduplication is not yet implemented.
- A real sandbox adapter is not yet implemented; repository code must not be run on the
  API host in production.
- The webhook route records accepted runs but does not yet dispatch a background worker.
- GitHub App installation authorization and repository allowlisting are not implemented.
- No scheduled work exists; there is no `cron.md`.
- No email capability exists; there is no `emails.md`.
- No public indexable UI exists; there is no `seo.md`.

## Related documents

- [flows.md](flows.md)
- [permissions.md](permissions.md)
- [variables.md](variables.md)
- [automation.md](automation.md)
- [tests.md](tests.md)

