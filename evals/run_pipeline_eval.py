"""
End-to-end pipeline evaluation against labeled claims.

Usage:
  python evals/run_pipeline_eval.py --limit 10
  python evals/run_pipeline_eval.py --ragas-subset 15
  python evals/run_pipeline_eval.py --output evals/results/pipeline_eval_latest.json
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Project root on PYTHONPATH
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agents.manager_agent import FactCheckResult, run_fact_check
from agents.social_manager_agent import SocialFactCheckResult, run_social_fact_check
from config import get_settings
from evals.fixture_loader import DEFAULT_FIXTURE, LabeledClaim, load_labeled_claims

logger = logging.getLogger(__name__)

TRUE_VERDICTS = {"true", "supported", "mostly true"}
FALSE_VERDICTS = {"false", "refuted", "mostly false"}


def _normalize_predicted(verdict: str) -> str:
    v = verdict.lower().strip()
    if v in TRUE_VERDICTS:
        return "true"
    if v in FALSE_VERDICTS:
        return "false"
    return "inconclusive"


def _is_correct(expected: str, predicted_verdict: str) -> bool:
    pred = _normalize_predicted(predicted_verdict)
    if pred == "inconclusive":
        return False
    return pred == expected


def _run_single(item: LabeledClaim) -> tuple[FactCheckResult | SocialFactCheckResult, str]:
    if item.use_social_pipeline:
        result = run_social_fact_check(url=item.url, claim=item.claim)
        pipeline = "social"
    else:
        result = run_fact_check(url=item.url, claim=item.claim)
        pipeline = "standard"
    return result, pipeline


def _result_to_record(
    item: LabeledClaim,
    result: FactCheckResult | SocialFactCheckResult,
    pipeline: str,
    *,
    correct: bool,
    error: str | None = None,
) -> dict[str, Any]:
    citations: list[Any] = []
    if hasattr(result, "citations"):
        citations = list(getattr(result, "citations", []) or [])
    return {
        "claim": item.claim,
        "category": item.category,
        "expected": item.label,
        "predicted_verdict": result.verdict,
        "correct": correct,
        "confidence": result.confidence,
        "summary_snippet": (result.summary or "")[:200],
        "pipeline": pipeline,
        "citations_count": len(citations),
        "error": error,
    }


def evaluate_pipeline(
    claims: list[LabeledClaim],
    *,
    max_samples: int | None = None,
) -> dict[str, Any]:
    subset = claims[:max_samples] if max_samples else claims
    correct = 0
    failures: list[dict[str, Any]] = []
    by_category: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0})
    records: list[dict[str, Any]] = []

    for item in subset:
        by_category[item.category]["total"] += 1
        try:
            result, pipeline = _run_single(item)
            ok = _is_correct(item.label, result.verdict)
        except Exception as exc:
            logger.exception("Pipeline failed for claim=%r", item.claim)
            ok = False
            record = {
                "claim": item.claim,
                "category": item.category,
                "expected": item.label,
                "predicted_verdict": "error",
                "correct": False,
                "confidence": 0.0,
                "summary_snippet": "",
                "pipeline": "social" if item.use_social_pipeline else "standard",
                "citations_count": 0,
                "error": str(exc),
            }
            records.append(record)
            failures.append(record)
            continue

        if ok:
            correct += 1
            by_category[item.category]["correct"] += 1
        else:
            failures.append(
                _result_to_record(item, result, pipeline, correct=False)
            )

        records.append(_result_to_record(item, result, pipeline, correct=ok))

    total = len(subset)
    accuracy = correct / total if total else 0.0
    category_accuracy = {
        cat: (stats["correct"] / stats["total"] if stats["total"] else 0.0)
        for cat, stats in by_category.items()
    }

    settings = get_settings()
    return {
        "metadata": {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "model_id": settings.vllm_model_id,
            "vllm_base_url": settings.vllm_base_url,
            "fixture": str(DEFAULT_FIXTURE),
            "total_samples": total,
        },
        "metrics": {
            "correct": correct,
            "total": total,
            "accuracy": round(accuracy, 4),
            "by_category": category_accuracy,
        },
        "failures": failures[:25],
        "records": records,
    }


def run_ragas_subset(
    eval_report: dict[str, Any],
    *,
    subset_size: int,
) -> dict[str, Any]:
    """Run Ragas faithfulness / answer_relevancy on a subset of successful records."""
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import answer_relevancy, faithfulness
    except ImportError as exc:
        logger.warning("Ragas not available: %s", exc)
        return {"error": str(exc), "subset_size": subset_size}

    records = [
        r
        for r in eval_report.get("records", [])
        if not r.get("error") and r.get("summary_snippet")
    ][:subset_size]
    if not records:
        return {"subset_size": 0, "faithfulness": None, "answer_relevancy": None}

    rows = []
    for r in records:
        rows.append(
            {
                "question": f"Is this claim true or false? {r['claim']}",
                "answer": r["summary_snippet"],
                "contexts": [r["summary_snippet"]],
            }
        )

    dataset = Dataset.from_list(rows)
    try:
        scores = evaluate(dataset, metrics=[faithfulness, answer_relevancy])
        df = scores.to_pandas()
        return {
            "subset_size": len(rows),
            "faithfulness": float(df["faithfulness"].mean()) if "faithfulness" in df else None,
            "answer_relevancy": float(df["answer_relevancy"].mean())
            if "answer_relevancy" in df
            else None,
        }
    except Exception as exc:
        logger.exception("Ragas evaluation failed")
        return {"subset_size": len(rows), "error": str(exc)}


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="End-to-end pipeline evaluation")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evals/results/pipeline_eval_latest.json"),
    )
    parser.add_argument("--ragas-subset", type=int, default=0)
    parser.add_argument("--categories", type=str, default=None, help="Comma-separated filter")
    args = parser.parse_args()

    if not args.fixture.exists():
        raise FileNotFoundError(f"Fixture not found: {args.fixture}")

    claims = load_labeled_claims(args.fixture)
    if args.categories:
        allowed = {c.strip() for c in args.categories.split(",")}
        claims = [c for c in claims if c.category in allowed]

    report = evaluate_pipeline(claims, max_samples=args.limit)

    if args.ragas_subset > 0:
        report["ragas"] = run_ragas_subset(report, subset_size=args.ragas_subset)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    metrics = report["metrics"]
    logger.info(
        "Pipeline eval complete — accuracy=%.1f%% (%d/%d)",
        metrics["accuracy"] * 100,
        metrics["correct"],
        metrics["total"],
    )
    print(json.dumps({"metrics": metrics, "ragas": report.get("ragas")}, indent=2))


if __name__ == "__main__":
    os.environ.setdefault("ENABLE_TELEMETRY", "false")
    main()
