"""Manager agent — orchestrates the multi-agent fact-checking pipeline."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

from config import Settings, get_settings

from agents.base import build_code_agent
from agents.claim_agent import create_claim_agent
from agents.extractor_agent import create_extractor_agent
from agents.prompts import FINAL_ANSWER_INSTRUCTIONS
from agents.research_agent import create_research_agent

logger = logging.getLogger(__name__)

MANAGER_INSTRUCTIONS = r"""
You orchestrate the full fact-checking pipeline for URLs and/or direct claims.

Workflow:
1. If a URL is provided, delegate to extractor_agent to obtain raw text.
2. Delegate to claim_agent to extract verifiable claims from the text.
3. For each claim (or a user-supplied claim), delegate to research_agent.
4. Synthesize a structured JSON verdict with keys:
   - verdict: "true" | "false" | "mixed" | "inconclusive"
   - confidence: float between 0.0 and 1.0
   - claims: list of per-claim results
   - summary: short human-readable explanation

Use managed agents by name. Do not skip the research step for any claim.
Prefer concise, structured outputs.

Example completion (put JSON in the second argument):
final_answer(
    r"mixed",
    r'{"verdict":"mixed","confidence":0.72,"claims":[],"summary":"..."}',
    r"",
)
""" + FINAL_ANSWER_INSTRUCTIONS


@dataclass
class FactCheckResult:
    """Normalized API response for a fact-check run."""

    verdict: str
    confidence: float
    summary: str
    claims: list[dict[str, Any]]
    raw_output: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "confidence": self.confidence,
            "summary": self.summary,
            "claims": self.claims,
            "raw_output": self.raw_output,
        }


def create_manager_agent(settings: Settings | None = None):
    """Compose sub-agents and return the top-level orchestrator."""
    cfg = settings or get_settings()
    managed = [
        create_extractor_agent(cfg),
        create_claim_agent(cfg),
        create_research_agent(cfg),
    ]
    return build_code_agent(
        settings=cfg,
        tools=[],
        managed_agents=managed,
        name="fact_check_manager",
        description="I orchestrate extraction, claim isolation, and web verification.",
        instructions=MANAGER_INSTRUCTIONS,
        max_steps=cfg.agent_max_steps * 2,
    )


def _build_task(url: str | None, claim: str | None) -> str:
    parts: list[str] = ["Fact-check the following input and return structured JSON."]
    if url:
        parts.append(f"URL: {url}")
    if claim:
        parts.append(f"Direct claim: {claim}")
    if not url and not claim:
        raise ValueError("At least one of 'url' or 'claim' must be provided.")
    return "\n".join(parts)


def _parse_agent_output(raw: str) -> FactCheckResult:
    """Best-effort parse of manager output; falls back to safe defaults.

    The manager is instructed to return JSON, but it may also return the
    three-section markdown produced by our custom `final_answer` tool.
    """
    default = FactCheckResult(
        verdict="inconclusive",
        confidence=0.0,
        summary=raw[:500] if raw else "No output produced.",
        claims=[],
        raw_output=raw,
    )

    def _infer_verdict(text: str) -> str:
        t = text.lower()
        if any(k in t for k in ("mixed", "partly", "partially")):
            return "mixed"
        if any(k in t for k in ("refuted", "false", "incorrect", "not true", "does not", "isn't true")):
            return "false"
        if any(k in t for k in ("supported", "true", "correct", "verified")):
            return "true"
        return "inconclusive"

    def _infer_confidence(verdict: str) -> float:
        return {
            "true": 0.65,
            "false": 0.65,
            "mixed": 0.55,
            "inconclusive": 0.35,
        }.get(verdict, 0.35)

    def _parse_three_section_markdown(text: str) -> tuple[str, str, str] | None:
        t = text.strip()
        # Output format comes from FactCheckFinalAnswerTool.forward()
        h1 = "### 1. Task outcome (short version):"
        h2 = "### 2. Task outcome (extremely detailed version):"
        h3 = "### 3. Additional context (if relevant):"

        i1 = t.find(h1)
        i2 = t.find(h2)
        i3 = t.find(h3)
        if i1 == -1 or i2 == -1 or i3 == -1:
            # tolerate headings without the dot after the number
            h1 = "### 1 Task outcome (short version):"
            h2 = "### 2 Task outcome (extremely detailed version):"
            h3 = "### 3 Additional context (if relevant):"
            i1 = t.find(h1)
            i2 = t.find(h2)
            i3 = t.find(h3)
            if i1 == -1 or i2 == -1 or i3 == -1:
                return None

        short = t[i1 + len(h1) : i2].strip()
        detailed = t[i2 + len(h2) : i3].strip()
        ctx = t[i3 + len(h3) :].strip()
        return short, detailed, ctx
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end <= start:
            sections = _parse_three_section_markdown(raw)
            if not sections:
                return default

            short, detailed, ctx = sections

            # If the detailed section is JSON, parse it and return structured fields.
            try:
                if detailed.startswith("{") and detailed.endswith("}"):
                    payload = json.loads(detailed)
                    return FactCheckResult(
                        verdict=str(payload.get("verdict", "inconclusive")),
                        confidence=float(payload.get("confidence", 0.0)),
                        summary=str(payload.get("summary", short)),
                        claims=list(payload.get("claims", [])),
                        raw_output=raw,
                    )
            except Exception:
                pass

            verdict = _infer_verdict(short + "\n" + detailed)
            confidence = _infer_confidence(verdict)
            summary = short or detailed[:500] or default.summary
            if ctx:
                summary = summary + "\n\n" + ctx

            return FactCheckResult(
                verdict=verdict,
                confidence=confidence,
                summary=summary,
                claims=[],
                raw_output=raw,
            )
        payload = json.loads(raw[start:end])
        return FactCheckResult(
            verdict=str(payload.get("verdict", "inconclusive")),
            confidence=float(payload.get("confidence", 0.0)),
            summary=str(payload.get("summary", "")),
            claims=list(payload.get("claims", [])),
            raw_output=raw,
        )
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.warning("Could not parse manager JSON output: %s", exc)
        return default


def run_fact_check(
    url: str | None = None,
    claim: str | None = None,
    *,
    settings: Settings | None = None,
) -> FactCheckResult:
    """
    Execute the full fact-checking pipeline.

    Args:
        url: Optional source URL to scrape and analyze.
        claim: Optional direct claim to verify (skips extraction when alone).
        settings: Optional runtime overrides.
    """
    task = _build_task(url, claim)
    manager = create_manager_agent(settings)
    logger.info("Starting fact-check run (url=%s, claim=%s)", url, claim)
    raw = manager.run(task)
    return _parse_agent_output(str(raw))
