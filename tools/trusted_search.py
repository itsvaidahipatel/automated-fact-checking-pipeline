"""Trusted-domain web search tool using DuckDuckGo."""

from __future__ import annotations

import re
from functools import lru_cache

from smolagents import DuckDuckGoSearchTool, tool

DEFAULT_TRUSTED = [
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "snopes.com",
    "who.int",
    "cdc.gov",
    "gov",
    "edu",
]


@lru_cache(maxsize=1)
def _ddg() -> DuckDuckGoSearchTool:
    return DuckDuckGoSearchTool(max_results=12)


def _extract_links(markdown_text: str) -> list[str]:
    # Result format from DDG tool: [title](url)\ndescription
    return re.findall(r"\[[^\]]+\]\((https?://[^)]+)\)", markdown_text)


@tool
def trusted_web_search(query: str, trusted_domains_csv: str = "") -> str:
    """
    Search the web and prioritize evidence from trusted domains.

    Args:
        query: Fact-check search query.
        trusted_domains_csv: Optional comma-separated domains to prioritize.
    """
    if not query.strip():
        raise ValueError("query must not be empty")

    raw = str(_ddg()(query))
    domains = [d.strip().lower() for d in trusted_domains_csv.split(",") if d.strip()] or DEFAULT_TRUSTED
    links = _extract_links(raw)

    trusted_links = [u for u in links if any(dom in u.lower() for dom in domains)]
    other_links = [u for u in links if u not in trusted_links]

    trusted_block = "\n".join(f"- {u}" for u in trusted_links[:8]) or "- none found"
    others_block = "\n".join(f"- {u}" for u in other_links[:8]) or "- none"

    return (
        f"## Query\n{query}\n\n"
        f"## Trusted domains used\n{', '.join(domains)}\n\n"
        f"## Trusted source URLs\n{trusted_block}\n\n"
        f"## Other URLs\n{others_block}\n\n"
        f"## Raw Search Snippets\n{raw[:12000]}"
    )

