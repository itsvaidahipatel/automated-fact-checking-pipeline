"""Social extractor agent for social-media URLs."""

from __future__ import annotations

from config import Settings, get_settings

from agents.base import build_code_agent
from agents.prompts import FINAL_ANSWER_INSTRUCTIONS
from tools.social_extractor import extract_social_content

SOCIAL_EXTRACTOR_INSTRUCTIONS = r"""
You extract content from social-media URLs.
Use extract_social_content(url) and return:
- text content
- metadata (platform/channel/title if available)
- caveats if extraction quality is limited.
""" + FINAL_ANSWER_INSTRUCTIONS


def create_social_extractor_agent(settings: Settings | None = None):
    cfg = settings or get_settings()
    return build_code_agent(
        settings=cfg,
        tools=[extract_social_content],
        name="social_extractor_agent",
        description="Extracts text and metadata from social-media URLs.",
        instructions=SOCIAL_EXTRACTOR_INSTRUCTIONS,
        max_steps=cfg.agent_max_steps,
        provide_run_summary=True,
    )

