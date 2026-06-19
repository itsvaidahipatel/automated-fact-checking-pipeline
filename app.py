"""Streamlit front-end for the multi-agent fact-checking API."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

import requests
import streamlit as st

BASE_API_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
API_KEY = os.getenv("API_KEY", "")
HISTORY_KEY = "run_history"


def call_fact_check_api(endpoint: str, payload: dict[str, str]) -> dict[str, Any]:
    """Call FastAPI and return JSON response."""
    url = f"{BASE_API_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=300)
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not reach API at {url}: {exc}") from exc

    try:
        data: dict[str, Any] = response.json()
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Non-JSON response from API: {response.text[:400]}") from exc

    if not response.ok:
        msg = data.get("detail") or data.get("message") or response.text
        raise RuntimeError(f"API error {response.status_code}: {msg}")
    return data


def _init_history() -> None:
    if HISTORY_KEY not in st.session_state:
        st.session_state[HISTORY_KEY] = []


def _append_history(
    *,
    mode: str,
    claim: str,
    url: str,
    endpoint: str,
    data: dict[str, Any],
) -> None:
    _init_history()
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode,
        "claim": claim[:120] if claim else "",
        "url": url[:120] if url else "",
        "endpoint": endpoint,
        "status": data.get("status", "unknown"),
        "verdict": data.get("verdict", "—"),
        "confidence": data.get("confidence"),
        "summary": (data.get("summary") or data.get("message") or "")[:300],
        "citations_count": len(data.get("citations") or []),
        "raw": data,
    }
    st.session_state[HISTORY_KEY].insert(0, entry)


def render_run_history() -> None:
    """Show session run history for demo repeatability."""
    _init_history()
    history: list[dict[str, Any]] = st.session_state[HISTORY_KEY]

    st.markdown("### Run History (This Session)")
    if not history:
        st.caption("No runs yet. Verify a claim to populate history.")
        return

    rows = [
        {
            "Time": h["timestamp"],
            "Mode": h["mode"],
            "Verdict": h["verdict"],
            "Confidence": (
                f"{float(h['confidence']):.2f}"
                if isinstance(h.get("confidence"), (int, float))
                else "N/A"
            ),
            "Claim": h["claim"] or "—",
            "Citations": h["citations_count"],
        }
        for h in history
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)

    with st.expander("Inspect a past run", expanded=False):
        labels = [
            f"{h['timestamp']} | {h['verdict']} | {(h['claim'] or h['url'] or 'input')[:40]}"
            for h in history
        ]
        idx = st.selectbox("Select run", range(len(labels)), format_func=lambda i: labels[i])
        selected = history[idx]
        st.markdown(f"**Endpoint:** `{selected['endpoint']}`")
        if selected.get("url"):
            st.markdown(f"**URL:** {selected['url']}")
        if selected.get("claim"):
            st.markdown(f"**Claim:** {selected['claim']}")
        st.markdown(f"**Summary:** {selected.get('summary', '')}")
        st.json(selected.get("raw", {}))


def render_backend_explainer(mode: str) -> None:
    """Explain what happens in the backend pipeline."""
    st.markdown("### What Happens In The Backend")
    if mode == "Standard Claims":
        st.markdown(
            "1. **Manager Agent** receives your claim/URL.\n"
            "2. **Extractor Agent** pulls source text (when URL is provided).\n"
            "3. **Claim Agent** isolates verifiable statements.\n"
            "4. **Research Agent** cross-checks with web sources.\n"
            "5. Manager synthesizes final **verdict, confidence, summary**."
        )
    else:
        st.markdown(
            "1. **Social Manager Agent** routes your input.\n"
            "2. **Social Extractor Agent** tries free extraction from social URL "
            "(YouTube via `yt-dlp`, X via `nitter` fallback, or webpage parsing).\n"
            "3. **Claim Agent** isolates checkable statements.\n"
            "4. **Social Research Agent** runs trusted-domain-first web verification.\n"
            "5. Manager returns **verdict, confidence, summary, citations**."
        )


def render_architecture_diagram(mode: str) -> None:
    """Render the pipeline architecture flow diagram."""
    st.markdown("### Architecture Flow")
    if mode == "Standard Claims":
        graph = """
        digraph G {
            rankdir=LR;
            node [shape=box, style=rounded];
            User [label="User Input\\n(Claim/URL)"];
            API [label="FastAPI\\n/fact-check"];
            Manager [label="Manager Agent"];
            Extractor [label="Extractor Agent"];
            Claim [label="Claim Agent"];
            Research [label="Research Agent"];
            Search [label="DuckDuckGo Tool"];
            VLLM [label="vLLM Inference", shape=ellipse];
            Resp [label="JSON Response\\n(verdict, confidence, summary)"];

            User -> API -> Manager;
            Manager -> Extractor;
            Manager -> Claim;
            Manager -> Research;
            Research -> Search;
            Manager -> VLLM;
            Extractor -> VLLM;
            Claim -> VLLM;
            Research -> VLLM;
            Manager -> Resp;
        }
        """
    else:
        graph = """
        digraph G {
            rankdir=LR;
            node [shape=box, style=rounded];
            User [label="User Input\\n(Claim/Social URL)"];
            API [label="FastAPI\\n/fact-check-social"];
            Manager [label="Social Manager Agent"];
            SExtract [label="Social Extractor Agent"];
            Claim [label="Claim Agent"];
            SResearch [label="Social Research Agent"];
            FreeTools [label="Free Tools\\n(yt-dlp / nitter / bs4)", shape=box];
            Trusted [label="Trusted Search Tool\\n(DuckDuckGo + domain filter)"];
            VLLM [label="vLLM Inference", shape=ellipse];
            Resp [label="JSON Response\\n(+ citations)"];

            User -> API -> Manager;
            Manager -> SExtract;
            Manager -> Claim;
            Manager -> SResearch;
            SExtract -> FreeTools;
            SResearch -> Trusted;
            Manager -> VLLM;
            SExtract -> VLLM;
            Claim -> VLLM;
            SResearch -> VLLM;
            Manager -> Resp;
        }
        """
    st.graphviz_chart(graph, use_container_width=True)


def render_run_timeline(mode: str) -> None:
    """Show execution timeline to explain backend orchestration."""
    st.markdown("### Pipeline Timeline")
    if mode == "Standard Claims":
        steps = [
            ("T+0s", "Request accepted by FastAPI"),
            ("T+1s", "Manager agent plans workflow"),
            ("T+2s", "Extractor agent reads source text"),
            ("T+4s", "Claim agent isolates factual statements"),
            ("T+6s", "Research agent verifies claims with web search"),
            ("T+9s", "Manager synthesizes verdict + confidence + summary"),
        ]
    else:
        steps = [
            ("T+0s", "Request accepted by FastAPI"),
            ("T+1s", "Social manager plans extraction + verification"),
            ("T+2s", "Social extractor parses post/video metadata"),
            ("T+4s", "Claim agent isolates verifiable claims"),
            ("T+6s", "Social research agent validates via trusted domains"),
            ("T+9s", "Manager returns verdict + citations"),
        ]
    for t, msg in steps:
        st.markdown(f"- **{t}** — {msg}")


def render_confidence_signal(confidence: Any) -> None:
    """Render visual confidence bar for quick scanning."""
    st.markdown("#### Confidence Signal")
    if not isinstance(confidence, (int, float)):
        st.info("Confidence score unavailable.")
        return
    c = max(0.0, min(1.0, float(confidence)))
    st.progress(c)
    if c >= 0.75:
        st.success("High confidence")
    elif c >= 0.5:
        st.warning("Medium confidence")
    else:
        st.error("Low confidence")


def render_result(data: dict[str, Any]) -> None:
    """Render API output with polished UI blocks."""
    if data.get("status") == "refused":
        st.warning(data.get("refusal_reason") or data.get("message", "Request refused"))
        return

    if data.get("status") == "error":
        st.error(data.get("message", "Pipeline failed"))
        return

    verdict = data.get("verdict")
    confidence = data.get("confidence")
    summary = data.get("summary") or "No summary returned."
    citations = data.get("citations") or []

    if verdict is None:
        st.warning("Verdict missing from response. Showing raw payload.")
        st.json(data)
        return

    verdict_text = str(verdict)
    verdict_lower = verdict_text.lower()

    c1, c2 = st.columns([2, 1])
    with c1:
        if verdict_lower in {"true", "supported"}:
            st.success(f"Verdict: {verdict_text}")
        elif verdict_lower in {"false", "refuted"}:
            st.error(f"Verdict: {verdict_text}")
        elif verdict_lower == "mixed":
            st.warning(f"Verdict: {verdict_text}")
        else:
            st.info(f"Verdict: {verdict_text}")
    with c2:
        if isinstance(confidence, (int, float)):
            st.metric("Confidence", f"{confidence:.2f}")
        else:
            st.metric("Confidence", "N/A")
        render_confidence_signal(confidence)

    st.markdown("#### Summary")
    st.markdown(summary)

    if citations:
        st.markdown("#### Citations")
        for idx, item in enumerate(citations, start=1):
            if isinstance(item, dict):
                url = item.get("url", "")
                snippet = item.get("snippet", "")
                title = item.get("source_title", "")
                label = title or url
                st.markdown(f"{idx}. [{label}]({url})")
                if snippet:
                    st.caption(snippet[:300])
            else:
                st.markdown(f"{idx}. [{item}]({item})")

    with st.expander("View raw API response"):
        st.json(data)


def main() -> None:
    st.set_page_config(
        page_title="Fact-Checking Pipeline | Vaidahi Patel",
        page_icon="✅",
        layout="wide",
    )

    st.title("Automated Fact-Checking Pipeline")
    st.caption("By Vaidahi Patel · FastAPI · smolagents · vLLM")

    _init_history()

    with st.sidebar:
        st.markdown("**Vaidahi Patel**")
        st.markdown("[GitHub](https://github.com/itsvaidahipatel)")
        st.markdown("---")
        st.header("Verification Mode")
        mode = st.radio("Choose pipeline", ["Standard Claims", "Social Media"], index=0)
        st.markdown("---")
        st.markdown(
            "**API Endpoints**\n"
            "- Standard: `/fact-check`\n"
            "- Social: `/fact-check-social`"
        )
        st.markdown("---")
        st.metric("Runs this session", len(st.session_state[HISTORY_KEY]))
        if st.button("Clear run history", use_container_width=True):
            st.session_state[HISTORY_KEY] = []
            st.rerun()

    left, right = st.columns([3, 2])
    with left:
        claim = st.text_area(
            "Claim",
            placeholder='e.g. "The sun rises from the west."',
            height=140,
        )
        url = st.text_input(
            "Optional Source URL",
            placeholder="https://example.com/article-or-post",
        )
        verify = st.button("Verify Claim", type="primary")

    with right:
        render_backend_explainer(mode)
        with st.expander("Show architecture diagram", expanded=True):
            render_architecture_diagram(mode)
        with st.expander("Show execution timeline", expanded=False):
            render_run_timeline(mode)

    if not verify:
        st.markdown("---")
        render_run_history()
        return

    if not claim.strip() and not url.strip():
        st.warning("Please enter either a claim, a URL, or both.")
        return

    endpoint = "/fact-check-social" if mode == "Social Media" else "/fact-check"
    payload: dict[str, str] = {}
    if claim.strip():
        payload["claim"] = claim.strip()
    if url.strip():
        payload["url"] = url.strip()

    with st.spinner("Running agentic fact-checking pipeline..."):
        try:
            data = call_fact_check_api(endpoint, payload)
        except Exception as exc:
            st.error(f"Request failed: {exc}")
            _append_history(
                mode=mode,
                claim=claim.strip(),
                url=url.strip(),
                endpoint=endpoint,
                data={"status": "error", "message": str(exc)},
            )
            st.markdown("---")
            render_run_history()
            return

    _append_history(
        mode=mode,
        claim=claim.strip(),
        url=url.strip(),
        endpoint=endpoint,
        data=data,
    )

    st.markdown("---")
    render_result(data)
    st.markdown("---")
    render_run_history()


if __name__ == "__main__":
    main()

