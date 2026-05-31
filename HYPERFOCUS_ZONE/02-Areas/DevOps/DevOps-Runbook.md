---
type: area
title: DevOps Runbook
tags:
  - area
  - devops
  - docker
  - infrastructure
created: 2026-05-31
updated: 2026-05-31
---

# 🐳 DevOps Runbook

> Quick reference for the whole infra. When something's down, come here first.

---

## 🌐 Port Map (Local)

| Port | Service | Repo |
|---|---|---|
| 3001 | Grafana | HyperCode-V2.4 |
| 8000 | HyperCode Core API | HyperCode-V2.4 |
| 8088 | HyperCode Dashboard | HyperCode-V2.4 |
| 8100 | **HYPER BRAIN Engine** | BROski-Obsidian-Brain |
| 8101 | GitHub Webhook Server | BROski-Obsidian-Brain |
| 8820 | MCP Bridge | BROski-Obsidian-Brain |
| 9090 | Prometheus | HyperCode-V2.4 |
| 5173 | Vibe Course (dev) | Hyper-Vibe-Coding-Course |

---

## 🏥 Health Checks (Copy-Paste)

```powershell
# Brain Engine
curl.exe -s http://localhost:8100/health

# Grafana
curl.exe -s http://localhost:3001/api/health

# Prometheus targets
# Open: http://localhost:9090/targets

# HyperCode API
curl.exe -s http://localhost:8000/health
```

---

## 🐳 Container Quick Commands

```powershell
# See all running containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Brain container specifically
docker ps --filter name=hyper-brain

# Restart brain
docker restart hyper-brain

# Full ecosystem logs (last 50 lines)
docker logs hyper-brain --tail 50

# Disk usage (check monthly)
docker system df

# Nuclear cleanup (careful!)
# docker system prune -af
```

---

## 🔥 Common Fixes

### "Container won't start"
1. Check if the network exists: `docker network ls | findstr hyper-brain-net`
2. If missing: `docker network create hyper-brain-net`
3. Retry: `docker compose -f docker/docker-compose.hyper-brain.yml up -d`

### "Could not validate credentials" (HyperCode)
- Check JWT / auth token config in `.env`
- Restart the auth container
- See: [[01-Projects/HyperCode-V2.4]]

### "Port already in use"
```powershell
netstat -ano | findstr :<PORT>
# Find the PID → taskkill /PID <pid> /F
```

### "Grafana dashboards blank"
- Check Prometheus is scraping: `http://localhost:9090/targets`
- Check data source in Grafana: Settings → Data Sources → Prometheus → Test

---

## 📊 Monitoring Links

- Grafana: [localhost:3001](http://localhost:3001)
- Prometheus: [localhost:9090](http://localhost:9090)
- Prometheus Targets: [localhost:9090/targets](http://localhost:9090/targets)
- Grafana Dashboards: [localhost:3001/dashboards](http://localhost:3001/dashboards)

---

> 📖 Full infra docs: `HyperCode-V2.4/Hyper-Docker/EXECUTIVE_SUMMARY.md`
