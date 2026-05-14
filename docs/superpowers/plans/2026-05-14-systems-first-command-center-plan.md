# Systems-first Command Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Serve a Systems-first dashboard at `/ui` and add the missing API endpoints (`/events`, `/gamification/summary`) so the UI can render status, HUD, events, and quick actions (Briefing/Snapshot/Start/End Focus).

**Architecture:** Hyper Brain FastAPI serves static `web/` assets. A lightweight in-memory event feed provides `/events`. A gamification summary endpoint computes 7-day totals by scanning session notes + reads streaks JSON.

**Tech Stack:** FastAPI, vanilla HTML/CSS/JS, PyYAML, aiofiles, pytest (dev)

---

## Files to Create / Modify

**Create**
- `h:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/web/index.html`
- `h:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/web/styles.css`
- `h:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/web/app.js`
- `h:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/events_feed.py`
- `h:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/gamification_summary.py`
- `h:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/requirements-dev.txt`
- `h:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/tests/test_events_feed.py`
- `h:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/tests/test_gamification_summary.py`

**Modify**
- `h:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/hyper_brain_core.py`
- `h:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/Dockerfile.hyper-brain`

---

### Task 1: Add dev test dependencies

**Files:**
- Create: `requirements-dev.txt`

- [ ] **Step 1: Add `requirements-dev.txt`**

```txt
pytest==8.2.2
pytest-asyncio==0.23.7
httpx==0.27.0
```

- [ ] **Step 2: Verify deps install**

Run:
```powershell
python -m pip install -r requirements-dev.txt
```

Expected: installs `pytest` and `httpx` without error.

- [ ] **Step 3: Commit**

```powershell
git add requirements-dev.txt
git commit -m "chore: add dev test dependencies"
```

---

### Task 2: Implement `/events` backing store (ring buffer)

**Files:**
- Create: `events_feed.py`
- Test: `tests/test_events_feed.py`

- [ ] **Step 1: Write failing tests for EventsFeed**

Create `tests/test_events_feed.py`:

```python
from events_feed import EventsFeed


def test_events_feed_respects_limit_and_order():
    feed = EventsFeed(maxlen=3)
    feed.add(event_type="a", summary="1")
    feed.add(event_type="b", summary="2")
    feed.add(event_type="c", summary="3")
    feed.add(event_type="d", summary="4")

    data = feed.list(limit=10)
    assert [e["type"] for e in data] == ["b", "c", "d"]
    assert [e["summary"] for e in data] == ["2", "3", "4"]


def test_events_feed_limit_parameter():
    feed = EventsFeed(maxlen=10)
    for i in range(5):
        feed.add(event_type="x", summary=str(i))

    data = feed.list(limit=2)
    assert len(data) == 2
    assert [e["summary"] for e in data] == ["3", "4"]
```

- [ ] **Step 2: Run tests to confirm failure**

Run:
```powershell
python -m pytest -q
```

Expected: FAIL (module `events_feed` not found).

- [ ] **Step 3: Implement `events_feed.py`**

Create `events_feed.py`:

```python
from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Deque, Dict, List, Optional


class EventsFeed:
    def __init__(self, maxlen: int = 200):
        self._events: Deque[Dict[str, Any]] = deque(maxlen=maxlen)
        self._lock = Lock()

    def add(self, event_type: str, summary: str, payload: Optional[Dict[str, Any]] = None) -> None:
        e: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "type": event_type,
            "summary": summary,
        }
        if payload is not None:
            e["payload"] = payload

        with self._lock:
            self._events.append(e)

    def list(self, limit: int = 10) -> List[Dict[str, Any]]:
        limit = max(1, min(200, int(limit)))
        with self._lock:
            data = list(self._events)
        return data[-limit:]
```

- [ ] **Step 4: Run tests to confirm pass**

Run:
```powershell
python -m pytest -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add events_feed.py tests/test_events_feed.py
git commit -m "feat: add events feed ring buffer"
```

---

### Task 3: Implement gamification summary builder

**Files:**
- Create: `gamification_summary.py`
- Test: `tests/test_gamification_summary.py`

- [ ] **Step 1: Write failing tests for session-note parsing and 7d rollup**

Create `tests/test_gamification_summary.py`:

```python
import json
from pathlib import Path

import pytest

from gamification_summary import compute_gamification_summary


@pytest.mark.asyncio
async def test_compute_gamification_summary_rolls_up_frontmatter(tmp_path: Path):
    vault = tmp_path / "vault"
    sessions = vault / "05-Focus-Sessions"
    streaks_dir = vault / "07-Streaks-Achievements"
    sessions.mkdir(parents=True)
    streaks_dir.mkdir(parents=True)

    (streaks_dir / "streak-data.json").write_text(
        json.dumps({"current_streak": 2, "longest_streak": 5, "recovery_tokens": 1}),
        encoding="utf-8",
    )

    (sessions / "Session_abc_2026-05-14.md").write_text(
        \"\"\"---
created: 2026-05-14T10:00:00Z
coins_earned: 25
xp_earned: 15
---
# Session
\"\"\",
        encoding="utf-8",
    )

    (sessions / "Session_def_2026-05-13.md").write_text(
        \"\"\"---
created: 2026-05-13T10:00:00Z
coins_earned: 10
xp_earned: 5
---
# Session
\"\"\",
        encoding="utf-8",
    )

    summary = await compute_gamification_summary(str(vault), level=20)
    assert summary["level"] == 20
    assert summary["coins_total_7d"] == 35
    assert summary["xp_total_7d"] == 20
    assert summary["sessions_7d"] == 2
    assert summary["streaks"]["current_streak"] == 2
```

- [ ] **Step 2: Run tests to confirm failure**

Run:
```powershell
python -m pytest -q
```

Expected: FAIL (module `gamification_summary` not found).

- [ ] **Step 3: Implement `gamification_summary.py`**

Create `gamification_summary.py`:

```python
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import aiofiles
import yaml


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def _read_frontmatter(path: str) -> Optional[Dict[str, Any]]:
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            raw = await f.read()
    except FileNotFoundError:
        return None

    if not raw.startswith("---"):
        return None

    parts = raw.split("---", 2)
    if len(parts) < 3:
        return None

    fm_raw = parts[1].strip()
    if not fm_raw:
        return None

    data = yaml.safe_load(fm_raw)
    return data if isinstance(data, dict) else None


def _parse_created(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value:
        return None

    v = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(v)
    except ValueError:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


async def compute_gamification_summary(vault_path: str, level: int) -> Dict[str, Any]:
    streaks_dir = os.path.join(vault_path, "07-Streaks-Achievements")
    streaks_path = os.path.join(streaks_dir, "streak-data.json")

    streaks = {"current_streak": 0, "longest_streak": 0, "recovery_tokens": 1}
    try:
        async with aiofiles.open(streaks_path, "r", encoding="utf-8") as f:
            content = await f.read()
        if content:
            loaded = json.loads(content)
            if isinstance(loaded, dict):
                streaks.update({k: loaded.get(k, streaks[k]) for k in streaks})
    except FileNotFoundError:
        pass

    sessions_dir = os.path.join(vault_path, "05-Focus-Sessions")
    cutoff = _utcnow() - timedelta(days=7)

    coins_total = 0
    xp_total = 0
    sessions_count = 0

    if os.path.isdir(sessions_dir):
        for name in os.listdir(sessions_dir):
            if not name.lower().startswith("session_") or not name.lower().endswith(".md"):
                continue

            fm = await _read_frontmatter(os.path.join(sessions_dir, name))
            if not fm:
                continue

            created = _parse_created(fm.get("created"))
            if not created or created < cutoff:
                continue

            coins = fm.get("coins_earned", 0)
            xp = fm.get("xp_earned", 0)

            try:
                coins_total += int(coins)
            except (TypeError, ValueError):
                pass

            try:
                xp_total += int(xp)
            except (TypeError, ValueError):
                pass

            sessions_count += 1

    return {
        "level": int(level),
        "coins_total_7d": coins_total,
        "xp_total_7d": xp_total,
        "sessions_7d": sessions_count,
        "streaks": streaks,
        "generated_at": _utcnow().isoformat().replace("+00:00", "Z"),
    }
```

- [ ] **Step 4: Run tests to confirm pass**

Run:
```powershell
python -m pytest -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add gamification_summary.py tests/test_gamification_summary.py
git commit -m "feat: add gamification summary builder"
```

---

### Task 4: Add API routes and event emission in Hyper Brain

**Files:**
- Modify: `hyper_brain_core.py`

- [ ] **Step 1: Confirm MVP test strategy**

MVP automated tests cover:
- `EventsFeed` ordering/limits
- `compute_gamification_summary` rollups from vault files

This plan does not add FastAPI endpoint tests in MVP because app startup starts watchdog + background loops via `FocusTracker.start()`, which is not test-friendly without adding a test-mode switch.

- [ ] **Step 2: Wire `EventsFeed` + `compute_gamification_summary` into app state**

Update imports and global state in `hyper_brain_core.py`:

```python
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from events_feed import EventsFeed
from gamification_summary import compute_gamification_summary
```

Add globals:

```python
events_feed: Optional[EventsFeed] = None
```

Initialize in `startup()`:

```python
    events_feed = EventsFeed(maxlen=200)
    events_feed.add("system", "hyper_brain_startup", {"version": "3.0.0"})
```

- [ ] **Step 3: Implement `GET /events`**

Add route:

```python
@app.get("/events")
async def events(limit: int = 10):
    if not events_feed:
        return {"events": []}
    return {"events": events_feed.list(limit=limit)}
```

- [ ] **Step 4: Implement `GET /gamification/summary`**

Add route:

```python
@app.get("/gamification/summary")
async def gamification_summary():
    return await compute_gamification_summary(VAULT_PATH, level=20)
```

- [ ] **Step 5: Emit events from existing action routes**

In these handlers, add an `events_feed.add(...)` call (guarded if `events_feed` is None):
- `/focus/start`
- `/focus/end`
- `/focus/snapshot`
- `/briefing/generate`

Example for `/focus/start`:

```python
    if events_feed:
        events_feed.add("focus_start", f"Focus started: {req.intent}", {"session_id": session["id"]})
```

Example for `/focus/end`:

```python
    if events_feed:
        events_feed.add(
            "focus_end",
            f"Focus ended: {result.get('intent', '')}",
            {"session_id": req.session_id, "actual_minutes": req.actual_minutes, "mood": req.mood},
        )
```

- [ ] **Step 6: Run formatting + quick import sanity check**

Run:
```powershell
python -c "import hyper_brain_core"
```

Expected: no import errors.

- [ ] **Step 7: Commit**

```powershell
git add hyper_brain_core.py
git commit -m "feat: add events and gamification summary endpoints"
```

---

### Task 5: Serve the UI at `/ui`

**Files:**
- Modify: `hyper_brain_core.py`
- Create: `web/index.html`
- Create: `web/styles.css`
- Create: `web/app.js`

- [ ] **Step 1: Add static mounting in FastAPI**

In `hyper_brain_core.py`, define a web directory:

```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
```

Mount assets:

```python
app.mount("/ui/assets", StaticFiles(directory=WEB_DIR), name="ui-assets")
```

Serve index:

```python
@app.get("/ui")
async def ui_index():
    return FileResponse(os.path.join(WEB_DIR, "index.html"))
```

- [ ] **Step 2: Create `web/index.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>HYPER BRAIN — Command Center</title>
    <link rel="stylesheet" href="/ui/assets/styles.css" />
  </head>
  <body>
    <header class="topbar">
      <div class="brand">
        <div class="brand__title">HYPER BRAIN</div>
        <div class="brand__sub">Systems-first Command Center</div>
      </div>
      <div class="topbar__right">
        <div id="connectionPill" class="pill pill--offline">OFFLINE</div>
        <div class="hud">
          <div class="hud__item"><span class="hud__label">LV</span> <span id="hudLevel">—</span></div>
          <div class="hud__item"><span class="hud__label">XP</span> <span id="hudXp">—</span></div>
          <div class="hud__item"><span class="hud__label">$</span> <span id="hudCoins">—</span></div>
          <div class="hud__item"><span class="hud__label">STREAK</span> <span id="hudStreak">—</span></div>
        </div>
      </div>
    </header>

    <main class="grid">
      <section class="panel">
        <div class="panel__title">Constellation</div>
        <div id="tiles" class="tiles"></div>
      </section>

      <section class="panel">
        <div class="panel__title">System JSON</div>
        <div class="panel__tabs">
          <button class="tab" data-json="health">health</button>
          <button class="tab" data-json="focus">focus_status</button>
          <button class="tab" data-json="game">gamification_summary</button>
        </div>
        <pre id="jsonPanel" class="json"></pre>
      </section>

      <section class="panel">
        <div class="panel__title">Quick Actions</div>
        <div class="actions">
          <button id="btnBriefing" class="btn btn--primary">Generate Briefing</button>
          <button id="btnSnapshot" class="btn btn--secondary">Snapshot Now</button>
        </div>
        <div class="panel__title panel__title--spaced">Output</div>
        <pre id="outputPanel" class="json json--output"></pre>
      </section>

      <section class="panel">
        <div class="panel__title">Focus Controls</div>
        <div class="forms">
          <form id="startForm" class="form">
            <div class="form__row">
              <label>Intent</label>
              <input name="intent" required placeholder="What are we doing?" />
            </div>
            <div class="form__row">
              <label>Estimated minutes</label>
              <input name="estimated_minutes" type="number" value="25" min="5" max="180" />
            </div>
            <div class="form__row">
              <label>Project</label>
              <input name="project" placeholder="Optional" />
            </div>
            <div class="form__row">
              <label>Tags</label>
              <input name="tags" placeholder="comma,separated" />
            </div>
            <div class="form__row">
              <label>Difficulty</label>
              <select name="difficulty_preference">
                <option value="auto">auto</option>
                <option value="easy">easy</option>
                <option value="medium">medium</option>
                <option value="hard">hard</option>
              </select>
            </div>
            <button class="btn btn--primary" type="submit">Start Focus</button>
          </form>

          <form id="endForm" class="form">
            <div class="form__row">
              <label>Session ID</label>
              <input name="session_id" id="sessionIdInput" placeholder="auto-filled when started" />
            </div>
            <div class="form__row">
              <label>Actual minutes</label>
              <input name="actual_minutes" type="number" value="25" min="1" max="600" required />
            </div>
            <div class="form__row">
              <label>Mood (1–10)</label>
              <input name="mood" type="number" value="5" min="1" max="10" />
            </div>
            <div class="form__row">
              <label>Notes</label>
              <textarea name="notes" rows="3" placeholder="Quick reflection"></textarea>
            </div>
            <div class="actions">
              <button class="btn btn--secondary" type="submit">End Focus</button>
              <button id="btnClearSession" class="btn btn--ghost" type="button">Clear Active Session</button>
            </div>
          </form>
        </div>
      </section>

      <section class="panel">
        <div class="panel__title">Achievements</div>
        <div id="achievements" class="achievements"></div>
      </section>

      <section class="panel">
        <div class="panel__title">Events</div>
        <div id="events" class="events"></div>
      </section>
    </main>

    <script src="/ui/assets/app.js"></script>
  </body>
</html>
```

- [ ] **Step 3: Create `web/styles.css`**

```css
:root {
  --bg: #0b0f14;
  --panel: #101823;
  --panel2: #0f1620;
  --text: #e7eef7;
  --muted: #93a4b8;
  --border: rgba(231, 238, 247, 0.12);
  --good: #2dd4bf;
  --bad: #fb7185;
  --warn: #fbbf24;
  --accent: #60a5fa;
  --shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  --radius: 14px;
}

* { box-sizing: border-box; }
html, body { height: 100%; }
body {
  margin: 0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji",
    "Segoe UI Emoji";
  background: radial-gradient(1200px 600px at 20% 10%, rgba(96, 165, 250, 0.18), transparent 55%),
    radial-gradient(1000px 700px at 80% 30%, rgba(45, 212, 191, 0.12), transparent 60%),
    var(--bg);
  color: var(--text);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 18px;
  position: sticky;
  top: 0;
  background: rgba(11, 15, 20, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
}

.brand__title { font-weight: 800; letter-spacing: 0.06em; }
.brand__sub { color: var(--muted); font-size: 12px; margin-top: 2px; }

.topbar__right { display: flex; align-items: center; gap: 12px; }

.pill {
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: 999px;
  font-size: 12px;
  letter-spacing: 0.08em;
}
.pill--online { border-color: rgba(45, 212, 191, 0.5); color: var(--good); }
.pill--offline { border-color: rgba(251, 113, 133, 0.5); color: var(--bad); }

.hud { display: flex; gap: 10px; align-items: center; }
.hud__item { font-size: 12px; color: var(--text); border: 1px solid var(--border); border-radius: 999px; padding: 6px 10px; }
.hud__label { color: var(--muted); margin-right: 6px; }

.grid {
  padding: 18px;
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 14px;
}

.panel {
  background: linear-gradient(180deg, rgba(16, 24, 35, 0.92), rgba(15, 22, 32, 0.92));
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 14px;
  min-height: 140px;
}

.panel__title {
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text);
}
.panel__title--spaced { margin-top: 12px; }

.panel:nth-child(1) { grid-column: span 4; }
.panel:nth-child(2) { grid-column: span 4; }
.panel:nth-child(3) { grid-column: span 4; }
.panel:nth-child(4) { grid-column: span 6; }
.panel:nth-child(5) { grid-column: span 3; }
.panel:nth-child(6) { grid-column: span 3; }

@media (max-width: 1100px) {
  .panel { grid-column: span 12 !important; }
}

.tiles { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.tile {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px;
  background: rgba(0, 0, 0, 0.18);
}
.tile__name { font-weight: 700; font-size: 13px; }
.tile__state { font-size: 12px; color: var(--muted); margin-top: 6px; }
.tile--on { border-color: rgba(45, 212, 191, 0.5); }
.tile--off { border-color: rgba(251, 113, 133, 0.4); }

.btn {
  appearance: none;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 12px;
  color: var(--text);
  background: rgba(0, 0, 0, 0.18);
  cursor: pointer;
  font-weight: 700;
}
.btn:focus { outline: 2px solid rgba(96, 165, 250, 0.7); outline-offset: 2px; }
.btn--primary { border-color: rgba(96, 165, 250, 0.6); }
.btn--secondary { border-color: rgba(45, 212, 191, 0.5); }
.btn--ghost { border-color: rgba(231, 238, 247, 0.2); color: var(--muted); }

.actions { display: flex; gap: 10px; flex-wrap: wrap; }

.json {
  background: rgba(0, 0, 0, 0.22);
  border: 1px solid rgba(231, 238, 247, 0.14);
  border-radius: 12px;
  padding: 10px;
  overflow: auto;
  max-height: 320px;
  margin: 0;
  color: rgba(231, 238, 247, 0.92);
}
.json--output { max-height: 240px; }

.panel__tabs { display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
.tab { font-size: 12px; padding: 8px 10px; border-radius: 999px; border: 1px solid var(--border); background: rgba(0,0,0,0.16); color: var(--muted); cursor: pointer; }
.tab.is-active { color: var(--text); border-color: rgba(96, 165, 250, 0.55); }

.forms { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 1100px) { .forms { grid-template-columns: 1fr; } }

.form { display: grid; gap: 10px; }
.form__row { display: grid; gap: 6px; }
label { font-size: 12px; color: var(--muted); }
input, select, textarea {
  width: 100%;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(231, 238, 247, 0.16);
  background: rgba(0, 0, 0, 0.18);
  color: var(--text);
}

.achievements { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
@media (max-width: 900px) { .achievements { grid-template-columns: repeat(2, 1fr); } }
.badge { border: 1px solid var(--border); border-radius: 12px; padding: 10px; background: rgba(0,0,0,0.16); }
.badge__name { font-weight: 700; font-size: 13px; }
.badge__state { font-size: 12px; color: var(--muted); margin-top: 6px; }
.badge--on { border-color: rgba(45, 212, 191, 0.45); }
.badge--off { border-color: rgba(231, 238, 247, 0.14); opacity: 0.8; }

.events { display: grid; gap: 10px; }
.event { border: 1px solid rgba(231, 238, 247, 0.14); border-radius: 12px; padding: 10px; background: rgba(0,0,0,0.14); }
.event__top { display: flex; justify-content: space-between; gap: 10px; }
.event__type { font-weight: 800; font-size: 12px; letter-spacing: 0.06em; color: var(--accent); }
.event__ts { font-size: 12px; color: var(--muted); }
.event__summary { margin-top: 6px; font-size: 13px; }

@media (prefers-reduced-motion: reduce) {
  * { scroll-behavior: auto !important; transition: none !important; animation: none !important; }
}
```

- [ ] **Step 4: Create `web/app.js`**

```js
const ACTIVE_SESSION_KEY = "hyper_brain_active_session_id";

function $(id) {
  return document.getElementById(id);
}

function pretty(obj) {
  return JSON.stringify(obj, null, 2);
}

async function fetchJson(url, options) {
  const res = await fetch(url, options);
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { raw: text };
  }
  if (!res.ok) {
    const err = new Error("Request failed");
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

function setConnection(online, version) {
  const pill = $("connectionPill");
  pill.classList.toggle("pill--online", online);
  pill.classList.toggle("pill--offline", !online);
  pill.textContent = online ? `ONLINE v${version || "?"}` : "OFFLINE";
}

function renderTiles(services) {
  const root = $("tiles");
  root.innerHTML = "";
  const entries = Object.entries(services || {});
  for (const [name, ok] of entries) {
    const el = document.createElement("div");
    el.className = `tile ${ok ? "tile--on" : "tile--off"}`;
    el.innerHTML = `<div class="tile__name">${name}</div><div class="tile__state">${ok ? "online" : "offline"}</div>`;
    root.appendChild(el);
  }
}

function renderEvents(events) {
  const root = $("events");
  root.innerHTML = "";
  for (const e of events || []) {
    const el = document.createElement("div");
    el.className = "event";
    el.innerHTML = `
      <div class="event__top">
        <div class="event__type">${e.type || "event"}</div>
        <div class="event__ts">${e.ts || ""}</div>
      </div>
      <div class="event__summary">${e.summary || ""}</div>
    `;
    root.appendChild(el);
  }
}

function renderAchievements(summary) {
  const root = $("achievements");
  root.innerHTML = "";

  const streak = summary?.streaks?.current_streak || 0;
  const sessions7d = summary?.sessions_7d || 0;

  const badges = [
    { name: "First Focus", on: sessions7d >= 1, state: sessions7d >= 1 ? "unlocked" : "locked" },
    { name: "3 Sessions / 7d", on: sessions7d >= 3, state: sessions7d >= 3 ? "unlocked" : "locked" },
    { name: "7 Sessions / 7d", on: sessions7d >= 7, state: sessions7d >= 7 ? "unlocked" : "locked" },
    { name: "Streak 3", on: streak >= 3, state: streak >= 3 ? "unlocked" : "locked" },
    { name: "Streak 7", on: streak >= 7, state: streak >= 7 ? "unlocked" : "locked" },
    { name: "Recovery Token", on: (summary?.streaks?.recovery_tokens || 0) > 0, state: "available" },
  ];

  while (badges.length < 12) badges.push({ name: `Badge ${badges.length + 1}`, on: false, state: "locked" });

  for (const b of badges.slice(0, 12)) {
    const el = document.createElement("div");
    el.className = `badge ${b.on ? "badge--on" : "badge--off"}`;
    el.innerHTML = `<div class="badge__name">${b.name}</div><div class="badge__state">${b.state}</div>`;
    root.appendChild(el);
  }
}

function setHud(health, summary) {
  $("hudLevel").textContent = health?.level ?? "—";
  $("hudXp").textContent = summary?.xp_total_7d ?? "—";
  $("hudCoins").textContent = summary?.coins_total_7d ?? "—";
  $("hudStreak").textContent = summary?.streaks?.current_streak ?? "—";
}

function setActiveSessionId(id) {
  if (id) localStorage.setItem(ACTIVE_SESSION_KEY, id);
  else localStorage.removeItem(ACTIVE_SESSION_KEY);
  $("sessionIdInput").value = localStorage.getItem(ACTIVE_SESSION_KEY) || "";
}

async function refreshAll() {
  try {
    const [health, focus, events, game] = await Promise.all([
      fetchJson("/health"),
      fetchJson("/focus/status"),
      fetchJson("/events?limit=10"),
      fetchJson("/gamification/summary"),
    ]);

    setConnection(true, health.version);
    renderTiles(health.services);
    setHud(health, game);
    renderAchievements(game);
    renderEvents(events.events);

    const store = { health, focus, game };
    window.__jsonStore = store;

    const activeTab = document.querySelector(".tab.is-active")?.dataset?.json || "health";
    if (activeTab === "health") $("jsonPanel").textContent = pretty(health);
    if (activeTab === "focus") $("jsonPanel").textContent = pretty(focus);
    if (activeTab === "game") $("jsonPanel").textContent = pretty(game);
  } catch (e) {
    setConnection(false);
    $("outputPanel").textContent = pretty({ error: true, status: e.status, data: e.data });
  }
}

function setJsonTab(tab) {
  document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("is-active", b.dataset.json === tab));
  const store = window.__jsonStore || {};
  if (tab === "health") $("jsonPanel").textContent = pretty(store.health || {});
  if (tab === "focus") $("jsonPanel").textContent = pretty(store.focus || {});
  if (tab === "game") $("jsonPanel").textContent = pretty(store.game || {});
}

function wire() {
  document.querySelectorAll(".tab").forEach((b) => {
    b.addEventListener("click", () => setJsonTab(b.dataset.json));
  });
  setJsonTab("health");

  $("btnBriefing").addEventListener("click", async () => {
    try {
      const data = await fetchJson("/briefing/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      $("outputPanel").textContent = pretty(data);
      await refreshAll();
    } catch (e) {
      $("outputPanel").textContent = pretty({ error: true, status: e.status, data: e.data });
    }
  });

  $("btnSnapshot").addEventListener("click", async () => {
    try {
      const data = await fetchJson("/focus/snapshot", { method: "POST" });
      $("outputPanel").textContent = pretty(data);
      await refreshAll();
    } catch (e) {
      $("outputPanel").textContent = pretty({ error: true, status: e.status, data: e.data });
    }
  });

  $("startForm").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const fd = new FormData(ev.currentTarget);
    const tags = String(fd.get("tags") || "")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const payload = {
      intent: String(fd.get("intent") || ""),
      estimated_minutes: Number(fd.get("estimated_minutes") || 25),
      project: String(fd.get("project") || "") || null,
      tags,
      difficulty_preference: String(fd.get("difficulty_preference") || "auto"),
    };

    try {
      const data = await fetchJson("/focus/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const id = data?.session?.id;
      if (id) setActiveSessionId(id);
      $("outputPanel").textContent = pretty(data);
      await refreshAll();
    } catch (e) {
      $("outputPanel").textContent = pretty({ error: true, status: e.status, data: e.data });
    }
  });

  $("endForm").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const fd = new FormData(ev.currentTarget);
    const payload = {
      session_id: String(fd.get("session_id") || ""),
      actual_minutes: Number(fd.get("actual_minutes") || 0),
      mood: Number(fd.get("mood") || 5),
      notes: String(fd.get("notes") || ""),
    };

    try {
      const data = await fetchJson("/focus/end", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setActiveSessionId(null);
      $("outputPanel").textContent = pretty(data);
      await refreshAll();
    } catch (e) {
      $("outputPanel").textContent = pretty({ error: true, status: e.status, data: e.data });
    }
  });

  $("btnClearSession").addEventListener("click", () => setActiveSessionId(null));

  setActiveSessionId(localStorage.getItem(ACTIVE_SESSION_KEY));
}

wire();
refreshAll();
setInterval(refreshAll, 5000);
```

- [ ] **Step 5: Commit**

```powershell
git add web/index.html web/styles.css web/app.js hyper_brain_core.py
git commit -m "feat: serve systems-first command center UI at /ui"
```

---

### Task 6: Ensure Docker image includes `web/` assets

**Files:**
- Modify: `Dockerfile.hyper-brain`

- [ ] **Step 1: Copy `web/` into the image**

Update `Dockerfile.hyper-brain` to include:

```dockerfile
COPY web ./web
```

Placed after:
```dockerfile
COPY *.py ./
```

- [ ] **Step 2: Build container**

Run:
```powershell
docker build -f Dockerfile.hyper-brain -t hyper-brain:dev .
```

Expected: succeeds.

- [ ] **Step 3: Commit**

```powershell
git add Dockerfile.hyper-brain
git commit -m "chore: include web assets in hyper-brain image"
```

---

### Task 7: Manual verification (local Python)

**Files:**
- No changes expected

- [ ] **Step 1: Run the API**

Run:
```powershell
python hyper_brain_core.py
```

Expected: server starts; `/health` responds.

- [ ] **Step 2: Open UI**

Open:
- `http://localhost:8100/ui`

Expected:
- Connection pill shows ONLINE + version
- Tiles render services
- Events list is visible (may be empty initially)

- [ ] **Step 3: Start Focus**

Expected:
- Start Focus returns `session.id`
- Session id auto-fills End Focus
- `/events` shows a `focus_start` event

- [ ] **Step 4: End Focus**

Expected:
- End Focus clears stored session id
- `/gamification/summary` totals change after at least one saved session note
- `/events` shows a `focus_end` event

- [ ] **Step 5: Briefing + Snapshot**

Expected:
- Output panel shows JSON response
- `/events` shows `briefing` and `snapshot`

---

### Task 8: Manual verification (Docker Compose)

**Files:**
- No changes expected

- [ ] **Step 1: Start container**

Run:
```powershell
docker compose -f docker-compose.hyper-brain.yml up -d --build
```

Expected: container becomes healthy.

- [ ] **Step 2: Open UI**

Open:
- `http://localhost:8100/ui`

Expected: same behavior as local Python run.

---

## Plan Self-Review (completed before execution)
- Spec coverage: UI, `/events`, `/gamification/summary`, focus start/end, briefing, snapshot, Docker inclusion
- Placeholder scan: no TBD/TODO steps required for MVP
- Type consistency: client payload matches `FocusSessionStart` and `FocusSessionEnd` models
