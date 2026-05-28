"""FastAPI application exposing the fact-checking pipeline."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from pydantic import BaseModel, Field, model_validator

from agents.manager_agent import run_fact_check
from agents.social_manager_agent import run_social_fact_check
from serve.safety import check_fact_check_request
from serve.schemas import Citation, FactCheckResponse, HealthResponse, RootResponse
from telemetry.langfuse_setup import init_langfuse_telemetry, shutdown_telemetry

logger = logging.getLogger(__name__)


class FactCheckRequest(BaseModel):
    """Inbound payload for fact-check endpoints."""

    url: str | None = Field(
        default=None,
        description="Source URL to scrape and fact-check.",
        examples=["https://example.com/article"],
    )
    claim: str | None = Field(
        default=None,
        description="Direct claim to verify (optional when url is provided).",
        examples=["The Eiffel Tower is located in Berlin."],
    )

    @model_validator(mode="after")
    def require_url_or_claim(self) -> "FactCheckRequest":
        if not self.url and not self.claim:
            raise ValueError("At least one of 'url' or 'claim' must be provided.")
        return self


def _to_citation_models(citations: list[dict[str, str]]) -> list[Citation]:
    return [
        Citation(
            url=c["url"],
            snippet=c.get("snippet", ""),
            source_title=c.get("source_title", ""),
        )
        for c in citations
        if c.get("url")
    ]


def _refused(reason: str) -> FactCheckResponse:
    return FactCheckResponse(
        status="refused",
        message=reason,
        refusal_reason=reason,
    )


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize observability on startup and flush on shutdown."""
    telemetry_active = init_langfuse_telemetry()
    app.state.telemetry_enabled = telemetry_active
    logger.info("API startup complete (telemetry=%s)", telemetry_active)
    yield
    shutdown_telemetry()
    logger.info("API shutdown complete.")


def create_app() -> FastAPI:
    """Application factory for tests and ASGI servers."""
    application = FastAPI(
        title="Enterprise Fact-Checking API",
        description="Multi-agent automated fact-checking powered by smolagents + vLLM.",
        version="0.2.0",
        lifespan=lifespan,
    )

    @application.get("/", response_model=RootResponse)
    async def root() -> RootResponse:
        return RootResponse(
            service="Enterprise Fact-Checking API",
            version="0.2.0",
            docs="/docs",
            endpoints={
                "health": "GET /health",
                "fact_check": "POST /fact-check",
                "fact_check_social": "POST /fact-check-social",
            },
        )

    @application.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            telemetry_enabled=getattr(application.state, "telemetry_enabled", False),
        )

    @application.post("/fact-check", response_model=FactCheckResponse)
    async def fact_check(body: FactCheckRequest) -> FactCheckResponse:
        safety = check_fact_check_request(body.claim, body.url)
        if not safety.allowed:
            return _refused(safety.reason or "Request refused.")

        try:
            result = run_fact_check(url=body.url, claim=body.claim)
        except Exception as exc:
            logger.exception("Fact-check pipeline failed")
            return FactCheckResponse(status="error", message=str(exc))

        return FactCheckResponse(
            status="success",
            verdict=result.verdict,
            confidence=result.confidence,
            summary=result.summary,
            citations=_to_citation_models(result.citations),
        )

    @application.post("/fact-check-social", response_model=FactCheckResponse)
    async def fact_check_social(body: FactCheckRequest) -> FactCheckResponse:
        safety = check_fact_check_request(body.claim, body.url)
        if not safety.allowed:
            return _refused(safety.reason or "Request refused.")

        try:
            result = run_social_fact_check(url=body.url, claim=body.claim)
        except Exception as exc:
            logger.exception("Social fact-check pipeline failed")
            return FactCheckResponse(status="error", message=str(exc))

        return FactCheckResponse(
            status="success",
            verdict=result.verdict,
            confidence=result.confidence,
            summary=result.summary,
            citations=_to_citation_models(result.citations),
        )

    return application


app = create_app()
