"""
Shared model client for the repair and test-writing modules.

If the orchestrator already defines a shared settings object elsewhere in
this repo, prefer importing that instead of this standalone settings class
-- this exists so the two modules below aren't blocked waiting for one.
"""

import json
from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from openai import OpenAI


class RepairModuleSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-5.6-sol"      # matches .env.example -- confirm exact string with team
    max_repair_iterations: int = 3          # matches .env.example MAX_REPAIR_ITERATIONS


class ModelResponse(BaseModel):
    raw_text: str
    parsed: Optional[dict] = None
    parse_error: Optional[str] = None


class ModelClient:
    """
    Thin wrapper for structured JSON calls to the model. Used by both
    RepairAgent (diagnose/fix) and TestWritingAgent (regression test).
    Retries on malformed JSON, since that's the most common failure mode
    when relying on strict structured output.
    """

    def __init__(self, settings: Optional[RepairModuleSettings] = None):
        self.settings = settings or RepairModuleSettings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)

    def call(self, system_prompt: str, user_prompt: str, max_retries: int = 2) -> ModelResponse:
        last_error = None
        raw_text = ""
        for _ in range(max_retries + 1):
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            raw_text = response.choices[0].message.content

            try:
                parsed = self._extract_json(raw_text)
                return ModelResponse(raw_text=raw_text, parsed=parsed)
            except (json.JSONDecodeError, ValueError) as e:
                last_error = str(e)
                user_prompt = (
                    f"{user_prompt}\n\nYour previous response could not be parsed "
                    f"as valid JSON ({last_error}). Respond with ONLY the JSON "
                    f"object, no markdown fences, no extra text."
                )

        return ModelResponse(raw_text=raw_text, parsed=None, parse_error=last_error)

    @staticmethod
    def _extract_json(text: str) -> dict:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned.strip())
