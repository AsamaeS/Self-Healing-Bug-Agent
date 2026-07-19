from pydantic import BaseModel, Field

from healing_agent.models import TriggerType


class CreateRunRequest(BaseModel):
    repo_full_name: str = Field(pattern=r"^[^/\s]+/[^/\s]+$")
    base_sha: str = Field(min_length=7)
    bug_report: str = Field(min_length=1)
    trigger_type: TriggerType = TriggerType.MANUAL


class AcceptedRun(BaseModel):
    run_id: str
    status: str

