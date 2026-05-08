---
name: hyper-brain-modules
description: THE HYPER BRAIN v3.0 module map — 8 FastAPI modules on port 8100 (focus_tracker, ai_distraction_filter, hyper_split, mcp_bridge, analytics_engine, github_webhook_server, morning_briefing_ai, session_snapshot). Use when the user says "brain module", "endpoint X not responding", "8100", "/focus", "/hypersplit", "/briefing", "module reference", or extends the Brain API.
---

# hyper-brain-modules

THE HYPER BRAIN v3.0 — 8 modules behind one FastAPI on `http://localhost:8100`. Container #30 in the Hyperfocus Zone stack. Memory cap: 256MB.

## Module Map (all green as of May 7, 2026)

| Module | File | Endpoints | Purpose |
|---|---|---|---|
| `focus_tracker` | `focus_tracker.py` | `/focus/start` `/focus/end` `/focus/status` `/focus/snapshot` | Track focus sessions, log to `05-Focus-Sessions/` |
| `ai_distraction_filter` | `ai_distraction_filter.py` | `/distraction/report` `/distraction/patterns` | Detect + log distractions during sessions |
| `hyper_split` | `hyper_split.py` | `/hypersplit` | Recursive task decomposition into micro-tasks |
| `mcp_bridge` | `mcp_bridge.py` | `/mcp/status` `/mcp/query` | Bridge to HyperAgent MCP gateway (port 8820) |
| `analytics_engine` | `analytics_engine.py` | `/analytics/weekly` `/analytics/heatmap` | Focus analytics, weekly reports, heatmaps |
| `github_webhook_server` | `github_webhook_server.py` | `/webhook/github` | Real-time GitHub issue/PR → vault notes |
| `morning_briefing_ai` | `morning_briefing_ai.py` | `/briefing/generate` | AI-generated daily briefing → `00-Inbox/Briefings/` |
| `session_snapshot` | (in `focus_tracker.py`) | `/focus/snapshot` | Snapshot active session state |

All modules wired in `hyper_brain_core.py` (the FastAPI entrypoint).

## Health Check

```powershell
curl http://localhost:8100/health
# → {"status":"hyper","level":20,"containers":30}
```

If `level < 20` → some modules failed to load. Check container logs.

## Bring The Brain Up

```powershell
cd H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne

# Set required env vars
$env:OBSIDIAN_VAULT_PATH    = "H:/BROski-Obsidian-Brain-for-HyperFocus-z0ne/HYPERFOCUS_ZONE"
$env:GITHUB_WEBHOOK_SECRET  = "<your secret>"
$env:GITHUB_PAT             = "github_pat_xxx"

# Ensure external networks exist (created by HyperCode stack normally)
docker network create app-net 2>$null
docker network create agents-net 2>$null

# Build + run
docker compose -f docker-compose.hyper-brain.yml up -d --build

# Verify
curl http://localhost:8100/health
```

## CANONICAL PYTHON FILES — Iron Rule

**Two sets of `.py` files exist. Root = canonical. `scripts/` = stubs.**

| Location | Status | Action |
|---|---|---|
| Root `*.py` (e.g. `focus_tracker.py`) | ✅ **CANONICAL v3.0** | Edit these |
| `scripts/*.py` (9 stub files, ~150 lines each) | ❌ **OLD STUBS** | NEVER edit |
| `scripts/github_to_obsidian.py` | ✅ Real script | OK to edit |
| `scripts/setup.ps1` | ✅ Real bootstrap | OK to edit |
| `scripts/setup_hyper_brain.ps1` | ✅ Real bootstrap | OK to edit |

**NEVER edit `scripts/*.py` (the stubs).** They're skeletons left over from v2.x. The Dockerfile copies root `.py` files, not `scripts/`.

## Endpoint Quick Reference

```powershell
# Start a focus session
curl -X POST http://localhost:8100/focus/start `
  -H "Content-Type: application/json" `
  -d '{"task": "Write skill", "intensity": "hyper"}'

# Get current session status
curl http://localhost:8100/focus/status

# End session
curl -X POST http://localhost:8100/focus/end `
  -H "Content-Type: application/json" `
  -d '{"notes": "Shipped 5 skills"}'

# Generate today's briefing
curl -X POST http://localhost:8100/briefing/generate

# Decompose a task
curl -X POST http://localhost:8100/hypersplit `
  -H "Content-Type: application/json" `
  -d '{"task": "Build a payment system", "depth": 3}'

# Weekly analytics
curl http://localhost:8100/analytics/weekly

# Focus heatmap (last 30 days)
curl http://localhost:8100/analytics/heatmap

# MCP status
curl http://localhost:8100/mcp/status

# Webhook (real GitHub deliveries hit this)
curl -X POST http://localhost:8100/webhook/github `
  -H "X-Hub-Signature-256: sha256=<hmac>" `
  -d '{"action":"opened","issue":{...}}'
```

## Adding a New Module

1. Create `<module_name>.py` at the **repo root** (NOT in `scripts/`)
2. Define a FastAPI `APIRouter` with your endpoints
3. Import + include in `hyper_brain_core.py`:
   ```python
   from <module_name> import router as <module_name>_router
   app.include_router(<module_name>_router)
   ```
4. Add any new env vars to `docker-compose.hyper-brain.yml` `environment:`
5. Rebuild + restart:
   ```powershell
   docker compose -f docker-compose.hyper-brain.yml up -d --build
   ```
6. Add the module to this skill's table

## Common Failures

| Symptom | Cause | Fix |
|---|---|---|
| `curl: (7) Failed to connect` on 8100 | Container not running | `docker compose ps`, check logs |
| `level: 12` (lower than 20) in `/health` | Some modules failed import | `docker compose logs hyper-brain` for tracebacks |
| `/briefing/generate` errors | LLM not reachable, or env var missing | Check container env vars; test LLM endpoint directly |
| Webhook returns 403 | `GITHUB_WEBHOOK_SECRET` mismatch | Re-sync secret in GitHub repo settings + container env |
| Imports work locally but fail in container | Editing `scripts/*.py` instead of root `.py` | Edit root canonical files only |
| External network errors on `up` | `app-net` or `agents-net` missing | `docker network create app-net agents-net` |
| Hot-reload changes don't reflect | Volume not mounted or built into image | Rebuild: `up -d --build` (no shortcut for first-time-built containers) |

## Companion Skills

- `morning-briefing-ai` — deep dive on `/briefing/generate`
- `vault-para-structure` — where module outputs land in the vault
- `level-progression` — what each module unlocks (Level 13–17)
- `obsidian-git-vault` — vault auto-commit ensures outputs survive

## Hard Rules

- **NEVER edit `scripts/*.py` stubs** — root canonical files only
- **NEVER create `.py` files in repo root** that aren't intended modules
- **`docker-compose.hyper-brain.yml` at root is canonical** — NOT the one in `docker/`
- **External networks `app-net` + `agents-net`** must exist before `up`
- **Memory cap 256MB** — keep modules light
- **Port 8100 is reserved** for the Brain API (in V2.4 stack)
