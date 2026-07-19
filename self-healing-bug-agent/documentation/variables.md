# Variables and secrets

| Name | Used by | Scope | Source | Rotation | Risk |
| --- | --- | --- | --- | --- | --- |
| `APP_ENV` | API | Server | Environment | N/A | Wrong mode can weaken local-only behavior |
| `LOG_LEVEL` | API/worker | Server | Environment | N/A | Debug logs may expose repository content |
| `OPENAI_API_KEY` | Agent adapter | Server only | Secret manager | On exposure | Model API access and cost |
| `OPENAI_MODEL` | Agent adapter | Server | Environment | N/A | Behavior/cost changes |
| `GITHUB_WEBHOOK_SECRET` | Webhook | Server only | GitHub + secret manager | On exposure | Forged events |
| `GITHUB_APP_ID` | GitHub adapter | Server | Environment | N/A | Installation identity |
| `GITHUB_PRIVATE_KEY_PATH` | GitHub adapter | Server only | Mounted secret file | On exposure | Repository write access |
| `GITHUB_AUTOFIX_LABEL` | Parser | Server | Environment | N/A | Controls issue-trigger scope |
| `MAX_REPAIR_ITERATIONS` | Orchestrator | Server | Environment | N/A | Cost and runaway-loop control |
| `WORKSPACE_ROOT` | Sandbox adapter | Server | Environment | N/A | Filesystem isolation boundary |

No secret may be bundled into a UI, copied into a prompt, written to repository files,
or included in workflow artifacts. `.env` and workspace directories are ignored by Git.

## Pre-demo checklist

- Use a GitHub App installation token scoped to the demo repository.
- Use a dedicated webhook secret.
- Confirm `.env` is untracked.
- Scan the final diff and artifacts for secrets.
- Revoke temporary credentials after the hackathon demo.

