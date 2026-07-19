# Self-Healing Bug Agent

A closed-loop backend that receives a bug report or failed GitHub Actions run,
reproduces the failure in a workspace, iterates on a fix, adds a regression test,
runs targeted and full verification, and only then allows a pull request to open.

## Current milestone

The repository currently contains the Backend/Orchestration foundation:

- FastAPI service with health, manual run, run-status, and GitHub webhook routes.
- Signed GitHub webhook parsing for failed workflows and labeled issues.
- Explicit repair state machine with an auditable event timeline.
- Pluggable contracts for workspace, reproduction, repair, test writing, verification,
  and PR publishing modules.
- A hard `VerificationGate` that prevents an unverified PR.
- Automated tests for the green loop, retry loop, iteration limit, webhook signature,
  and gate bypass attempts.

Real repository execution, OpenAI Agents SDK repair logic, GitHub App publishing,
and persistent storage are the next integration milestone.

## Architecture principle

The model may propose a diagnosis, patch, or test. It cannot declare itself green.
Only deterministic command results assembled into `VerificationReport` can move a
run to `ready_for_pr`, and only that state may invoke the PR publisher.

## Local setup

Python 3.11 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
cp .env.example .env
python -m pytest
uvicorn healing_agent.app:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the API explorer.

## API surface

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health |
| `POST` | `/api/v1/runs` | Create a manual repair run |
| `GET` | `/api/v1/runs` | List repair runs |
| `GET` | `/api/v1/runs/{id}` | Inspect state and timeline |
| `POST` | `/webhooks/github` | Receive signed GitHub events |

## Project map

```text
src/healing_agent/
  api/                 Request and response schemas
  integrations/        GitHub and future provider adapters
  modules/             Contracts for team-owned specialist modules
  orchestrator/        State machine, workflow, gate, and run store
  app.py                FastAPI composition root
documentation/          Reviewable architecture and safety contracts
tests/                  Closed-loop and webhook tests
```

See [documentation/architecture.md](documentation/architecture.md) for the full
system boundary and next implementation milestone.

