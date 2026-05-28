"""Research agent specialized for social-media claims."""

from __future__ import annotations

from agents.base import build_code_agent
from agents.prompts import FINAL_ANSWER_INSTRUCTIONS
from config import Settings, get_settings
from tools.trusted_search import trusted_web_search

SOCIAL_RESEARCH_INSTRUCTIONS = r"""
You verify social-media claims with web evidence.
For each claim:
1) Generate focused search queries.
2) Use trusted_web_search with trusted domains prioritized.
3) Determine supported/refuted/inconclusive with citation URLs.
Prefer Reuters/AP/official sources when available.
""" + FINAL_ANSWER_INSTRUCTIONS


def create_social_research_agent(settings: Settings | None = None):
    cfg = settings or get_settings()
    return build_code_agent(
        settings=cfg,
        tools=[trusted_web_search],
        name="social_research_agent",
        description="Cross-references social-media claims with trusted sources.",
        instructions=SOCIAL_RESEARCH_INSTRUCTIONS,
        max_steps=cfg.agent_max_steps,
        provide_run_summary=True,
    )

