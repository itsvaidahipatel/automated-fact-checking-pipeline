"""Citation extraction and grounding rules for fact-check outputs."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

_URL_PATTERN = re.compile(r"https?://[^\s\]\)\"'<>]+", re.IGNORECASE)


def extract_urls(text: str) -> list[str]:
    if not text:
        return []
    seen: set[str] = set()
    urls: list[str] = []
    for match in _URL_PATTERN.findall(text):
        url = match.rstrip(".,;)")
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def normalize_citations(raw: Any) -> list[dict[str, str]]:
    """Normalize citations from strings or dicts into a stable shape."""
    if not raw:
        return []

    out: list[dict[str, str]] = []
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, list):
        return out

    for item in raw:
        if isinstance(item, str):
            url = item.strip()
            if url.startswith("http"):
                out.append({"url": url, "snippet": "", "source_title": ""})
        elif isinstance(item, dict):
            url = str(item.get("url", "")).strip()
            if url.startswith("http"):
                out.append(
                    {
                        "url": url,
                        "snippet": str(item.get("snippet", ""))[:500],
                        "source_title": str(item.get("source_title", ""))[:200],
                    }
                )
    return out


def citations_from_payload_and_raw(
    payload: dict[str, Any] | None,
    raw_output: str,
    claims: list[dict[str, Any]] | None = None,
) -> list[dict[str, str]]:
    citations: list[dict[str, str]] = []
    if payload:
        citations.extend(normalize_citations(payload.get("citations")))
    citations.extend(
        {"url": u, "snippet": "", "source_title": ""} for u in extract_urls(raw_output)
    )
    if claims:
        for claim_row in claims:
            if isinstance(claim_row, dict):
                citations.extend(normalize_citations(claim_row.get("citations")))
                for u in extract_urls(str(claim_row.get("evidence", ""))):
                    citations.append({"url": u, "snippet": "", "source_title": ""})

    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for c in citations:
        url = c["url"]
        if url not in seen:
            seen.add(url)
            deduped.append(c)
    return deduped


def apply_grounding(
    *,
    verdict: str,
    confidence: float,
    summary: str,
    citations: list[dict[str, str]],
    require_citations: bool,
) -> tuple[str, float, str]:
    """
    Downgrade overconfident verdicts when evidence links are missing.
    """
    v = verdict.lower().strip()
    if not require_citations:
        return verdict, confidence, summary

    has_evidence = len(citations) > 0
    if v in {"true", "false", "mixed", "supported", "refuted"} and not has_evidence:
        new_summary = (
            summary
            + "\n\n[Grounding] Verdict downgraded to inconclusive: no citations found."
        ).strip()
        return "inconclusive", min(confidence, 0.4), new_summary
    return verdict, confidence, summary


def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False
