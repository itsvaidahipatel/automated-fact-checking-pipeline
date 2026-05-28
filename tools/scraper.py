"""URL scraping tool backed by BeautifulSoup."""

from __future__ import annotations

import logging

import httpx
from bs4 import BeautifulSoup
from smolagents import tool

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; FactCheckBot/1.0; +https://github.com/example/fact-check)"
    ),
}
MAX_CONTENT_CHARS = 50_000


def _extract_visible_text(soup: BeautifulSoup) -> str:
    """Strip scripts/styles and collapse whitespace from page HTML."""
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


@tool
def scrape_url_text(url: str) -> str:
    """
    Fetch a web page and return its main visible text content.

    Args:
        url: Fully qualified HTTP or HTTPS URL to scrape.
    """
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid URL scheme (expected http/https): {url}")

    try:
        with httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers=DEFAULT_HEADERS,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.exception("HTTP error while scraping %s", url)
        raise RuntimeError(f"Failed to fetch URL: {url}") from exc

    content_type = response.headers.get("content-type", "")
    if "html" not in content_type.lower():
        return response.text[:MAX_CONTENT_CHARS]

    soup = BeautifulSoup(response.text, "html.parser")
    text = _extract_visible_text(soup)
    if len(text) > MAX_CONTENT_CHARS:
        text = text[:MAX_CONTENT_CHARS] + "\n...[truncated]"
    if not text:
        raise RuntimeError(f"No extractable text found at URL: {url}")
    return text
