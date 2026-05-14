# Systems-first Web UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the FastAPI-served web Command Center to a “Systems-first” layout with constellation tiles, gamification HUD, achievements grid, events stream, and quick actions for briefing + snapshot.

**Architecture:** Static `web/` assets (HTML/CSS/JS) render a single-page layout. `app.js` fetches JSON from existing FastAPI endpoints (`/health`, `/events`, `/gamification/summary`) and wires POST actions (`/briefing/generate`, `/focus/snapshot`) to UI buttons.

**Tech Stack:** HTML + CSS + vanilla JS (Fetch API). No framework.

---

### Task 1: Systems-first layout + styling

**Files:**
- Modify: [index.html](file:///workspace/BROski-Obsidian-Brain-for-HyperFocus-z0ne/web/index.html)
- Modify: [styles.css](file:///workspace/BROski-Obsidian-Brain-for-HyperFocus-z0ne/web/styles.css)

- [ ] Replace the current 2-panel grid with a Systems-first dashboard:
  - Topbar: brand, connection pill, compact HUD (XP/coins)
  - Main: responsive grid with
    - Constellation tile board (services)
    - System JSON panel
    - Quick actions panel + output
    - Achievements grid
    - Events stream
- [ ] Add CSS tokens and components:
  - Tile states (online/offline/dormant)
  - HUD (level + XP bar + coins)
  - Achievements badge grid (locked/unlocked)
  - Buttons (primary/secondary) + reduced-motion support

### Task 2: Client-side rendering + quick actions

**Files:**
- Modify: [app.js](file:///workspace/BROski-Obsidian-Brain-for-HyperFocus-z0ne/web/app.js)

- [ ] Fetch on load (parallel):
  - `GET /health`
  - `GET /events?limit=10`
  - `GET /gamification/summary`
- [ ] Render:
  - Status pill: online/offline + version from health
  - Constellation tiles: derived from `health.services`
  - HUD: level/XP + coins
  - Achievements: take 12–16 from unlocked+available
  - Events stream: latest items
- [ ] Wire quick actions:
  - `POST /briefing/generate` (JSON body `{}`) output rendered into the actions output panel
  - `POST /focus/snapshot` output rendered into the actions output panel

### Task 3: Validation

**Files:**
- No changes expected

- [ ] Run unit tests:

```bash
python3.12 -m pytest -q
```

Expected: PASS

Notes:
- Do not change [bg.js](file:///workspace/BROski-Obsidian-Brain-for-HyperFocus-z0ne/web/bg.js).
- Do not commit changes (per user request).

