# Resume copy blocks

Use these on your resume, LinkedIn, or application forms. Replace `X%` after you run the full pipeline eval on vLLM.

## Project link

https://github.com/itsvaidahipatel/automated-fact-checking-pipeline

## One-line description

Multi-agent fact-checking pipeline (FastAPI, smolagents, vLLM) that verifies claims and social URLs with structured verdicts, citations, and evaluation harness.

## Bullet accomplishments (customize metrics after eval run)

- Designed a distributed architecture separating orchestration from GPU inference (vLLM OpenAI-compatible API), reducing reliance on paid cloud LLM APIs.
- Implemented hierarchical agents (extract → claim → research) plus a social-media pipeline with citation grounding and safety refusals.
- Built an evaluation suite over 52 labeled claims with per-category accuracy and optional Ragas metrics ([docs/EVAL.md](EVAL.md)).
- Added Docker Compose, GitHub Actions CI, and pytest coverage for API, grounding, and tools.

## Skills to tag

Python · FastAPI · Multi-agent systems · smolagents · vLLM · RAG / web retrieval · LLM evaluation · Ragas · Docker · GitHub Actions · Streamlit · Langfuse / OpenTelemetry

## Interview talking points

1. **Why multi-agent?** Specialization beats a single prompt for scrape → decompose → verify steps.
2. **Hallucination control:** Citation extraction + downgrade to inconclusive when evidence is missing.
3. **Eval discipline:** Binary labeled set, end-to-end accuracy, failure analysis in EVAL.md.
4. **Cost:** Burst GPU for eval/demo; static artifacts on GitHub for recruiters.
