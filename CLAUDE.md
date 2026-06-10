# 🧠 BROski-Obsidian-Brain — CLAUDE.md

> **Read MASTER first:** [HyperCode-V2.4/CLAUDE.md](https://github.com/welshDog/HyperCode-V2.4/blob/main/CLAUDE.md)
> That file has: who Lyndz is, comms rules, all sacred rules, ecosystem map, AI behaviour.
> This file has: Obsidian Brain-specific rules only.

---

## 📍 What This Repo Is

- **Purpose:** Second Brain vault — PARA method + Dataview + GitHub bridge
- **Local path:** `H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne`
- **Obsidian vault** synced to GitHub via Obsidian Git plugin
- **4-agent brain cluster** defined in `cluster.json` ✅
- **Graduate build CLI:** IMPLEMENTED ✅ — strict build passes (4x green). Agents live in V2.4 on ports 3301/3302/3303/3304 (`--profile brain-agents`)

---

## 🔴 Sacred Rules — Obsidian Brain

| # | Rule | Why |
|---|---|---|
| 1 | **NEVER manually edit `cluster.json` without updating all 4 agent manifests** | Must stay in sync — graduate build fails silently with wrong agent count |
| 2 | **NEVER commit Obsidian workspace files (`.obsidian/workspace*`)** | Local UI state only — causes merge conflicts across machines |
| 3 | **PARA structure is sacred — Projects / Areas / Resources / Archive** | Dataview queries depend on exact folder names |
| 4 | **`github_to_obsidian.py` is the sync bridge — run it, don't rewrite it** | Fragile regex patterns tuned to GitHub API output |
| 5 | **Brain agents = `hyper-brain-core`, `mcp-bridge`, `focus-tracker`, `morning-briefing`** | These 4 only — don't add agents without Lyndz sign-off |
| 6 | **Morning Briefing agent = Level 13 — LIVE on :3304** | Profile `brain-agents` — `/brain-briefing` Discord command + daily 7am UTC auto-DM |
| 7 | **NEVER commit `__pycache__/` or `output/`** | Already in `.gitignore` — delete tracked copies if they appear |

---

## 🗂️ Key Files

```
cluster.json                    — 4-agent brain cluster spec
.agents/hyper-brain-core/       — core brain agent manifest
.agents/mcp-bridge/             — MCP bridge agent manifest
.agents/focus-tracker/          — focus tracker manifest
.agents/morning-briefing/       — morning briefing manifest
brain/                          — Python brain tools (core, focus, briefing, analytics)
scripts/github_to_obsidian.py   — GitHub → Obsidian sync bridge
Projects/                       — PARA: active projects
Areas/                          — PARA: ongoing responsibilities
Resources/                      — PARA: reference material
Archive/                        — PARA: completed/inactive
docs/                           — analysis, roadmap, insights, upgrade notes
```

---

## ⚡ Brain Agent Cluster — Status

```
✅ Step 1 — graduate build passes (4x green, 2026-06-09)
✅ Step 2 — wired into HyperCode-V2.4 docker-compose.brain.yml
✅ Step 3 — Morning Briefing agent (Level 13) — LIVE 2026-06-09
```

**Live agents** (`docker compose --profile brain-agents up -d`):

| Agent | Port | Health |
|---|---|---|
| `agent-hyper-brain-core` | 3301 | `GET /health` |
| `agent-mcp-bridge` | 3302 | `GET /health` |
| `agent-focus-tracker` | 3303 | `GET /health` |
| `agent-morning-briefing` | 3304 | `GET /health` |

**Discord:** `/brain-briefing` command (admin) + daily auto-DM at `BRIEFING_HOUR_UTC` (default 07:00 UTC).

---

## 🕸️ Graph Brain

**Last ran:** 2026-06-09 · Tool: AST static analysis (brain-graph-analysis)
**CANONICAL artifact:** `HYPERFOCUS_ZONE/06-AI-Context/graph.json` (v1) — THE memory-hub source of truth for all agents.
Inside containers: `/vault/06-AI-Context/graph.json` (all 4 brain agents mount the vault).
Served live by `agent-mcp-bridge` (:3302) via `GET /graph` + `GET /graph/node/{id}`.
Human report: `HYPERFOCUS_ZONE/06-AI-Context/GRAPHIFY_BRAIN_MAP.md`. (Old `graphify-out/` duplicate removed 2026-06-10; folder moved into the vault per the PARA plan — slot 06 was reserved for exactly this.)

**Top 5 nodes:** `hyper_brain_core` (centrality 10) › `analytics_engine` › `mcp_bridge` › `focus_tracker` › `morning_briefing_ai`

**Top 3 suggestions:**
1. ✅ DONE 2026-06-09 — `agent-morning-briefing` → `agent-mcp-bridge` wired via HTTP (RemoteMCPBridge; `:3304/health` shows `connected:true`)
2. Centralise streak-data reads — `morning_briefing_ai` and `analytics_engine` both parse the same JSON file
3. AIFS watcher sidecar in compose — AIFS is built but completely disconnected from agents

**Dead code identified:** `scripts/` (stale mirror), root `github_webhook_server.py` (orphaned)

---

> 🐶♾️ Part of the Hyperfocus z0ne — @welshDog
