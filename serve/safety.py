"""Lightweight request safety and refusal checks (no external APIs)."""

from __future__ import annotations

import re
from dataclasses import dataclass

_INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.I),
    re.compile(r"disregard\s+(the\s+)?(system|above)\s+prompt", re.I),
    re.compile(r"you\s+are\s+now\s+(in\s+)?(developer|admin)\s+mode", re.I),
)

_MEDICAL_DIAGNOSIS = re.compile(
    r"\b(diagnose|prescription|dosage|take\s+\d+\s*mg|cure\s+cancer)\b",
    re.I,
)


@dataclass
class SafetyResult:
    allowed: bool
    reason: str | None = None


def check_fact_check_request(claim: str | None, url: str | None) -> SafetyResult:
    claim_text = (claim or "").strip()
    url_text = (url or "").strip()

    if not claim_text and not url_text:
        return SafetyResult(allowed=False, reason="At least one of claim or URL is required.")

    combined = f"{claim_text}\n{url_text}"
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(combined):
            return SafetyResult(
                allowed=False,
                reason="Request rejected: potential prompt-injection pattern detected.",
            )

    if claim_text and _MEDICAL_DIAGNOSIS.search(claim_text):
        return SafetyResult(
            allowed=False,
            reason=(
                "Request refused: medical diagnosis or treatment claims require "
                "professional review; this pipeline does not provide medical advice."
            ),
        )

    if len(claim_text) > 4000:
        return SafetyResult(allowed=False, reason="Claim text exceeds maximum length (4000).")

    return SafetyResult(allowed=True)
