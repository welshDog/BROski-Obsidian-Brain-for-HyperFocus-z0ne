---
created: 2026-05-05
type: command-center
tags: [focus, command, control]
---
# ⚡ Focus Command Center

> Control your focus state. Start, stop, snapshot, recover.

---

## 🎮 Session Controls

### Start Focus Session
```powershell
$body = @{
    intent = "Build HyperSplit API endpoint"
    estimated_minutes = 25
    project = "HyperCode-V2.4"
    tags = @("api", "backend")
    difficulty_preference = "auto"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8100/focus/start" -Method POST -Body $body -ContentType "application/json"
```

### End Focus Session
```powershell
$body = @{
    session_id = "SESSION_ID_HERE"
    actual_minutes = 30
    distractions_blocked = 3
    notes = "Great flow after first 10 min"
    mood = 8
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8100/focus/end" -Method POST -Body $body -ContentType "application/json"
```

### Emergency Snapshot
```powershell
Invoke-RestMethod -Uri "http://localhost:8100/focus/snapshot" -Method POST
```

---

## 🪓 HyperSplit a Task
```powershell
$body = @{
    task_title = "Implement Stripe webhook handler"
    task_description = "Need to handle checkout.session.completed and award BROski$"
    max_depth = 3
    target_minutes_per_task = 15
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8100/hypersplit" -Method POST -Body $body -ContentType "application/json"
```

---

## 🌅 Generate Morning Briefing
```powershell
$body = @{
    date = "2026-05-05"
    include_ai_suggestions = $true
    include_focus_forecast = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8100/briefing/generate" -Method POST -Body $body -ContentType "application/json"
```

---

## 📊 Get Analytics
```powershell
# Weekly report
Invoke-RestMethod -Uri "http://localhost:8100/analytics/weekly"

# Streaks
Invoke-RestMethod -Uri "http://localhost:8100/analytics/streaks"

# Focus heatmap (30 days)
Invoke-RestMethod -Uri "http://localhost:8100/analytics/heatmap?days=30"
```

---

## 🧠 MCP Queries
```powershell
# Query vault via local LLM
$body = @{ query = "What are my overdue tasks?" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8100/mcp/query" -Method POST -Body $body -ContentType "application/json"
```

---

## 🔥 Distraction Reporting
```powershell
$body = @{
    source = "social_media"
    context = "Saw Twitter notification about new framework"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8100/distraction/report" -Method POST -Body $body -ContentType "application/json"
```

---

## 🐳 Docker Commands
```powershell
# Start hyper-brain
docker compose -f docker/docker-compose.hyper-brain.yml up -d

# View logs
docker logs hyper-brain --tail 50 -f

# Health check
Invoke-RestMethod -Uri "http://localhost:8100/health"

# Restart
docker restart hyper-brain
```

---

> *"The best time to focus was yesterday. The second best time is now."*  
> **Ctrl+Shift+F → GO BROski. ♾️🔥**
