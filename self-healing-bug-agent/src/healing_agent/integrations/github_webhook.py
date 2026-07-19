from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any

from healing_agent.models import RepairRun, TriggerType


class InvalidWebhook(ValueError):
    pass


class IgnoredWebhook(ValueError):
    pass


def verify_signature(body: bytes, signature: str | None, secret: str) -> bool:
    if not secret or not signature or not signature.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"), body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@dataclass(frozen=True)
class GitHubWebhookParser:
    autofix_label: str
    max_iterations: int

    def parse(self, event_name: str, body: bytes) -> RepairRun:
        try:
            payload: dict[str, Any] = json.loads(body)
        except json.JSONDecodeError as exc:
            raise InvalidWebhook("request body is not valid JSON") from exc

        repository = payload.get("repository") or {}
        repo_full_name = repository.get("full_name")
        if not repo_full_name:
            raise InvalidWebhook("repository.full_name is required")

        if event_name == "workflow_run":
            return self._workflow_failure(repo_full_name, payload)
        if event_name == "issues":
            return self._labeled_issue(repo_full_name, payload)
        raise IgnoredWebhook(f"unsupported GitHub event: {event_name}")

    def _workflow_failure(
        self, repo_full_name: str, payload: dict[str, Any]
    ) -> RepairRun:
        workflow = payload.get("workflow_run") or {}
        if payload.get("action") != "completed" or workflow.get("conclusion") != "failure":
            raise IgnoredWebhook("workflow run is not a completed failure")
        return RepairRun(
            repo_full_name=repo_full_name,
            trigger_type=TriggerType.CI_FAILURE,
            base_sha=workflow.get("head_sha") or "",
            workflow_run_id=workflow.get("id"),
            bug_report=(
                f"GitHub Actions workflow '{workflow.get('name', 'unknown')}' failed. "
                f"Logs URL: {workflow.get('logs_url', 'unavailable')}"
            ),
            max_iterations=self.max_iterations,
        )

    def _labeled_issue(
        self, repo_full_name: str, payload: dict[str, Any]
    ) -> RepairRun:
        label = (payload.get("label") or {}).get("name")
        if payload.get("action") != "labeled" or label != self.autofix_label:
            raise IgnoredWebhook("issue does not carry the configured autofix label")
        issue = payload.get("issue") or {}
        repository = payload.get("repository") or {}
        return RepairRun(
            repo_full_name=repo_full_name,
            trigger_type=TriggerType.ISSUE_LABEL,
            base_sha=repository.get("default_branch") or "main",
            issue_number=issue.get("number"),
            bug_report=f"{issue.get('title', '')}\n\n{issue.get('body') or ''}".strip(),
            max_iterations=self.max_iterations,
        )

