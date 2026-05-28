# Evaluation methodology

## Dataset

- **Fixture:** [`evals/fixtures/labeled_claims.json`](../evals/fixtures/labeled_claims.json)
- **Size:** 52 labeled claims
- **Categories:** `science`, `geography`, `health`, `history`, `technology`, `social_url`
- **Labels:** `true` or `false` (binary ground truth)

Claims with `category: social_url` or an optional `url` field are evaluated via the social pipeline (`run_social_fact_check`). All others use the standard manager pipeline (`run_fact_check`).

## Metrics

| Metric | Definition |
|--------|------------|
| **End-to-end accuracy** | Fraction of samples where predicted verdict (normalized to true/false) matches the label. `inconclusive` counts as incorrect. |
| **Per-category accuracy** | Accuracy broken down by fixture `category`. |
| **Ragas (subset)** | Optional `faithfulness` and `answer_relevancy` on the first N successful runs (default 15). |

## How to run

Requires a running **vLLM** instance and `.env` with `VLLM_BASE_URL` set.

```bash
export PYTHONPATH=.
set -a && source .env && set +a

# Quick smoke test (10 claims)
python evals/run_pipeline_eval.py --limit 10

# Full suite (~2–3 hours on GPU depending on model latency)
python evals/run_pipeline_eval.py --ragas-subset 15 \
  --output evals/results/pipeline_eval_latest.json
```

Research-agent-only baseline (faster, narrower):

```bash
python evals/hallucination_check.py --max-samples 20
```

## Latest results

Results are stored in [`evals/results/pipeline_eval_latest.json`](../evals/results/pipeline_eval_latest.json).

After a full GPU run, update the README **Results** section with the committed `metrics.accuracy` and `ragas` values.

## Failure analysis (template)

Document 3 representative failures from `failures` in the JSON report:

1. **False negative (labeled true, predicted false)** — Often weak retrieval or ambiguous wording.
2. **False positive (labeled false, predicted true)** — Model may rely on priors without URL evidence; grounding should downgrade when citations are empty.
3. **Social URL sample** — Extraction or rate limits on external platforms.

## Cost note

Run eval during a short GPU burst (start instance → vLLM → eval → stop). Do not leave GPU running for portfolio hosting; commit the JSON artifact instead.
