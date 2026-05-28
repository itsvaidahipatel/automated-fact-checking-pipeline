FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py .
COPY agents/ agents/
COPY tools/ tools/
COPY telemetry/ telemetry/
COPY serve/ serve/

EXPOSE 8080

CMD ["uvicorn", "serve.api:app", "--host", "0.0.0.0", "--port", "8080"]
