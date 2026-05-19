# 🧠 BROski-Obsidian-Brain — CLAUDE.md

> **Read MASTER first:** [HyperCode-V2.4/CLAUDE.md](https://github.com/welshDog/HyperCode-V2.4/blob/main/CLAUDE.md)
> That file has: who Lyndz is, comms rules, all sacred rules, ecosystem map, AI behaviour.
> This file has: Obsidian Brain-specific rules only.

---

## 📍 What This Repo Is

- **Purpose:** Second Brain vault — PARA method + Dataview + GitHub bridge
- **Local path:** `H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne`
- **Obsidian vault** synced to GitHub via Obsidian Git plugin
- **4-agent brain cluster** defined in `cluster.json` — PUSHED May 15 ✅

---

## 🔴 Sacred Rules — Obsidian Brain

| # | Rule | Why | Consequence if broken |
|---|---|---|---|
| 1 | **NEVER manually edit `cluster.json` structure without updating all 4 agent manifests** | `cluster.json` and `.agents/*/manifest.json` must stay in sync | Graduate build fails silently with wrong agent count |
| 2 | **NEVER commit Obsidian workspace files (`.obsidian/workspace*`)** | Local UI state only — causes merge conflicts across machines | Constant vault conflicts |
| 3 | **PARA structure is sacred — Projects / Areas / Resources / Archive — no custom root folders** | Dataview queries depend on exact folder names | All Dataview dashboards break |
| 4 | **`github_to_obsidian.py` is the sync bridge — run it, don’t rewrite it** | Fragile regex patterns tuned to GitHub API output | Sync breaks silently |
| 5 | **Brain agents = `hyper-brain-core`, `mcp-bridge`, `focus-tracker`, `morning-briefing`** | These 4 only — don’t add agents to cluster without Lyndz sign-off | Cluster grows beyond graduate build spec |
| 6 | **Morning Briefing agent is Level 13 — not yet live** | Designed, not implemented — don’t deploy half-built | Broken auto-post to Discord |

---

## 📂 Key Files

```
cluster.json                    — 4-agent brain cluster spec
.agents/hyper-brain-core/       — core brain agent manifest
.agents/mcp-bridge/             — MCP bridge agent manifest
.agents/focus-tracker/          — focus tracker manifest
.agents/morning-briefing/       — morning briefing manifest
scripts/github_to_obsidian.py   — GitHub → Obsidian sync bridge
Projects/                       — PARA: active projects
Areas/                          — PARA: ongoing responsibilities
Resources/                      — PARA: reference material
Archive/                        — PARA: completed/inactive
```

---

## ⚡ Next Step for Brain Agents

Once `hyper-agent graduate build` CLI is implemented in HyperAgent-SDK:

```bash
hyper-agent graduate build cluster.json --out brain-bundle/ --strict
```

> Status: Waiting on HyperAgent-SDK CLI implementation.

---

> 🐶♾️ Part of the Hyperfocus z0ne — @welshDog
