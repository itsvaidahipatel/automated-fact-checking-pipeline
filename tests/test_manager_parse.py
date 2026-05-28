"""Tests for manager output parsing."""

from agents.manager_agent import parse_agent_output


def test_parse_json_payload():
    raw = '{"verdict": "false", "confidence": 0.8, "summary": "Incorrect.", "claims": []}'
    result = parse_agent_output(raw, require_citations=False)
    assert result.verdict == "false"
    assert result.confidence == 0.8


def test_parse_three_section_markdown():
    raw = """### 1. Task outcome (short version):
The claim is false.

### 2. Task outcome (extremely detailed version):
The claim is not supported by evidence.

### 3. Additional context (if relevant):
"""
    result = parse_agent_output(raw, require_citations=False)
    assert result.verdict in {"false", "inconclusive", "true"}


def test_parse_json_in_detailed_section():
    raw = """### 1. Task outcome (short version):
done

### 2. Task outcome (extremely detailed version):
{"verdict": "true", "confidence": 0.7, "summary": "Supported.", "claims": []}

### 3. Additional context (if relevant):
"""
    result = parse_agent_output(raw, require_citations=False)
    assert result.verdict == "true"
    assert result.confidence == 0.7
