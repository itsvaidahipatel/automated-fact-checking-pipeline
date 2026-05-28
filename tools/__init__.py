"""Custom smolagents tools for the fact-checking pipeline."""

from tools.scraper import scrape_url_text
from tools.search import web_search
from tools.social_extractor import extract_social_content
from tools.trusted_search import trusted_web_search

__all__ = ["scrape_url_text", "web_search", "extract_social_content", "trusted_web_search"]
