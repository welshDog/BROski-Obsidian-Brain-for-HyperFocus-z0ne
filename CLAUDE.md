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
- **Graduate build CLI:** IMPLEMENTED in HyperAgent-SDK ✅ — run `hyper-agent graduate build cluster.json --out brain-bundle/ --strict` to wire agents into V2.4

---

## 🔴 Sacred Rules — Obsidian Brain

| # | Rule | Why |
|---|---|---|
| 1 | **NEVER manually edit `cluster.json` without updating all 4 agent manifests** | Must stay in sync — graduate build fails silently with wrong agent count |
| 2 | **NEVER commit Obsidian workspace files (`.obsidian/workspace*`)** | Local UI state only — causes merge conflicts across machines |
| 3 | **PARA structure is sacred — Projects / Areas / Resources / Archive** | Dataview queries depend on exact folder names |
| 4 | **`github_to_obsidian.py` is the sync bridge — run it, don't rewrite it** | Fragile regex patterns tuned to GitHub API output |
| 5 | **Brain agents = `hyper-brain-core`, `mcp-bridge`, `focus-tracker`, `morning-briefing`** | These 4 only — don't add agents without Lyndz sign-off |
| 6 | **Morning Briefing agent = Level 13 — designed, NOT yet live** | Don't deploy half-built — would post broken briefings to Discord |
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

## ⚡ Brain Agent Cluster — Next Steps

```bash
# Step 1 — Run graduate build (SDK CLI is LIVE)
hyper-agent graduate build cluster.json --out brain-bundle/ --strict

# Step 2 — Add brain-bundle to V2.4 docker compose
# Step 3 — Wire morning-briefing agent (Level 13) once bundle is confirmed
```

**Pending:** Morning Briefing agent (L13) — designed, not yet deployed.

---

> 🐶♾️ Part of the Hyperfocus z0ne — @welshDog
