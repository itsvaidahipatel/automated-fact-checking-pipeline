#!/usr/bin/env bash
# Verify showcase stack: vLLM (optional), Railway API, env vars.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

API_URL="${API_BASE_URL:-http://localhost:8080}"
VLLM_URL="${VLLM_BASE_URL:-http://localhost:8000/v1}"

echo "=== API health ($API_URL) ==="
curl -sf "${API_URL%/}/health" | python3 -m json.tool || echo "API unreachable"

echo ""
echo "=== vLLM models ($VLLM_URL) ==="
curl -sf "${VLLM_URL%/v1}/v1/models" 2>/dev/null | python3 -m json.tool | head -20 \
  || curl -sf "${VLLM_URL%/}/models" 2>/dev/null | python3 -m json.tool | head -20 \
  || echo "vLLM unreachable (start GPU host first)"

echo ""
echo "=== Sample fact-check (requires API_KEY if set) ==="
HDR=(-H "Content-Type: application/json")
if [ -n "${API_KEY:-}" ]; then
  HDR+=(-H "X-API-Key: $API_KEY")
fi
curl -sf -X POST "${API_URL%/}/fact-check" \
  "${HDR[@]}" \
  -d '{"claim":"Water boils at 100 degrees Celsius at sea level."}' \
  | python3 -m json.tool || echo "Fact-check failed"

echo ""
echo "Done."
