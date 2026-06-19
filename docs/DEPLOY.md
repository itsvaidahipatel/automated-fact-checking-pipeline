# Deployment

This project has two deployable tiers:

| Tier | Service | Host options |
|------|---------|--------------|
| **Orchestration** | FastAPI + Streamlit | Render, Railway, Fly.io, any VPS |
| **Inference** | vLLM (GPU) | RunPod, Lambda Labs, AWS g5 (burst), local GPU |

vLLM is **not** included in Docker Compose. Point `VLLM_BASE_URL` at your GPU server.

---

## Option A — Docker on a VPS (recommended demo)

**Requirements:** Linux VPS (1 vCPU+ for API/UI), separate GPU machine for vLLM.

```bash
git clone https://github.com/itsvaidahipatel/automated-fact-checking-pipeline.git
cd automated-fact-checking-pipeline
cp .env.example .env
```

Edit `.env`:

```bash
VLLM_BASE_URL=http://YOUR_GPU_IP:8000/v1
API_KEY=generate-a-long-random-string
API_BASE_URL=http://YOUR_VPS_IP:8080
```

```bash
docker compose up --build -d
```

| URL | Service |
|-----|---------|
| `http://VPS:8080/docs` | FastAPI |
| `http://VPS:8501` | Streamlit UI |

Test:

```bash
curl -X POST http://VPS:8080/fact-check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"claim": "Water boils at 100°C at sea level."}'
```

---

## Option B — Render (free/cheap API)

1. Push repo to GitHub.
2. [Render](https://render.com) → **New Web Service** → connect repo.
3. Settings:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `uvicorn serve.api:app --host 0.0.0.0 --port $PORT`
   - **Environment:** add `VLLM_BASE_URL`, `API_KEY`, `ENABLE_TELEMETRY=false`, `PYTHONPATH=.`

Use the included [`render.yaml`](render.yaml) for one-click deploy.

Streamlit: deploy separately on [Streamlit Community Cloud](https://streamlit.io/cloud) with secrets:

- `API_BASE_URL` = your Render API URL  
- `API_KEY` = same key as the API  

---

## Option C — Streamlit Community Cloud (UI only)

1. Connect GitHub repo at share.streamlit.io.
2. Main file: `app.py`
3. **Secrets** (TOML):

```toml
API_BASE_URL = "https://your-api.onrender.com"
API_KEY = "your-api-key"
```

The API must be deployed separately (Option A or B).

---

## vLLM on GPU (inference)

Start vLLM on a GPU host when you need live fact-checking:

```bash
vllm serve Qwen/Qwen2.5-3B-Instruct --host 0.0.0.0 --port 8000
```

Ensure port 8000 is reachable from your API host (security group / firewall). **Stop the GPU instance when not demoing** to avoid cost.

See [serve/vllm_config.md](../serve/vllm_config.md).

---

## Production checklist

- [ ] Set `API_KEY` on the API service  
- [ ] Set matching `API_KEY` on Streamlit (if used)  
- [ ] Never commit `.env`  
- [ ] Restrict vLLM port to API server IP only  
- [ ] `ENABLE_TELEMETRY=false` unless Langfuse keys are configured  

---

## Author

**Vaidahi Patel** — https://github.com/itsvaidahipatel
