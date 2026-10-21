# Standalone GitHub-to-Obsidian sync image.
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ ./scripts/
COPY docs/ ./docs/

RUN addgroup --system appuser && adduser --system --ingroup appuser appuser \
    && mkdir -p /vault \
    && chown -R appuser:appuser /app /vault

ENV PYTHONUNBUFFERED=1 \
    OBSIDIAN_VAULT_PATH=/vault

USER appuser

CMD ["python3", "scripts/github_to_obsidian_v2.py"]
