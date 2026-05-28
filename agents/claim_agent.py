"""Claim agent — isolates verifiable statements from raw text."""

from __future__ import annotations

from config import Settings, get_settings

from agents.base import build_code_agent
from agents.prompts import FINAL_ANSWER_INSTRUCTIONS

CLAIM_INSTRUCTIONS = r"""
You extract atomic, verifiable factual claims from provided text.
Return a JSON-serializable list of claim strings — one distinct fact per item.
Exclude opinions, predictions, rhetorical questions, and vague statements.
Each claim must be self-contained and checkable against external sources.

Example completion:
final_answer(
    r"Extracted 3 verifiable claims.",
    r'["claim one", "claim two", "claim three"]',
    r"",
)
""" + FINAL_ANSWER_INSTRUCTIONS


def create_claim_agent(settings: Settings | None = None):
    """Build a managed agent that extracts checkable claims from text."""
    cfg = settings or get_settings()
    return build_code_agent(
        settings=cfg,
        tools=[],
        name="claim_agent",
        description="I extract verifiable factual claims from text.",
        instructions=CLAIM_INSTRUCTIONS,
        max_steps=cfg.agent_max_steps,
        provide_run_summary=True,
    )
