# 📊 AIFS Hub — Dashboard v0.5

> See every folder contract, in-flight file, audit log, and agent trust tier in one live view.

## Quick Start

```bash
# Install deps
pip install fastapi uvicorn watchdog requests

# Start the hub (from repo root)
python AIFS/hub/aifs_hub_server.py --root .

# Open dashboard
open http://localhost:7331
```

## What You See

| Panel | What It Shows |
|-------|---------------|
| 📊 **Overview** | Total contracts, locked paths, in-flight files, active agents |
| 📁 **Folders** | Every folder with a contract — status, permissions, read-only flag |
| ⚠️ **In-Flight** | All files currently protected by context.md across the whole project |
| 🚫 **Locks** | Every .ailock pattern — hard stops at a glance |
| 👤 **Trust** | Agent trust tiers across all folders |
| 📝 **Audit Log** | CHANGELOG.ai.md entries — who touched what, when |

## Endpoints

| Endpoint | Returns |
|----------|---------|
| `GET /` | Dashboard HTML |
| `GET /api/summary` | Overview stats |
| `GET /api/contracts` | All resolved contracts |
| `GET /api/in-flight` | All in-flight files across project |
| `GET /api/locks` | All .ailock patterns |
| `GET /api/trust` | All agent trust tiers |
| `GET /api/audit` | Recent audit log entries |
| `GET /api/contract/{path}` | Single folder contract |

## Stack

- **Backend:** FastAPI + uvicorn
- **Frontend:** Single HTML file, vanilla JS, no build step
- **Style:** Dark theme, AIFS purple/green brand colours
- **Live refresh:** Auto-polls every 10 seconds

---
*AIFS v0.5 — Built by welshDog × Perplexity — June 2026*
