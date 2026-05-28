# Project summary

**Repository:** https://github.com/itsvaidahipatel/automated-fact-checking-pipeline  
**Author:** Vaidahi Patel

## Description

Multi-agent fact-checking pipeline built with FastAPI, smolagents, and vLLM. Verifies text claims and social-media URLs, returning structured verdicts, confidence scores, and citations.

## Accomplishments

- Designed orchestration separate from GPU inference using a vLLM OpenAI-compatible API.
- Implemented hierarchical agents (extract → claim → research) and a social-media verification path.
- Added citation grounding, safety refusals, and a 52-claim evaluation suite with optional Ragas metrics.
- Shipped Docker Compose, GitHub Actions CI, and pytest coverage for API and tools.

## Technical skills demonstrated

Python · FastAPI · Multi-agent systems · smolagents · vLLM · Web retrieval · LLM evaluation · Ragas · Docker · GitHub Actions · Streamlit · Langfuse / OpenTelemetry

## Talking points

1. **Multi-agent design** — Specialized sub-agents replace a single monolithic prompt for scrape, decompose, and verify steps.
2. **Grounding** — Citations are required for confident verdicts; missing evidence downgrades to inconclusive.
3. **Evaluation** — Labeled dataset, end-to-end accuracy, per-category breakdown, documented failure modes.
4. **Operations** — Short GPU bursts for inference and eval; static JSON artifacts document quality without always-on hosting.
