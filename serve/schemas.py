"""Shared API response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Citation(BaseModel):
    url: str
    snippet: str = ""
    source_title: str = ""


class FactCheckResponse(BaseModel):
    status: Literal["success", "error", "refused"]
    verdict: str | None = None
    confidence: float | None = None
    summary: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    message: str | None = None
    refusal_reason: str | None = None


class HealthResponse(BaseModel):
    status: str
    telemetry_enabled: bool


class RootResponse(BaseModel):
    service: str
    version: str
    docs: str
    endpoints: dict[str, str]
