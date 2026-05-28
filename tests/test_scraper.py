"""Tests for scraper tool with mocked HTTP."""

from unittest.mock import MagicMock, patch

from tools.scraper import scrape_url_text


@patch("tools.scraper.httpx.Client")
def test_scrape_url_text(mock_client_cls):
    mock_response = MagicMock()
    mock_response.text = "<html><body><p>Hello world fact.</p></body></html>"
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = mock_response
    mock_client_cls.return_value = mock_client

    result = scrape_url_text("https://example.com")
    assert "Hello world" in result
