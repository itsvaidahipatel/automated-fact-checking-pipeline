"""Research agent — cross-references claims using web search."""

from __future__ import annotations

from smolagents import DuckDuckGoSearchTool

from config import Settings, get_settings

from agents.base import build_code_agent
from agents.prompts import FINAL_ANSWER_INSTRUCTIONS

RESEARCH_INSTRUCTIONS = r"""
You fact-check individual claims using web search evidence.
For each claim: formulate a targeted search query, call the DuckDuckGo search tool, and synthesize
whether the claim is supported, refuted, or inconclusive.
Cite search snippets in your reasoning. Do not invent sources.
Never use input() — the claim is always provided in the task.

When finished, your last code block must call final_answer exactly like this
(three positional raw strings only — no keyword arguments):

final_answer(
    r"Short version here",
    r"Extremely detailed version here",
    r"Additional context here"
)
""" + FINAL_ANSWER_INSTRUCTIONS


def create_research_agent(settings: Settings | None = None):
    """Build a managed agent equipped with DuckDuckGo web search."""
    cfg = settings or get_settings()
    search_tool = DuckDuckGoSearchTool()
    return build_code_agent(
        settings=cfg,
        tools=[search_tool],
        name="research_agent",
        description="I search the web to verify claims.",
        instructions=RESEARCH_INSTRUCTIONS,
        max_steps=cfg.agent_max_steps,
        provide_run_summary=True,
    )
