# WHATS_DONE.md -- BROski Obsidian Brain

> Single source of truth. Check this before building ANYTHING.
> Last updated: 2026-06-03

---

## Core Python Brain Tools (ALL EXIST -- do not rebuild)

| File | Status | What it does |
|---|---|---|
| `hyper_brain_core.py` | DONE | Core brain engine, knowledge retrieval |
| `focus_tracker.py` | DONE | Focus session tracking + state |
| `analytics_engine.py` | DONE | Productivity analytics + heatmaps |
| `morning_briefing_ai.py` | DONE | Daily AI briefing generator |
| `mcp_bridge.py` | DONE | MCP bridge (runs on :8823) |
| `session_snapshot.py` | DONE | Saves session state to vault |
| `constellation_builder.py` | DONE | Knowledge graph from Obsidian notes |
| `ai_distraction_filter.py` | DONE | AI-powered distraction detection |
| `gamification_summary.py` | DONE | XP, levels, BROski tokens |
| `events_feed.py` | DONE | Events stream |
| `github_webhook_server.py` | DONE | GitHub webhook listener |
| `difficulty_dial.py` | DONE | Task difficulty adjustment |
| `hyper_split.py` | DONE | Vault note splitter |
| `AIFS-LAUNCH.ps1` | DONE | AI File System launcher |

## PSAI + aish Integration (ADDED 2026-06-03)

| File | Status | What it does |
|---|---|---|
| `PSAI-Register-Tools.ps1` | NEW | Registers all 10 brain tools as PSAI agent-callable functions |
| `aish-mcp-config.json` | NEW | Wires aish to mcp_bridge.py + HyperCode gateway |
| `BROski-Brain-Quick-Start.ps1` | NEW | One-script boot: deps + MCP bridge + PSAI tools |

## Vault Structure

| Folder | Status | What it is |
|---|---|---|
| `HYPERFOCUS_ZONE/` | DONE | Main vault -- course reviews, project notes |
| `HYPER-SILLs/` | DONE | Skills + learning notes |
| `sessions/` | DONE | Session snapshots |
| `Ops-Logs/` | DONE | Operational logs |
| `.obsidian/` | DONE | Obsidian config |
| `.agents/` | DONE | Agent configs |
| `.claude/` | DONE | Claude context files |

## Key Docs

| File | What it is |
|---|---|
| `AGENT-START.md` | Agent onboarding + skill load |
| `CLAUDE.md` | Sacred rules for AI partners |
| `CLAUDE_CONTEXT.md` | Extended Claude context |
| `ANALYSIS_AND_ROADMAP.md` | Full roadmap |
| `UPGRADE_COMPLETE_SUMMARY.md` | Previous upgrade history |
| `NEXT_SESSION_HANDOVER_2026-06-02.md` | Last handover |

## DO NOT rebuild

- Any Python file listed above -- they exist and work
- `.obsidian/` config -- already tuned
- `cluster.json` -- knowledge graph config
- `docker-compose.hyper-brain.yml` -- brain Docker setup
