"""Web search tool integrating DuckDuckGo via smolagents' WebSearchTool."""

from __future__ import annotations

import logging
from functools import lru_cache

from smolagents import WebSearchTool, tool

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_duckduckgo_search_tool() -> WebSearchTool:
    """Lazy singleton for the underlying DuckDuckGo-backed search tool."""
    return WebSearchTool()


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo and return summarized results for fact-checking.

    Args:
        query: Natural-language search query derived from the claim under review.
        max_results: Maximum number of search snippets to include in the response.
    """
    if not query.strip():
        raise ValueError("Search query must not be empty.")
    if max_results < 1 or max_results > 10:
        raise ValueError("max_results must be between 1 and 10.")

    try:
        raw = _get_duckduckgo_search_tool()(query)
    except Exception as exc:
        logger.exception("DuckDuckGo search failed for query=%r", query)
        raise RuntimeError(f"Web search failed for query: {query}") from exc

    if isinstance(raw, list):
        snippets = raw[:max_results]
        return "\n\n".join(str(item) for item in snippets)
    return str(raw)[:8_000]
