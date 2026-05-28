"""Extractor agent — fetches and returns raw text from a URL."""

from __future__ import annotations

from config import Settings, get_settings
from tools.scraper import scrape_url_text

from agents.base import build_code_agent
from agents.prompts import FINAL_ANSWER_INSTRUCTIONS

EXTRACTOR_INSTRUCTIONS = r"""
You extract webpage text for fact-checking.
Given a URL, call scrape_url_text and return the full raw text body.
Do not summarize or interpret.

Example completion:
final_answer(
    r"Extracted raw text from the URL.",
    r"Paste full scraped text here.",
    r"",
)
""" + FINAL_ANSWER_INSTRUCTIONS


def create_extractor_agent(settings: Settings | None = None):
    """Build a managed agent specialized in URL text extraction."""
    cfg = settings or get_settings()
    return build_code_agent(
        settings=cfg,
        tools=[scrape_url_text],
        name="extractor_agent",
        description="I fetch and return raw webpage text from a URL.",
        instructions=EXTRACTOR_INSTRUCTIONS,
        max_steps=cfg.agent_max_steps,
        provide_run_summary=True,
    )
