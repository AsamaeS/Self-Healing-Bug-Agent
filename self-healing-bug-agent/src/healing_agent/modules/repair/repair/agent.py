"""
RepairAgent: produces a Diagnosis, then a PatchProposal.

TODO before wiring into the orchestrator: confirm the actual contract
(Protocol/ABC, method names, input/output types) this needs to implement
against the real source in this repo's modules/ package. The class below
is a best-effort guess based on the README and architecture diagram, not
the authoritative interface -- get that file from the backend/orchestration
owner before treating this as final.

Also confirm: does the orchestrator call this as a plain Python class
(as below), or does it expect an OpenAI Agents SDK `Agent` invoked via
`Runner.run(...)`? pyproject.toml lists `openai-agents` as an optional
dependency, which may mean the whole pipeline runs on that SDK instead.
"""

from .schemas import BugContext, Diagnosis, PatchProposal, RepairProposal
from .prompts import (
    DIAGNOSE_SYSTEM_PROMPT,
    DIAGNOSE_USER_TEMPLATE,
    FIX_SYSTEM_PROMPT,
    FIX_USER_TEMPLATE,
    RETRY_CONTEXT_TEMPLATE,
    build_relevant_files_block,
)
from ..shared.model_client import ModelClient


class RepairAgent:
    def __init__(self, model_client: ModelClient):
        self.client = model_client

    def diagnose(self, context: BugContext) -> Diagnosis:
        user_prompt = DIAGNOSE_USER_TEMPLATE.format(
            bug_report=context.bug_report,
            failing_test_name=context.failing_test_name,
            failing_test_output=context.failing_test_output,
            stack_trace=context.stack_trace,
            relevant_files_block=build_relevant_files_block(context.relevant_files),
        )
        response = self.client.call(DIAGNOSE_SYSTEM_PROMPT, user_prompt)
        if response.parsed is None:
            raise ValueError(f"Diagnosis failed to parse: {response.parse_error}")
        return Diagnosis(**response.parsed)

    def propose_fix(
        self, context: BugContext, diagnosis: Diagnosis, iteration_number: int
    ) -> PatchProposal:
        retry_block = ""
        if context.previous_attempt_failure:
            retry_block = RETRY_CONTEXT_TEMPLATE.format(
                iteration_number=iteration_number,
                previous_attempt_failure=context.previous_attempt_failure,
            )
        user_prompt = FIX_USER_TEMPLATE.format(
            diagnosis_json=diagnosis.model_dump_json(),
            relevant_files_block=build_relevant_files_block(context.relevant_files),
            retry_context_block=retry_block,
        )
        response = self.client.call(FIX_SYSTEM_PROMPT, user_prompt)
        if response.parsed is None:
            raise ValueError(f"Fix generation failed to parse: {response.parse_error}")
        return PatchProposal(**response.parsed)

    def run(self, context: BugContext, iteration_number: int) -> RepairProposal:
        """Full diagnose -> fix cycle for one iteration. Produces a proposal only."""
        diagnosis = self.diagnose(context)
        patch = self.propose_fix(context, diagnosis, iteration_number)
        return RepairProposal(
            iteration_number=iteration_number, diagnosis=diagnosis, patch=patch
        )
