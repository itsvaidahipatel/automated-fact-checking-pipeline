"""Tests for evaluation fixtures."""

from pathlib import Path

from evals.fixture_loader import load_labeled_claims


def test_labeled_claims_count():
    claims = load_labeled_claims(
        Path("evals/fixtures/labeled_claims.json")
    )
    assert len(claims) >= 50


def test_social_url_category():
    claims = load_labeled_claims(
        Path("evals/fixtures/labeled_claims.json")
    )
    social = [c for c in claims if c.use_social_pipeline]
    assert len(social) >= 1
