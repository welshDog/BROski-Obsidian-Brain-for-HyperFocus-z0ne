# ⚡ Focus Command Center
> HYPER BRAIN v3.0 — API Quick Reference
> Port 8100 | Container 30 | Level 20

---

## 🚀 Core Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| Health check | `GET` | `http://localhost:8100/health` |
| System status | `GET` | `http://localhost:8100/status` |
| Start focus session | `POST` | `http://localhost:8100/focus/start` |
| Split a task | `POST` | `http://localhost:8100/task/split` |
| Morning briefing | `GET` | `http://localhost:8100/briefing/today` |
| GitHub webhooks | `POST` | `http://localhost:8101/webhook/github` |

---

## 🎯 Start a Focus Session

```powershell
$body = @{
    task_title = "Your task here"
    duration_minutes = 25
    mode = "pomodoro"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8100/focus/start" `
    -Method POST -Body $body -ContentType "application/json"
```

## 🧩 HyperSplit a Task

```powershell
$body = @{
    title = "Big scary task"
    priority = "high"
    energy_level = 7
    estimated_minutes = 60
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8100/task/split" `
    -Method POST -Body $body -ContentType "application/json"
```

## 📊 Health Check

```powershell
Invoke-RestMethod http://localhost:8100/health
# → {"status":"hyper","version":"3.0.0","level":20,"containers":30}
```

---

## 🐳 Container Management

```powershell
# Start container 30
docker compose -f docker/docker-compose.hyper-brain.yml up -d

# Check status
docker ps --filter name=hyper-brain

# View logs
docker logs hyper-brain --tail 50 -f

# Restart
docker restart hyper-brain

# Stop
docker compose -f docker/docker-compose.hyper-brain.yml down
```

---

## 🧠 Module Map

- **hyper_brain_core.py** → FastAPI orchestrator (port 8100)
- **focus_tracker.py** → DifficultyDial + session XP
- **analytics_engine.py** → Streaks, heatmaps, reports
- **hyper_split.py** → Recursive task decomposition
- **ai_distraction_filter.py** → Context scoring + interventions
- **mcp_bridge.py** → Local LLM (Ollama/LMStudio) + Vault RAG
- **morning_briefing_ai.py** → AI daily briefing
- **session_snapshot.py** → State capture + recovery
- **github_webhook_server.py** → Issues + PRs → vault (port 8101)

---

*HYPER BRAIN v3.0 — Level 20 ♾️🧠⚡*
