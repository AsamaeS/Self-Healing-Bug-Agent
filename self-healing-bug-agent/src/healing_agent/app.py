from __future__ import annotations

from uuid import UUID
import asyncio

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from healing_agent.api.schemas import AcceptedRun, CreateRunRequest
from healing_agent.config import Settings, get_settings
from healing_agent.integrations.github_webhook import (
    GitHubWebhookParser,
    IgnoredWebhook,
    InvalidWebhook,
    verify_signature,
)
from healing_agent.models import RepairRun
from healing_agent.orchestrator.store import InMemoryRunStore, RunNotFound
from healing_agent.orchestrator.workflow import ClosedLoopOrchestrator
from healing_agent.modules.contracts import OrchestrationModules
from healing_agent.modules.mock_workspace import MockWorkspaceManager
from healing_agent.modules.mock_reproducer import MockReproducer
from healing_agent.modules.repair_adapter import RepairAgentAdapter
from healing_agent.modules.test_writer_adapter import RegressionTestWriterAdapter
from healing_agent.modules.mock_pr_publisher import MockPullRequestPublisher
from healing_agent.modules.sandbox_verification.adapter import SandboxTestRunnerAdapter


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(
        title="Self-Healing Bug Agent",
        version="0.1.0",
        description="Closed-loop backend that only opens verified-green PRs.",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:8082", "http://localhost:8081"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.settings = settings
    app.state.run_store = InMemoryRunStore()
    app.state.webhook_parser = GitHubWebhookParser(
        autofix_label=settings.github_autofix_label,
        max_iterations=settings.max_repair_iterations,
    )
    
    # Initialize orchestrator modules
    workspace_manager = MockWorkspaceManager(settings.workspace_root)
    reproducer = MockReproducer()
    repair_agent = RepairAgentAdapter()
    regression_test_writer = RegressionTestWriterAdapter()
    test_runner = SandboxTestRunnerAdapter()
    pr_publisher = MockPullRequestPublisher()
    
    modules = OrchestrationModules(
        workspace_manager=workspace_manager,
        reproducer=reproducer,
        repair_agent=repair_agent,
        regression_test_writer=regression_test_writer,
        test_runner=test_runner,
        verifier=test_runner,
        pr_publisher=pr_publisher,
    )
    
    app.state.orchestrator = ClosedLoopOrchestrator(modules, app.state.run_store)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/api/v1/runs",
        response_model=AcceptedRun,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def create_run(request: CreateRunRequest) -> AcceptedRun:
        run = RepairRun(
            repo_full_name=request.repo_full_name,
            base_sha=request.base_sha,
            bug_report=request.bug_report,
            trigger_type=request.trigger_type,
            max_iterations=settings.max_repair_iterations,
        )
        app.state.run_store.save(run)
        
        # Execute workflow asynchronously
        asyncio.create_task(execute_workflow(run))
        
        return AcceptedRun(run_id=str(run.id), status=run.status.value)
    
    async def execute_workflow(run: RepairRun) -> None:
        """Execute the repair workflow for a given run."""
        try:
            updated_run = await app.state.orchestrator.execute(run)
            app.state.run_store.save(updated_run)
        except Exception as e:
            # Log error and update run status
            run.add_event(
                run.status,
                f"Workflow execution failed: {str(e)}",
                {"error_type": type(e).__name__}
            )
            app.state.run_store.save(run)

    @app.get("/api/v1/runs", response_model=list[RepairRun])
    async def list_runs() -> list[RepairRun]:
        return app.state.run_store.list()

    @app.get("/api/v1/runs/{run_id}", response_model=RepairRun)
    async def get_run(run_id: UUID) -> RepairRun:
        try:
            return app.state.run_store.get(run_id)
        except RunNotFound as exc:
            raise HTTPException(status_code=404, detail="run not found") from exc

    @app.post(
        "/webhooks/github",
        response_model=AcceptedRun,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def github_webhook(
        request: Request,
        x_github_event: str = Header(default="", alias="X-GitHub-Event"),
        x_hub_signature_256: str | None = Header(
            default=None, alias="X-Hub-Signature-256"
        ),
    ) -> AcceptedRun:
        body = await request.body()
        if not verify_signature(
            body, x_hub_signature_256, settings.github_webhook_secret
        ):
            raise HTTPException(status_code=401, detail="invalid webhook signature")
        try:
            run = app.state.webhook_parser.parse(x_github_event, body)
        except IgnoredWebhook as exc:
            raise HTTPException(status_code=202, detail=str(exc)) from exc
        except InvalidWebhook as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        app.state.run_store.save(run)
        return AcceptedRun(run_id=str(run.id), status=run.status.value)

    return app


app = create_app()
