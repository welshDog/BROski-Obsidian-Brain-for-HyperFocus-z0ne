---
name: level-progression
description: THE HYPER BRAIN level tracker — 1–20 progression, what each level represents, what's unlocked, what's pending (Level 18–20). Use when the user says "level X", "level up", "what's next", "level 18", "constellation", or asks about Brain progression status.
---

# level-progression

The Brain is a 20-level system. Each level = a feature/capability shipped. **Levels 1–17 done as of May 7, 2026. Levels 18–20 in flight.**

## Level Tracker (current)

```
✅ 1–8   Vault scaffold + plugins + PARA structure
✅ 9     GitHub bridge (4hr polling) — scripts/github_to_obsidian.py
✅ 10    Vault immortal (Obsidian Git auto-commit, 10min)
✅ 11    BROski$ Coin Tracker (Dataview widget)
✅ 12    Hyperfocus CSS Modes (Focus / Calm / Hyper)
✅ 13    Morning Briefing AI                  ✅ May 7
✅ 14    GitHub Webhooks real-time            ✅ May 7
✅ 15    HyperAgent MCP Bridge                ✅ May 7
✅ 16    Focus Tracker + Analytics            ✅ May 7
✅ 17    HyperSplit Task Decomposition        ✅ May 7
⏳ 18    AI Distraction Filter (wired to focus sessions)   ← NEXT
⏳ 19    DifficultyDial + Dynamic XP
⏳ 20    THE HYPER BRAIN Constellation (MCP mesh + RAG)
```

## What Each Level Unlocks

### Foundational (1–8)

The vault structure, Obsidian plugins, PARA folders. Done in early sprints. `vault-para-structure` skill covers this.

### Level 9 — GitHub Bridge

`scripts/github_to_obsidian.py` polls GitHub every 4 hours, syncs issues + PRs into `00-Inbox/GitHub/<repo>/`. Cron-driven, not real-time.

### Level 10 — Vault Immortal

Obsidian Git plugin auto-commits the vault every 10 mins, auto-pushes to remote. Means the vault never loses a note even if a machine dies.

### Level 11 — BROski$ Coin Tracker

Dataview query renders a coin balance widget in the Dashboard note. Reads from vault frontmatter (`coins:` field).

### Level 12 — Hyperfocus CSS Modes

Three CSS themes:
- `focus-mode` — minimal, distraction-free
- `calm-mode` — softer colors, longer sessions
- `hyper-mode` — high contrast, fast scanning

Toggle via Obsidian command palette.

### Level 13 — Morning Briefing AI ✅ May 7

`/briefing/generate` → AI summarizes overnight GitHub activity, today's tasks, focus stats → drops into `00-Inbox/Briefings/<date>.md`. Runs on demand or via cron.

### Level 14 — GitHub Webhooks Real-Time ✅ May 7

`/webhook/github` receives GitHub events live. New issue → instant note in `00-Inbox/GitHub/<repo>/`. Replaces 4hr polling for connected repos.

### Level 15 — HyperAgent MCP Bridge ✅ May 7

`/mcp/query` exposes the vault as an MCP source. HyperAgent agents (V2.4 stack) can query vault notes via MCP gateway port 8820.

### Level 16 — Focus Tracker + Analytics ✅ May 7

`/focus/start` + `/focus/end` log sessions to `05-Focus-Sessions/`. `/analytics/weekly` + `/analytics/heatmap` produce reports.

### Level 17 — HyperSplit Task Decomposition ✅ May 7

`/hypersplit` recursively breaks a task into micro-tasks (default depth 3). Output → `01-Projects/<project>/HyperSplit-<task>.md` with linked sub-tasks.

### Level 18 — AI Distraction Filter (NEXT)

Code DONE: `ai_distraction_filter.py` exists, has `/distraction/report` + `/distraction/patterns`. **Needs wiring into focus sessions** — when a session is active, distractions logged via the filter feed into the session's record.

The work:
1. In `focus_tracker.py` `/focus/start`: register session ID + intensity
2. When `/distraction/report` is called during a session: increment session's distraction count
3. When `/focus/end`: include distraction summary in the session log
4. Cross-correlate in `/analytics/weekly` (focus quality score)

### Level 19 — DifficultyDial + Dynamic XP

XP per task currently flat. Level 19 = task XP scales with difficulty (HyperSplit's micro-task count, time estimate, distractions). DifficultyDial = a UI knob in the Dashboard to set today's difficulty target (which auto-tunes briefing tone).

Not yet started.

### Level 20 — THE HYPER BRAIN Constellation

The endgame: full MCP mesh (Brain ↔ V2.4 ↔ Course ↔ Pets ↔ SDK) with RAG over the vault. Means any agent in the ecosystem can query the vault and receive contextual answers grounded in Bro's notes.

Not yet started. Depends on Level 19.

## Confirming Level Status

```powershell
curl http://localhost:8100/health
# → {"status":"hyper","level":20,"containers":30}
# (level=20 here means "all 8 modules loaded" — not the progression level)
```

The **module-level health** (from `/health`) is different from the **progression level**. Health=20 means engine green. Progression level is hand-tracked in `CLAUDE_CONTEXT.md`.

## Update The Tracker

When a level ships:

1. Update `CLAUDE_CONTEXT.md` (root) — change ⏳ to ✅, add date
2. Update `CLAUDE.md` (root) — same
3. Update this skill's table
4. If the level adds endpoints → update `hyper-brain-modules` skill's module map
5. Commit + let Obsidian Git push automatically

## What To Work On Next

**Level 18 first** — the code is already there, just wiring required. Estimate: 1–2hrs.

After 18:
- **Level 19** — design pass first (what defines "difficulty"? what does the dial UI look like?), then implement
- **Level 20** — dependent on stable MCP mesh; talk to V2.4's `mcp-gateway` skill

## Companion Skills

- `hyper-brain-modules` — module-level reference
- `morning-briefing-ai` — Level 13 deep dive
- `vault-para-structure` — Levels 1–8 foundation
- `obsidian-git-vault` — Level 10 mechanics

## Hard Rules

- **One level at a time** — finish 18 before starting 19
- **Track levels in `CLAUDE_CONTEXT.md`** — it's the source of truth, this skill mirrors it
- **Honest tracker** — code "done but not wired" is ⏳, not ✅
- **Docker compose path** is `docker-compose.hyper-brain.yml` at root, not `docker/`
