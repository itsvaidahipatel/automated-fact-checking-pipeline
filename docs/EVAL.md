# Evaluation methodology

## Dataset

- **Fixture:** [`evals/fixtures/labeled_claims.json`](../evals/fixtures/labeled_claims.json)
- **Size:** 52 labeled claims
- **Categories:** `science`, `geography`, `health`, `history`, `technology`, `social_url`
- **Labels:** `true` or `false`

Claims with `category: social_url` or an optional `url` field use the social pipeline (`run_social_fact_check`). All others use the standard pipeline (`run_fact_check`).

## Metrics

| Metric | Definition |
|--------|------------|
| **End-to-end accuracy** | Predicted verdict (true/false) matches label; `inconclusive` counts as incorrect. |
| **Per-category accuracy** | Accuracy by fixture `category`. |
| **Ragas (subset)** | Optional `faithfulness` and `answer_relevancy` on the first N successful runs. |

## How to run

Requires vLLM and `VLLM_BASE_URL` in `.env`.

```bash
export PYTHONPATH=.
set -a && source .env && set +a

python evals/run_pipeline_eval.py --limit 10
python evals/run_pipeline_eval.py --ragas-subset 15 \
  --output evals/results/pipeline_eval_latest.json
```

Research-agent baseline (narrower, faster):

```bash
python evals/hallucination_check.py --max-samples 20
```

## Results artifact

[`evals/results/pipeline_eval_latest.json`](../evals/results/pipeline_eval_latest.json) stores the latest run. Update the README **Results** table after a full eval.

## Failure analysis

When documenting a run, include three examples from the `failures` array:

1. **False negative** — Weak retrieval or ambiguous claim wording.
2. **False positive** — Model affirms without URL evidence; grounding should downgrade.
3. **Social URL** — Extraction or external platform limits.

## GPU usage

Run the full suite during a bounded GPU session (start vLLM → eval → stop). Commit the JSON output; hosting inference 24/7 is not required to reproduce reported metrics.
