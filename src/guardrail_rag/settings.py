"""Environment-backed application settings."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Environment-backed application configuration."""
    environment: str = "development"
    database_url: str = "sqlite:///./guardrail-rag.sqlite3"
    provider: str = "fake"

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings from environment variables and defaults."""
        return cls(
            environment=os.getenv("GUARDRAIL_RAG_ENV", cls.environment),
            database_url=os.getenv("GUARDRAIL_RAG_DATABASE_URL", cls.database_url),
            provider=os.getenv("GUARDRAIL_RAG_PROVIDER", cls.provider),
        )
