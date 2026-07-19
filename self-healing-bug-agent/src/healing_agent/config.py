from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    openai_model: str = "gpt-5.6-sol"
    github_webhook_secret: str = ""
    github_app_id: str = ""
    github_private_key_path: Path | None = None
    github_autofix_label: str = "agent-fix"
    max_repair_iterations: int = Field(default=3, ge=1, le=10)
    workspace_root: Path = Path("workspaces")

    @model_validator(mode="after")
    def production_requires_webhook_secret(self) -> "Settings":
        if self.app_env == "production" and not self.github_webhook_secret:
            raise ValueError("GITHUB_WEBHOOK_SECRET is required in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

