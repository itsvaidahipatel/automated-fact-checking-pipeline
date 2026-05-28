"""
Hallucination / accuracy evaluation for the research agent.

Runs the research agent against a labeled claim dataset and reports accuracy.
Extend with ragas metrics once the pipeline is fully implemented.
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from agents.research_agent import create_research_agent

logger = logging.getLogger(__name__)

VerdictLabel = Literal["true", "false"]

DEFAULT_FIXTURE = Path(__file__).parent / "fixtures" / "labeled_claims.json"


@dataclass
class LabeledClaim:
    claim: str
    label: VerdictLabel
    category: str = "general"


@dataclass
class EvalMetrics:
    total: int
    correct: int
    accuracy: float
    failures: list[dict[str, str]]

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "correct": self.correct,
            "accuracy": self.accuracy,
            "failures": self.failures,
        }


def load_labeled_claims(path: Path) -> list[LabeledClaim]:
    """Load evaluation fixtures (JSON array)."""
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    return [LabeledClaim(**item) for item in raw]


def _normalize_verdict(agent_output: str) -> str:
    """Map free-form agent text to true/false/inconclusive."""
    lower = agent_output.lower()
    if any(token in lower for token in ("refuted", "false", "incorrect", "unsupported")):
        return "false"
    if any(token in lower for token in ("supported", "true", "correct", "verified")):
        return "true"
    return "inconclusive"


def evaluate_research_agent(
    claims: list[LabeledClaim],
    *,
    max_samples: int | None = None,
) -> EvalMetrics:
    """
    Run the research agent on labeled claims and compute accuracy.

    Note: This is a scaffold — verdict parsing is heuristic until structured
    outputs are enforced in research_agent instructions.
    """
    agent = create_research_agent()
    subset = claims[:max_samples] if max_samples else claims
    correct = 0
    failures: list[dict[str, str]] = []

    for item in subset:
        task = (
            f"Fact-check this claim and state whether it is supported or refuted:\n"
            f"Claim: {item.claim}"
        )
        try:
            output = str(agent.run(task))
            predicted = _normalize_verdict(output)
        except Exception as exc:
            logger.exception("Agent run failed for claim=%r", item.claim)
            failures.append({"claim": item.claim, "error": str(exc)})
            continue

        if predicted == item.label:
            correct += 1
        else:
            failures.append(
                {
                    "claim": item.claim,
                    "expected": item.label,
                    "predicted": predicted,
                    "raw_output": output[:500],
                }
            )

    total = len(subset)
    accuracy = correct / total if total else 0.0
    return EvalMetrics(total=total, correct=correct, accuracy=accuracy, failures=failures)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Research agent hallucination check")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--output", type=Path, default=Path("evals/results/hallucination_report.json"))
    args = parser.parse_args()

    if not args.fixture.exists():
        raise FileNotFoundError(
            f"Fixture not found: {args.fixture}. "
            "Create labeled_claims.json or pass --fixture."
        )

    claims = load_labeled_claims(args.fixture)
    metrics = evaluate_research_agent(claims, max_samples=args.max_samples)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(metrics.to_dict(), handle, indent=2)

    logger.info(
        "Evaluation complete — accuracy=%.2f%% (%d/%d)",
        metrics.accuracy * 100,
        metrics.correct,
        metrics.total,
    )
    print(json.dumps(metrics.to_dict(), indent=2))


if __name__ == "__main__":
    main()
