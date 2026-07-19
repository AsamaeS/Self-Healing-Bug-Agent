from __future__ import annotations

from threading import RLock
from uuid import UUID

from healing_agent.models import RepairRun


class RunNotFound(KeyError):
    pass


class InMemoryRunStore:
    """MVP store; replace with PostgreSQL without changing workflow contracts."""

    def __init__(self) -> None:
        self._runs: dict[UUID, RepairRun] = {}
        self._lock = RLock()

    def save(self, run: RepairRun) -> RepairRun:
        with self._lock:
            self._runs[run.id] = run.model_copy(deep=True)
            return run.model_copy(deep=True)

    def get(self, run_id: UUID) -> RepairRun:
        with self._lock:
            try:
                return self._runs[run_id].model_copy(deep=True)
            except KeyError as exc:
                raise RunNotFound(str(run_id)) from exc

    def list(self) -> list[RepairRun]:
        with self._lock:
            return [run.model_copy(deep=True) for run in self._runs.values()]

