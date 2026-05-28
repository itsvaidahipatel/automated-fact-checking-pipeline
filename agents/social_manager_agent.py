"""Manager for social-media fact-checking workflow."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from config import Settings, get_settings

from agents.base import build_code_agent
from agents.claim_agent import create_claim_agent
from agents.prompts import FINAL_ANSWER_INSTRUCTIONS
from agents.social_extractor_agent import create_social_extractor_agent
from agents.social_research_agent import create_social_research_agent

SOCIAL_MANAGER_INSTRUCTIONS = r"""
You orchestrate a social-media fact-checking workflow.

Steps:
1) If URL is provided, call social_extractor_agent.
2) Run claim_agent to isolate verifiable claims from extracted text.
3) For each claim, call social_research_agent to gather evidence/citations.
4) Return a JSON object with:
   - verdict: true|false|mixed|inconclusive
   - confidence: 0.0..1.0
   - summary: concise explanation
   - citations: list of URLs
   - claims: list of per-claim findings
""" + FINAL_ANSWER_INSTRUCTIONS


@dataclass
class SocialFactCheckResult:
    verdict: str
    confidence: float
    summary: str
    claims: list[dict[str, Any]]
    citations: list[str]
    raw_output: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "confidence": self.confidence,
            "summary": self.summary,
            "claims": self.claims,
            "citations": self.citations,
            "raw_output": self.raw_output,
        }


def create_social_manager_agent(settings: Settings | None = None):
    cfg = settings or get_settings()
    managed = [
        create_social_extractor_agent(cfg),
        create_claim_agent(cfg),
        create_social_research_agent(cfg),
    ]
    return build_code_agent(
        settings=cfg,
        tools=[],
        managed_agents=managed,
        name="social_fact_check_manager",
        description="Orchestrates social-media extraction, claim isolation, and verification.",
        instructions=SOCIAL_MANAGER_INSTRUCTIONS,
        max_steps=cfg.agent_max_steps * 2,
    )


def _build_task(url: str | None, claim: str | None) -> str:
    parts = ["Fact-check this social-media content and return structured JSON."]
    if url:
        parts.append(f"Social URL: {url}")
    if claim:
        parts.append(f"Direct social claim: {claim}")
    if not url and not claim:
        raise ValueError("At least one of 'url' or 'claim' is required.")
    return "\n".join(parts)


def _parse_output(raw: str) -> SocialFactCheckResult:
    default = SocialFactCheckResult(
        verdict="inconclusive",
        confidence=0.35,
        summary=raw[:500] if raw else "No output produced.",
        claims=[],
        citations=[],
        raw_output=raw,
    )
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end <= start:
            return default
        payload = json.loads(raw[start:end])
        return SocialFactCheckResult(
            verdict=str(payload.get("verdict", "inconclusive")),
            confidence=float(payload.get("confidence", 0.35)),
            summary=str(payload.get("summary", "")),
            claims=list(payload.get("claims", [])),
            citations=list(payload.get("citations", [])),
            raw_output=raw,
        )
    except Exception:
        return default


def run_social_fact_check(
    url: str | None = None,
    claim: str | None = None,
    *,
    settings: Settings | None = None,
) -> SocialFactCheckResult:
    task = _build_task(url, claim)
    manager = create_social_manager_agent(settings)
    raw = manager.run(task)
    return _parse_output(str(raw))

