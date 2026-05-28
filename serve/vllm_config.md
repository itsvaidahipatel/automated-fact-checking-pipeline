# Local vLLM Server Configuration

This project routes all agent inference through a **local vLLM** instance exposing an OpenAI-compatible API. vLLM uses **PagedAttention** to maximize GPU throughput and reduce memory fragmentation during multi-agent workloads.

## Prerequisites

- NVIDIA GPU with sufficient VRAM (≥ 8 GB recommended for Qwen2.5-3B-Instruct)
- CUDA-compatible driver stack
- Python 3.10+

## Install vLLM

```bash
pip install vllm
```

## Launch the Server

```bash
vllm serve Qwen/Qwen2.5-3B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype auto \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --enable-prefix-caching
```

### Key Flags

| Flag | Purpose |
|------|---------|
| `--dtype auto` | Selects optimal precision (FP16/BF16) for your GPU |
| `--max-model-len` | Caps context length; tune down if you hit OOM |
| `--gpu-memory-utilization` | Fraction of GPU memory vLLM may allocate |
| `--enable-prefix-caching` | Reuses KV cache for repeated system prompts across agent steps |

## Verify the Endpoint

```bash
curl http://localhost:8000/v1/models
```

Expected: JSON listing `Qwen/Qwen2.5-3B-Instruct`.

## Application Environment Variables

```bash
export VLLM_BASE_URL="http://localhost:8000/v1"
export VLLM_API_KEY="EMPTY"
export VLLM_MODEL_ID="Qwen/Qwen2.5-3B-Instruct"
```

## Multi-GPU / Tensor Parallelism

For larger models, shard across GPUs:

```bash
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --tensor-parallel-size 2 \
  --port 8000
```

## Production Notes

- Place vLLM behind a reverse proxy with rate limiting for the FastAPI layer.
- Monitor GPU memory and p95 latency; multi-agent runs issue sequential LLM calls.
- After QLoRA fine-tuning (`finetuning/unsloth_qlora.py`), serve the merged adapter checkpoint with the same OpenAI-compatible interface.
