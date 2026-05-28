"""Free-tool social content extraction helpers."""

from __future__ import annotations

import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from smolagents import tool

MAX_CHARS = 40_000
UA = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    )
}


def _clip(text: str, n: int = MAX_CHARS) -> str:
    t = text.strip()
    if len(t) <= n:
        return t
    return t[:n] + "\n...[truncated]"


def _extract_visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)


def _fetch(url: str) -> str:
    with httpx.Client(timeout=30.0, follow_redirects=True, headers=UA) as client:
        res = client.get(url)
        res.raise_for_status()
        return res.text


@tool
def extract_social_content(url: str) -> str:
    """
    Extract text + metadata from social media or web URLs using free tooling.

    Args:
        url: Social media post URL (X/Twitter, YouTube, generic webpage).
    """
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")

    host = (urlparse(url).hostname or "").lower()

    # YouTube: try free yt-dlp metadata (no API key).
    if "youtube.com" in host or "youtu.be" in host:
        try:
            import yt_dlp  # type: ignore

            opts = {"quiet": True, "skip_download": True, "writesubtitles": False}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            title = info.get("title", "")
            channel = info.get("uploader", "")
            description = info.get("description", "")
            out = (
                f"[platform] youtube\n"
                f"[title] {title}\n"
                f"[channel] {channel}\n"
                f"[description]\n{description}"
            )
            return _clip(out)
        except Exception as exc:
            return _clip(f"[platform] youtube\n[warning] yt-dlp extraction failed: {exc}\n[url] {url}")

    # X/Twitter: nitter mirror fallback for free extraction.
    if "twitter.com" in host or "x.com" in host:
        nitter_url = re.sub(r"https?://(www\.)?(x|twitter)\.com", "https://nitter.net", url)
        try:
            html = _fetch(nitter_url)
            text = _extract_visible_text(html)
            return _clip(f"[platform] x\n[source] nitter\n[url] {nitter_url}\n\n{text}")
        except Exception:
            # fallback to original URL (often blocked, but still worth trying)
            html = _fetch(url)
            text = _extract_visible_text(html)
            return _clip(f"[platform] x\n[source] original\n[url] {url}\n\n{text}")

    # Generic webpage fallback.
    html = _fetch(url)
    text = _extract_visible_text(html)
    return _clip(f"[platform] web\n[url] {url}\n\n{text}")

