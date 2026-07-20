# Demo runbook

## What is real today

- Backend API and closed-loop state machine run locally.
- The demo bug is reproduced by executing the original code.
- Repair and test-writing modules produce a preserved diff and complete test artifact.
- Module 3 proves the generated test fails before the patch, applies the patch in a
  disposable copy, and proves the full suite passes afterward.
- The backend hard gate allows PR publication only after normalized evidence is green.
- The current PR publisher returns a mock URL. Real GitHub branch push and PR creation
  still need the GitHub App/publisher adapter and repository access.
- The dashboard currently displays synchronized static demo evidence; live API streaming
  is not connected yet.

## Local checks

Backend:

```bash
cd self-healing-bug-agent
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest
```

Frontend:

```bash
cd ai-repair-dashboard
npm ci
npm run build
npm run lint
```

## Start the demo

Terminal 1:

```bash
cd self-healing-bug-agent
.venv/bin/uvicorn healing_agent.app:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
cd ai-repair-dashboard
npm run dev -- --host 127.0.0.1
```

Create a run:

```bash
curl -sS http://127.0.0.1:8000/api/v1/runs \
  -H 'Content-Type: application/json' \
  -d '{
    "repo_full_name": "demo/calculator",
    "base_sha": "abcdef123456",
    "bug_report": "divide(10, 0) must raise ValueError instead of ZeroDivisionError",
    "trigger_type": "manual"
  }'
```

Open `http://127.0.0.1:5173/dashboard` and the run-status endpoint returned by the API.

## 90-second video sequence

1. **0:00-0:12 — Problem.** “Most AI coding tools propose a patch. They do not prove
   that the patch fixes the bug without breaking the repository.”
2. **0:12-0:25 — Trigger.** Show the bug report/API request and the accepted run ID.
3. **0:25-0:42 — Actual reproduction.** Show `reproducing -> diagnosing -> patching` and
   explain that code is executed, not merely read from the log.
4. **0:42-0:58 — Closed evidence loop.** Show the preserved diff, complete regression
   test, and the pre-patch failure evidence.
5. **0:58-1:12 — Post-patch proof.** Show sandbox patch application and full-suite green.
6. **1:12-1:22 — Hard gate.** Show `ready_for_pr -> pr_created`; explain that the model
   cannot call the publisher directly.
7. **1:22-1:30 — Pitch.** “It is not an assistant explaining a stack trace. It is an
   autonomous write-run-check-repeat system that only ships verified-green work.”

## Recording checklist

- Record at 1920×1080 with browser zoom fixed before starting.
- Hide API keys, GitHub tokens, local usernames, notifications, and unrelated tabs.
- Clear old run/workspace data so the video shows one clean attempt.
- Keep terminal font large enough to read in the final compressed video.
- Do one rehearsal with mock mode, then record the same deterministic path.
- Do not claim a real GitHub PR until the real publisher is connected and observed.

