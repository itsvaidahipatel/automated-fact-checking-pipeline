"""Langfuse + OpenTelemetry instrumentation for smolagents."""

from __future__ import annotations

import logging
import os
from typing import Any

from config import Settings, get_settings

logger = logging.getLogger(__name__)

_instrumentor: Any | None = None

_PLACEHOLDER_MARKERS = ("...", "your-key", "changeme", "xxx")


def _is_placeholder_credential(value: str | None) -> bool:
    """Detect unset example keys copied from .env.example."""
    if not value:
        return True
    normalized = value.strip().lower()
    return any(marker in normalized for marker in _PLACEHOLDER_MARKERS)


def _configure_langfuse_env(settings: Settings) -> None:
    """Map project settings to Langfuse / OTEL environment variables."""
    if settings.langfuse_public_key:
        os.environ.setdefault("LANGFUSE_PUBLIC_KEY", settings.langfuse_public_key)
    if settings.langfuse_secret_key:
        os.environ.setdefault("LANGFUSE_SECRET_KEY", settings.langfuse_secret_key)
    os.environ.setdefault("LANGFUSE_HOST", settings.langfuse_host)

    # Langfuse OTLP ingestion endpoint (OpenTelemetry exporter)
    host = settings.langfuse_host.rstrip("/")
    os.environ.setdefault(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        f"{host}/api/public/otel",
    )
    os.environ.setdefault("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")


def init_langfuse_telemetry(settings: Settings | None = None) -> bool:
    """
    Initialize SmolagentsInstrumentor and verify Langfuse connectivity.

    Returns:
        True when instrumentation is active, False when skipped or unavailable.
    """
    global _instrumentor

    cfg = settings or get_settings()
    if not cfg.enable_telemetry:
        logger.info("Telemetry disabled via ENABLE_TELEMETRY.")
        return False

    if (
        not cfg.langfuse_public_key
        or not cfg.langfuse_secret_key
        or _is_placeholder_credential(cfg.langfuse_public_key)
        or _is_placeholder_credential(cfg.langfuse_secret_key)
    ):
        logger.warning(
            "Langfuse credentials missing or still placeholders; "
            "API will start without tracing. Set real LANGFUSE_* keys or "
            "ENABLE_TELEMETRY=false in .env."
        )
        return False

    _configure_langfuse_env(cfg)

    try:
        from langfuse import get_client
        from openinference.instrumentation.smolagents import SmolagentsInstrumentor
    except ImportError as exc:
        logger.warning("Telemetry dependencies not installed: %s", exc)
        return False

    try:
        langfuse = get_client()
        if hasattr(langfuse, "auth_check"):
            langfuse.auth_check()
    except Exception as exc:
        # auth_check() raises UnauthorizedError on bad keys — must not block startup
        logger.warning(
            "Langfuse auth failed (%s). Starting without telemetry. "
            "Fix LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST, "
            "or set ENABLE_TELEMETRY=false.",
            exc,
        )
        return False

    global _instrumentor
    try:
        _instrumentor = SmolagentsInstrumentor()
        _instrumentor.instrument()
    except Exception as exc:
        logger.warning("Failed to instrument smolagents: %s", exc)
        _instrumentor = None
        return False

    logger.info("SmolagentsInstrumentor active — traces exported to Langfuse.")
    return True


def shutdown_telemetry() -> None:
    """Uninstrument smolagents and flush pending spans."""
    global _instrumentor
    if _instrumentor is not None:
        try:
            _instrumentor.uninstrument()
        except Exception as exc:
            logger.warning("Error during telemetry shutdown: %s", exc)
        _instrumentor = None
