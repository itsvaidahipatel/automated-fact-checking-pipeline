"""API key authentication tests."""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from agents.manager_agent import FactCheckResult
from serve.api import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


@patch("serve.api.run_fact_check")
def test_api_key_required_when_configured(mock_run, client, monkeypatch):
    monkeypatch.setenv("API_KEY", "secret-key")
    mock_run.return_value = FactCheckResult(
        verdict="true",
        confidence=0.7,
        summary="ok",
        claims=[],
        citations=[],
        raw_output="",
    )
    response = client.post("/fact-check", json={"claim": "test claim"})
    assert response.status_code == 401

    response = client.post(
        "/fact-check",
        json={"claim": "test claim"},
        headers={"X-API-Key": "secret-key"},
    )
    assert response.status_code == 200


def test_api_key_optional_when_unset(client, monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    with patch("serve.api.run_fact_check") as mock_run:
        mock_run.return_value = FactCheckResult(
            verdict="true",
            confidence=0.7,
            summary="ok",
            claims=[],
            citations=[],
            raw_output="",
        )
        response = client.post("/fact-check", json={"claim": "Earth orbits the Sun."})
        assert response.status_code == 200
