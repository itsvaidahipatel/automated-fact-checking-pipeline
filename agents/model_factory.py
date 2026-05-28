"""LLM backend factory — routes inference to a local vLLM OpenAI-compatible server."""

from __future__ import annotations

from smolagents import OpenAIModel

from config import Settings, get_settings


def create_vllm_model(settings: Settings | None = None) -> OpenAIModel:
    """
    Instantiate an OpenAI-compatible client pointed at the local vLLM server.

    Model ID is read from ``VLLM_MODEL_ID`` (see ``config.get_settings()``).
    All agents, including the manager, use this factory — do not hardcode model names here.
    """
    cfg = settings or get_settings()
    return OpenAIModel(
        model_id=cfg.vllm_model_id,
        api_base=cfg.vllm_base_url,
        api_key=cfg.vllm_api_key,
        timeout=cfg.request_timeout_seconds,
    )
