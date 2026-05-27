# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal for async HTTP)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scripts/ ./scripts/
COPY docs/ ./docs/

# Create vault directory (will be mounted)
RUN mkdir -p /vault

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OBSIDIAN_VAULT_PATH=/vault

# Default command: run the async sync
CMD ["python3", "scripts/github_to_obsidian_v2.py"]
