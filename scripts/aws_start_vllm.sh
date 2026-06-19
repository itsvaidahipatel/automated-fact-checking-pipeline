#!/usr/bin/env bash
# Run on AWS GPU instance (Ubuntu + NVIDIA) after SSH.
# Usage: bash scripts/aws_start_vllm.sh
set -euo pipefail

MODEL="${VLLM_MODEL_ID:-Qwen/Qwen2.5-3B-Instruct}"
PORT="${VLLM_PORT:-8000}"

echo "Starting vLLM: $MODEL on 0.0.0.0:$PORT"
echo "Ensure security group allows inbound TCP $PORT from your Railway egress IP."

export HF_TOKEN="${HF_TOKEN:-}"
if [ -z "$HF_TOKEN" ]; then
  echo "Warning: HF_TOKEN not set (needed for some gated models)."
fi

vllm serve "$MODEL" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --max-model-len 8192
