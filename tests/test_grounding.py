"""Tests for citation grounding."""

from agents.grounding import apply_grounding, citations_from_payload_and_raw, extract_urls


def test_extract_urls():
    text = "See https://example.com/page and http://test.org."
    urls = extract_urls(text)
    assert "https://example.com/page" in urls
    assert "http://test.org" in urls


def test_apply_grounding_downgrades_without_citations():
    verdict, confidence, summary = apply_grounding(
        verdict="true",
        confidence=0.9,
        summary="Claim is true.",
        citations=[],
        require_citations=True,
    )
    assert verdict == "inconclusive"
    assert confidence <= 0.4
    assert "Grounding" in summary


def test_apply_grounding_skipped_when_disabled():
    verdict, confidence, _ = apply_grounding(
        verdict="true",
        confidence=0.9,
        summary="Claim is true.",
        citations=[],
        require_citations=False,
    )
    assert verdict == "true"
    assert confidence == 0.9


def test_citations_from_payload():
    payload = {"citations": ["https://a.com", {"url": "https://b.com", "snippet": "quote"}]}
    cites = citations_from_payload_and_raw(payload, "extra https://c.com", [])
    urls = {c["url"] for c in cites}
    assert urls == {"https://a.com", "https://b.com", "https://c.com"}
