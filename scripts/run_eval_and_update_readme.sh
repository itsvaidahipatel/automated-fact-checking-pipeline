#!/usr/bin/env bash
# Run pipeline eval and refresh README Results section from JSON output.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=.

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

OUT="${1:-evals/results/pipeline_eval_latest.json}"
LIMIT="${EVAL_LIMIT:-20}"

echo "Running pipeline eval (limit=$LIMIT) -> $OUT"
python evals/run_pipeline_eval.py --limit "$LIMIT" --ragas-subset 10 --output "$OUT"

python3 <<'PY'
import json
import re
from pathlib import Path

report = json.loads(Path("evals/results/pipeline_eval_latest.json").read_text())
metrics = report.get("metrics")
if not metrics:
    raise SystemExit("No metrics in report — is vLLM running?")

acc = metrics["accuracy"]
total = metrics["total"]
correct = metrics["correct"]
pct = round(acc * 100, 1)
by_cat = metrics.get("by_category", {})

readme = Path("README.md").read_text()
# Update accuracy row
readme = re.sub(
    r"\| End-to-end accuracy \|[^|]+\|",
    f"| End-to-end accuracy | **{pct}%** ({correct}/{total} on Qwen2.5-3B) |",
    readme,
    count=1,
)
# Update dataset row
readme = re.sub(
    r"\| Eval dataset \|[^|]+\|",
    f"| Eval dataset | {total} labeled claims ([fixture](evals/fixtures/labeled_claims.json)) |",
    readme,
    count=1,
)
Path("README.md").write_text(readme)
print(f"Updated README: {pct}% ({correct}/{total})")
if by_cat:
    print("By category:", json.dumps(by_cat, indent=2))
PY

echo "Commit evals/results/pipeline_eval_latest.json and README.md when satisfied."
