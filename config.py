"""Shared runtime configuration for the fact-checking pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    """Environment-driven settings with sensible local defaults."""

    vllm_base_url: str = "http://localhost:8000/v1"
    vllm_api_key: str = "EMPTY"
    vllm_model_id: str = "Qwen/Qwen2.5-3B-Instruct"
    agent_max_steps: int = 12
    request_timeout_seconds: float = 120.0
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"
    enable_telemetry: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once per process."""
    return Settings(
        vllm_base_url=os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1"),
        vllm_api_key=os.getenv("VLLM_API_KEY", "EMPTY"),
        vllm_model_id=os.getenv("VLLM_MODEL_ID", "Qwen/Qwen2.5-3B-Instruct"),
        agent_max_steps=int(os.getenv("AGENT_MAX_STEPS", "12")),
        request_timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "120")),
        langfuse_public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        langfuse_secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        langfuse_host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        enable_telemetry=os.getenv("ENABLE_TELEMETRY", "true").lower() in {"1", "true", "yes"},
    )
