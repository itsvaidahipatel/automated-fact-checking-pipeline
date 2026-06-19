"""API key authentication for fact-check endpoints."""

from __future__ import annotations

import os
import secrets

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_configured_api_key() -> str | None:
    key = os.getenv("API_KEY", "").strip()
    return key or None


async def require_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    """
    Enforce X-API-Key when API_KEY is set in the environment.
    When API_KEY is unset, auth is disabled (local development).
    """
    expected = get_configured_api_key()
    if expected is None:
        return
    if not api_key or not secrets.compare_digest(api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
