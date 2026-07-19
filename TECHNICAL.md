# Technical Details

## Backend Architecture (FastAPI + Python)

### Core Components

1. **FastAPI Application (`app.py`)**
   - HTTP server with endpoints for health checks, run creation, run listing, and GitHub webhooks
   - CORS middleware enabled for frontend integration
   - Depends on Settings for configuration
   - Uses InMemoryRunStore as the default run store

2. **Orchestrator (`orchestrator/workflow.py`)**
   - `ClosedLoopOrchestrator` is the central controller that manages the entire workflow
   - Uses `StateMachine` to track the run state
   - Uses `InMemoryRunStore` for persistence (can be replaced with PostgreSQL later)
   - Has hard `VerificationGate` that only allows PRs after full verification passes
   - Handles retries, iteration limits, and timeouts

3. **Pluggable Modules**
   - **Workspace Manager**: Manages cloning/checking out repository
   - **Reproducer**: Reproduces the failure in the workspace
   - **Repair Agent**: Generates fixes using LLM (planned adapter for OpenAI Agents SDK)
   - **Test Writer**: Creates regression tests
   - **Sandbox Verifier**: Runs tests and produces VerificationReport
   - **PR Publisher**: Creates pull requests (planned adapter)

### State Machine

Run states:
- `AWAITING_REPRODUCTION`: Waiting to reproduce the failure
- `AWAITING_REPAIR`: Waiting for AI repair
- `AWAITING_TEST`: Waiting for regression test
- `AWAITING_VERIFICATION`: Waiting for verification
- `READY_FOR_PR`: Verification passed
- `COMPLETED`: PR created
- `FAILED`: Too many retries or other failure

### GitHub Webhook Handling

- Verifies HMAC signature of incoming GitHub webhooks
- Accepts events like labeled issues or failed workflows
- Stores received runs in the in-memory store for later processing

## Frontend Architecture (React + TypeScript)

### Core Libraries

- **React 18**: UI framework
- **TanStack Router**: File-based routing
- **TanStack Query**: Data fetching and caching
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Animations
- **Lucide React**: Icons
- **Vite**: Bundler and dev server

### Project Structure

- `components/dashboard/`: Dashboard-specific UI components (RepoCard, IssueCard, WorkflowTimeline, etc.)
- `components/ui/`: Reusable UI components (Button, Input, etc.)
- `components/`: Landing page components (LandingHero, LandingFeatures, etc.)
- `lib/`: API client, hooks, and utilities
- `routes/`: File-based routes using TanStack Router

### API Integration

- `lib/api.ts`: TypeScript functions for making API calls
- `lib/hooks.ts`: React Query hooks for data fetching and mutations
- `VITE_API_URL`: Environment variable for backend URL (defaults to http://localhost:8000)

## Development Setup

### Backend

- Python 3.11+ required
- Virtual environment recommended
- `pyproject.toml`: Project dependencies and metadata
- To run: `uvicorn healing_agent.app:app --reload --port 8000`
- API docs: http://127.0.0.1:8000/docs

### Frontend

- Node.js 20+ and npm/yarn required
- `package.json`: Project dependencies and scripts
- To run: `npm run dev` or `vite`
- Runs on http://localhost:8082 by default

## Modules Overview

### 1. Self-Healing Bug Agent (`self-healing-bug-agent/`)

- **Purpose**: Core backend, orchestrator, and state machine
- **Key files**:
  - `src/healing_agent/app.py`: FastAPI app and endpoints
  - `src/healing_agent/orchestrator/workflow.py`: Orchestrator and state machine
  - `src/healing_agent/models.py`: Pydantic models for data validation
  - `api/schemas.py`: API request/response schemas

### 2. AI Repair Dashboard (`ai-repair-dashboard/`)

- **Purpose**: User interface for the bug agent
- **Key features**:
  - Landing page with hero, features, and architecture
  - Dashboard with metrics, live status, logs, etc.
  - OpenAI-style minimalist design

### 3. Sandbox & Verification (`module3_sandbox_verification/`)

- **Purpose**: Sandboxed environment for running tests
- **Key files**:
  - `src/healing_agent/modules/sandbox_verification/adapter.py`: Adapter for integration with orchestrator
  - `src/healing_agent/modules/sandbox_verification/sandbox.py`: Sandbox execution logic

## Future Enhancements

- **Persistence**: Replace InMemoryRunStore with PostgreSQL for durable storage
- **GitHub App**: Implement GitHub App for full integration
- **Streaming**: Use SSE for live run status updates in frontend
- **Docker Sandbox**: Use Docker for more secure, reproducible test environments
- **Deduplication**: Implement webhook delivery deduplication
- **Background Jobs**: Use a task queue (like Celery) for running workflows asynchronously
- **Email Alerts**: Send email notifications for run completions/failures
