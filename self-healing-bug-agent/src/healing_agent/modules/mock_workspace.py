"""Mock WorkspaceManager implementation for demo purposes."""

from __future__ import annotations

from pathlib import Path
import subprocess

from healing_agent.models import RepairRun
from healing_agent.modules.contracts import Workspace


class MockWorkspaceManager:
    """Mock workspace manager that creates a local directory for demo purposes.
    
    In production, this would clone the actual GitHub repository.
    """

    def __init__(self, workspace_root: Path = Path("workspaces")) -> None:
        self.workspace_root = workspace_root
        self.workspace_root.mkdir(parents=True, exist_ok=True)

    async def prepare(self, run: RepairRun) -> Workspace:
        """Prepare a workspace by creating a local directory with sample files."""
        
        # Create a unique workspace directory
        workspace_path = self.workspace_root / f"{run.repo_full_name.replace('/', '_')}_{run.id}"
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize git repository
        subprocess.run(
            ["git", "init"],
            cwd=workspace_path,
            capture_output=True,
        )
        
        # Create sample Python files for demo
        self._create_sample_files(workspace_path)
        
        # Configure git
        subprocess.run(
            ["git", "config", "user.email", "demo@example.com"],
            cwd=workspace_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Demo User"],
            cwd=workspace_path,
            capture_output=True,
        )
        
        # Create initial commit
        subprocess.run(
            ["git", "add", "."],
            cwd=workspace_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=workspace_path,
            capture_output=True,
        )
        
        # Create branch for the repair
        branch_name = f"repair-{run.id}"
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=workspace_path,
            capture_output=True,
        )
        
        return Workspace(
            path=workspace_path,
            branch_name=branch_name,
        )

    def _create_sample_files(self, workspace_path: Path) -> None:
        """Create sample Python files for the demo."""
        
        # Create a simple Python module with a bug
        (workspace_path / "calculator.py").write_text("""
def add(a, b):
    return a + b

def divide(a, b):
    return a / b  # Bug: no division by zero check
""")
        
        # Create a test file
        (workspace_path / "test_calculator.py").write_text("""
import pytest
from calculator import add, divide

def test_add():
    assert add(2, 3) == 5

def test_divide():
    assert divide(10, 2) == 5
""")
        
        # Create README
        (workspace_path / "README.md").write_text("""
# Sample Calculator Module

A simple calculator with a division bug.
""")
        
        # Create pyproject.toml
        (workspace_path / "pyproject.toml").write_text("""
[project]
name = "calculator"
version = "0.1.0"
""")
