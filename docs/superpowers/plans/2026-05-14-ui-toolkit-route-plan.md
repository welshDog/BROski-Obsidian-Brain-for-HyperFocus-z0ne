# UI Toolkit Route + Nav Tabs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Serve `web/toolkit.html` at `GET /ui/toolkit` and add a nav tab link in the Command Center so you can jump between `/ui` and `/ui/toolkit`.

**Architecture:** Add a small FastAPI route returning `FileResponse(toolkit.html)`. Add a minimal nav in `web/index.html` and shared CSS tokens in `web/styles.css`.

**Tech Stack:** FastAPI, static HTML/CSS

---

### Task 1: Add `/ui/toolkit` route

**Files:**
- Modify: `h:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/hyper_brain_core.py`

- [ ] Add:
  - `@app.get("/ui/toolkit")` -> `FileResponse(os.path.join(WEB_DIR, "toolkit.html"))`

- [ ] Verify:

```powershell
python -m uvicorn hyper_brain_core:app --host 0.0.0.0 --port 8100
```

Then:

```powershell
(Invoke-WebRequest -UseBasicParsing http://localhost:8100/ui/toolkit).StatusCode
```

Expected: `200`

---

### Task 2: Add nav tabs to Command Center

**Files:**
- Modify: `h:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/web/index.html`
- Modify: `h:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/web/styles.css`

- [ ] Add a nav with links:
  - `/ui` (active)
  - `/ui/toolkit`

- [ ] Add minimal CSS for `.nav-tabs` / `.nav-tab` that matches existing dark theme.

---

### Task 3: Smoke test

**Files:**
- No changes expected

- [ ] Load:
  - `http://localhost:8100/ui`
  - click “Tool Kit” -> `http://localhost:8100/ui/toolkit`
  - click “Command Center” -> `http://localhost:8100/ui`

