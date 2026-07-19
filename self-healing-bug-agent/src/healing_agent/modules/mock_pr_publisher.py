"""Mock PullRequestPublisher implementation for demo purposes."""

from __future__ import annotations

from healing_agent.models import RepairRun
from healing_agent.modules.contracts import PullRequestResult, Workspace


class MockPullRequestPublisher:
    """Mock PR publisher that simulates creating a pull request.
    
    In production, this would use the GitHub API to create an actual PR.
    """

    def __init__(self) -> None:
        self._pr_counter = 0

    async def open_pr(
        self, run: RepairRun, workspace: Workspace
    ) -> PullRequestResult:
        """Simulate opening a pull request."""
        
        self._pr_counter += 1
        
        # In production, this would:
        # 1. Push the branch to GitHub
        # 2. Create a PR via GitHub API
        # 3. Return the actual PR URL and number
        
        # For demo, return a simulated PR
        return PullRequestResult(
            url=f"https://github.com/{run.repo_full_name}/pull/{self._pr_counter}",
            number=self._pr_counter,
        )
