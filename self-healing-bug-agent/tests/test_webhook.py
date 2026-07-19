import hashlib
import hmac
import json

from httpx import ASGITransport, AsyncClient

from healing_agent.app import create_app
from healing_agent.config import Settings


SECRET = "webhook-test-secret"


def sign(body: bytes) -> str:
    digest = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def workflow_failure_payload() -> dict:
    return {
        "action": "completed",
        "repository": {"full_name": "demo/repo", "default_branch": "main"},
        "workflow_run": {
            "id": 99,
            "name": "CI",
            "head_sha": "abcdef1234567890",
            "conclusion": "failure",
            "logs_url": "https://api.github.test/logs/99",
        },
    }


async def test_accepts_signed_failed_workflow() -> None:
    app = create_app(Settings(github_webhook_secret=SECRET))
    body = json.dumps(workflow_failure_payload()).encode()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/webhooks/github",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-GitHub-Event": "workflow_run",
                "X-Hub-Signature-256": sign(body),
            },
        )
        runs = (await client.get("/api/v1/runs")).json()

    assert response.status_code == 202
    assert response.json()["status"] == "received"
    assert runs[0]["workflow_run_id"] == 99


async def test_rejects_invalid_signature() -> None:
    app = create_app(Settings(github_webhook_secret=SECRET))
    body = json.dumps(workflow_failure_payload()).encode()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/webhooks/github",
            content=body,
            headers={
                "X-GitHub-Event": "workflow_run",
                "X-Hub-Signature-256": "sha256=wrong",
            },
        )

    assert response.status_code == 401
