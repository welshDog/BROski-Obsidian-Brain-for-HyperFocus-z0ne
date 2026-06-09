FROM python:3.11-slim
WORKDIR /app
# Copy all root-level brain modules (analytics_engine, hyper_split, etc.)
COPY *.py ./
# All 4 agent entrypoints live in their own folders — bring them all into /app
COPY .agents/hyper-brain-core/hyper_brain_core.py ./
COPY .agents/mcp-bridge/mcp_bridge.py ./
COPY .agents/focus-tracker/focus_tracker.py ./
COPY .agents/morning-briefing/morning_briefing_ai.py ./
COPY web/ ./web/
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
CMD ["sh", "-c", "uvicorn hyper_brain_core:app --host 0.0.0.0 --port ${PORT:-3301}"]
