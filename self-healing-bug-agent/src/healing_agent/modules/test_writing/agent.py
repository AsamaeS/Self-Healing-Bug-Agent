"""
TestWritingAgent: produces a regression test proposal.

Kept as its own module rather than folded into `repair/`, matching the
backend README's list of independently pluggable contracts (workspace,
reproduction, repair, test writing, verification, PR publishing).

Same caveat as repair/agent.py: confirm the real contract signature and
whether this should be an OpenAI Agents SDK Agent instead of a plain class.
"""

from ..repair.schemas import BugContext, Diagnosis, PatchProposal
from ..shared.model_client import ModelClient
from .schemas import TestProposal
from .prompts import TEST_SYSTEM_PROMPT, TEST_USER_TEMPLATE


class TestWritingAgent:
    def __init__(self, model_client: ModelClient):
        self.client = model_client

    def propose_regression_test(
        self,
        context: BugContext,
        diagnosis: Diagnosis,
        patch: PatchProposal,
        existing_test_sample: str,
    ) -> TestProposal:
        user_prompt = TEST_USER_TEMPLATE.format(
            diagnosis_json=diagnosis.model_dump_json(),
            patch_diff=patch.diff,
            existing_test_file_sample=existing_test_sample,
            test_framework=context.test_framework,
        )
        response = self.client.call(TEST_SYSTEM_PROMPT, user_prompt)
        if response.parsed is None:
            raise ValueError(f"Test generation failed to parse: {response.parse_error}")
        return TestProposal(**response.parsed)
